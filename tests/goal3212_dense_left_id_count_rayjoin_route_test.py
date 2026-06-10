from __future__ import annotations

from pathlib import Path
import unittest

from examples.current.research_benchmarks.spatial_rayjoin import rtdl_rayjoin_v2_spatial_join_app as app


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "spatial_rayjoin" / "rtdl_rayjoin_v2_spatial_join_app.py"
README = ROOT / "examples" / "v2_0" / "research_benchmarks" / "spatial_rayjoin" / "README.md"


class Goal3212DenseLeftIdCountRayJoinRouteTest(unittest.TestCase):
    def test_cli_and_workload_helper_are_wired(self) -> None:
        source = APP.read_text(encoding="utf-8")

        self.assertIn("run_rayjoin_prepared_optix_left_id_dense_count_workload", source)
        self.assertIn("prepared_optix_left_id_dense_count", source)
        self.assertIn("run_packed_left_dense_count", source)
        self.assertIn("pack_rayjoin_optix_compact_grouped_count_left_segments", source)
        self.assertIn("generic segment-pair left-id count device-column primitive", source)
        self.assertIn('"public_speedup_claim_authorized": False', source)
        self.assertNotIn("rtdl_optix_rayjoin", source)
        self.assertNotIn("rtdl_optix_run_rayjoin", source)

    def test_route_rejects_non_lsi_workloads_before_optix_import(self) -> None:
        with self.assertRaisesRegex(ValueError, "supports only the lsi workload"):
            app.run_rayjoin_prepared_optix_left_id_dense_count_workload("pip")

    def test_readme_mentions_dense_count_contract(self) -> None:
        readme = README.read_text(encoding="utf-8")

        for phrase in (
            "run_packed_left_dense_count",
            "generic fused",
            "dense count-column contract",
            "count[index]",
        ):
            self.assertIn(phrase, readme)


if __name__ == "__main__":
    unittest.main()
