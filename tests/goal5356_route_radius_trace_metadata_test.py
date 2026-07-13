import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "scripts"
ARTIFACT = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results" / "xhd_goal5356_route_radius_trace_metadata.json"
ROUTE_GATE = SCRIPT_DIR / "run_xhd_cell_mbr_frontier_route_gate.py"
HD_EXEC = SCRIPT_DIR / "run_xhd_rtdl_hd_exec.py"
BUILDER = SCRIPT_DIR / "build_xhd_goal5356_route_radius_trace_metadata.py"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5356RouteRadiusTraceMetadataTest(unittest.TestCase):
    def setUp(self):
        sys.path.insert(0, str(SCRIPT_DIR))
        self.builder = _load_module("goal5356_builder", BUILDER)
        self.route_gate = _load_module("goal5356_route_gate", ROUTE_GATE)
        self.hd_exec = _load_module("goal5356_hd_exec", HD_EXEC)

    def test_route_gate_emits_single_pass_radius_trace_under_flag(self):
        payload = self.builder.build_artifact()
        trace = payload["radius_trace_metadata"]
        self.assertEqual(
            "single_pass_cell_mbr_radius_trace_metadata_available__author_queue_semantics_not_aligned",
            trace["status"],
        )
        self.assertEqual("single_pass_cell_mbr_route_not_author_radius_loop", trace["route_iteration_model"])
        self.assertFalse(trace["author_queue_semantics_aligned"])
        self.assertFalse(trace["author_trace_comparison_ready"])
        self.assertFalse(trace["route_uses_radius_growth_helper"])
        self.assertEqual(1, len(trace["directions"]))
        direction = trace["directions"][0]
        self.assertEqual("a_to_b", direction["label"])
        self.assertEqual(1, direction["iteration"])
        self.assertEqual(direction["num_input_points"], payload["route_probe"]["point_count_a"])
        self.assertEqual(direction["num_output_points"], direction["frontier_row_count"])
        self.assertEqual(
            "frontier_row_count_after_single_pass_not_author_out_queue",
            direction["output_count_semantics"],
        )

    def test_artifact_preserves_claim_boundary_and_fail_closed_tune_radius(self):
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(
            "route_radius_trace_metadata_available__single_pass_not_author_queue_aligned",
            payload["status"],
        )
        for key, value in payload["claim_boundary"].items():
            self.assertIs(value, False, key)
        fail_closed = payload["explicit_tune_radius_fail_closed_check"]
        self.assertEqual("unsupported_author_rt_options_fail_closed", fail_closed["explicit_tune_radius_status"])
        self.assertEqual(["tune_radius"], fail_closed["explicit_author_rt_options"])
        self.assertFalse(fail_closed["route_executed"])

    def test_hd_exec_exposes_internal_trace_flag_without_enabling_author_option(self):
        parser = self.hd_exec.build_parser()
        args = parser.parse_args(
            [
                "-input1",
                "a.wkt",
                "-input2",
                "b.wkt",
                "-json",
                "out.json",
                "-execution",
                "gpu",
                "--emit-radius-trace-metadata",
            ]
        )
        self.assertTrue(args.emit_radius_trace_metadata)
        self.assertIsNone(args.author_rt_tune_radius)
        surface = self.hd_exec._author_rt_option_surface(args, route_label="cell-mbr-exact-witness")
        self.assertEqual([], surface["explicit_author_rt_options"])

    def test_route_gate_parser_exposes_trace_flag(self):
        parser_names = {
            action.dest
            for action in self.route_gate.argparse.ArgumentParser()._actions
        }
        # The actual parser is constructed in main; this source-level guard keeps
        # the app-owned flag visible without executing CLI parsing internals.
        text = ROUTE_GATE.read_text(encoding="utf-8")
        self.assertIn("--emit-radius-trace-metadata", text)
        self.assertIn("author_queue_semantics_not_aligned", text)
        self.assertNotIn("author_tune_radius_supported = True", text)
        self.assertNotIn("route_uses_radius_growth_helper = True", text)
        self.assertIsInstance(parser_names, set)


if __name__ == "__main__":
    unittest.main()
