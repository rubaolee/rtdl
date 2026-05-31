from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal2875_numba_runtime_conformance_smoke_2026-05-31.md"


def _numba_stack():
    import numpy as np
    from numba import cuda

    return cuda, np


class Goal2875NumbaRuntimeConformanceMetadataTest(unittest.TestCase):
    def test_numba_rows_are_pod_runtime_conformance_rows(self) -> None:
        for operation in ("segmented_count_i64", "segmented_sum_f64"):
            cell = rt.plan_v2_5_partner_conformance(operation, "numba")

            self.assertEqual(rt.V2_5_CONFORMANCE_STATUS_POD_RUNTIME, cell["conformance_status"])
            self.assertEqual("Goal2875", cell["evidence_goal"])
            self.assertFalse(cell["release_blocker"])

    def test_partner_conformance_matrix_has_no_preview_runtime_gaps(self) -> None:
        matrix = rt.v2_5_partner_conformance_matrix()
        validation = rt.validate_v2_5_partner_conformance_matrix(matrix)

        self.assertEqual("accept", validation["status"])
        self.assertTrue(matrix["preview_runtime_conformance_complete"])
        self.assertEqual(0, matrix["runtime_conformance_gap_count"])
        self.assertEqual(0, matrix["release_blocker_count"])
        self.assertFalse(matrix["release_conformance_complete"])
        self.assertFalse(matrix["public_speedup_claim_authorized"])

    def test_readiness_packet_indexes_goal2875(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)
        validation = rt.validate_v2_5_internal_readiness_packet(repo_root=ROOT)
        path = "docs/reports/goal2875_numba_runtime_conformance_smoke_2026-05-31.md"

        self.assertEqual("accept", validation["status"])
        self.assertTrue(packet["required_report_presence"][path])

    def test_report_records_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal2875",
            "Numba",
            "segmented_count_i64",
            "segmented_sum_f64",
            "not a v2.5 release authorization",
            "not a public speedup claim",
        ):
            self.assertIn(phrase, text)


@unittest.skipUnless(rt.numba_partner_available(), "Numba CUDA runtime conformance smoke requires Numba CUDA")
class Goal2875NumbaRuntimeConformanceSmokeTest(unittest.TestCase):
    def test_segmented_count_and_sum_match_reference(self) -> None:
        cuda, np = _numba_stack()
        group_ids_host = np.array([0, 2, 2, 1, 0], dtype=np.int64)
        values_host = np.array([1.0, 2.5, 3.5, 4.0, 6.0], dtype=np.float64)
        group_ids = cuda.to_device(group_ids_host)
        values = cuda.to_device(values_host)

        count = rt.run_numba_segmented_count_i64(group_ids, group_count=4)
        total = rt.run_numba_segmented_sum_f64(group_ids, values, group_count=4)
        count_reference = rt.execute_v2_5_partner_continuation_reference(
            "segmented_count_i64",
            {"group_ids": group_ids_host.tolist(), "group_count": 4},
        )
        sum_reference = rt.execute_v2_5_partner_continuation_reference(
            "segmented_sum_f64",
            {"group_ids": group_ids_host.tolist(), "values": values_host.tolist(), "group_count": 4},
        )

        self.assertEqual(count_reference["outputs"]["counts"], count["outputs"]["counts"].copy_to_host().tolist())
        self.assertEqual(sum_reference["outputs"]["sums"], total["outputs"]["sums"].copy_to_host().tolist())
        self.assertEqual("accept", count["phase_timing"]["validation"]["status"])
        self.assertEqual("accept", total["phase_timing"]["validation"]["status"])
        self.assertFalse(count["promoted_performance_path"])
        self.assertFalse(total["promoted_performance_path"])

    def test_invalid_group_ids_fail_closed_before_reduction(self) -> None:
        cuda, np = _numba_stack()
        group_ids = cuda.to_device(np.array([0, 4], dtype=np.int64))

        with self.assertRaisesRegex(ValueError, "group_ids must be in"):
            rt.run_numba_segmented_count_i64(group_ids, group_count=4)


if __name__ == "__main__":
    unittest.main()
