from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "Paper-reproduction-apps" / "x-hd-paper"
RESULT = APP_DIR / "results" / "xhd_goal5351_author_variant_semantics_audit.json"
SCRIPT = APP_DIR / "scripts" / "build_xhd_goal5351_variant_semantics_audit.py"


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _load_builder():
    spec = importlib.util.spec_from_file_location("xhd_goal5351_builder", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Goal5351XhdAuthorVariantSemanticsAuditTest(unittest.TestCase):
    def test_variant_matrix_separates_value_surface_from_algorithm_parity(self) -> None:
        payload = _load_json(RESULT)
        rows = {row["author_flag"]: row for row in payload["variant_semantics"]}

        self.assertEqual(set(rows), {"eb", "nn", "clover", "itk", "rt"})
        self.assertEqual(rows["eb"]["author_impl"], "HausdorffDistanceEarlyBreak")
        self.assertEqual(rows["nn"]["author_impl"], "HausdorffDistanceNearestNeighborSearch")
        self.assertEqual(rows["clover"]["author_impl"], "HausdorffDistanceClover")
        self.assertEqual(rows["itk"]["author_impl"], "HausdorffDistanceITK")
        self.assertEqual(rows["rt"]["author_impl"], "HausdorffDistanceRT")

        for name, row in rows.items():
            with self.subTest(variant=name):
                self.assertFalse(row["algorithm_equivalence_claimed"])
                self.assertFalse(row["performance_equivalence_claimed"])
                self.assertTrue(row["gap_to_close_for_full_parity"])

        self.assertEqual(rows["rt"]["current_rtdl_status"], "partial_level_b_value_route")
        self.assertEqual(rows["clover"]["figure5_label"], "NN-Clover")
        self.assertIn("cuKD", " ".join(rows["nn"]["author_algorithm_semantics"]))

    def test_script_surface_keeps_rt_hdist_and_compare_methods_out_of_supported_variants(self) -> None:
        payload = _load_json(RESULT)
        cli = payload["author_cli_surface"]
        fig5 = payload["figure5_script_surface"]

        self.assertIn("compare-methods", cli["main_cpp_variants"])
        self.assertNotIn("compare-methods", cli["supported_goal5349_rtdl_value_surface"])
        self.assertIn("no switch case", cli["compare_methods_status"])

        self.assertIn("rt_hdist", fig5["graphics_variants"])
        self.assertIn("RT-HDIST", fig5["graphics_labels"])
        external = fig5["external_baselines_not_hd_exec_variants"][0]
        self.assertEqual(external["label"], "RT-HDIST")
        self.assertEqual(external["status"], "external_script_baseline_not_reproduced_by_rtdl")

    def test_current_rtdl_summary_keeps_full_parity_false(self) -> None:
        payload = _load_json(RESULT)
        summary = payload["current_rtdl_parity_summary"]
        boundary = payload["claim_boundary"]

        self.assertEqual(
            summary["value_surface"]["status"],
            "all_author_variant_names_accepted_for_directed_hdresult_value_output",
        )
        self.assertFalse(summary["algorithm_surface"]["full_author_variant_algorithm_parity_ready"])
        self.assertIn("eb", summary["algorithm_surface"]["not_closed"])
        self.assertIn("RT-HDIST external baseline", summary["algorithm_surface"]["not_closed"])
        self.assertFalse(summary["performance_surface"]["author_variant_performance_parity_ready"])

        self.assertTrue(boundary)
        self.assertTrue(all(value is False for value in boundary.values()))

    def test_builder_can_emit_without_author_source_root_as_unchecked_readiness(self) -> None:
        builder = _load_builder()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "audit.json"
            rc = builder.main(["--output", str(out)])
            payload = _load_json(out)

        self.assertEqual(rc, 0)
        verification = payload["author_provenance"]["source_verification"]
        self.assertFalse(verification["checked"])
        self.assertEqual(verification["status"], "not_checked__no_author_source_root_supplied")
        self.assertEqual(payload["exit_label"], "author_variant_semantics_audit_ready__non_rt_algorithm_parity_not_closed")


if __name__ == "__main__":
    unittest.main()
