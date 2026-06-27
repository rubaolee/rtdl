#!/usr/bin/env python3
from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import json
import math
from pathlib import Path
import statistics
import struct
import subprocess
import sys
import threading
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

import rtdsl as rt  # noqa: E402
from rtdsl.prepared_execution import audit_prepared_execution_session_metadata  # noqa: E402
from examples.current.research_benchmarks.triangle_counting import (  # noqa: E402
    rtdl_triangle_counting_benchmark_app as triangle_app,
)
from scripts import v3_optix_hardware_gate  # noqa: E402


SCHEMA = "rtdl.phoenix_v3.triangle_runner_m18_pod_ab.v1"
STATUS_NOT_RELEASE = "triangle_runner_m18_harness_ready_not_pod_authorized"
SERIOUS_CLIQUE_FLOOR = 80_000
DEFAULT_OUT_DIR = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_triangle_runner_m18_focused_pod_ab_20260622"
)
DEFAULT_EDGE_FILE = ROOT / "build" / "phoenix_v3_m18_triangle" / "k4_cliques_80000.edge"
EMBREE = "embree_same_contract_control"
LEGACY = "legacy_app_front_door_optix"
RUNNER = "productized_prepared_execution_runner"
OUTPUT_CONTRACT = "generic_ray_triangle_weighted_any_hit_summary_device_output_stream_v1"


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    args.output_dir = args.output_dir.resolve()
    args.edge_file = args.edge_file.resolve()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    payload = run_packet(args)
    (args.output_dir / "summary.json").write_text(
        json.dumps(_json_ready(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (args.output_dir / "README.md").write_text(_readme(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2, sort_keys=True), flush=True)
    return 0 if not payload["failed_checks"] else 2


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Phoenix V3 M18 Triangle focused A/B harness. This compares Embree "
            "same-contract control, old OptiX app-front-door control, and the "
            "M16 productized prepared-execution runner route. It never authorizes release."
        )
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--edge-file", type=Path, default=DEFAULT_EDGE_FILE)
    parser.add_argument("--cliques", type=int, default=SERIOUS_CLIQUE_FLOOR)
    parser.add_argument("--partner", choices=("cupy", "numba"), default="cupy")
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--timeout-sec", type=int, default=1800)
    parser.add_argument("--heartbeat-sec", type=float, default=30.0)
    parser.add_argument("--require-rt-hardware", action="store_true")
    parser.add_argument("--allow-non-serious-local-smoke", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--generate-edge-file", action="store_true")
    return parser.parse_args(argv)


def run_packet(args: argparse.Namespace) -> dict[str, Any]:
    if int(args.cliques) < SERIOUS_CLIQUE_FLOOR and not bool(args.allow_non_serious_local_smoke):
        raise SystemExit(
            "cliques is below the Phoenix V3 Triangle serious scale floor; pass "
            "--allow-non-serious-local-smoke only for local smoke tests"
        )
    if int(args.repeat) < 5:
        raise SystemExit("repeat must be >= 5 for Triangle M18 material-probe protocol")

    edge_file = prepare_edge_file(args)
    environment = environment_payload(require_rt_hardware=bool(args.require_rt_hardware))
    if bool(args.require_rt_hardware) and environment["hardware_gate"].get("status") != "pass":
        return build_payload(
            args=args,
            environment=environment,
            edge_file=edge_file,
            variant_payloads={},
            run_errors={
                "optix_hardware_gate": environment["hardware_gate"].get("fail_closed_reason")
                or "OptiX RT hardware gate failed"
            },
        )

    if not bool(args.dry_run) and not bool(edge_file["usable_for_m18"]):
        return build_payload(
            args=args,
            environment=environment,
            edge_file=edge_file,
            variant_payloads={},
            run_errors={
                "edge_file_preflight": "K4 edge-file identity preflight failed before variants"
            },
        )

    variant_payloads: dict[str, dict[str, Any]] = {}
    run_errors: dict[str, str] = {}
    for variant in (EMBREE, LEGACY, RUNNER):
        try:
            print(
                f"[phoenix-v3-triangle-m18] variant={variant} "
                f"cliques={int(args.cliques)} repeat={int(args.repeat)}",
                flush=True,
            )
            payload = run_variant(args, variant=variant)
            variant_payloads[variant] = payload
            (args.output_dir / f"{variant}.json").write_text(
                json.dumps(_json_ready(payload), indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        except Exception as exc:  # pragma: no cover - hardware/environment dependent
            run_errors[variant] = repr(exc)
            (args.output_dir / f"{variant}.error.txt").write_text(
                repr(exc) + "\n",
                encoding="utf-8",
            )

    return build_payload(
        args=args,
        environment=environment,
        edge_file=edge_file,
        variant_payloads=variant_payloads,
        run_errors=run_errors,
    )


def prepare_edge_file(args: argparse.Namespace) -> dict[str, Any]:
    generated_now = False
    if bool(args.generate_edge_file) and not bool(args.dry_run):
        generate_edge_file(args)
        generated_now = True
    return edge_file_metadata(
        args.edge_file,
        cliques=int(args.cliques),
        generated_now=generated_now,
        dry_run=bool(args.dry_run),
    )


def generate_edge_file(args: argparse.Namespace) -> None:
    command = [
        sys.executable,
        str(ROOT / "scripts" / "goal2631_generate_triangle_k4_binary.py"),
        "--output",
        str(args.edge_file),
        "--cliques",
        str(int(args.cliques)),
    ]
    subprocess.run(command, cwd=ROOT, check=True)


def edge_file_metadata(
    path: Path,
    *,
    cliques: int,
    generated_now: bool,
    dry_run: bool,
) -> dict[str, Any]:
    expected_edge_count = int(cliques) * 6
    expected_bytes = expected_edge_count * 8
    expected_sha256 = expected_k4_binary_edge_sha256(int(cliques))
    exists = path.exists()
    actual_bytes: int | None = None
    actual_edge_count: int | None = None
    actual_sha256: str | None = None
    file_size_multiple_of_edge_record = False
    if exists:
        data = path.read_bytes()
        actual_bytes = len(data)
        file_size_multiple_of_edge_record = actual_bytes % 8 == 0
        actual_edge_count = actual_bytes // 8 if file_size_multiple_of_edge_record else None
        actual_sha256 = hashlib.sha256(data).hexdigest()
    if dry_run and not exists:
        actual_edge_count_matches_expected = None
        actual_bytes_matches_expected = None
        checksum_matches_expected = None
    else:
        actual_edge_count_matches_expected = actual_edge_count == expected_edge_count
        actual_bytes_matches_expected = actual_bytes == expected_bytes
        checksum_matches_expected = actual_sha256 == expected_sha256
    usable_for_m18 = bool(
        exists
        and file_size_multiple_of_edge_record
        and actual_edge_count_matches_expected
        and actual_bytes_matches_expected
        and checksum_matches_expected
    )
    return {
        "path": str(path),
        "exists": exists,
        "generated_now": bool(generated_now),
        "dry_run": bool(dry_run),
        "expected_cliques": int(cliques),
        "expected_edge_count": expected_edge_count,
        "expected_oracle_triangle_count": int(cliques) * 4,
        "expected_bytes": expected_bytes,
        "expected_sha256": expected_sha256,
        "actual_bytes": actual_bytes,
        "actual_edge_count": actual_edge_count,
        "actual_sha256": actual_sha256,
        "file_size_multiple_of_edge_record": file_size_multiple_of_edge_record,
        "actual_edge_count_matches_expected": actual_edge_count_matches_expected,
        "actual_bytes_matches_expected": actual_bytes_matches_expected,
        "checksum_matches_expected": checksum_matches_expected,
        "usable_for_m18": usable_for_m18,
        "preflight_status": (
            "dry_run_not_required"
            if dry_run and not exists
            else ("pass" if usable_for_m18 else "fail")
        ),
        "identity_rule": "generated_k4_clique_ladder_binary_edges_sha256_must_match_before_variants",
    }


def expected_k4_binary_edge_sha256(cliques: int) -> str:
    digest = hashlib.sha256()
    for index in range(int(cliques)):
        base = index * 4
        for src, dst in (
            (base + 0, base + 1),
            (base + 0, base + 2),
            (base + 0, base + 3),
            (base + 1, base + 2),
            (base + 1, base + 3),
            (base + 2, base + 3),
        ):
            digest.update(struct.pack("<ii", src, dst))
    return digest.hexdigest()


def run_variant(args: argparse.Namespace, *, variant: str) -> dict[str, Any]:
    if bool(args.dry_run):
        return {
            "variant": variant,
            "status": "dry_run",
            "command": build_command(args, variant=variant),
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "broad_v3_faster_than_v2_claim_authorized": False,
            "all_app_rerun_authorized": False,
            "focused_pod_spend_authorized_now": False,
        }
    if variant in {EMBREE, LEGACY}:
        return run_subprocess_variant(args, variant=variant)
    if variant == RUNNER:
        return run_productized_runner_variant(args)
    raise ValueError(f"unsupported variant: {variant}")


def build_command(args: argparse.Namespace, *, variant: str) -> list[str]:
    if variant == EMBREE:
        backend = "embree"
        partner = "none"
        return [
            sys.executable,
            "examples/current/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py",
            "--mode",
            "rt_graph_2a1_generic_rt",
            "--edge-file",
            str(args.edge_file),
            "--edge-format",
            "binary",
            "--backend",
            backend,
            "--detail",
            "summary",
            "--partner",
            partner,
            "--warmup",
            str(int(args.warmup)),
            "--repeat",
            str(int(args.repeat)),
        ]
    if variant == LEGACY:
        return [
            sys.executable,
            "examples/current/research_benchmarks/triangle_counting/rtdl_triangle_counting_benchmark_app.py",
            "--mode",
            "rt_graph_2a1_generic_rt",
            "--edge-file",
            str(args.edge_file),
            "--edge-format",
            "binary",
            "--backend",
            "optix",
            "--detail",
            "summary",
            "--partner",
            str(args.partner),
            "--warmup",
            str(int(args.warmup)),
            "--repeat",
            str(int(args.repeat)),
        ]
    if variant == RUNNER:
        command = [
            sys.executable,
            "scripts/v3_phoenix_triangle_runner_m18_pod_ab.py",
            "--output-dir",
            str(args.output_dir),
            "--edge-file",
            str(args.edge_file),
            "--cliques",
            str(int(args.cliques)),
            "--partner",
            str(args.partner),
            "--warmup",
            str(int(args.warmup)),
            "--repeat",
            str(int(args.repeat)),
        ]
        if bool(args.require_rt_hardware):
            command.append("--require-rt-hardware")
        return command
    raise ValueError(f"unsupported variant: {variant}")


def run_subprocess_variant(args: argparse.Namespace, *, variant: str) -> dict[str, Any]:
    command = build_command(args, variant=variant)
    stdout_path = args.output_dir / f"{variant}.stdout.json"
    stderr_path = args.output_dir / f"{variant}.stderr.txt"
    started = time.perf_counter()
    process = subprocess.Popen(
        [str(part) for part in command],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr, timed_out = communicate_with_heartbeat(
        process,
        label=variant,
        started=started,
        timeout_sec=float(args.timeout_sec),
        heartbeat_sec=float(args.heartbeat_sec),
    )
    wall_sec = time.perf_counter() - started
    stdout_path.write_text(stdout or "", encoding="utf-8")
    stderr_path.write_text(stderr or "", encoding="utf-8")
    parsed, parse_error = parse_json_object(stdout)
    return {
        "variant": variant,
        "status": "ok" if process.returncode == 0 and parsed is not None and not timed_out else "failed",
        "returncode": process.returncode,
        "timed_out": timed_out,
        "command": command,
        "stdout_path": _rel(stdout_path),
        "stderr_path": _rel(stderr_path),
        "parse_error": parse_error,
        "wrapper_wall_sec": wall_sec,
        "payload": parsed,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "all_app_rerun_authorized": False,
        "focused_pod_spend_authorized_now": False,
    }


def communicate_with_heartbeat(
    process: subprocess.Popen[str],
    *,
    label: str,
    started: float,
    timeout_sec: float,
    heartbeat_sec: float,
) -> tuple[str, str, bool]:
    deadline = started + timeout_sec
    next_heartbeat = started + heartbeat_sec
    timed_out = False
    while process.poll() is None:
        now = time.perf_counter()
        if now >= deadline:
            timed_out = True
            process.kill()
            break
        if now >= next_heartbeat:
            print(f"[phoenix-v3-triangle-m18] heartbeat variant={label} elapsed={now - started:.1f}s", flush=True)
            next_heartbeat = now + heartbeat_sec
        time.sleep(0.2)
    stdout, stderr = process.communicate()
    return stdout or "", stderr or "", timed_out


class PreparedTriangleWeightedSummaryDeviceOutput:
    def __init__(
        self,
        *,
        scene: Any,
        ray_batch: Any,
        ray_weights: Any,
        weighted_hit_sum_out: Any,
        stream: Any,
        executor: Any,
        primitive_count: int,
        ray_count: int,
        partner: str,
    ) -> None:
        self.scene = scene
        self.ray_batch = ray_batch
        self.ray_weights = ray_weights
        self.weighted_hit_sum_out = weighted_hit_sum_out
        self.stream = stream
        self.executor = executor
        self.primitive_count = int(primitive_count)
        self.ray_count = int(ray_count)
        self.partner = str(partner)
        self.prepare_seconds = float(getattr(scene, "prepare_seconds", 0.0)) + float(
            getattr(ray_batch, "prepare_seconds", 0.0)
        ) + float(getattr(executor, "prepare_seconds", 0.0))
        self.launches: list[dict[str, Any]] = []

    def launch_weighted_summary_device_output_stream(self) -> dict[str, Any]:
        self.weighted_hit_sum_out[...] = 0
        launch = self.executor.launch(self.stream)
        self.stream.synchronize()
        self.launches.append(dict(launch))
        return {
            "launch": dict(launch),
            "metadata": {
                "contract": OUTPUT_CONTRACT,
                "partner": self.partner,
                "primitive_count": self.primitive_count,
                "ray_count": self.ray_count,
                "device_output_stream_validated": True,
                "caller_owned_device_output_scalar": True,
                "prepared_scene_reused": True,
                "prepared_ray_batch_reused": True,
                "ray_weights_device_resident": True,
                "output_scalar_device_resident_until_finalize": True,
                "hot_path_host_materialization": False,
                "host_scalar_materialized_during_hot_path": False,
                "m113_graph_capture_claim_authorized": False,
                "m113_cuda_graph_capture_validated": False,
                "device_output_executor_contract": launch.get("contract"),
                "native_symbol": launch.get("native_symbol"),
                "weighted_hit_sum_materialized_in_finalize": True,
            },
        }

    def finalize_weighted_summary_device_output_stream(self, measured_output: dict[str, Any]) -> dict[str, Any]:
        weighted_hit_sum = int(self.weighted_hit_sum_out.get()[0])
        output = dict(measured_output)
        metadata = dict(output.get("metadata", {}))
        metadata["weighted_hit_sum"] = weighted_hit_sum
        metadata["host_scalar_materialized_during_finalize"] = True
        metadata["host_scalar_materialized_during_hot_path"] = False
        output["weighted_hit_sum"] = weighted_hit_sum
        output["metadata"] = metadata
        return output

    def close(self) -> None:
        for value in (self.executor, self.ray_batch, self.scene):
            close = getattr(value, "close", None)
            if callable(close):
                close()


def run_productized_runner_variant(args: argparse.Namespace) -> dict[str, Any]:
    with heartbeat("productized_prepared_execution_runner", interval_sec=float(args.heartbeat_sec)):
        started = time.perf_counter()
        contract = triangle_app._build_rt_graph_triangle_summary_contract_binary(  # noqa: SLF001
            str(args.edge_file),
            partner=str(args.partner),
        )
        built_contract = time.perf_counter()
        print("[phoenix-v3-triangle-m18] runner stage=contract_built", flush=True)
        triangles, rays, ray_weights = triangle_app._build_rt_graph_2a1_device_geometry(  # noqa: SLF001
            contract,
            partner=str(args.partner),
        )
        built_geometry = time.perf_counter()
        print("[phoenix-v3-triangle-m18] runner stage=geometry_built", flush=True)
        primitive_count = triangle_app._record_count(triangles)  # noqa: SLF001
        ray_count = triangle_app._record_count(rays)  # noqa: SLF001

        prepared_holder: dict[str, PreparedTriangleWeightedSummaryDeviceOutput] = {}

        def prepare_session() -> PreparedTriangleWeightedSummaryDeviceOutput:
            cp = __import__("cupy")
            scene = rt.prepare_optix_static_triangle_scene_3d_device_triangles(triangles)
            ray_batch = scene.prepare_ray_batch_device_columns(rays)
            weighted_hit_sum_out = cp.zeros(1, dtype=cp.uint64)
            stream = cp.cuda.Stream(non_blocking=True)
            executor = scene.prepare_ray_batch_any_hit_weighted_sum_device_output_graph_executor(
                ray_batch,
                ray_weights,
                weighted_hit_sum_out,
            )
            prepared = PreparedTriangleWeightedSummaryDeviceOutput(
                scene=scene,
                ray_batch=ray_batch,
                ray_weights=ray_weights,
                weighted_hit_sum_out=weighted_hit_sum_out,
                stream=stream,
                executor=executor,
                primitive_count=primitive_count,
                ray_count=ray_count,
                partner=str(args.partner),
            )
            prepared_holder["value"] = prepared
            print("[phoenix-v3-triangle-m18] runner stage=prepared_session_ready", flush=True)
            return prepared

        cache = rt.ExplicitPreparedSessionCache(max_entries=1)
        try:
            result = rt.run_ray_triangle_weighted_summary_device_output_stream_prepared_session(
                triangle_fingerprint={
                    "edge_file": str(args.edge_file),
                    "cliques": int(args.cliques),
                    "primitive_count": int(primitive_count),
                },
                ray_batch_fingerprint={
                    "edge_file": str(args.edge_file),
                    "ray_count": int(ray_count),
                    "source": "rt_graph_2a1_device_columns",
                },
                weight_fingerprint={
                    "edge_file": str(args.edge_file),
                    "ray_count": int(ray_count),
                    "source": "rt_graph_2a1_device_weights",
                },
                primitive_count=int(primitive_count),
                ray_count=int(ray_count),
                expected_weighted_hit_sum=int(contract.triangle_count),
                partner=str(args.partner),
                cache=cache,
                prepare_session=prepare_session,
                run_weighted_summary=lambda prepared: prepared.launch_weighted_summary_device_output_stream(),
                finalize_weighted_summary=lambda prepared, measured_output: prepared.finalize_weighted_summary_device_output_stream(
                    measured_output
                ),
                backend="optix",
                output_contract=OUTPUT_CONTRACT,
                validate_output=lambda output: {
                    "oracle_match": int(output["weighted_hit_sum"]) == int(contract.triangle_count)
                },
                device="cuda:0",
                warmup_count=int(args.warmup),
                measured_repeat_count=int(args.repeat),
                require_repeat5_material_probe=True,
            )
            metadata = result.to_metadata()
            step3_audit = audit_prepared_execution_session_metadata(metadata)
            output = result.output
            print("[phoenix-v3-triangle-m18] runner stage=measured_repeats_done", flush=True)
        finally:
            prepared = prepared_holder.get("value")
            if prepared is not None:
                prepared.close()

        wall_sec = time.perf_counter() - started
        return {
            "variant": RUNNER,
            "status": "ok" if metadata.get("runtime_trunk_executes_end_to_end") else "failed",
            "schema": SCHEMA,
            "mode": "m18_productized_prepared_execution_runner",
            "edge_file": str(args.edge_file),
            "cliques": int(args.cliques),
            "partner": str(args.partner),
            "oracle_triangle_count": int(contract.triangle_count),
            "weighted_hit_sum": int(output["weighted_hit_sum"]),
            "triangle_count_matches_oracle": int(output["weighted_hit_sum"]) == int(contract.triangle_count),
            "primitive_count": int(primitive_count),
            "ray_count": int(ray_count),
            "timing_sec": {
                "build_contract": built_contract - started,
                "build_geometry": built_geometry - built_contract,
                "outer_wall": wall_sec,
                "runner_measured_median": float(metadata["measured_median_sec"]),
                "runner_measured_total": float(metadata["measured_total_sec"]),
                "runner_prepare_or_cache": float(metadata["outer_prepare_or_cache_sec"]),
            },
            "prepared_execution_session_runner_metadata": metadata,
            "step3_audit": step3_audit,
            "step3_residency_default_ready": bool(
                step3_audit.get("step3_residency_default_ready")
            ),
            "productized_execution_path": "prepared_execution_session_runner",
            "runtime_trunk_executes_end_to_end": bool(metadata.get("runtime_trunk_executes_end_to_end")),
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "broad_v3_faster_than_v2_claim_authorized": False,
            "focused_pod_spend_authorized_now": False,
            "all_app_rerun_authorized": False,
        }


@contextmanager
def heartbeat(label: str, *, interval_sec: float):
    stop = threading.Event()
    started = time.perf_counter()

    def run() -> None:
        while not stop.wait(max(1.0, float(interval_sec))):
            print(
                f"[phoenix-v3-triangle-m18] heartbeat variant={label} "
                f"elapsed={time.perf_counter() - started:.1f}s",
                flush=True,
            )

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    try:
        yield
    finally:
        stop.set()
        thread.join(timeout=1.0)


def build_payload(
    *,
    args: argparse.Namespace,
    environment: dict[str, Any],
    edge_file: dict[str, Any],
    variant_payloads: dict[str, dict[str, Any]],
    run_errors: dict[str, str],
) -> dict[str, Any]:
    comparisons = comparison_payload(variant_payloads)
    oracle_checks = oracle_check_payload(
        variant_payloads,
        expected_oracle_triangle_count=int(edge_file["expected_oracle_triangle_count"]),
        dry_run=bool(args.dry_run),
    )
    failed_checks = failure_checks(
        variant_payloads,
        run_errors,
        comparisons,
        edge_file=edge_file,
        oracle_checks=oracle_checks,
        dry_run=bool(args.dry_run),
    )
    runner_payload = variant_payloads.get(RUNNER, {})
    runner_step3_audit = (
        dict(runner_payload.get("step3_audit", {}))
        if isinstance(runner_payload.get("step3_audit"), dict)
        else {}
    )
    summary = {
        "schema": SCHEMA,
        "status": STATUS_NOT_RELEASE,
        "dry_run": bool(args.dry_run),
        "variant_count": len(variant_payloads),
        "failed_check_count": len(failed_checks),
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "focused_pod_spend_authorized_now": False,
        "all_app_pod_spend_authorized": False,
        "third_strict_set_a_material_probe_closed": False,
        "runner_harness_exists": True,
        "pod_run_authorized_by_m18": False,
        "requires_later_2ai_for_pod": True,
        "comparisons": comparisons,
        "edge_file_preflight_status": edge_file["preflight_status"],
        "edge_file_sha256": edge_file["actual_sha256"],
        "edge_file_checksum_matches_expected": edge_file["checksum_matches_expected"],
        "edge_file_generated_now": edge_file["generated_now"],
        "all_variant_oracle_checks_passed": bool(oracle_checks.get("all_passed")),
        "runner_step3_audit": runner_step3_audit,
        "runner_step3_residency_default_ready": bool(
            runner_step3_audit.get("step3_residency_default_ready")
        ),
    }
    return {
        "schema": SCHEMA,
        "tool": "v3_phoenix_triangle_runner_m18_pod_ab",
        "status": STATUS_NOT_RELEASE,
        "date": "2026-06-22",
        "args": {
            "edge_file": str(args.edge_file),
            "cliques": int(args.cliques),
            "partner": str(args.partner),
            "repeat": int(args.repeat),
            "warmup": int(args.warmup),
            "dry_run": bool(args.dry_run),
            "require_rt_hardware": bool(args.require_rt_hardware),
        },
        "environment": environment,
        "edge_file": edge_file,
        "variants": variant_payloads,
        "oracle_checks": oracle_checks,
        "run_errors": run_errors,
        "comparisons": comparisons,
        "failed_checks": failed_checks,
        "summary": summary,
        "claim_boundary": {
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "broad_v3_faster_than_v2_claim_authorized": False,
            "focused_pod_spend_authorized_now": False,
            "all_app_pod_spend_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "external_embedding_or_zero_copy_claim_authorized": False,
        },
        "goal_level_decision_audit": {
            "decision": "implement a local Triangle runner harness but do not run POD",
            "was_i_foolish": "No.",
            "foolish_actions": (
                "It would be foolish to run the harness on the POD before the M18 "
                "packet is reviewed and focused POD is explicitly authorized."
            ),
            "other_path": "Rerun the old Triangle app route. That would not test the M16 productized runner.",
            "different_path_now": "Use dry-run and local unit tests to prove the harness shape, then request 2-AI review.",
        },
    }


def failure_checks(
    variant_payloads: dict[str, dict[str, Any]],
    run_errors: dict[str, str],
    comparisons: dict[str, Any],
    *,
    edge_file: dict[str, Any],
    oracle_checks: dict[str, Any],
    dry_run: bool,
) -> list[str]:
    failed: list[str] = []
    if run_errors:
        failed.append("variant_run_errors_present")
    missing = {EMBREE, LEGACY, RUNNER} - set(variant_payloads)
    if missing:
        failed.append("missing_variants:" + ",".join(sorted(missing)))
    if dry_run:
        return failed
    if not bool(edge_file.get("exists")):
        failed.append("edge_file_missing")
    if not bool(edge_file.get("file_size_multiple_of_edge_record")):
        failed.append("edge_file_not_binary_edge_record_multiple")
    if not bool(edge_file.get("actual_edge_count_matches_expected")):
        failed.append("edge_file_edge_count_mismatch")
    if not bool(edge_file.get("actual_bytes_matches_expected")):
        failed.append("edge_file_byte_count_mismatch")
    if not bool(edge_file.get("checksum_matches_expected")):
        failed.append("edge_file_checksum_mismatch")
    for variant in (EMBREE, LEGACY, RUNNER):
        if variant_payloads.get(variant, {}).get("status") != "ok":
            failed.append(f"{variant}_status_not_ok")
        check = oracle_checks.get("variants", {}).get(variant, {})
        if check and not bool(check.get("passed")):
            failed.append(f"{variant}_oracle_mismatch")
        elif not check:
            failed.append(f"{variant}_oracle_check_missing")
    runner = variant_payloads.get(RUNNER, {})
    if runner and not bool(runner.get("runtime_trunk_executes_end_to_end")):
        failed.append("runner_runtime_trunk_not_end_to_end")
    if runner and not bool(runner.get("step3_residency_default_ready")):
        failed.append("runner_step3_residency_default_not_ready")
    if runner and not bool(runner.get("triangle_count_matches_oracle")):
        failed.append("runner_oracle_mismatch")
    if comparisons.get("runner_vs_embree_hot_speedup") is not None and comparisons["runner_vs_embree_hot_speedup"] < 1.20:
        failed.append("runner_vs_embree_hot_below_1_20x")
    if comparisons.get("runner_vs_embree_wall_speedup") is not None and comparisons["runner_vs_embree_wall_speedup"] < 1.20:
        failed.append("runner_vs_embree_wall_below_1_20x")
    if comparisons.get("runner_vs_legacy_wall_speedup") is not None and comparisons["runner_vs_legacy_wall_speedup"] < 0.98:
        failed.append("runner_vs_legacy_wall_below_0_98x")
    return failed


def oracle_check_payload(
    variant_payloads: dict[str, dict[str, Any]],
    *,
    expected_oracle_triangle_count: int,
    dry_run: bool,
) -> dict[str, Any]:
    if dry_run:
        return {
            "status": "dry_run_no_oracle_interpretation",
            "expected_oracle_triangle_count": int(expected_oracle_triangle_count),
            "all_passed": False,
            "variants": {},
        }
    checks = {
        variant: _variant_oracle_check(
            variant_payloads.get(variant, {}),
            variant=variant,
            expected_oracle_triangle_count=int(expected_oracle_triangle_count),
        )
        for variant in (EMBREE, LEGACY, RUNNER)
    }
    return {
        "status": "computed",
        "expected_oracle_triangle_count": int(expected_oracle_triangle_count),
        "all_passed": all(bool(item["passed"]) for item in checks.values()),
        "variants": checks,
    }


def _variant_oracle_check(
    payload: dict[str, Any],
    *,
    variant: str,
    expected_oracle_triangle_count: int,
) -> dict[str, Any]:
    if not payload:
        return {
            "variant": variant,
            "passed": False,
            "reason": "missing_variant_payload",
        }
    source = payload if variant == RUNNER else payload.get("payload")
    if not isinstance(source, dict):
        return {
            "variant": variant,
            "passed": False,
            "reason": "missing_parsed_payload",
        }
    oracle = _optional_int(source.get("oracle_triangle_count"))
    observed = _optional_int(
        source.get("weighted_hit_sum")
        if variant == RUNNER
        else source.get("generic_rt_weighted_triangle_count")
    )
    if observed is None:
        observed = _optional_int(source.get("rtdl_triangle_count"))
    if observed is None:
        observed = _optional_int(source.get("generic_rt_triangle_count"))
    matches_flag = source.get("triangle_count_matches_oracle")
    has_required_fields = oracle is not None and observed is not None and isinstance(matches_flag, bool)
    expected_matches = (
        oracle == int(expected_oracle_triangle_count)
        and observed == int(expected_oracle_triangle_count)
        and bool(matches_flag)
    )
    return {
        "variant": variant,
        "passed": bool(has_required_fields and expected_matches),
        "has_required_fields": has_required_fields,
        "oracle_triangle_count": oracle,
        "observed_triangle_count": observed,
        "triangle_count_matches_oracle": matches_flag,
        "expected_oracle_triangle_count": int(expected_oracle_triangle_count),
        "reason": "pass" if has_required_fields and expected_matches else "oracle_or_observed_count_mismatch",
    }


def comparison_payload(variant_payloads: dict[str, dict[str, Any]]) -> dict[str, Any]:
    if {EMBREE, LEGACY, RUNNER} - set(variant_payloads):
        return {}
    if any(variant_payloads[item].get("status") == "dry_run" for item in (EMBREE, LEGACY, RUNNER)):
        return {"status": "dry_run_no_performance_interpretation"}
    embree = variant_payloads[EMBREE]["payload"]
    legacy = variant_payloads[LEGACY]["payload"]
    runner = variant_payloads[RUNNER]
    embree_hot = _payload_query_median_sec(embree)
    legacy_hot = _payload_query_median_sec(legacy)
    runner_hot = float(runner["timing_sec"]["runner_measured_median"])
    embree_wall = float(variant_payloads[EMBREE]["wrapper_wall_sec"])
    legacy_wall = float(variant_payloads[LEGACY]["wrapper_wall_sec"])
    runner_wall = float(runner["timing_sec"]["outer_wall"])
    return {
        "status": "computed",
        "runner_vs_embree_hot_speedup": _safe_div(embree_hot, runner_hot),
        "runner_vs_embree_wall_speedup": _safe_div(embree_wall, runner_wall),
        "runner_vs_legacy_hot_speedup": _safe_div(legacy_hot, runner_hot),
        "runner_vs_legacy_wall_speedup": _safe_div(legacy_wall, runner_wall),
        "legacy_vs_embree_hot_speedup": _safe_div(embree_hot, legacy_hot),
        "legacy_vs_embree_wall_speedup": _safe_div(embree_wall, legacy_wall),
    }


def _payload_query_median_sec(payload: dict[str, Any]) -> float:
    return float(payload["timing_ms"]["query_median_ms"]) / 1000.0


def _safe_div(numerator: float, denominator: float) -> float | None:
    if denominator <= 0.0 or math.isnan(denominator):
        return None
    return float(numerator) / float(denominator)


def _optional_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def environment_payload(*, require_rt_hardware: bool) -> dict[str, Any]:
    return {
        "platform": sys.platform,
        "python": sys.version.split()[0],
        "hardware_gate": v3_optix_hardware_gate.build_payload(
            require_rt_hardware=bool(require_rt_hardware),
            sample_nvidia_smi=None,
        ),
    }


def parse_json_object(text: str) -> tuple[dict[str, Any] | None, str | None]:
    try:
        loaded = json.loads(text or "")
    except json.JSONDecodeError as exc:
        return None, str(exc)
    if not isinstance(loaded, dict):
        return None, "stdout JSON is not an object"
    return loaded, None


def _json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
    return value


def _readme(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Phoenix V3 Triangle M18 Focused Runner Harness Evidence",
        "",
        f"Status: `{payload['status']}`",
        "",
        "```json",
        json.dumps(_json_ready(summary), indent=2, sort_keys=True),
        "```",
        "",
        "This harness does not authorize release, public speedup wording, broad V3-over-V2 wording, or all-app POD.",
        "",
    ]
    return "\n".join(lines)


def _rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
