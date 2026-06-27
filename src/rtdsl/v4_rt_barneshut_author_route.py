from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import subprocess
import time
from typing import Sequence

from .rt_barneshut_author_contract import (
    RT_BARNESHUT_AUTHOR_COMMIT,
    RT_BARNESHUT_AUTHOR_CONTRACT_VERSION,
    RtBarnesHutFileType,
    parse_rt_barneshut_author_stdout,
    run_rt_barneshut_cpu_author_semantics_oracle,
    validate_rt_barneshut_author_contract_summary,
    write_trimmed_rt_barneshut_author_dataset,
)


V4_RT_BARNESHUT_AUTHOR_ROUTE_VERSION = "rtdl.v4.rt_barneshut.external_author_rt_core_reference_route.v1"
V4_RT_BARNESHUT_AUTHOR_ROUTE_STATUS = "external_author_rt_core_reference_route_ready_not_native_v4_operator"


@dataclass(frozen=True)
class V4RtBarnesHutAuthorBinaryRun:
    cmd: tuple[str, ...]
    returncode: int
    wall_seconds: float
    parsed_stdout: dict[str, float | int]
    stdout_tail: tuple[str, ...]
    stderr_tail: tuple[str, ...]


@dataclass(frozen=True)
class V4RtBarnesHutAuthorRouteResult:
    status: str
    route_version: str
    contract_version: str
    author_commit: str
    source_dataset: str
    trimmed_dataset: str
    file_type: RtBarnesHutFileType
    limit: int
    route_kind: str
    rt_core_execution: bool
    external_author_binary: bool
    native_v4_operator: bool
    v4_performance_claim_authorized: bool
    author_binary_run: V4RtBarnesHutAuthorBinaryRun
    rtdl_cpu_author_semantics_oracle: dict[str, object]
    checksum_validation: dict[str, object]
    phase_seconds: dict[str, float | None]
    claim_boundary: dict[str, bool | str]

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def _tail(text: str, *, count: int = 40) -> tuple[str, ...]:
    return tuple(text.splitlines()[-count:])


def _checksum_validation(
    *,
    parsed_stdout: dict[str, float | int],
    oracle_checksum: float,
) -> dict[str, object]:
    if "rt_force_checksum" not in parsed_stdout:
        return {
            "available": False,
            "author_rt_force_checksum": None,
            "rtdl_cpu_oracle_checksum": oracle_checksum,
            "absolute_error": None,
            "relative_error": None,
            "passes_float_output_tolerance": False,
            "reason": "author binary did not emit RT Force checksum; apply tools/rtbarneshut_author_force_checksum_audit.patch for audit runs",
        }
    author_checksum = float(parsed_stdout["rt_force_checksum"])
    absolute_error = abs(author_checksum - oracle_checksum)
    relative_error = absolute_error / abs(oracle_checksum) if oracle_checksum else absolute_error
    return {
        "available": True,
        "author_rt_force_checksum": author_checksum,
        "rtdl_cpu_oracle_checksum": oracle_checksum,
        "absolute_error": absolute_error,
        "relative_error": relative_error,
        "passes_float_output_tolerance": relative_error <= 1.0e-4,
        "reason": "checksum compares author RT output against RTDL author-semantics CPU oracle",
    }


def run_v4_rt_barneshut_external_author_rt_core_route(
    *,
    dataset: str | Path,
    file_type: RtBarnesHutFileType,
    limit: int,
    author_binary: str | Path,
    trimmed_dataset: str | Path,
    author_command_prefix: Sequence[str] = (),
) -> V4RtBarnesHutAuthorRouteResult:
    if limit <= 0:
        raise ValueError("limit must be positive")
    dataset = Path(dataset)
    trimmed_dataset = Path(trimmed_dataset)
    author_binary = Path(author_binary)

    write_trimmed_rt_barneshut_author_dataset(
        dataset,
        trimmed_dataset,
        file_type=file_type,
        limit=limit,
    )
    oracle = run_rt_barneshut_cpu_author_semantics_oracle(
        trimmed_dataset,
        file_type=file_type,
        limit=limit,
    )
    validate_rt_barneshut_author_contract_summary(oracle)

    cmd = tuple(str(part) for part in (*author_command_prefix, author_binary, file_type, trimmed_dataset))
    start = time.perf_counter()
    proc = subprocess.run(cmd, text=True, capture_output=True, check=False)
    wall = time.perf_counter() - start
    parsed = parse_rt_barneshut_author_stdout(proc.stdout)
    binary_run = V4RtBarnesHutAuthorBinaryRun(
        cmd=cmd,
        returncode=proc.returncode,
        wall_seconds=wall,
        parsed_stdout=parsed,
        stdout_tail=_tail(proc.stdout),
        stderr_tail=_tail(proc.stderr),
    )
    checksum = _checksum_validation(
        parsed_stdout=parsed,
        oracle_checksum=oracle.force_checksum,
    )

    return V4RtBarnesHutAuthorRouteResult(
        status=V4_RT_BARNESHUT_AUTHOR_ROUTE_STATUS,
        route_version=V4_RT_BARNESHUT_AUTHOR_ROUTE_VERSION,
        contract_version=RT_BARNESHUT_AUTHOR_CONTRACT_VERSION,
        author_commit=RT_BARNESHUT_AUTHOR_COMMIT,
        source_dataset=str(dataset),
        trimmed_dataset=str(trimmed_dataset),
        file_type=file_type,
        limit=limit,
        route_kind="external_author_rt_core_reference_route",
        rt_core_execution=True,
        external_author_binary=True,
        native_v4_operator=False,
        v4_performance_claim_authorized=False,
        author_binary_run=binary_run,
        rtdl_cpu_author_semantics_oracle=asdict(oracle),
        checksum_validation=checksum,
        phase_seconds={
            "preprocessing_seconds": (
                float(parsed["preprocessing_seconds"]) if "preprocessing_seconds" in parsed else None
            ),
            "rt_force_seconds": float(parsed["rt_force_seconds"]) if "rt_force_seconds" in parsed else None,
            "execution_seconds": float(parsed["execution_seconds"]) if "execution_seconds" in parsed else None,
            "wall_seconds": wall,
        },
        claim_boundary={
            "same_input_author_contract": True,
            "same_force_checksum_when_available": bool(checksum["passes_float_output_tolerance"]),
            "rt_core_execution": True,
            "external_author_binary": True,
            "native_v4_operator": False,
            "v4_performance_claim_authorized": False,
            "v2_v3_v4_speedup_claim_authorized": False,
            "public_release_claim_authorized": False,
            "purpose": "same-semantics RT-core reference route; not a native V4 operator implementation",
        },
    )


def validate_v4_rt_barneshut_author_route_result(result: V4RtBarnesHutAuthorRouteResult) -> None:
    if result.route_version != V4_RT_BARNESHUT_AUTHOR_ROUTE_VERSION:
        raise ValueError("unexpected route version")
    if result.author_binary_run.returncode != 0:
        raise ValueError("author RT-core route failed")
    if not result.rt_core_execution:
        raise ValueError("route must record RT-core execution")
    if not result.external_author_binary:
        raise ValueError("Goal4761 route must honestly record external author binary use")
    if result.native_v4_operator:
        raise ValueError("external author route must not claim native V4 operator status")
    if result.v4_performance_claim_authorized:
        raise ValueError("external author route must not authorize V4 performance claims")
    if result.checksum_validation["available"] and not result.checksum_validation["passes_float_output_tolerance"]:
        raise ValueError("author RT checksum does not match RTDL CPU oracle")
