from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "spatial_rayjoin" / "rtdl_rayjoin_v2_spatial_join_app.py"
README = ROOT / "examples" / "v2_0" / "research_benchmarks" / "spatial_rayjoin" / "README.md"


class Goal3207PackedLeftRayJoinCompactRouteTest(unittest.TestCase):
    def test_packed_left_api_is_explicit_and_app_layer_scoped(self) -> None:
        source = APP.read_text(encoding="utf-8")

        self.assertIn("class RayJoinOptixCompactGroupedCountPackedLeftSegments", source)
        self.assertIn("pack_rayjoin_optix_compact_grouped_count_left_segments", source)
        self.assertIn("def run_packed_left(", source)
        self.assertIn("packed_left.packed_segments", source)
        self.assertIn("packed_left.original_left_ids", source)
        self.assertIn("query_pack_paid_in_call", source)
        self.assertIn("prepared_optix_compact_grouped_count_reuse", source)
        self.assertIn("RayJoin workload interpretation, prepared-handle reuse, and left-ID remapping stay in Python", source)
        self.assertNotIn("rtdl_optix_rayjoin", source)
        self.assertNotIn("rtdl_optix_run_rayjoin", source)

    def test_ordinary_run_delegates_to_packed_left_path(self) -> None:
        source = APP.read_text(encoding="utf-8")
        run_start = source.index("    def run(\n        self,\n        left_segments,")
        run_end = source.index("    def run_packed_left(", run_start)
        body = source[run_start:run_end]

        self.assertIn("packed_left = self.pack_left_segments(left_segments)", body)
        self.assertIn("self.run_packed_left(", body)
        self.assertIn('"query_pack_sec": packed_left.pack_seconds', body)
        self.assertIn('"enabled": False', body)
        self.assertIn('"query_pack_paid_in_call": True', body)

    def test_readme_documents_repeated_left_query_reuse(self) -> None:
        readme = README.read_text(encoding="utf-8")

        for phrase in (
            "pack_rayjoin_optix_compact_grouped_count_left_segments",
            "packed_left =",
            "run_packed_left",
            "avoid paying Python query packing on every call",
            "app-layer code",
            "RayJoin route policy",
        ):
            self.assertIn(phrase, readme)


if __name__ == "__main__":
    unittest.main()
