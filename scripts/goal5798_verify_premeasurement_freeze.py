"""Independent stdlib-only verification of the Goal5798 design freeze."""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import struct


ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "history" / "internal_docs"
FREEZE = HISTORY / "goal5798_s0_premeasurement_design_freeze_v4_20260823.json"
OUTPUT = HISTORY / (
    "goal5798_s0_premeasurement_design_independent_verification_20260823.json")

ARMS = (
    "A_DIRECT_CUDA_OPTIX", "B_STOCK_CURRENT_PYOPTIX_9_1", "D_RTDL_PUBLIC")
TASKS = (
    "CUSTOM_AABB_CLOSED_RELATION_COUNT_V1",
    "BUILTIN_TRIANGLE_WEIGHTED_ALL_HIT_V1",
)
MODES = ("COLD_FRESH_PROCESS", "PREPARED_EXECUTION")


def canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def f32(value: float) -> float:
    return struct.unpack("<f", struct.pack("<f", float(value)))[0]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def independent_workload_projection() -> dict[str, object]:
    indexed = []
    expected_rows = []
    for item_id in range(4096):
        indexed.append([
            f32(2 * item_id), f32(0), f32(2 * item_id + 1), f32(1), item_id])
        expected_rows.append([item_id, item_id])
    vertices = []
    rays = []
    weights = []
    for ray_id in range(16384):
        x = 3 * ray_id
        vertices.extend([
            [f32(x - 1), f32(-1), f32(1)],
            [f32(x + 1), f32(-1), f32(1)],
            [f32(x), f32(1), f32(1)],
        ])
        rays.append([[f32(x), f32(0), f32(0)], [f32(0), f32(0), f32(1)]])
        weights.append(1 + ray_id % 7)
    return {
        "relation": {
            "indexed_sha256": digest(indexed),
            "queries_sha256": digest(indexed),
            "expected_rows_sha256": digest(expected_rows),
        },
        "triangle": {
            "vertices_sha256": digest(vertices),
            "rays_sha256": digest(rays),
            "weights_sha256": digest(weights),
            "expected_per_ray_sha256": digest([1] * 16384),
            "expected_weighted_sum": sum(weights),
        },
    }


