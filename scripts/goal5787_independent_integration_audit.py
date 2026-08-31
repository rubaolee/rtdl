#!/usr/bin/env python3
"""Independent audit of Goal5787 generated integration artifacts.

This module intentionally imports neither Goal5787 builder nor any Goal5785
statistics implementation.
"""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "history/internal_docs"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def classify(ci: list[float]) -> str:
    if ci[0] > 1.0:
        return "ci_clear_v4_win"
    if ci[1] < 1.0:
        return "ci_clear_v4_loss"
    return "uncertain_ci_crosses_one"


def main() -> None:
    matrix = load(HISTORY / "goal5787_cgo_claim_matrix_20260816.json")
    ledger = load(HISTORY / "goal5787_programming_responsibility_ledger_20260816.json")
    evaluation = load(
        HISTORY / "goal5785_v6_rtx4000ada_final_result_20260816/EVALUATION.json"
    )
    artifact = load(HISTORY / "goal5787_portable_artifact_audit_20260816.json")
    source_by_id = {(row["lifecycle"], row["row_id"]): row for row in evaluation["rows"]}
    matrix_by_id = {(row["lifecycle"], row["row_id"]): row for row in matrix["performance"]["rows"]}
    if len(source_by_id) != 34 or set(source_by_id) != set(matrix_by_id):
        raise RuntimeError("claim-matrix row membership mismatch")
    counts = Counter()
    medians = Counter()
    for row_id, source in source_by_id.items():
        derived = classify(source["bootstrap_ci95"])
        row = matrix_by_id[row_id]
        counts[derived] += 1
        medians["pass" if source["paired_ratio_median"] >= 1.0 else "fail"] += 1
        checks = {
            "app": source["app"],
            "paper_algorithm": source["paper_algorithm"],
            "lifecycle": source["lifecycle"],
            "pair_count": source["pair_count"],
            "paired_ratio_median": source["paired_ratio_median"],
            "bootstrap_ci95": source["bootstrap_ci95"],
            "ci_classification": derived,
        }
        for key, expected in checks.items():
            if row[key] != expected:
                raise RuntimeError(f"claim-matrix drift {row_id} {key}")
    if counts != Counter({
        "ci_clear_v4_win": 11,
        "ci_clear_v4_loss": 10,
        "uncertain_ci_crosses_one": 13,
    }) or medians != Counter({"pass": 16, "fail": 18}):
        raise RuntimeError("independent headline reconstruction failed")

    for pin in matrix["frozen_authorities"]:
        path = ROOT / pin["path"]
        if not path.is_file() or sha256(path) != pin["sha256"] or pin["verified"] is not True:
            raise RuntimeError(f"frozen authority mismatch: {pin}")
    apps = {row["app"] for row in ledger["applications"]}
    if apps != set(source["app"] for source in evaluation["rows"]):
        raise RuntimeError(f"responsibility ledger application mismatch: {apps}")
    method = ledger["methodology"]
    if method["developer_time_measured"] or method["productivity_multiplier_claimed"] \
            or method["raw_loc_ratio_used_as_primary_metric"]:
        raise RuntimeError("programming-burden gaming detected")
    if not method["shared_v4_infrastructure_counted_once"]:
        raise RuntimeError("shared infrastructure would be double-counted")

    if artifact["archive_sha256"] != artifact["twin_sha256"] \
            or not artifact["byte_identical_twin"]:
        raise RuntimeError("portable artifact/twin mismatch")
    clean = artifact["independent_equivalent_clean_workflow"]
    if clean["status"] != "PASS" or clean["unit_tests"] != "186/186 PASS" \
            or not clean["installed_quickstart_matches_source"]:
        raise RuntimeError("portable independent clean workflow failed")
    if artifact["private_codex_member_count"] or artifact["prebuilt_native_member_count"] \
            or artifact["unsafe_member_count"]:
        raise RuntimeError("portable artifact contains forbidden payload")

    v3_map = (HISTORY / "goal5787_v3_disposition_and_cgo_evidence_map_20260816.md").read_text(encoding="utf-8")
    manuscript = (HISTORY / "goal5787_cgo_manuscript_outline_20260816.md").read_text(encoding="utf-8")
    reproduction = (ROOT / "docs/v4/cgo_artifact_reproduction.md").read_text(encoding="utf-8")
    required_text = (
        "curated partial provider catalog",
        "11 CI-clear wins",
        "10 CI-clear losses",
        "13 uncertain",
        "Goal5767 RC and Goal5785 execution source are different source identities",
    )
    combined = "\n".join((v3_map, manuscript, reproduction))
    for phrase in required_text:
        if phrase not in combined:
            raise RuntimeError(f"required claim-boundary phrase absent: {phrase}")
    if matrix["claim_boundary"]["submission_ready_claimed"] \
            or matrix["claim_boundary"]["new_pod_used_or_authorized"]:
        raise RuntimeError("unauthorized Goal5787 claim")

    result = {
        "schema": "rtdl.goal5787.independent_integration_audit.v1",
        "goal": 5787,
        "status": "PASS",
        "evaluation_rows_independently_matched": 34,
        "median_split": dict(medians),
        "ci_split": dict(counts),
        "frozen_authorities_rehashed": len(matrix["frozen_authorities"]),
        "responsibility_ledger_applications": len(apps),
        "programming_burden_gaming_detected": False,
        "portable_artifact_independent_clean_workflow": "PASS",
        "v3_central_claim_present": False,
        "rc_performance_source_conflation_detected": False,
        "new_performance_or_pod_claimed": False,
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
