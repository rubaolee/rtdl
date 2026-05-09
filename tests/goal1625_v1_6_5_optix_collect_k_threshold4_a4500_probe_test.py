from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/goal1625_v1_6_5_optix_collect_k_threshold4_a4500_probe.py"


class Goal1625OptixCollectKThreshold4A4500ProbeTest(unittest.TestCase):
    def test_probe_compares_optimized_baseline_to_gated_candidate(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn('"RTDL_OPTIX_COLLECT_K_GATED_CANDIDATE": "1"', text)
        self.assertIn('"RTDL_OPTIX_COLLECT_K_CUB_TILE_SORT": "1"', text)
        self.assertIn('"RTDL_OPTIX_COLLECT_K_DEVICE_FINAL_COUNTS": "1"', text)
        self.assertIn("DEFAULT_COUNTS = (65536, 65537, 65538, 65552, 69632, 69633)", text)
        self.assertIn('"baseline": str(item["baseline"]), "gated": str(item["gated"])', text)

    def test_probe_records_internal_claim_boundary_only(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn('"public_speedup_wording_authorized": False', text)
        self.assertIn('"true_zero_copy_wording_authorized": False', text)
        self.assertIn('"stable_collect_k_promotion_authorized": False', text)
        self.assertIn('"broad_rtx_gpu_wording_authorized": False', text)
        self.assertIn('"release_action_authorized": False', text)
        self.assertIn("internal same-host OptiX collect-k threshold-4 diagnostic evidence only", text)

    def test_probe_summarizes_round_level_deltas_and_payload_copies(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn('"avg_delta_ms"', text)
        self.assertIn('"median_delta_ms"', text)
        self.assertIn('"faster_rounds"', text)
        self.assertIn('"baseline_payload_copies"', text)
        self.assertIn('"gated_payload_copies"', text)
        self.assertIn('"all_parity"', text)


if __name__ == "__main__":
    unittest.main()
