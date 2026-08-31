from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "history" / "internal_docs"
U64_MAX = (1 << 64) - 1


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    helper_path = ROOT / "src" / "rtdsl" / "v4_checked_u64_device_reduction.py"
    runtime_path = ROOT / "src" / "rtdsl" / "v4_triangle_reduction_device_runtime.py"
    app_path = ROOT / "Paper-reproduction-apps" / "triangle-counting-paper" / "v4_whole_app.py"
    generic_path = DOCS / "goal5778_home_checked_u64_reduction_validation_20260814.json"
    triangle_path = DOCS / "goal5778_home_triangle_checked_reduction_validation_20260814.json"

    generic = load_json(generic_path)
    triangle = load_json(triangle_path)

    helper_hash = sha256(helper_path)
    runtime_hash = sha256(runtime_path)
    app_hash = sha256(app_path)
    require(generic["source"]["helper_sha256"] == helper_hash,
            "generic result helper hash drift")
    require(triangle["source"]["checked_reduction_sha256"] == helper_hash,
            "triangle result helper hash drift")
    require(triangle["source"]["triangle_runtime_sha256"] == runtime_hash,
            "triangle result runtime hash drift")
    require(triangle["source"]["triangle_app_sha256"] == app_hash,
            "triangle result app hash drift")

    exact_cases = generic["exact_cases"]
    require(len(exact_cases) == 4, "expected four generic exact cases")
    for row in exact_cases:
        require(row["exact"] is True, "generic reduction mismatch")
        require(row["device_kernel_launch_count"] == 1,
                "generic reduction must use one kernel")
        require(row["host_synchronization_count"] == 1,
                "generic reduction must use one synchronization")

    attacks = generic["attacks"]
    require(len(attacks) == 3, "expected three fail-closed attacks")
    require(all(row["failed_closed"] is True for row in attacks),
            "a malformed reduction summary did not fail closed")
    require({row["attack"] for row in attacks} == {
        "weight_sum_bound", "weighted_value_bound", "value_exceeds_declared_bound"
    }, "attack set drift")

    second = generic["real_non_triangle_consumer"]
    require(second["consumer"] == "RT-DBSCAN route-independent exact directed-edge total",
            "second consumer identity drift")
    require(second["exact"] is True, "RT-DBSCAN second consumer is not exact")
    require(second["directed_edge_count"] == second["expected_directed_edge_count"],
            "RT-DBSCAN directed-edge recount mismatch")
    require(second["same_checked_reduction_contract"] is True,
            "second consumer did not use checked reduction contract")
    require(second["production_route_changed"] is False,
            "Goal5778 must not change the RT-DBSCAN production route")

    rows = {row["paper_algorithm"]: row for row in triangle["rows"]}
    require(set(rows) == {"RT-1A2", "RT-2A1"}, "Triangle algorithm set drift")
    require(triangle["expected_triangle_count"] == 2_224_385,
            "Triangle author count drift")
    require(all(row["matched"] is True for row in rows.values()),
            "Triangle output mismatch")
    require(all(row["behavioral_true_optix"] is True for row in rows.values()),
            "Triangle route is not behaviorally true OptiX")
    require(all(value is None for value in rows["RT-1A2"]["checked_reduction_receipts"]),
            "unweighted RT-1A2 unexpectedly used weighted reduction")

    weighted_receipts = rows["RT-2A1"]["checked_reduction_receipts"]
    require(len(weighted_receipts) == rows["RT-2A1"]["segment_count"] == 8,
            "weighted Triangle receipt count mismatch")
    for receipt in weighted_receipts:
        require(receipt["schema"] == "rtdl.v4.checked_u64_weighted_reduction.receipt.v1",
                "weighted reduction receipt schema drift")
        require(receipt["device_kernel_launch_count"] == 1,
                "weighted segment used more than one reduction kernel")
        require(receipt["host_synchronization_count"] == 1,
                "weighted segment used more than one host synchronization")
        require(receipt["maximum_value"] <= receipt["value_upper_bound"],
                "device maximum exceeds declared Triangle bound")
        require(receipt["maximum_weight"] == 0 or
                receipt["value_count"] <= U64_MAX // receipt["maximum_weight"],
                "Triangle weight-sum proof is unsafe")
        require(receipt["weight_sum"] == 0 or
                receipt["value_upper_bound"] <= U64_MAX // receipt["weight_sum"],
                "Triangle weighted-sum proof is unsafe")
        require(receipt["provisional_sum_trusted_only_after_bounds"] is True,
                "provisional device sum was trusted before bounds")

    helper_text = helper_path.read_text(encoding="utf-8").lower()
    require("triangle" not in helper_text and "rtdbscan" not in helper_text and
            "rt-dbscan" not in helper_text,
            "generic reduction helper contains application dispatch identity")

    claim_boundary = {
        "home_gtx1070_functional_only": True,
        "pod_used": False,
        "registered_performance_result_created": False,
        "target_rtx_saving_predicted": False,
        "goal5776_rescored_or_changed": False,
    }
    result = {
        "schema": "rtdl.goal5778.independent_home_evidence_recount.v1",
        "verdict": "passed",
        "source_hashes": {
            "helper": helper_hash,
            "triangle_runtime": runtime_hash,
            "triangle_app": app_hash,
        },
        "input_hashes": {
            "generic_home_result": sha256(generic_path),
            "triangle_home_result": sha256(triangle_path),
        },
        "generic_exact_case_count": len(exact_cases),
        "fail_closed_attack_count": len(attacks),
        "real_non_triangle_consumer": second["consumer"],
        "triangle_algorithm_count": len(rows),
        "triangle_exact_algorithm_count": sum(row["matched"] is True for row in rows.values()),
        "triangle_behavioral_true_optix_count": sum(
            row["behavioral_true_optix"] is True for row in rows.values()),
        "weighted_triangle_receipt_count": len(weighted_receipts),
        "weighted_triangle_one_kernel_one_sync_count": sum(
            row["device_kernel_launch_count"] == 1 and
            row["host_synchronization_count"] == 1
            for row in weighted_receipts),
        "claim_boundary": claim_boundary,
    }
    output = DOCS / "goal5778_independent_recount_20260814.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
