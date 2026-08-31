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


def _load_runner():
    spec = importlib.util.spec_from_file_location("xhd_rtdl_hd_exec_goal5349", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Goal5349XhdHdExecVariantValueSurfaceTest(unittest.TestCase):
    def test_all_author_variants_are_accepted_for_value_output_on_bounded_fixture(self) -> None:
        runner = _load_runner()
        expected_variants = {"eb", "nn", "itk", "clover", "rt"}
        self.assertEqual(set(runner.AUTHOR_VARIANTS), expected_variants)

        with tempfile.TemporaryDirectory() as tmp:
            for variant in sorted(expected_variants):
                with self.subTest(variant=variant):
                    out = Path(tmp) / f"{variant}.json"
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
                            variant,
                            "-execution",
                            "cpu",
                            "-json",
                            str(out),
                        ]
                    )
                    payload = json.loads(out.read_text(encoding="utf-8"))

                    self.assertEqual(rc, 0)
                    self.assertEqual(payload["HDResult"], 0.5)
                    self.assertEqual(payload["RTDL"]["variant"], variant)
                    self.assertEqual(payload["RTDL"]["route_label"], "public-columnar")
                    self.assertEqual(payload["RTDL"]["hd_result_semantics"], "directed_input1_to_input2")
                    self.assertTrue(payload["RTDL"]["route"]["per_source_witness_exact"])

    def test_non_rt_variants_are_explicitly_not_algorithm_or_performance_claims(self) -> None:
        runner = _load_runner()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "clover.json"
            runner.main(
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
                    "clover",
                    "-execution",
                    "cpu",
                    "-json",
                    str(out),
                ]
            )
            payload = json.loads(out.read_text(encoding="utf-8"))

        support = payload["RTDL"]["variant_support"]
        boundary = payload["RTDL"]["claim_boundary"]

        self.assertEqual(support["requested_author_variant"], "clover")
        self.assertEqual(support["status"], "author_variant_value_compatible_route_only")
        self.assertTrue(support["hdresult_value_supported"])
        self.assertFalse(support["author_variant_algorithm_equivalence_claimed"])
        self.assertFalse(support["performance_parity_claimed"])
        self.assertFalse(boundary["author_variant_algorithm_equivalence_claimed"])
        self.assertFalse(boundary["author_rt_core_algorithm_equivalence_claim_authorized"])
        self.assertFalse(boundary["performance_claim_authorized"])
        self.assertIn("value-compatible", payload["RTDL"]["boundary"])
        self.assertIn("not reproduced", payload["RTDL"]["boundary"])

    def test_rt_variant_keeps_xhd_value_route_status_without_algorithm_parity_claim(self) -> None:
        runner = _load_runner()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "rt.json"
            runner.main(
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
                ]
            )
            payload = json.loads(out.read_text(encoding="utf-8"))

        support = payload["RTDL"]["variant_support"]
        self.assertEqual(support["requested_author_variant"], "rt")
        self.assertEqual(support["status"], "xhd_rt_value_route")
        self.assertTrue(support["hdresult_value_supported"])
        self.assertFalse(support["author_variant_algorithm_equivalence_claimed"])


if __name__ == "__main__":
    unittest.main()
