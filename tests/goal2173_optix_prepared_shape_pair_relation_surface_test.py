from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
OPTIX_API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
OPTIX_PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
OPTIX_WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
OPTIX_RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
RUNNER = ROOT / "scripts" / "goal2159_rayjoin_public_cdb_runner.py"


class Goal2173OptixPreparedShapePairRelationSurfaceTest(unittest.TestCase):
    def test_native_surface_exposes_generic_prepared_shape_pair_relation(self) -> None:
        api = OPTIX_API.read_text(encoding="utf-8")
        prelude = OPTIX_PRELUDE.read_text(encoding="utf-8")
        workloads = OPTIX_WORKLOADS.read_text(encoding="utf-8")

        self.assertIn("rtdl_optix_prepare_shape_pair_relation_flags", api)
        self.assertIn("rtdl_optix_run_prepared_shape_pair_relation_flags", api)
        self.assertIn("rtdl_optix_destroy_prepared_shape_pair_relation_flags", api)
        self.assertIn("rtdl_optix_prepare_shape_pair_relation_flags", prelude)
        self.assertIn("rtdl_optix_run_prepared_shape_pair_relation_flags", prelude)
        self.assertIn("PreparedShapePairRelationBuild", workloads)
        self.assertIn("run_shape_pair_relation_flags_with_prepared_right_optix", workloads)
        self.assertIn("ensure_shape_pair_relation_pipeline", workloads)

        for forbidden in ("rayjoin", "county", "soil"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, api.lower())
                self.assertNotIn(forbidden, prelude.lower())

    def test_python_runtime_wraps_prepared_shape_pair_handle(self) -> None:
        runtime = OPTIX_RUNTIME.read_text(encoding="utf-8")

        self.assertIn("PreparedOptixShapePairRelation", runtime)
        self.assertIn("prepare_shape_pair_relation_flags_optix", runtime)
        self.assertIn("rtdl_optix_prepare_shape_pair_relation_flags", runtime)
        self.assertIn("rtdl_optix_run_prepared_shape_pair_relation_flags", runtime)
        self.assertIn("rtdl_optix_destroy_prepared_shape_pair_relation_flags", runtime)
        self.assertIn("PackedPolygons", runtime)

    def test_runner_can_select_prepared_overlay_seed_backend(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")

        self.assertIn("optix_prepared_overlay_seed", text)
        self.assertIn("prepared_optix_shape_pair_relation_reused_build_side", text)
        self.assertIn("prepare_shape_pair_relation_flags_optix", text)
        self.assertIn("prepared_build_side_reused", text)


if __name__ == "__main__":
    unittest.main()
