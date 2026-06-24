from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "scripts" / "v4_section8_device_array_frontdoor_validation.py"


def _load_harness_module():
    spec = importlib.util.spec_from_file_location("v4_section8_device_array_frontdoor_validation", HARNESS)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class V4Section8DeviceArrayFrontdoorValidationTest(unittest.TestCase):
    def test_dry_run_records_frontdoor_boundary_and_non_release_claims(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(HARNESS), "--dry-run", "--copies", "8192"],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )
        payload = json.loads(proc.stdout)
        self.assertEqual("dry_run", payload["status"])
        self.assertEqual("v4_section8_device_array_frontdoor_validation", payload["protocol"])
        self.assertFalse(payload["release_claim_authorized"])
        self.assertFalse(payload["near_handwritten_optix_claim_authorized"])
        self.assertFalse(payload["tier3_callback_claim_authorized"])
        self.assertTrue(payload["frontdoor_contract"]["no_python_point_rows_in_hot_path"])
        self.assertEqual("torch", payload["partner"])
        self.assertEqual("caller_supplied_torch_device_point_columns", payload["frontdoor_contract"]["input"])
        self.assertEqual("reused_torch_device_output_columns", payload["frontdoor_contract"]["output"])
        self.assertEqual(["torch"], payload["frontdoor_contract"]["measured_partners"])
        self.assertIn("cupy", payload["frontdoor_contract"]["partner_support_declared_unmeasured"])
        self.assertEqual(10.0, payload["product_boundary_gate"]["min_gap_reduction_factor"])
        self.assertEqual(100.0, payload["product_boundary_gate"]["max_device_array_to_route_d_rows_gap"])

    def test_gate_requires_material_gap_reduction_not_parity(self) -> None:
        module = _load_harness_module()
        good_result = {
            "copies": 8192,
            "correctness_passed": True,
            "routes": {
                "device_array_frontdoor_prepared": {
                    "python_point_object_boundary_in_hot_path": False,
                    "host_materialization_in_hot_path": False,
                }
            },
            "comparisons": {
                "route_d_count_rows": {"device_array_to_route_d_rows_gap": 20.0},
                "prior_prepared_summary_gap": {"device_array_gap_reduction_over_prior_summary": 30.0},
            },
        }
        trivial_result = {
            "copies": 32768,
            "correctness_passed": True,
            "routes": {
                "device_array_frontdoor_prepared": {
                    "python_point_object_boundary_in_hot_path": False,
                    "host_materialization_in_hot_path": False,
                }
            },
            "comparisons": {
                "route_d_count_rows": {"device_array_to_route_d_rows_gap": 90.0},
                "prior_prepared_summary_gap": {"device_array_gap_reduction_over_prior_summary": 1.03},
            },
        }
        gate = module._evaluate_gate([good_result, trivial_result])
        self.assertEqual("fail", gate["status"])
        self.assertIn("product-boundary gap did not shrink enough", gate["failures"][0])

    def test_baseline_extractors_use_route_d_rows_and_prior_summary(self) -> None:
        module = _load_harness_module()
        route_d = {
            "results": [
                {"copies": 8192, "routes": {"route_d_count_rows": {"median_s": 0.5}}},
            ]
        }
        summary = {
            "results": [
                {"copies": 8192, "routes": {"summary_prepared_hot": {"median_s": 5.0}}},
            ]
        }
        self.assertEqual({8192: 0.5}, module._route_d_rows_by_copies(route_d))
        self.assertEqual({8192: 5.0}, module._prepared_summary_by_copies(summary))


if __name__ == "__main__":
    unittest.main()
