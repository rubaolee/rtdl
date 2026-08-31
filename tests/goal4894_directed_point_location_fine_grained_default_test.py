import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal4894DirectedPointLocationFineGrainedDefaultTest(unittest.TestCase):
    def test_native_directed_point_location_defaults_to_fine_grained_ranges(self) -> None:
        source = (ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp").read_text(
            encoding="utf-8"
        )

        self.assertIn("enum class RayjoinCdbGroupMode {\n    FineGrained,", source)
        self.assertIn("return RayjoinCdbGroupMode::FineGrained;", source)
        self.assertIn('value == "fine_grained" || value == "per_segment"', source)
        self.assertIn('value == "fixed8" || value == "fixed_8"', source)
        self.assertIn("group_mode == RayjoinCdbGroupMode::FineGrained", source)
        self.assertIn("ranges.resize(segments.size());", source)
        self.assertIn("aabbs.resize(segments.size());", source)
        self.assertIn("static_cast<uint32_t>(index + 1)", source)
        self.assertIn("aabbs[index] = rounded(segment_bounds(index));", source)

    def test_block_merge64_default_does_not_remerge_fine_grained_blocks(self) -> None:
        source = (ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp").read_text(
            encoding="utf-8"
        )

        self.assertIn("static int rayjoin_cdb_group_max_iter_from_env()", source)
        self.assertIn("return 0;", source)
        self.assertIn('value == "block_merge64" || value == "author_block_merge64"', source)

    def test_bundled_helper_auto_mode_uses_measured_zero_merge_setting(self) -> None:
        overlay = (ROOT / "src" / "rtdsl" / "rayjoin_overlay.py").read_text(encoding="utf-8")

        auto_env = overlay.split("def _directed_segment_point_location_grouping_env", 1)[1]
        values_block = auto_env.split("values = {", 1)[1].split("}", 1)[0]
        self.assertIn('"RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_MODE": "block_merge64"', values_block)
        self.assertIn('"RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_MAX_ITER": "0"', values_block)
        self.assertNotIn('"RTDL_DIRECTED_SEGMENT_POINT_LOCATION_GROUP_MAX_ITER": "5"', values_block)


if __name__ == "__main__":
    unittest.main()
