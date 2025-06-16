from enum import StrEnum

from metriq_gym.benchmarks.benchmark import Benchmark, BenchmarkData
from metriq_gym.benchmarks.qml_kernel import QMLKernel, QMLKernelData
from metriq_gym.benchmarks.clops import Clops, ClopsData
from metriq_gym.benchmarks.quantum_volume import QuantumVolume, QuantumVolumeData
from metriq_gym.benchmarks.bseq import BSEQ, BSEQData
from metriq_gym.benchmarks.mirror_circuits import MirrorCircuits, MirrorCircuitsData
from metriq_gym.benchmarks.wormhole import Wormhole, WormholeData
from metriq_gym.benchmarks.bernstein_vazirani import BernsteinVazirani, BernsteinVaziraniData


class JobType(StrEnum):
    BSEQ = "BSEQ"
    CLOPS = "CLOPS"
    QML_KERNEL = "QML Kernel"
    QUANTUM_VOLUME = "Quantum Volume"
    MIRROR_CIRCUITS = "Mirror Circuits"
    WORMHOLE = "Wormhole"
    BERNSTEIN_VAZIRANI = "Bernstein-Vazirani"


BENCHMARK_HANDLERS: dict[JobType, type[Benchmark]] = {
    JobType.BSEQ: BSEQ,
    JobType.CLOPS: Clops,
    JobType.QML_KERNEL: QMLKernel,
    JobType.QUANTUM_VOLUME: QuantumVolume,
    JobType.MIRROR_CIRCUITS: MirrorCircuits,
    JobType.WORMHOLE: Wormhole,
    JobType.BERNSTEIN_VAZIRANI: BernsteinVazirani,
}

BENCHMARK_DATA_CLASSES: dict[JobType, type[BenchmarkData]] = {
    JobType.BSEQ: BSEQData,
    JobType.CLOPS: ClopsData,
    JobType.QML_KERNEL: QMLKernelData,
    JobType.QUANTUM_VOLUME: QuantumVolumeData,
    JobType.MIRROR_CIRCUITS: MirrorCircuitsData,
    JobType.WORMHOLE: WormholeData,
    JobType.BERNSTEIN_VAZIRANI: BernsteinVaziraniData,
}

SCHEMA_MAPPING = {
    JobType.BSEQ: "bseq.schema.json",
    JobType.CLOPS: "clops.schema.json",
    JobType.QML_KERNEL: "qml_kernel.schema.json",
    JobType.QUANTUM_VOLUME: "quantum_volume.schema.json",
    JobType.MIRROR_CIRCUITS: "mirror_circuits.schema.json",
    JobType.WORMHOLE: "wormhole.schema.json",
    JobType.BERNSTEIN_VAZIRANI: "bernstein_vazirani.schema.json",
}


def get_available_benchmarks() -> list[str]:
    return [jt.value for jt in JobType]
