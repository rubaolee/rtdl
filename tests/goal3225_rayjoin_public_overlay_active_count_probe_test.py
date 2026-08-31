from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3225_rayjoin_public_overlay_active_count_probe.py"


class Goal3225RayJoinPublicOverlayActiveCountProbeTest(unittest.TestCase):
    def test_probe_reuses_public_cdb_runner_and_overlay_cases(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("overlay_county128_soil128", text)
        self.assertIn("overlay_county256_soil256", text)
        self.assertIn("_maybe_download_samples", text)
        self.assertIn("_materialize_slices", text)
        self.assertIn("_resolve_dataset_template", text)
        self.assertIn("goal3225 probe supports only overlay_seed cases", text)

    def test_probe_compares_active_seed_count_contract(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("active_seed_count", text)
        self.assertIn("expected_active_seed_count", text)
        self.assertIn("prepared_overlay_active_count", text)
        self.assertIn("include_rows_measured", text)
        self.assertIn("run_rayjoin_prepared_optix_workload", text)

    def test_probe_preserves_claim_boundaries_and_metadata(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        for phrase in (
            "public_speedup_claim_authorized",
            "rt_core_speedup_claim_authorized",
            "true_zero_copy_claim_authorized",
            "rayjoin_paper_reproduction_claim_authorized",
            "rtdl_beats_rayjoin_claim_authorized",
            "release_authorized",
            "cuda_driver_query",
            "nvcc_version",
            "rtdl_optix_library",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
