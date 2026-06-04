from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3220_spatial_rayjoin_current_best_count_harness.py"


class Goal3220SpatialRayJoinCurrentBestCountHarnessTest(unittest.TestCase):
    def test_harness_routes_lsi_to_dense_count_and_keeps_other_routes(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("GOAL3220_HARNESS_VERSION", text)
        self.assertIn("run_rayjoin_prepared_optix_left_id_dense_count_workload", text)
        self.assertIn("run_rayjoin_prepared_optix_workload", text)
        self.assertIn('"prepared_optix_left_id_dense_count"', text)
        self.assertIn('"prepared_optix"', text)
        self.assertIn("lsi_dense_count_else_prepared_optix_count", text)
        self.assertIn("DEFAULT_DATASET_BY_WORKLOAD", text)
        self.assertIn("derived/authored_overlay_squares_tiled_x64", text)
        self.assertIn("per_workload_defaults_unless_overridden", text)

    def test_harness_preserves_claim_boundaries_and_generic_language(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        for phrase in (
            "SEGMENT_PAIR_LEFT_ID_COUNT_DEVICE_COLUMNS_2D",
            "current_best_primitive_first_rt_count_or_parity",
            "public_speedup_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "true_zero_copy_claim_authorized",
            "paper_reproduction_claim_authorized",
            "rtdl_beats_rayjoin_claim_authorized",
            "native_engine_customization",
            "RayJoin workload",
            "interpretation stays in Python",
        ):
            self.assertIn(phrase, text)

    def test_harness_metadata_matches_reproducible_pod_artifact_standard(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        for phrase in (
            "cuda_driver_query",
            "nvcc_version",
            "rtdl_optix_library",
            "RTDL_OPTIX_LIBRARY",
            "/usr/local/cuda/bin/nvcc",
            "--query",
            "--display=COMPUTE",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
