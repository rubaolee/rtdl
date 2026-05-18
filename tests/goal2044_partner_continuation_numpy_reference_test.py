import math
import pathlib
import subprocess
import sys
import unittest

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2044_partner_continuation_numpy_reference_2026-05-14.md"

sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from examples import rtdl_hausdorff_distance_app as hausdorff


class Goal2044PartnerContinuationNumpyReferenceTest(unittest.TestCase):
    def test_segmented_reference_primitives(self):
        keys = np.asarray([0, 1, 0, 2, 1, 2, 2], dtype=np.int64)
        values = np.asarray([1.5, 2.0, 3.5, 4.0, -1.0, 5.0, 0.5], dtype=np.float64)

        np.testing.assert_array_equal(rt.numpy_segmented_count(keys, 4), np.asarray([2, 2, 3, 0]))
        np.testing.assert_allclose(rt.numpy_segmented_sum(keys, values, 4), np.asarray([5.0, 1.0, 9.5, 0.0]))
        np.testing.assert_allclose(
            rt.numpy_segmented_minmax(keys, values, 4, reduce="min"),
            np.asarray([1.5, -1.0, 0.5, math.inf]),
        )
        np.testing.assert_allclose(
            rt.numpy_segmented_minmax(keys, values, 4, reduce="max"),
            np.asarray([3.5, 2.0, 5.0, -math.inf]),
        )

    def test_group_topk_is_deterministic(self):
        result = rt.numpy_group_topk(
            group_ids=[0, 0, 0, 1, 1],
            item_ids=[7, 3, 5, 9, 8],
            scores=[1.0, 1.0, 0.5, 2.0, 2.0],
            group_count=2,
            k=2,
        )
        np.testing.assert_array_equal(result["group_ids"], np.asarray([0, 0, 1, 1]))
        np.testing.assert_array_equal(result["item_ids"], np.asarray([5, 3, 8, 9]))
        np.testing.assert_allclose(result["scores"], np.asarray([0.5, 1.0, 2.0, 2.0]))
        np.testing.assert_array_equal(result["rank"], np.asarray([1, 2, 1, 2]))

    def test_group_argmin_then_global_argmax_with_witness(self):
        result = rt.numpy_group_argmin_then_global_argmax_with_witness(
            group_ids=[0, 0, 1, 1, 2, 2],
            item_ids=[10, 11, 20, 21, 30, 31],
            values=[3.0, 1.0, 2.5, 2.0, 4.0, 5.0],
            group_count=3,
        )
        self.assertEqual(result["group_id"], 2)
        self.assertEqual(result["item_id"], 30)
        self.assertEqual(result["value"], 4.0)
        self.assertEqual(result["contract"], "generic_group_argmin_then_global_argmax_with_witness")

    def test_hausdorff_partner_numpy_exact_matches_oracle(self):
        payload = hausdorff.run_app("partner_numpy_exact", copies=3)
        self.assertTrue(payload["matches_oracle"])
        self.assertEqual(payload["partner"], "numpy")
        self.assertEqual(
            payload["partner_reference_contract"],
            "generic_group_argmin_then_global_argmax_with_witness",
        )
        self.assertFalse(payload["native_continuation_active"])
        self.assertFalse(payload["rt_core_accelerated"])
        self.assertIn("generic group-argmin-then-global-argmax", payload["rtdl_role"])

    def test_cli_exposes_partner_numpy_exact(self):
        completed = subprocess.run(
            [
                sys.executable,
                "examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_distance_app.py",
                "--backend",
                "partner_numpy_exact",
                "--copies",
                "2",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn('"backend": "partner_numpy_exact"', completed.stdout)
        self.assertIn('"matches_oracle": true', completed.stdout)

    def test_report_records_boundaries(self):
        text = REPORT.read_text(encoding="utf-8")
        required = [
            "does not make exact Hausdorff fast at large scale",
            "does not provide a CuPy implementation",
            "does not provide an OptiX zero-copy candidate-row handoff",
            "does not authorize v2.0 release",
        ]
        for phrase in required:
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
