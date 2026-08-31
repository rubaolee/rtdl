import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "scripts" / "run_xhd_rtdl_hd_exec.py"
ARTIFACT = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results" / "xhd_goal5353_author_rt_option_surface_gate.json"


def _load_runner():
    spec = importlib.util.spec_from_file_location("run_xhd_rtdl_hd_exec_goal5353", RUNNER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5353XhdAuthorRtOptionSurfaceGateTest(unittest.TestCase):
    def setUp(self):
        self.runner = _load_runner()

    def parse_args(self, extra):
        base = [
            "-input1",
            "missing-a.ply",
            "-input2",
            "missing-b.ply",
            "-json",
            "out.json",
            "-variant",
            "rt",
            "-execution",
            "gpu",
        ]
        return self.runner.build_parser().parse_args(base + list(extra))

    def test_omitted_author_rt_options_record_defaults_without_claiming_parity(self):
        args = self.parse_args([])
        route_label = self.runner._select_route_label(
            requested=args.rtdl_route,
            n_dims=args.n_dims,
            execution=args.execution,
        )
        surface = self.runner._author_rt_option_surface(args, route_label=route_label)
        self.assertEqual("no_explicit_author_rt_options__author_defaults_recorded_only", surface["status"])
        self.assertEqual([], surface["explicit_author_rt_options"])
        self.assertIsNone(surface["all_explicit_author_rt_options_supported"])
        self.assertFalse(surface["claim_boundary"]["author_rt_option_surface_complete_claimed"])
        self.assertFalse(surface["claim_boundary"]["author_rt_core_algorithm_equivalence_claimed"])
        self.assertEqual(True, surface["options"]["eb"]["author_default"])
        self.assertEqual(True, surface["options"]["prune"]["author_default"])
        self.assertEqual(256, surface["options"]["lb"]["author_default"])
        self.assertEqual("adaptive", surface["options"]["tune_radius"]["author_default"])

    def test_explicit_author_rt_options_are_parsed_and_fail_closed(self):
        args = self.parse_args(["-eb=false", "-lb", "0", "-tune_radius", "double"])
        route_label = self.runner._select_route_label(
            requested=args.rtdl_route,
            n_dims=args.n_dims,
            execution=args.execution,
        )
        surface = self.runner._author_rt_option_surface(args, route_label=route_label)
        self.assertEqual("unsupported_explicit_author_rt_options", surface["status"])
        self.assertEqual(["eb", "lb", "tune_radius"], surface["explicit_author_rt_options"])
        self.assertFalse(surface["all_explicit_author_rt_options_supported"])
        self.assertEqual(False, surface["options"]["eb"]["effective_value"])
        self.assertEqual(0, surface["options"]["lb"]["effective_value"])
        self.assertEqual("double", surface["options"]["tune_radius"]["effective_value"])
        with self.assertRaises(self.runner.UnsupportedAuthorRtOptionsError):
            self.runner._raise_if_unsupported_author_rt_options(surface)

    def test_main_writes_fail_closed_json_before_loading_missing_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out.json"
            exit_code = self.runner.main(
                [
                    "-input1",
                    "does-not-exist-a.ply",
                    "-input2",
                    "does-not-exist-b.ply",
                    "-json",
                    str(out),
                    "-variant",
                    "rt",
                    "-execution",
                    "gpu",
                    "-lb",
                    "0",
                ]
            )
            self.assertEqual(2, exit_code)
            payload = json.loads(out.read_text(encoding="utf-8"))
        self.assertIsNone(payload["HDResult"])
        self.assertEqual("unsupported_author_rt_options_fail_closed", payload["RTDL"]["status"])
        surface = payload["RTDL"]["author_rt_option_surface"]
        self.assertEqual(["lb"], surface["explicit_author_rt_options"])
        self.assertEqual(0, surface["options"]["lb"]["effective_value"])
        self.assertFalse(payload["RTDL"]["claim_boundary"]["author_rt_option_surface_complete_claimed"])
        self.assertFalse(payload["RTDL"]["claim_boundary"]["author_rt_core_algorithm_equivalence_claim_authorized"])

    def test_author_rt_option_specs_do_not_list_radius_as_cli_flag(self):
        self.assertNotIn("radius", self.runner.AUTHOR_RT_OPTION_SPECS)
        for expected in [
            "fast_build_bvh",
            "rebuild_bvh",
            "eb",
            "prune",
            "lb",
            "n_points_cell",
            "tune_grid",
            "tune_radius",
        ]:
            self.assertIn(expected, self.runner.AUTHOR_RT_OPTION_SPECS)

    def test_goal5353_artifact_records_fail_closed_gate(self):
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(
            "author_rt_option_surface_gate_ready__explicit_options_fail_closed",
            payload["status"],
        )
        self.assertFalse(payload["radius_cli_flag_present"])
        self.assertEqual([], payload["default_surface"]["explicit_author_rt_options"])
        explicit = payload["explicit_surface"]
        self.assertEqual("unsupported_explicit_author_rt_options", explicit["status"])
        self.assertEqual(
            [
                "fast_build_bvh",
                "rebuild_bvh",
                "eb",
                "prune",
                "lb",
                "n_points_cell",
                "tune_grid",
                "tune_radius",
            ],
            explicit["explicit_author_rt_options"],
        )
        self.assertEqual("unsupported_author_rt_options_fail_closed", payload["fail_closed_payload_status"])
        for key, value in payload["claim_boundary"].items():
            self.assertIs(value, False, key)


if __name__ == "__main__":
    unittest.main()
