from __future__ import annotations

import json
from pathlib import Path
import unittest

from scripts import v3_phoenix_rtdbscan_same_contract_rerun as rerun

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_SUMMARY = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_rtdbscan_same_contract_20260620_fresh"
    / "summary.json"
)
INTAKE_DOC = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_rtdbscan_same_contract_pod_evidence_2026-06-20.md"


class V3PhoenixRTDBSCANSameContractRerunTest(unittest.TestCase):
    def test_dry_run_cases_include_validated_control_and_serious_large_rows(self) -> None:
        cases = rerun.build_cases(
            dataset="clustered3d",
            point_counts=(65_536, 262_144, 524_288),
            seed=20260519,
        )
        self.assertEqual(len(cases), 8)
        case_ids = {case["case_id"] for case in cases}
        self.assertIn("rtdbscan_embree_same_contract_clustered3d_4096_r3", case_ids)
        self.assertIn("rtdbscan_optix_same_contract_clustered3d_524288_r3", case_ids)
        self.assertTrue(any(case["validation_requested"] for case in cases))
        self.assertTrue(any(not case["validation_requested"] for case in cases))
        for case in cases:
            command = " ".join(case["command"])
            self.assertIn("rtdl_rt_dbscan_benchmark_app.py", command)
            self.assertIn("--partner numba", command)
            if case["validation_requested"]:
                self.assertNotIn("--no-validation", command)
            else:
                self.assertIn("--no-validation", command)

    def test_canonical_signature_ignores_label_ids_but_preserves_counts(self) -> None:
        left = {"cluster_sizes": {"10": 4, "99": 3}, "core_count": 7, "noise_count": 1}
        right = {"cluster_sizes": {"1": 3, "2": 4}, "core_count": 7, "noise_count": 1}
        self.assertEqual(
            rerun.canonical_component_signature(left),
            rerun.canonical_component_signature(right),
        )

    def test_pair_summary_keeps_claim_flags_false(self) -> None:
        rows = [
            {
                "case_id": "e",
                "status": "ok",
                "dataset": "clustered3d",
                "point_count": 524288,
                "repeat": 3,
                "warmup": 1,
                "backend": "embree",
                "validation_requested": False,
                "app_elapsed_sec": 8.0,
                "canonical_signature": {"cluster_sizes": (1, 2), "core_count": 3, "noise_count": 0},
                "timing_extract": {"embree_threshold_compact_rows_sec": 2.0},
            },
            {
                "case_id": "o",
                "status": "ok",
                "dataset": "clustered3d",
                "point_count": 524288,
                "repeat": 3,
                "warmup": 1,
                "backend": "optix",
                "validation_requested": False,
                "app_elapsed_sec": 4.0,
                "canonical_signature": {"cluster_sizes": (1, 2), "core_count": 3, "noise_count": 0},
                "timing_extract": {
                    "optix_rt_count_threshold_sec": 1.0,
                    "numba_component_continuation_sec": 2.0,
                },
            },
        ]
        pairs = rerun.build_pairs(rows)
        self.assertEqual(pairs[0]["optix_speedup_vs_embree"], 2.0)
        self.assertTrue(pairs[0]["same_canonical_component_signature"])
        self.assertFalse(pairs[0]["public_speedup_claim_authorized"])
        self.assertFalse(pairs[0]["m7_promotion_authorized"])

    def test_fresh_pod_evidence_is_not_promoted_and_rejects_1483x_reading(self) -> None:
        payload = json.loads(EVIDENCE_SUMMARY.read_text(encoding="utf-8"))
        summary = payload["summary"]
        self.assertEqual(summary["status"], "rtdbscan_same_contract_fresh_evidence_not_promoted")
        self.assertEqual(summary["failed_rows"], [])
        self.assertTrue(summary["validation_reference_pass"])
        self.assertTrue(summary["large_signature_pass"])
        self.assertGreater(summary["weakest_serious_optix_speedup_vs_embree"], 1.0)
        self.assertLess(summary["strongest_serious_optix_speedup_vs_embree"], 1.2)
        self.assertFalse(summary["m7_promotion_authorized"])
        self.assertFalse(summary["public_speedup_claim_authorized"])

    def test_intake_doc_keeps_rtdbscan_internal(self) -> None:
        text = INTAKE_DOC.read_text(encoding="utf-8")
        self.assertIn("rtdbscan_same_contract_pod_evidence_not_promoted", text)
        self.assertIn("does not support the old `1483x` RTDBSCAN reading", text)
        self.assertIn("1.071x", text)
        self.assertIn("Continuation dominates OptiX", text)
        self.assertIn("Phoenix M7-qualified release rows: 0", text)


if __name__ == "__main__":
    unittest.main()
