from __future__ import annotations

import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
TOPOLOGY = ROOT / "src/rtdsl/closed_shape_topology.py"
REPORT = ROOT / "docs/reports/goal3749_rayjoin_side_aware_topology_numba_reference_2026-06-07.md"
A5000_SUMMARY = ROOT / "docs/reports/goal3749_rayjoin_side_aware_topology_numba_a5000/summary.json"


def _host_tuple(array):
    return tuple(int(value) for value in array.copy_to_host().tolist())


class Goal3749RayjoinSideAwareTopologyNumbaReferenceTest(unittest.TestCase):
    def test_numba_side_aware_filter_is_exported_and_in_contract(self) -> None:
        self.assertTrue(hasattr(rt, "filter_closed_shape_membership_candidate_columns_by_owner_face_side_numba"))
        text = TOPOLOGY.read_text(encoding="utf-8")
        self.assertIn("def filter_closed_shape_membership_candidate_columns_by_owner_face_side_numba", text)
        self.assertIn("numba_cuda_jit_used", text)
        self.assertIn('"raw_cuda_kernel_required": False', text)

        contract = rt.validate_owner_face_priority_pipeline_contract()
        self.assertIn(
            "filter_closed_shape_membership_candidate_columns_by_owner_face_side_numba",
            contract["optional_columnar_pipeline_helpers"],
        )
        self.assertFalse(any(contract["claim_boundary"].values()))

    def test_report_records_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal3749", text)
        self.assertIn("Numba", text)
        self.assertIn("no-RawKernel", text)
        self.assertIn("not a public speedup claim", text)
        self.assertIn("A5000", text)

    def test_a5000_artifact_records_same_contract_numba_win_without_claim_leak(self) -> None:
        summary = json.loads(A5000_SUMMARY.read_text(encoding="utf-8"))
        self.assertEqual(summary["contract"], "generic_side_aware_owner_face_membership_filter")
        self.assertTrue(summary["all_keep_count_parity"])
        self.assertGreaterEqual(len(summary["rows"]), 4)
        self.assertFalse(any(summary["claim_boundary"].values()))

        largest = max(summary["rows"], key=lambda row: int(row["candidate_count"]))
        self.assertEqual(largest["candidate_count"], 1_048_576)
        self.assertTrue(largest["keep_count_parity"])
        self.assertGreater(largest["numba_vs_cupy_ratio"], 10.0)
        self.assertFalse(any(largest["claim_boundary"].values()))

    def test_numba_side_aware_filter_matches_columnar_reference_when_cuda_available(self) -> None:
        if not rt.numba_partner_available():
            self.skipTest("Numba CUDA is not available in this environment")
        expected = rt.filter_closed_shape_membership_candidate_columns_by_owner_face_side_columns(
            candidate_point_ids=(893, 893, 894, 894),
            candidate_shape_ids=(891, 16312, 891, 16312),
            topology_shape_ids=(891, 16312),
            topology_left_face_ids=(371, 384),
            topology_right_face_ids=(384, 607),
            owner_point_ids=(893, 894),
            owner_face_ids=(371, 384),
            owner_side_codes=("left", "right"),
        )
        actual = rt.filter_closed_shape_membership_candidate_columns_by_owner_face_side_numba(
            candidate_point_ids=(893, 893, 894, 894),
            candidate_shape_ids=(891, 16312, 891, 16312),
            topology_shape_ids=(891, 16312),
            topology_left_face_ids=(371, 384),
            topology_right_face_ids=(384, 607),
            owner_point_ids=(893, 894),
            owner_face_ids=(371, 384),
            owner_side_codes=("left", "right"),
        )

        self.assertEqual(_host_tuple(actual["point_id"]), expected["point_id"])
        self.assertEqual(_host_tuple(actual["shape_id"]), expected["shape_id"])
        self.assertEqual(_host_tuple(actual["membership"]), expected["membership"])
        self.assertEqual(_host_tuple(actual["owner_face_id"]), expected["owner_face_id"])
        self.assertEqual(_host_tuple(actual["owner_side_code"]), expected["owner_side_code"])
        self.assertEqual(actual["point_lookup_key_mode"], "public_point_id")
        self.assertEqual(actual["shape_lookup_key_mode"], "public_shape_id")
        self.assertEqual(
            actual["_metadata"]["partner_reference_contract"],
            "generic_side_aware_owner_face_membership_filter",
        )
        self.assertFalse(actual["_metadata"]["public_speedup_claim_authorized"])

    def test_numba_side_aware_filter_supports_ordinals_when_cuda_available(self) -> None:
        if not rt.numba_partner_available():
            self.skipTest("Numba CUDA is not available in this environment")
        actual = rt.filter_closed_shape_membership_candidate_columns_by_owner_face_side_numba(
            candidate_point_ids=(7, 7, 7, 7),
            candidate_shape_ids=(891, 16312, 891, 16312),
            candidate_point_ordinals=(0, 0, 1, 1),
            candidate_shape_ordinals=(0, 1, 0, 1),
            topology_shape_ids=(891, 16312),
            topology_shape_ordinals=(0, 1),
            topology_left_face_ids=(371, 384),
            topology_right_face_ids=(384, 607),
            owner_point_ids=(7, 7),
            owner_point_ordinals=(0, 1),
            owner_face_ids=(371, 384),
            owner_side_codes=("left", "right"),
        )

        self.assertEqual(_host_tuple(actual["point_id"]), (7, 7))
        self.assertEqual(_host_tuple(actual["shape_id"]), (891, 891))
        self.assertEqual(_host_tuple(actual["point_ordinal"]), (0, 1))
        self.assertEqual(_host_tuple(actual["shape_ordinal"]), (0, 0))
        self.assertEqual(actual["point_lookup_key_mode"], "input_ordinal")
        self.assertEqual(actual["shape_lookup_key_mode"], "prepared_shape_ordinal")


if __name__ == "__main__":
    unittest.main()
