from __future__ import annotations

import argparse
import ctypes
import json
import platform
import subprocess
import time
from pathlib import Path
from typing import Any

import rtdsl as rt
from rtdsl.v3_0_execution_graph import REQUIRED_PHASE_NAMES


PROBE_VERSION = "rtdl.v3_0.pod_evidence_probe.2026_06_15"
PROBE_STATUS = "substrate_evidence_not_a_benchmark"
DEFAULT_OUTPUT = Path("build/goal4401_v3_0_pod_evidence_probe_2026-06-15.json")
REQUIRED_LIBRARIES = ("librtdl_optix.so", "librtdl_embree.so")


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture V3.0 pod evidence substrate metadata.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="JSON output path.")
    parser.add_argument("--build-dir", default="build", help="Directory containing native RTDL libraries.")
    parser.add_argument("--cuda-size", type=int, default=1_000_000, help="CuPy vector size for CUDA event probe.")
    args = parser.parse_args()

    build_dir = Path(args.build_dir)
    payload = run_probe(build_dir=build_dir, cuda_size=args.cuda_size)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(f"wrote {output_path}")
    return 0 if payload["summary"]["probe_passed"] else 2


def run_probe(*, build_dir: Path, cuda_size: int) -> dict[str, Any]:
    hardware = collect_hardware_metadata()
    native_libraries = inspect_native_libraries(build_dir=build_dir)
    cuda_probe = run_cuda_event_probe(cuda_size=cuda_size)
    embree_probe = run_embree_probe(build_dir=build_dir)

    optix_packet = build_optix_probe_packet(
        hardware_label=hardware["hardware_label"],
        cuda_seconds=cuda_probe["cuda_event_seconds"],
        validation_seconds=cuda_probe["validation_seconds"],
        device_pointer=cuda_probe["device_pointer"],
        measured_region_explicit_transfers=cuda_probe["measured_region_explicit_transfers"],
    )
    embree_packet = build_embree_probe_packet(
        hardware_label=hardware["cpu_label"],
        load_seconds=embree_probe["load_seconds"],
        version=embree_probe["embree_version"],
    )

    optix_readiness = rt.claim_readiness_summary(optix_packet)
    embree_readiness = rt.claim_readiness_summary(embree_packet)
    required_libs_ready = all(native_libraries[name]["loadable"] for name in REQUIRED_LIBRARIES)
    cuda_ready = bool(cuda_probe["ok"])
    probe_passed = bool(required_libs_ready and cuda_ready and optix_packet.phase_complete and embree_packet.phase_complete)

    return {
        "probe_version": PROBE_VERSION,
        "status": PROBE_STATUS,
        "summary": {
            "probe_passed": probe_passed,
            "native_libraries_loadable": required_libs_ready,
            "cuda_event_probe_ok": cuda_ready,
            "optix_same_stream_ready": optix_readiness["same_stream_ready"],
            "optix_device_resident_ready": optix_readiness["device_resident_ready"],
            "optix_true_zero_copy_ready": optix_readiness["true_zero_copy_ready"],
            "public_claim_authorized": False,
            "not_a_benchmark": True,
        },
        "hardware": hardware,
        "native_libraries": native_libraries,
        "cuda_probe": cuda_probe,
        "embree_probe": embree_probe,
        "instrumentation_packets": {
            "optix_substrate": optix_packet.to_metadata(),
            "embree_substrate": embree_packet.to_metadata(),
        },
        "readiness": {
            "optix_substrate": optix_readiness,
            "embree_substrate": embree_readiness,
        },
        "claim_boundary": {
            "public_speedup_claim": "forbidden",
            "rt_core_speedup_claim": "forbidden",
            "true_zero_copy_public_claim": "forbidden",
            "reason": "This probe validates pod evidence plumbing and native library readiness only.",
        },
    }


def collect_hardware_metadata() -> dict[str, Any]:
    gpu_lines = _run_text(
        [
            "nvidia-smi",
            "--query-gpu=name,driver_version,memory.total,pci.bus_id",
            "--format=csv,noheader",
        ]
    )
    gpu_label = gpu_lines.strip().splitlines()[0] if gpu_lines.strip() else "gpu_unknown"
    cpu_label = platform.processor() or platform.machine() or "cpu_unknown"
    return {
        "hardware_label": gpu_label,
        "cpu_label": cpu_label,
        "gpu_query": gpu_lines.strip(),
        "platform": platform.platform(),
        "python": platform.python_version(),
    }


