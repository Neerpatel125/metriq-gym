"""
Bernstein-Vazirani Benchmark for metriq-gym
Credit to QED-C for implementing the benchmark.

The benchmark generates N circuits for X qubits ranging from min_qubits to max_qubits.
Each circuit is then run, and the metrics are computed.
"""

from dataclasses import dataclass

from qbraid import GateModelResultData, QuantumDevice, QuantumJob
from qbraid.runtime.result_data import MeasCount

from metriq_gym.benchmarks.benchmark import Benchmark, BenchmarkData, BenchmarkResult
from metriq_gym.helpers.task_helpers import flatten_counts

from qedc.bernstein_vazirani.bv_benchmark import run, analyze_and_print_result, qedc_benchmarks_init
from qedc._common import metrics

from qiskit import QuantumCircuit


"""
Type: QEDC_Metrics
Description: 
    The structure for all returned QEDC circuit metrics. 
    The first key represents the number of qubits for the group of circuits.
    The second key represents the unique identifier (secret str) for a circuit. 
    The third key represents the metric being stored.
Example:
{
'3':    {
        '1': {'create_time': 0.16371703147888184,
            'fidelity': 1.0,
            'hf_fidelity': 1.0},
        '2': {'create_time': 0.0005087852478027344,
            'fidelity': 1.0,
            'hf_fidelity': 1.0}
        },
'4':    {
        '1': {'create_time': 0.0005209445953369141,
            'fidelity': 1.0,
            'hf_fidelity': 1.0},
        '3': {'create_time': 0.00047206878662109375,
            'fidelity': 1.0,
            'hf_fidelity': 1.0},
        '5': {'create_time': 0.0005078315734863281,
            'fidelity': 1.0,
            'hf_fidelity': 1.0}
        }
}
"""
QEDC_Metrics = dict[str, dict[str, dict[str, float]]]


class BernsteinVaziraniResult(BenchmarkResult):
    """Stores the results from running Bernstein-Vazirani benchmark.
    Results:
        circuit_metrics: Stores all QED-C metrics to output.
    """

    circuit_metrics: QEDC_Metrics


@dataclass
class BernsteinVaziraniData(BenchmarkData):
    """Stores the input parameters or metadata for Bernstein-Vazirani benchmark.
    Parameters/Metadata:
        shots: number of shots for each circuit to be ran with.
        min_qubits: minimum number of qubits to start generating circuits for the benchmark.
        max_qubits: maximum number of qubits to stop generating circuits for the benchmark.
        skip_qubits: the step size for generating circuits from the min to max qubit sizes.
        max_circuits: maximum number of circuits generated for each qubit size in the benchmark.
        circuit_metrics: stores QED-C circuit creation metrics data.
        circuits: the list of quantum circuits ran, it's needed to poll the results with QED-C.
        circuit_identifiers: the unique identifiers for circuits (num qubits, secret str),
                             used to preserve order when polling.
    """

    shots: int
    min_qubits: int
    max_qubits: int
    skip_qubits: int
    max_circuits: int
    circuit_metrics: QEDC_Metrics
    circuits: list[QuantumCircuit]
    circuit_identifiers: list[tuple[str, str]]


def analyze_results(job_data: BernsteinVaziraniData, counts_list: list[MeasCount]) -> QEDC_Metrics:
    """
    Iterates over each circuit group and secret int to process results.
    Uses QED-C submodule to obtain calculations.

    Args:
        job_data: the BernsteinVaziraniData object for the job.
        counts_list: a list of all counts objects, each index corresponds to a circuit.

    Returns:
        circuit_metrics: the updated circuit metrics in QED-C's format.
    """

    class CountsWrapper:
        """
        A wrapper class to enable support with QED-C's method to analyze results.
        """

        def __init__(self, qc: QuantumCircuit, counts: dict[str, int]):
            self.qc = qc
            self.counts = counts

        def get_counts(self, qc):
            if qc == self.qc:
                return self.counts

    # Initialize metrics module in QED-C submodule.
    qedc_benchmarks_init()

    # Restore circuit metrics dictionary from the dispatch data
    metrics.circuit_metrics = job_data.circuit_metrics

    # Iterate and get the metrics for each circuit in the list.
    for curr_idx, (num_qubits, s_str) in enumerate(job_data.circuit_identifiers):
        counts: dict[str, int] = counts_list[curr_idx]

        qc = job_data.circuits[curr_idx]

        result_object = CountsWrapper(qc, counts)

        _, fidelity = analyze_and_print_result(
            qc, result_object, int(num_qubits), int(s_str), job_data.shots
        )

        metrics.store_metric(int(num_qubits), int(s_str), "fidelity", fidelity)

    return metrics.circuit_metrics


class BernsteinVazirani(Benchmark):
    """Benchmark class for Bernstein-Vazirani experiments."""

    def dispatch_handler(self, device: QuantumDevice) -> BernsteinVaziraniData:
        # For more information on the parameters, view the schema for this benchmark.
        shots = self.params.shots
        min_qubits = self.params.min_qubits
        max_qubits = self.params.max_qubits
        skip_qubits = self.params.skip_qubits
        max_circuits = self.params.max_circuits

        # Call the QED-C submodule to get the circuits and creation information.
        circuits: dict[str, dict[str, QuantumCircuit]]
        circuits, circuit_metrics = run(
            min_qubits=min_qubits,
            max_qubits=max_qubits,
            skip_qubits=skip_qubits,
            max_circuits=max_circuits,
            num_shots=shots,
            method=1,
            get_circuits=True,
        )

        # Remove the subtitle key to keep our desired format.
        circuit_metrics.pop("subtitle", None)

        # Store the circuit identifiers and a flat list of circuits.
        circuit_identifiers = []
        flat_circuits = []
        for num_qubits in circuit_metrics.keys():
            for s_str in circuit_metrics[num_qubits].keys():
                circuit_identifiers.append((num_qubits, s_str))
                flat_circuits.append(circuits[num_qubits][s_str])

        return BernsteinVaziraniData.from_quantum_job(
            quantum_job=device.run(flat_circuits, shots=shots),
            shots=shots,
            min_qubits=min_qubits,
            max_qubits=max_qubits,
            skip_qubits=skip_qubits,
            max_circuits=max_circuits,
            circuit_metrics=circuit_metrics,
            circuits=flat_circuits,
            circuit_identifiers=circuit_identifiers,
        )

    def poll_handler(
        self,
        job_data: BernsteinVaziraniData,
        result_data: list[GateModelResultData],
        quantum_jobs: list[QuantumJob],
    ) -> BernsteinVaziraniResult:
        counts_list = flatten_counts(result_data)

        # Call the QED-C method after some pre-processing to obtain metrics.
        circuit_metrics = analyze_results(job_data, counts_list)

        return BernsteinVaziraniResult(circuit_metrics=circuit_metrics)
