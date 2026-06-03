from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3218_rayjoin_public_lsi_dense_count_probe.py"


class Goal3218RayJoinPublicLsiDenseCountProbeTest(unittest.TestCase):
    def test_probe_uses_public_slices_and_both_count_routes(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("DEFAULT_CASES", source)
        self.assertIn("lsi_county256_soil256_count512", source)
        self.assertIn("prepare_rayjoin_optix_compact_grouped_count_segments", source)
        self.assertIn("pack_rayjoin_optix_compact_grouped_count_left_segments", source)
        self.assertIn("_load_rayjoin_case", source)
        self.assertIn('route == "dense"', source)
        self.assertIn('route == "compact"', source)
        self.assertIn("run_packed_left_dense_count", source)
        self.assertIn("run_packed_left(packed_left", source)

    def test_probe_records_methodology_hardware_and_claim_boundaries(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")

        for phrase in (
            "include_rows_measured",
            "dense_over_compact_ratio",
            "nvidia-smi",
            "nvcc_version",
            "rtdl_optix_library",
            "public_speedup_claim_authorized",
            "rt_core_speedup_claim_authorized",
            "rayjoin_paper_reproduction_claim_authorized",
            "rtdl_beats_rayjoin_claim_authorized",
            "release_authorized",
        ):
            self.assertIn(phrase, source)


if __name__ == "__main__":
    unittest.main()
