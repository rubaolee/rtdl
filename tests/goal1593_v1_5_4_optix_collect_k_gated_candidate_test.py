import os
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import goal1506_v1_5_4_optix_collect_k_stage_profile_probe as probe


ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"


class Goal1593V154OptixCollectKGatedCandidateTest(unittest.TestCase):
    def test_native_gated_candidate_is_opt_in_and_topology_guarded(self) -> None:
        source = API.read_text(encoding="utf-8")

        self.assertIn("RTDL_OPTIX_COLLECT_K_GATED_CANDIDATE", source)
        self.assertIn("collect_k_use_gated_fastest_candidate(candidate_count)", source)
        self.assertIn("candidate_copies < baseline_copies", source)

    def test_probe_gated_candidate_enables_only_predicted_copy_reduction(self) -> None:
        with patch.dict(os.environ, {"RTDL_OPTIX_COLLECT_K_GATED_CANDIDATE": "1"}, clear=True):
            topology_65535 = probe.expected_topology(65535, 2)
            topology_65537 = probe.expected_topology(65537, 2)

        self.assertEqual(topology_65535["carry_payload_copies"], 0)
        self.assertEqual(topology_65535["tile_count"], 16)
        self.assertEqual(topology_65535["sort_launches"], 16)

        self.assertEqual(topology_65537["carry_payload_copies"], 0)
        self.assertEqual(topology_65537["tile_count"], 33)
        self.assertEqual(topology_65537["sort_launches"], 1)

    def test_probe_gated_candidate_preserves_default_without_env(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            topology = probe.expected_topology(65537, 2)

        self.assertEqual(topology["carry_payload_copies"], 4)
        self.assertEqual(topology["tile_count"], 17)
        self.assertEqual(topology["sort_launches"], 17)


if __name__ == "__main__":
    unittest.main()
