from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
APP = ROOT / "Paper-reproduction-apps" / "rayjoin-paper" / "section57_overlay_columnar_binary.py"


class Goal4968PlanarMapLsiWorkspaceContractTest(unittest.TestCase):
    def test_runtime_exposes_generic_prepared_workspace_contract(self) -> None:
        source = RUNTIME.read_text(encoding="utf-8")

        self.assertIn("def prepare_workspace(self) -> dict[str, object]:", source)
        self.assertIn('"schema": "rtdl.optix.planar_map_lsi_2d.prepared_workspace.v1"', source)
        self.assertIn('"primitive": "PLANAR_MAP_LSI_2D"', source)
        self.assertIn('"workspace_depends_on_base_and_query": True', source)
        self.assertIn('"rayjoin_specific_core_primitive": False', source)
        self.assertIn("count_prepared_left_exact_intersections", source)

    def test_workspace_contract_does_not_reference_overlay_output_semantics(self) -> None:
        source = RUNTIME.read_text(encoding="utf-8")
        function_block = source.split("def prepare_workspace(self) -> dict[str, object]:", 1)[1].split(
            "def close(self) -> None:",
            1,
        )[0].lower()

        self.assertNotIn("output_chain", function_block)
        self.assertNotIn("overlay", function_block)
        self.assertNotIn("authorofficial", function_block)

    def test_public_app_uses_workspace_prepare_for_prepared_hot_route(self) -> None:
        source = APP.read_text(encoding="utf-8")

        self.assertIn("workspace = timed(\"lsi_prepare_workspace_sec\", query.prepare_workspace, phase_seconds)", source)
        self.assertIn("native_lsi_timings[\"prepared_workspace\"] = workspace", source)
        self.assertIn("lsi_prepared_replay_rows_sec", source)
        self.assertNotIn("lsi_public_rows_warmup_sec", source)


if __name__ == "__main__":
    unittest.main()
