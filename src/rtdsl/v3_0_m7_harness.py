from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from .v3_0_execution_graph import BACKENDS
from .v3_0_execution_graph import PARTNERS
from .v3_0_execution_graph import ClaimBoundary
from .v3_0_execution_graph import GraphValidationError
from .v3_0_execution_graph import V3_EXECUTION_GRAPH_IR_VERSION
from .v3_0_execution_graph import validate_v3_public_name
from .v3_0_instrumentation import InstrumentationPacket


V3_BENCHMARK_HARNESS_VERSION = "rtdl.v3_0.benchmark_harness.m7"
V3_BENCHMARK_HARNESS_STATUS = "m7_harness_skeleton_no_public_claim"
TIMING_BASES = (
    "cold_total",
    "warm_total",
    "steady_state",
    "phase_split",
    "external_system_reported",
)
COMPARISON_ROLES = (
    "rtdl_optix",
    "rtdl_embree",
    "external_system",
    "reference",
)


@dataclass(frozen=True)
class BenchmarkHarnessRow:
    row_id: str
    graph_id: str
    comparison_group: str
    comparison_role: str
    backend: str
    partner: str
    dataset: str
    scale: str
    hardware: str
    timing_basis: str
    same_contract_key: str
    instrumentation: InstrumentationPacket
    warmups: int
    repeats: int
    includes_build: bool
    includes_upload: bool
    includes_download: bool
    includes_validation: bool
    external_code_version: str | None = None
    external_timing_basis: str | None = None

    def __post_init__(self) -> None:
        validate_v3_public_name(self.row_id, label="benchmark row id")
        validate_v3_public_name(self.graph_id, label="benchmark graph id")
        validate_v3_public_name(self.comparison_group, label="comparison group")
        if self.comparison_role not in COMPARISON_ROLES:
            raise GraphValidationError("unsupported comparison role")
        if self.backend not in (*BACKENDS, "external"):
            raise GraphValidationError("unsupported benchmark row backend")
        if self.partner not in (*PARTNERS, "none", "external"):
            raise GraphValidationError("unsupported benchmark row partner")
        if not str(self.dataset).strip() or not str(self.scale).strip() or not str(self.hardware).strip():
            raise GraphValidationError("benchmark row requires dataset, scale, and hardware")
        if self.timing_basis not in TIMING_BASES:
            raise GraphValidationError("unsupported timing basis")
        if not str(self.same_contract_key).strip():
            raise GraphValidationError("benchmark row requires same_contract_key")
        if int(self.warmups) < 0 or int(self.repeats) <= 0:
            raise GraphValidationError("benchmark warmups/repeats are invalid")
        if not self.instrumentation.phase_complete:
            raise GraphValidationError("benchmark row requires phase-complete instrumentation")
        if self.comparison_role == "external_system":
            if not str(self.external_code_version or "").strip():
                raise GraphValidationError("external comparison row requires external_code_version")
            if not str(self.external_timing_basis or "").strip():
                raise GraphValidationError("external comparison row requires external_timing_basis")
        object.__setattr__(self, "warmups", int(self.warmups))
        object.__setattr__(self, "repeats", int(self.repeats))

    def to_metadata(self) -> dict[str, object]:
        return {
            "row_id": self.row_id,
            "graph_id": self.graph_id,
            "comparison_group": self.comparison_group,
            "comparison_role": self.comparison_role,
            "backend": self.backend,
            "partner": self.partner,
            "dataset": self.dataset,
            "scale": self.scale,
            "hardware": self.hardware,
            "timing_basis": self.timing_basis,
            "same_contract_key": self.same_contract_key,
            "instrumentation": self.instrumentation.to_metadata(),
            "warmups": self.warmups,
            "repeats": self.repeats,
            "includes_build": bool(self.includes_build),
            "includes_upload": bool(self.includes_upload),
            "includes_download": bool(self.includes_download),
            "includes_validation": bool(self.includes_validation),
            "external_code_version": self.external_code_version,
            "external_timing_basis": self.external_timing_basis,
            "public_claim_authorized": False,
        }


@dataclass(frozen=True)
class BenchmarkHarnessPacket:
    packet_id: str
    rows: tuple[BenchmarkHarnessRow, ...]
    claim_boundary: ClaimBoundary = field(default_factory=ClaimBoundary)
    ir_version: str = V3_EXECUTION_GRAPH_IR_VERSION
    harness_version: str = V3_BENCHMARK_HARNESS_VERSION

    def __post_init__(self) -> None:
        validate_v3_public_name(self.packet_id, label="benchmark packet id")
        if self.ir_version != V3_EXECUTION_GRAPH_IR_VERSION:
            raise GraphValidationError("unexpected benchmark harness IR version")
        if self.harness_version != V3_BENCHMARK_HARNESS_VERSION:
            raise GraphValidationError("unexpected benchmark harness version")
        rows = tuple(self.rows)
        if not rows:
            raise GraphValidationError("benchmark harness packet requires rows")
        row_ids = tuple(row.row_id for row in rows)
        if len(set(row_ids)) != len(row_ids):
            raise GraphValidationError("benchmark harness row ids must be unique")
        _validate_comparison_groups(rows)
        object.__setattr__(self, "rows", rows)

    def to_metadata(self) -> dict[str, object]:
        return {
            "packet_id": self.packet_id,
            "ir_version": self.ir_version,
            "harness_version": self.harness_version,
            "status": V3_BENCHMARK_HARNESS_STATUS,
            "rows": tuple(row.to_metadata() for row in self.rows),
            "claim_boundary": self.claim_boundary.to_metadata(),
            "public_claim_authorized": False,
        }


def validate_benchmark_harness_packet(packet: BenchmarkHarnessPacket) -> dict[str, object]:
    payload = packet.to_metadata()
    return {
        "status": V3_BENCHMARK_HARNESS_STATUS,
        "packet_id": payload["packet_id"],
        "row_count": len(packet.rows),
        "comparison_groups": tuple(sorted({row.comparison_group for row in packet.rows})),
        "public_claim_authorized": False,
    }


def _validate_comparison_groups(rows: tuple[BenchmarkHarnessRow, ...]) -> None:
    groups = sorted({row.comparison_group for row in rows})
    for group in groups:
        group_rows = tuple(row for row in rows if row.comparison_group == group)
        same_contract_keys = {row.same_contract_key for row in group_rows}
        if len(same_contract_keys) != 1:
            raise GraphValidationError("comparison group rows must share same_contract_key")
        roles = {row.comparison_role for row in group_rows}
        if "rtdl_optix" in roles and "rtdl_embree" not in roles:
            raise GraphValidationError("OptiX comparison groups require an Embree row")
        if "rtdl_embree" in roles and "rtdl_optix" not in roles:
            raise GraphValidationError("Embree comparison groups require an OptiX row")
        for row in group_rows:
            if row.comparison_role in {"rtdl_optix", "rtdl_embree"}:
                if not row.includes_build and row.timing_basis == "cold_total":
                    raise GraphValidationError("cold_total RTDL rows must include build")