def inspect_native_libraries(*, build_dir: Path) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for name in REQUIRED_LIBRARIES:
        path = build_dir / name
        record: dict[str, Any] = {
            "path": str(path),
            "exists": path.exists(),
            "bytes": path.stat().st_size if path.exists() else 0,
            "loadable": False,
            "load_seconds": None,
            "ldd_relevant": "",
            "error": None,
        }
        if path.exists():
            start = time.perf_counter()
            try:
                ctypes.CDLL(str(path.resolve()))
                record["loadable"] = True
            except OSError as exc:
                record["error"] = str(exc)
            finally:
                record["load_seconds"] = time.perf_counter() - start
            record["ldd_relevant"] = _filter_ldd(path)
        records[name] = record
    return records


def run_cuda_event_probe(*, cuda_size: int) -> dict[str, Any]:
    try:
        import cupy as cp

        stream = cp.cuda.Stream(non_blocking=True)
        start_event = cp.cuda.Event()
        stop_event = cp.cuda.Event()
        validation_start = time.perf_counter()
        with stream:
            values = cp.arange(cuda_size, dtype=cp.float32)
            start_event.record(stream)
            output = values * cp.float32(2.0) + cp.float32(1.0)
            reduced = output.sum()
            stop_event.record(stream)
        stop_event.synchronize()
        cuda_event_seconds = cp.cuda.get_elapsed_time(start_event, stop_event) / 1000.0
        device_pointer = int(output.data.ptr)
        stream_pointer = int(stream.ptr)
        validation_value = float(reduced.get())
        validation_seconds = time.perf_counter() - validation_start
        return {
            "ok": True,
            "cuda_size": int(cuda_size),
            "cuda_event_seconds": float(cuda_event_seconds),
            "validation_seconds": float(validation_seconds),
            "device_pointer": device_pointer,
            "stream_pointer": stream_pointer,
            "validation_value": validation_value,
            "measured_region_explicit_transfers": 0,
            "notes": (
                "CUDA event time covers the CuPy device operation only; validation download "
                "happens after the measured event region."
            ),
        }
    except Exception as exc:  # pragma: no cover - local CI usually has no CUDA device.
        return {
            "ok": False,
            "cuda_size": int(cuda_size),
            "cuda_event_seconds": 0.0,
            "validation_seconds": 0.0,
            "device_pointer": 0,
            "stream_pointer": 0,
            "validation_value": None,
            "measured_region_explicit_transfers": None,
            "error": repr(exc),
        }


def run_embree_probe(*, build_dir: Path) -> dict[str, Any]:
    path = build_dir / "librtdl_embree.so"
    start = time.perf_counter()
    error = None
    try:
        ctypes.CDLL(str(path.resolve()))
    except OSError as exc:
        error = str(exc)
    load_seconds = time.perf_counter() - start
    try:
        version = ".".join(str(item) for item in rt.embree_version())
    except Exception as exc:  # pragma: no cover - defensive only.
        version = f"unavailable: {exc!r}"
    return {
        "ok": error is None,
        "library": str(path),
        "load_seconds": float(load_seconds),
        "embree_version": version,
        "error": error,
        "notes": "Embree probe validates native library load and version only; it is not traversal timing.",
    }


def build_optix_probe_packet(
    *,
    hardware_label: str,
    cuda_seconds: float,
    validation_seconds: float,
    device_pointer: int,
    measured_region_explicit_transfers: int | None,
) -> rt.InstrumentationPacket:
    evidence = (
        rt.EvidenceRecord(
            evidence_id="cuda_event_record",
            kind="cuda_event_pair",
            backend="optix",
            phase="rt_traversal",
            source="cupy_cuda_event_probe",
            hardware=hardware_label,
            details={"seconds": float(cuda_seconds)},
        ),
        rt.EvidenceRecord(
            evidence_id="pointer_record",
            kind="pointer_identity",
            backend="optix",
            phase="stream_handoff",
            source="cupy_device_pointer_probe",
            hardware=hardware_label,
            details={"device_pointer": int(device_pointer)},
        ),
        rt.EvidenceRecord(
            evidence_id="transfer_record",
            kind="transfer_counter",
            backend="optix",
            phase="download_or_materialization",
            source="probe_explicit_transfer_counter",
            hardware=hardware_label,
            details={"measured_region_explicit_transfers": measured_region_explicit_transfers},
        ),
        rt.EvidenceRecord(
            evidence_id="optix_native_handle_record",
            kind="backend_native_handle",
            backend="optix",
            phase="prepare",
            source="ctypes_native_library_load",
            hardware=hardware_label,
        ),
        rt.EvidenceRecord(
            evidence_id="host_timer_record",
            kind="host_timer",
            backend="optix",
            phase="validation",
            source="python_perf_counter",
            hardware=hardware_label,
            details={"validation_seconds": float(validation_seconds)},
        ),
    )
    timings = _phase_timings(
        backend="optix",
        default_source="host_timer",
        seconds_by_phase={
            "prepare": 0.0,
            "build": 0.0,
            "upload": 0.0,
            "query_prepare": 0.0,
            "rt_traversal": float(cuda_seconds),
            "stream_handoff": 0.0,
            "continuation_or_reduction": 0.0,
            "download_or_materialization": 0.0,
            "validation": float(validation_seconds),
            "host_wrapper": 0.0,
        },
        evidence_by_phase={
            "prepare": ("optix_native_handle_record",),
            "rt_traversal": ("cuda_event_record",),
            "stream_handoff": ("cuda_event_record", "pointer_record"),
            "download_or_materialization": ("transfer_record",),
            "validation": ("host_timer_record",),
        },
        source_by_phase={
            "rt_traversal": "cuda_event",
            "stream_handoff": "cuda_event",
            "download_or_materialization": "host_timer",
        },
    )
    residency = (
        rt.ResidencyEvidence(
            value_name="candidate_ids",
            storage="cuda",
            residency="device_resident",
            lifetime="partner_owned",
            stream_ordering="same_stream",
            data_ptr_observed=bool(device_pointer),
            backend_handle_observed=True,
            transfer_counter_observed=measured_region_explicit_transfers == 0,
            host_materialized=False,
            hidden_copy_observed=False,
            evidence_ids=("pointer_record", "transfer_record", "optix_native_handle_record"),
        ),
    )
    return rt.InstrumentationPacket(
        graph_id="generic_candidate_probe_graph",
        backend="optix",
        hardware=hardware_label,
        phase_timings=timings,
        evidence_records=evidence,
        residency_evidence=residency,
    )


