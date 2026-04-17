#!/usr/bin/env python3
"""Validate the v0.7 DB columnar packaging manifest boundary."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED_PATHS = {
    "runtime": [
        "src/native/embree/rtdl_embree_api.cpp",
        "src/native/embree/rtdl_embree_prelude.h",
        "src/native/optix/rtdl_optix_api.cpp",
        "src/native/optix/rtdl_optix_prelude.h",
        "src/native/optix/rtdl_optix_workloads.cpp",
        "src/native/vulkan/rtdl_vulkan_api.cpp",
        "src/native/vulkan/rtdl_vulkan_core.cpp",
        "src/native/vulkan/rtdl_vulkan_prelude.h",
        "src/rtdsl/__init__.py",
        "src/rtdsl/db_perf.py",
        "src/rtdsl/embree_runtime.py",
        "src/rtdsl/optix_runtime.py",
        "src/rtdsl/vulkan_runtime.py",
    ],
    "tests": [
        "tests/goal432_v0_7_rt_db_phase_split_perf_test.py",
        "tests/goal434_v0_7_embree_native_prepared_db_dataset_test.py",
        "tests/goal435_v0_7_optix_native_prepared_db_dataset_test.py",
        "tests/goal436_v0_7_vulkan_native_prepared_db_dataset_test.py",
        "tests/goal440_v0_7_embree_columnar_prepared_db_dataset_transfer_test.py",
        "tests/goal441_v0_7_optix_columnar_prepared_db_dataset_transfer_test.py",
        "tests/goal442_v0_7_vulkan_columnar_prepared_db_dataset_transfer_test.py",
        "tests/goal445_v0_7_high_level_prepared_db_columnar_default_test.py",
    ],
    "scripts": [
        "scripts/goal432_db_phase_split_perf_gate.py",
        "scripts/goal434_embree_native_prepared_db_dataset_perf_gate.py",
        "scripts/goal435_optix_native_prepared_db_dataset_perf_gate.py",
        "scripts/goal436_vulkan_native_prepared_db_dataset_perf_gate.py",
        "scripts/goal437_repeated_query_db_perf_summary.py",
        "scripts/goal440_embree_columnar_transfer_perf_gate.py",
        "scripts/goal441_optix_columnar_transfer_perf_gate.py",
        "scripts/goal442_vulkan_columnar_transfer_perf_gate.py",
        "scripts/goal443_columnar_repeated_query_perf_gate.py",
    ],
    "release_docs": [
        "README.md",
        "docs/README.md",
        "docs/features/README.md",
        "docs/features/db_workloads/README.md",
        "docs/quick_tutorial.md",
        "docs/tutorials/db_workloads.md",
        "docs/release_facing_examples.md",
        "docs/release_reports/v0_7/audit_report.md",
        "docs/release_reports/v0_7/release_statement.md",
        "docs/release_reports/v0_7/support_matrix.md",
        "docs/release_reports/v0_7/tag_preparation.md",
        "docs/history/goals/v0_7_goal_sequence_2026-04-15.md",
    ],
    "evidence": [
        "docs/reports/goal443_columnar_repeated_query_perf_linux_2026-04-16.json",
        "docs/reports/goal443_v0_7_columnar_repeated_query_perf_gate_2026-04-16.md",
        "docs/reports/goal446_post_columnar_db_regression_linux_2026-04-16.log",
        "docs/reports/goal446_v0_7_post_columnar_db_regression_sweep_2026-04-16.md",
        "docs/reports/goal447_v0_7_db_columnar_packaging_readiness_audit_2026-04-16.md",
        "docs/reports/goal448_v0_7_db_columnar_packaging_manifest_2026-04-16.md",
    ],
    "valid_consensus": [
        "history/ad_hoc_reviews/2026-04-16-codex-consensus-goal440-v0_7-embree-columnar-prepared-db-dataset-transfer.md",
        "history/ad_hoc_reviews/2026-04-16-codex-consensus-goal441-v0_7-optix-columnar-prepared-db-dataset-transfer.md",
        "history/ad_hoc_reviews/2026-04-16-codex-consensus-goal442-v0_7-vulkan-columnar-prepared-db-dataset-transfer.md",
        "history/ad_hoc_reviews/2026-04-16-codex-consensus-goal443-v0_7-columnar-repeated-query-perf-gate.md",
        "history/ad_hoc_reviews/2026-04-16-codex-consensus-goal444-v0_7-release-docs-refresh-after-columnar-transfer.md",
        "history/ad_hoc_reviews/2026-04-16-codex-consensus-goal445-v0_7-high-level-prepared-db-columnar-default.md",
        "history/ad_hoc_reviews/2026-04-16-codex-consensus-goal446-v0_7-post-columnar-db-regression-sweep.md",
        "history/ad_hoc_reviews/2026-04-16-codex-consensus-goal447-v0_7-db-columnar-packaging-readiness-audit.md",
        "history/ad_hoc_reviews/2026-04-16-codex-consensus-goal448-v0_7-db-columnar-packaging-manifest.md",
    ],
}

INVALID_REVIEW_ARTIFACTS = [
    "docs/reports/goal445_external_review_gemini_attempt_invalid_2026-04-16.md",
]


def validate(root: Path) -> dict[str, object]:
    categories: dict[str, dict[str, object]] = {}
    missing_required: list[str] = []

    for category, paths in REQUIRED_PATHS.items():
        present = []
        missing = []
        for rel in paths:
            if (root / rel).exists():
                present.append(rel)
            else:
                missing.append(rel)
                missing_required.append(rel)
        categories[category] = {
            "present_count": len(present),
            "missing_count": len(missing),
            "present": present,
            "missing": missing,
        }

    invalid_review_artifacts = []
    for rel in INVALID_REVIEW_ARTIFACTS:
        invalid_review_artifacts.append(
            {
                "path": rel,
                "exists": (root / rel).exists(),
                "counts_as_consensus": False,
            }
        )

    return {
        "goal": 449,
        "repo_root": str(root),
        "required_path_count": sum(len(paths) for paths in REQUIRED_PATHS.values()),
        "missing_required_count": len(missing_required),
        "missing_required": missing_required,
        "categories": categories,
        "invalid_review_artifacts": invalid_review_artifacts,
        "valid": len(missing_required) == 0
        and all(not item["counts_as_consensus"] for item in invalid_review_artifacts),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--json-out", required=True)
    args = parser.parse_args()

    root = Path(args.repo_root).resolve()
    result = validate(root)
    out = Path(args.json_out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
