import json
from pathlib import Path
import unittest

from scripts import goal1472_v1_5_3_typed_host_reuse_sweep as sweep


ROOT = Path(__file__).resolve().parents[1]
POD_JSON = ROOT / "docs" / "reports" / "goal1472_v1_5_3_typed_host_reuse_sweep_pod_2026-05-07.json"


class Goal1472V153TypedHostReuseSweepTest(unittest.TestCase):
    def test_parse_default_and_explicit_sweep_specs(self) -> None:
        self.assertEqual(
            sweep.parse_sweep_specs(None),
            ((1024, 4, 20), (4096, 4, 20), (16384, 2, 12)),
        )
        self.assertEqual(
            sweep.parse_sweep_specs(["5:2:3", "8:4:1"]),
            ((5, 2, 3), (8, 4, 1)),
        )

    def test_rejects_malformed_sweep_spec(self) -> None:
        with self.assertRaisesRegex(ValueError, "unique_rows:repeats:iterations"):
            sweep.parse_sweep_specs(["5:2"])
        with self.assertRaisesRegex(ValueError, "positive"):
            sweep.parse_sweep_specs(["5:0:1"])

    def test_sweep_package_preserves_claim_boundaries(self) -> None:
        original_runner = sweep.run_benchmark_package
        try:
            sweep.run_benchmark_package = lambda **kwargs: {
                "accepted": True,
                "unique_rows": kwargs["unique_rows"],
                "repeats": kwargs["repeats"],
                "iterations": kwargs["iterations"],
                "results": (
                    {
                        "backend": "embree",
                        "status": "pass",
                        "candidate_row_count": kwargs["unique_rows"] * kwargs["repeats"],
                        "baseline_input_materialization_count": kwargs["iterations"],
                        "typed_input_materialization_count": 1,
                        "input_materialization_count_delta": kwargs["iterations"] - 1,
                        "baseline_elapsed_total_s": 1.0,
                        "typed_elapsed_total_s": 0.5,
                        "typed_to_baseline_elapsed_ratio": 0.5,
                    },
                ),
            }
            payload = sweep.run_sweep_package(
                backends=("embree",),
                required_backends=("embree",),
                sweep_specs=((5, 2, 3),),
            )
        finally:
            sweep.run_benchmark_package = original_runner

        self.assertTrue(payload["accepted"])
        self.assertFalse(payload["true_zero_copy_authorized"])
        self.assertFalse(payload["public_speedup_wording_authorized"])
        self.assertIn("does not authorize true zero-copy", payload["claim_boundary"])

    def test_pod_sweep_artifact_is_accepted_but_diagnostic_only(self) -> None:
        payload = json.loads(POD_JSON.read_text(encoding="utf-8"))

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["required_backends"], ["embree", "optix"])
        self.assertEqual(payload["failed_packages"], [])
        self.assertEqual(len(payload["packages"]), 3)
        for package in payload["packages"]:
            self.assertTrue(package["accepted"])
            self.assertEqual(package["skipped_required"], [])
            by_backend = {row["backend"]: row for row in package["results"]}
            self.assertEqual(set(by_backend), {"embree", "optix"})
            for backend, row in by_backend.items():
                with self.subTest(unique_rows=package["unique_rows"], backend=backend):
                    self.assertEqual(row["status"], "pass")
                    self.assertEqual(row["typed_input_materialization_count"], 1)
                    self.assertGreater(row["input_materialization_count_delta"], 0)
                    self.assertTrue(row["timing_recorded_for_diagnostics_only"])
        self.assertFalse(payload["true_zero_copy_authorized"])
        self.assertFalse(payload["public_speedup_wording_authorized"])
        self.assertIn("does not authorize true zero-copy", payload["claim_boundary"])


if __name__ == "__main__":
    unittest.main()