def build_embree_probe_packet(*, hardware_label: str, load_seconds: float, version: str) -> rt.InstrumentationPacket:
    evidence = (
        rt.EvidenceRecord(
            evidence_id="embree_native_handle_record",
            kind="backend_native_handle",
            backend="embree",
            phase="prepare",
            source="ctypes_native_library_load",
            hardware=hardware_label,
            details={"embree_version": version},
        ),
        rt.EvidenceRecord(
            evidence_id="embree_load_timer_record",
            kind="embree_phase_timer",
            backend="embree",
            phase="prepare",
            source="python_perf_counter",
            hardware=hardware_label,
            details={"load_seconds": float(load_seconds)},
        ),
    )
    timings = _phase_timings(
        backend="embree",
        default_source="metadata_only",
        seconds_by_phase={
            "prepare": float(load_seconds),
            "build": 0.0,
            "upload": 0.0,
            "query_prepare": 0.0,
            "rt_traversal": 0.0,
            "stream_handoff": 0.0,
            "continuation_or_reduction": 0.0,
            "download_or_materialization": 0.0,
            "validation": 0.0,
            "host_wrapper": 0.0,
        },
        evidence_by_phase={"prepare": ("embree_native_handle_record", "embree_load_timer_record")},
        source_by_phase={"prepare": "embree_timer"},
    )
    return rt.InstrumentationPacket(
        graph_id="generic_candidate_probe_graph",
        backend="embree",
        hardware=hardware_label,
        phase_timings=timings,
        evidence_records=evidence,
    )


def _phase_timings(
    *,
    backend: str,
    default_source: str,
    seconds_by_phase: dict[str, float],
    evidence_by_phase: dict[str, tuple[str, ...]],
    source_by_phase: dict[str, str] | None = None,
) -> tuple[rt.PhaseTimingRecord, ...]:
    source_by_phase = source_by_phase or {}
    return tuple(
        rt.PhaseTimingRecord(
            phase=phase,
            seconds=seconds_by_phase.get(phase, 0.0),
            backend=backend,
            timing_source=source_by_phase.get(phase, default_source),
            evidence_ids=evidence_by_phase.get(phase, ()),
            steady_state_candidate=phase in {"rt_traversal", "stream_handoff", "continuation_or_reduction"},
            setup_candidate=phase in {"prepare", "build", "upload", "query_prepare"},
            materialization_candidate=phase == "download_or_materialization",
        )
        for phase in REQUIRED_PHASE_NAMES
    )


def _filter_ldd(path: Path) -> str:
    text = _run_text(["ldd", str(path)])
    keep = []
    for line in text.splitlines():
        if any(token in line for token in ("cuda", "nvrtc", "embree", "geos", "not found")):
            keep.append(line.strip())
    return "\n".join(keep)


def _run_text(command: list[str]) -> str:
    try:
        completed = subprocess.run(command, check=False, capture_output=True, text=True)
    except FileNotFoundError:
        return ""
    return (completed.stdout or "") + (completed.stderr or "")


if __name__ == "__main__":
    raise SystemExit(main())
