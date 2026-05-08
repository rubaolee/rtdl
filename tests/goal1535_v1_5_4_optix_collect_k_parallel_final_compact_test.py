from pathlib import Path
import os
import unittest

from scripts import goal1506_v1_5_4_optix_collect_k_stage_profile_probe as probe


ROOT = Path(__file__).resolve().parents[1]
API_CPP = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
CORE_CPP = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"


class Goal1535V154OptixCollectKParallelFinalCompactTest(unittest.TestCase):
    def test_env_gated_source_path_is_present(self) -> None:
        source = API_CPP.read_text(encoding="utf-8") + CORE_CPP.read_text(encoding="utf-8")

        self.assertIn("RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT", source)
        self.assertIn("collect_k_bounded_i64_row_width2_final_materialize", source)
        self.assertIn("collect_k_bounded_i64_row_width2_final_mark_counts", source)
        self.assertIn("collect_k_bounded_i64_row_width2_final_compact", source)
        self.assertIn("collect_k_use_parallel_final_compact", source)

    def test_default_topology_stays_batched_merge_level(self) -> None:
        os.environ.pop("RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT", None)

        self.assertEqual(probe.expected_topology(131072, 2)["merge_launches"], 5)
        self.assertEqual(probe.expected_topology(131072, 2)["metadata_fields_downloaded"], 126)
        self.assertEqual(probe.expected_topology(131072, 2)["final_copies"], 1)

    def test_parallel_final_compact_topology_is_stricter_not_smoke(self) -> None:
        old_value = os.environ.get("RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT")
        os.environ["RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT"] = "1"
        try:
            topology_4097 = probe.expected_topology(4097, 2)
            topology_65537 = probe.expected_topology(65537, 2)
            topology_131072 = probe.expected_topology(131072, 2)
        finally:
            if old_value is None:
                os.environ.pop("RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT", None)
            else:
                os.environ["RTDL_OPTIX_COLLECT_K_PARALLEL_FINAL_COMPACT"] = old_value

        self.assertEqual(topology_4097["merge_launches"], 1)
        self.assertEqual(topology_4097["metadata_fields_downloaded"], 6)
        self.assertEqual(topology_4097["final_copies"], 1)
        self.assertEqual(topology_65537["merge_launches"], 9)
        self.assertEqual(topology_65537["metadata_fields_downloaded"], 64)
        self.assertEqual(topology_65537["final_copies"], 0)
        self.assertEqual(topology_131072["merge_launches"], 12)
        self.assertEqual(topology_131072["metadata_fields_downloaded"], 123)
        self.assertEqual(topology_131072["final_copies"], 0)


if __name__ == "__main__":
    unittest.main()
