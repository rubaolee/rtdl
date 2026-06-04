from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3232_rayjoin_public_row_continuation_probe.py"


class Goal3232RayJoinPublicRowContinuationProbeTest(unittest.TestCase):
    def test_script_uses_public_pip_and_overlay_row_mode(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        for phrase in (
            '"pip_county512"',
            '"lsi_county256_soil256_count512"',
            '"overlay_county128_soil128"',
            '"overlay_county256_soil256"',
            'result_mode="rows"',
            "include_rows=True",
            "row_set_matches_cpu",
            "symmetric_difference_count",
            "prepared PIP rows must be positive-only",
            "unattributed_prepared_total_minus_named_phases_sec",
            "positive_assignments_count",
            "active_seed_pairs_count",
            "max_lsi_coordinate_delta",
            "--artifact-goal",
            "--schema",
        ):
            self.assertIn(phrase, text)

    def test_script_normalizes_generic_rows_at_app_boundary(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        for phrase in (
            'shape_key = "shape_id" if source == "prepared_optix" else "polygon_id"',
            '"requires_lsi"',
            '"requires_pip"',
            "native_minus_cpu_sample",
            "cpu_minus_native_sample",
        ):
            self.assertIn(phrase, text)

    def test_script_preserves_claim_boundaries(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        for phrase in (
            "public_speedup_claim_authorized",
            "rt_core_speedup_claim_authorized",
            "true_zero_copy_claim_authorized",
            "rayjoin_paper_reproduction_claim_authorized",
            "rtdl_beats_rayjoin_claim_authorized",
            "release_authorized",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
