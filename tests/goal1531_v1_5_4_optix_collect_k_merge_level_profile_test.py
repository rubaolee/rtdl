from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
OPTIX_API_CPP = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"


class Goal1531V154OptixCollectKMergeLevelProfileTest(unittest.TestCase):
    def test_native_profile_records_per_merge_level_details(self) -> None:
        text = OPTIX_API_CPP.read_text(encoding="utf-8")

        self.assertIn("struct MergeLevel", text)
        self.assertIn("merge_level_profile", text)
        self.assertIn("input_segments", text)
        self.assertIn("pair_count", text)
        self.assertIn("sync_ms", text)
        self.assertIn("profile.record_merge_level(level_profile);", text)

    def test_instrumentation_remains_profile_env_gated(self) -> None:
        text = OPTIX_API_CPP.read_text(encoding="utf-8")

        self.assertIn("RTDL_OPTIX_COLLECT_K_PROFILE_JSONL", text)
        self.assertIn("if (enabled)", text)
        self.assertIn("Profiling must never change runtime behavior", text)


if __name__ == "__main__":
    unittest.main()
