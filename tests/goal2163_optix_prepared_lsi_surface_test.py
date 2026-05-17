from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
OPTIX_API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
OPTIX_PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
OPTIX_WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
OPTIX_RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
RUNNER = ROOT / "scripts" / "goal2159_rayjoin_public_cdb_runner.py"


class Goal2163OptixPreparedLsiSurfaceTest(unittest.TestCase):
    def test_native_surface_exposes_generic_prepared_segment_pair_intersection(self) -> None:
        api = OPTIX_API.read_text(encoding="utf-8")
        prelude = OPTIX_PRELUDE.read_text(encoding="utf-8")
        workloads = OPTIX_WORKLOADS.read_text(encoding="utf-8")

        for text in (api, prelude, workloads):
            with self.subTest(path="native"):
                self.assertIn("segment_pair_intersection", text)
                self.assertNotIn("rayjoin", text.lower())

        self.assertIn("rtdl_optix_prepare_segment_pair_intersection", api)
        self.assertIn("rtdl_optix_run_prepared_segment_pair_intersection", api)
        self.assertIn("rtdl_optix_destroy_prepared_segment_pair_intersection", api)
        self.assertIn("PreparedSegmentPairIntersectionBuild", workloads)

    def test_python_runtime_wraps_prepared_lsi_handle(self) -> None:
        runtime = OPTIX_RUNTIME.read_text(encoding="utf-8")

        self.assertIn("PreparedOptixSegmentPairIntersection", runtime)
        self.assertIn("prepare_segment_pair_intersection_optix", runtime)
        self.assertIn("rtdl_optix_run_prepared_segment_pair_intersection", runtime)
        self.assertIn("rtdl_optix_destroy_prepared_segment_pair_intersection", runtime)

    def test_runner_can_select_prepared_lsi_backend(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")

        self.assertIn("optix_prepared_lsi", text)
        self.assertIn("prepared_build_side_reused", text)
        self.assertIn("baseline_kind", text)


if __name__ == "__main__":
    unittest.main()
