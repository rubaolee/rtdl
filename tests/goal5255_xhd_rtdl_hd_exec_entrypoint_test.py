from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
SCRIPT_PATH = APP_DIR / "scripts" / "run_xhd_rtdl_hd_exec.py"
FIXTURE_A = APP_DIR / "data" / "fixtures" / "directed2d_asymmetric_a.wkt"
FIXTURE_B = APP_DIR / "data" / "fixtures" / "directed2d_asymmetric_b.wkt"
BOUNDED_A = APP_DIR / "data" / "fixtures" / "bounded2d_a.wkt"
BOUNDED_B = APP_DIR / "data" / "fixtures" / "bounded2d_b.wkt"


def _load_runner():
    spec = importlib.util.spec_from_file_location("xhd_rtdl_hd_exec", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Goal5255XhdRtdlHdExecEntrypointTest(unittest.TestCase):
    def test_author_style_cli_writes_directed_hdresult_json(self) -> None:
        runner = _load_runner()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "rtdl_hd_exec.json"
            rc = runner.main(
                [
                    "-input1",
                    str(FIXTURE_A),
                    "-input2",
                    str(FIXTURE_B),
                    "-n_dims",
                    "2",
                    "-input_type",
                    "wkt",
                    "-variant",
                    "rt",
                    "-execution",
                    "cpu",
                    "-json",
                    str(out),
                    "--rtdl-route",
                    "public-columnar",
                ]
            )
            payload = json.loads(out.read_text(encoding="utf-8"))

        self.assertEqual(rc, 0)
        self.assertEqual(payload["HDResult"], 0.5)
        self.assertIn("Running", payload)
        self.assertGreaterEqual(payload["Running"]["AvgTime"], 0.0)
        self.assertEqual(payload["Running"]["Algorithm"], "RTDL-public-columnar")
        self.assertIn("RTDL route wall time", payload["Running"]["TimeSemantics"])
        self.assertEqual(payload["RTDL"]["schema"], "rtdl.paper_reproduction.xhd.rtdl_hd_exec_compatible.v1")
        self.assertEqual(payload["RTDL"]["entrypoint_contract"], "author_hd_exec_key_flags_plus_rtdl_route_extension")
        self.assertEqual(payload["RTDL"]["hd_result_semantics"], "directed_input1_to_input2")
        self.assertIn("not be compared to author internal", payload["RTDL"]["running_avg_time_semantics"])
        self.assertEqual(payload["RTDL"]["route_label"], "public-columnar")
        self.assertEqual(payload["RTDL"]["route"]["route"], "rtdl_public_columnar_directed_2d")
        self.assertAlmostEqual(payload["RTDL"]["route"]["directed_a_to_b"]["distance"], 0.5)
        self.assertTrue(payload["RTDL"]["route"]["per_source_witness_exact"])
        self.assertFalse(payload["RTDL"]["claim_boundary"]["full_xhd_paper_reproduction_claim_authorized"])
        self.assertFalse(payload["RTDL"]["claim_boundary"]["author_rt_core_algorithm_equivalence_claim_authorized"])
        self.assertFalse(payload["RTDL"]["claim_boundary"]["performance_claim_authorized"])
        self.assertIn("not a claim of full paper reproduction", payload["RTDL"]["boundary"])

    def test_auto_route_uses_public_columnar_for_cpu_and_keeps_author_flag_names(self) -> None:
        runner = _load_runner()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "auto_cpu.json"
            rc = runner.main(
                [
                    "-input1",
                    str(BOUNDED_A),
                    "-input2",
                    str(BOUNDED_B),
                    "-n_dims",
                    "2",
                    "-input_type",
                    "wkt",
                    "-variant",
                    "rt",
                    "-execution",
                    "cpu",
                    "-json",
                    str(out),
                ]
            )
            payload = json.loads(out.read_text(encoding="utf-8"))

        self.assertEqual(rc, 0)
        self.assertEqual(payload["RTDL"]["route_label"], "public-columnar")
        self.assertEqual(payload["RTDL"]["variant"], "rt")
        self.assertEqual(payload["RTDL"]["execution"], "cpu")

    def test_non_rt_author_variants_are_value_compatible_not_algorithm_equivalent(self) -> None:
        runner = _load_runner()
        with tempfile.TemporaryDirectory() as tmp:
            common = [
                "-input1",
                str(BOUNDED_A),
                "-input2",
                str(BOUNDED_B),
                "-n_dims",
                "2",
                "-input_type",
                "wkt",
                "-execution",
                "cpu",
                "-json",
                str(Path(tmp) / "unused.json"),
            ]
            out = Path(tmp) / "nn.json"
            rc = runner.main([*common[:-1], str(out), "-variant", "nn"])
            payload = json.loads(out.read_text(encoding="utf-8"))

            self.assertEqual(rc, 0)
            self.assertEqual(payload["RTDL"]["variant"], "nn")
            self.assertEqual(
                payload["RTDL"]["variant_support"]["status"],
                "author_variant_value_compatible_route_only",
            )
            self.assertTrue(payload["RTDL"]["variant_support"]["hdresult_value_supported"])
            self.assertFalse(
                payload["RTDL"]["variant_support"]["author_variant_algorithm_equivalence_claimed"]
            )
            self.assertFalse(
                payload["RTDL"]["claim_boundary"]["author_variant_algorithm_equivalence_claimed"]
            )

    def test_fail_closed_for_image_input(self) -> None:
        runner = _load_runner()
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "does not yet support -input_type image"):
                runner.main(
                    [
                        "-input1",
                        str(BOUNDED_A),
                        "-input2",
                        str(BOUNDED_B),
                        "-n_dims",
                        "2",
                        "-input_type",
                        "image",
                        "-variant",
                        "rt",
                        "-execution",
                        "cpu",
                        "-json",
                        str(Path(tmp) / "unused.json"),
                    ]
                )

    def test_overwrite_false_rejects_existing_output(self) -> None:
        runner = _load_runner()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "existing.json"
            out.write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(FileExistsError, "already exists"):
                runner.main(
                    [
                        "-input1",
                        str(BOUNDED_A),
                        "-input2",
                        str(BOUNDED_B),
                        "-n_dims",
                        "2",
                        "-input_type",
                        "wkt",
                        "-variant",
                        "rt",
                        "-execution",
                        "cpu",
                        "-json",
                        str(out),
                        "-overwrite",
                        "false",
                    ]
                )

    def test_script_does_not_import_author_runner_or_add_core_semantics(self) -> None:
        text = SCRIPT_PATH.read_text(encoding="utf-8")
        self.assertNotIn("run_author(", text)
        self.assertIn("author_hd_exec_key_flags_plus_rtdl_route_extension", text)
        self.assertIn("full_xhd_paper_reproduction_claim_authorized", text)
        self.assertIn("author_rt_core_algorithm_equivalence_claim_authorized", text)
        self.assertIn("performance_claim_authorized", text)


if __name__ == "__main__":
    unittest.main()