def main() -> None:
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    require(freeze["schema"] == "rtdl.goal5798.premeasurement_freeze.v4",
            "schema mismatch")
    seal = freeze["freeze_sha256"]
    unsealed = dict(freeze)
    del unsealed["freeze_sha256"]
    require(digest(unsealed) == seal, "freeze seal mismatch")
    require(all(value is False for value in freeze["authorization"].values()),
            "an authorization is true")
    require(freeze["registered_performance_timing_count"] == 0,
            "timing count is nonzero")
    require(freeze["gpu_execution_count"] == 0, "GPU execution count is nonzero")

    manifest = freeze["source_manifest"]
    require(len(manifest) == freeze["source_manifest_file_count"] == 307,
            "source manifest count mismatch")
    paths = [row["path"] for row in manifest]
    require(paths == sorted(paths) and len(paths) == len(set(paths)),
            "source manifest ordering/uniqueness failure")
    for row in manifest:
        path = ROOT / row["path"]
        require(path.is_file(), f"missing source: {path}")
        require(path.stat().st_size == row["bytes"], f"source byte drift: {path}")
        require(sha_file(path) == row["sha256"], f"source hash drift: {path}")
    require(digest(manifest) == freeze["source_manifest_sha256"],
            "source manifest seal mismatch")

    workload_pin = freeze["workload_authority"]
    workload_path = ROOT / workload_pin["path"]
    require(workload_path.stat().st_size == workload_pin["bytes"],
            "workload authority bytes drift")
    require(sha_file(workload_path) == workload_pin["sha256"],
            "workload authority file drift")
    authority = json.loads(workload_path.read_text(encoding="utf-8"))
    authority_unsealed = dict(authority)
    authority_seal = authority_unsealed.pop("authority_sha256")
    require(digest(authority_unsealed) == authority_seal == workload_pin[
        "authority_sha256"], "workload authority seal mismatch")
    projected = independent_workload_projection()
    for family in ("relation", "triangle"):
        for key, expected in projected[family].items():
            require(authority[family][key] == expected,
                    f"independent workload mismatch: {family}.{key}")

    schedule = freeze["performance_schedule"]
    require(len(schedule) == 288, "performance worker count mismatch")
    require([row["sequence_index"] for row in schedule] == list(range(288)),
            "performance sequence is not contiguous")
    require(len({row["worker_id"] for row in schedule}) == 288,
            "duplicate performance worker id")
    row_counts = Counter((row["task"], row["mode"], row["arm"]) for row in schedule)
    require(set(row_counts) == {
        (task, mode, arm) for task in TASKS for mode in MODES for arm in ARMS},
        "performance row universe mismatch")
    require(all(count == 24 for count in row_counts.values()),
            "performance sample count mismatch")
    for key in row_counts:
        positions = Counter(row["arm_position"] for row in schedule if (
            row["task"], row["mode"], row["arm"]) == key)
        require(positions == {0: 8, 1: 8, 2: 8},
                f"unbalanced arm positions: {key}")
    require(digest(schedule) == freeze["performance_schedule_sha256"],
            "performance schedule digest mismatch")

    memory = freeze["memory_schedule"]
    require(len(memory) == 30, "memory worker count mismatch")
    require(all(row["timing_eligible"] is False for row in memory),
            "memory timing eligibility defect")
    memory_counts = Counter((row["task"], row["arm"]) for row in memory)
    require(set(memory_counts) == {
        (task, arm) for task in TASKS for arm in ARMS},
        "memory row universe mismatch")
    require(all(count == 5 for count in memory_counts.values()),
            "memory sample count mismatch")
    require(digest(memory) == freeze["memory_schedule_sha256"],
            "memory schedule digest mismatch")

    host = freeze["designated_host"]
    require(host["gpu_model"] == "NVIDIA RTX 4000 Ada Generation",
            "wrong host model")
    require(host["vram_bytes_minimum"] == 20_000_000_000,
            "A1 VRAM unit correction not controlling")
    require(host["physical_host_binding"] is None and not host[
            "execution_admission"], "physical host prematurely admitted")
    require(freeze["arms"]["B_STOCK_CURRENT_PYOPTIX_9_1"][
        "optix_api_version"] == "9.1.0", "B is not stock 9.1")
    require(freeze["claim_ceiling"][
        "cross_version_optix90_compatibility_timing_eligible"] is False,
        "OptiX90 compatibility timing became eligible")
    require(freeze["arms"]["C_OWL"]["status"] == "ANALYSED_NOT_IMPLEMENTED",
            "OWL scope drift")
    require(freeze["statistics"]["success_ratio_threshold"] is None,
            "performance threshold introduced")
    require(freeze["matched_resource_budget"] == {
        "relation_raw_event_capacity_formula": (
            "min(2 * indexed_count * query_count, 2 * (semantic_capacity + 1))"),
        "relation_raw_event_capacity": 8194,
        "relation_semantic_capacity": 4096,
        "relation_device_overflow_flag_required": True,
        "identical_for_A_B_D": True,
        "triangle_event_capacity": 16384,
    }, "matched resource budget mismatch")
    require(freeze["implementation_status"]["worker_zero_ready"] is False,
            "worker zero marked ready")
    memory_metrics = freeze["measurement_modes"]["MEMORY_SEPARATE_NON_TIMED"][
        "primary_metrics"]
    require("gpu_process_sampled_peak_bytes" in memory_metrics and
            "gpu_process_peak_bytes" not in memory_metrics,
            "GPU memory accuracy ceiling missing")

    verification: dict[str, object] = {
        "schema": "rtdl.goal5798.premeasurement_freeze_independent_verification.v1",
        "status": "PASS",
        "imports_goal5798_runtime": False,
        "imports_rtdl": False,
        "freeze_file_sha256": sha_file(FREEZE),
        "freeze_sha256": seal,
        "source_manifest_file_count": len(manifest),
        "source_manifest_rehash_count": len(manifest),
        "performance_worker_count": len(schedule),
        "performance_row_count": len(row_counts),
        "performance_samples_per_row": 24,
        "memory_worker_count": len(memory),
        "memory_samples_per_row": 5,
        "workload_projections_rebuilt": 9,
        "physical_host_bound": False,
        "worker_zero_ready": False,
        "registered_performance_timing_count": 0,
    }
    verification["result_sha256"] = digest(verification)
    OUTPUT.write_bytes(json.dumps(
        verification, indent=2, sort_keys=True,
    ).encode("utf-8") + b"\n")
    print(json.dumps({
        "status": "PASS",
        "output": OUTPUT.relative_to(ROOT).as_posix(),
        "file_sha256": sha_file(OUTPUT),
        "source_rehash_count": len(manifest),
        "performance_worker_count": len(schedule),
        "registered_performance_timing_count": 0,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
