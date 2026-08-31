import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "build_xhd_figure8_radius_strategy_audit.py"
)
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5293_figure8_radius_strategy_audit_2026-07-09.json"
)
MAPPING = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_paper_target_log_mapping_goal5177_2026-07-08.json"
)
TARGET_MATRIX = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_paper_target_matrix_2026-07-08.json"
)


def _load_script():
    spec = importlib.util.spec_from_file_location(
        "build_xhd_figure8_radius_strategy_audit",
        SCRIPT,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.path.insert(0, str(SCRIPT.parent))
    spec.loader.exec_module(module)
    return module


class Goal5293XhdFigure8RadiusStrategyAuditTest(unittest.TestCase):
    def test_builder_detects_script_contract_but_missing_numeric_matrix(self):
        module = _load_script()

        with tempfile.TemporaryDirectory() as tmp:
            author_repo = Path(tmp) / "author"
            (author_repo / "expr").mkdir(parents=True)
            (author_repo / "expr" / "run_radius_tuning.sh").write_text(
                "\n".join(
                    [
                        "function run_all_geo() {",
                        "  datasets1=(dtl_cnty.wkt lakes.bz2.wkt)",
                        "  datasets2=(uszipcode.wkt parks.bz2.wkt)",
                        '  run_xhd "geo" "$root/$dataset1" "$root/$dataset2" "wkt" 2 "rt" "gpu" "false" "add"',
                        '  run_xhd "geo" "$root/$dataset1" "$root/$dataset2" "wkt" 2 "rt" "gpu" "false" "double"',
                        '  run_xhd "geo" "$root/$dataset1" "$root/$dataset2" "wkt" 2 "rt" "gpu" "false" "adaptive"',
                        "}",
                        "function run_all_graphics() {",
                        "  datasets1=(dragon.ply thai_statuette.ply)",
                        "  datasets2=(asian_dragon.ply happy_buddha.ply)",
                        '  run_xhd "graphics" "$root/$dataset1" "$root/$dataset2" "ply" 3 "rt" "gpu" "false" "add"',
                        '  run_xhd "graphics" "$root/$dataset1" "$root/$dataset2" "ply" 3 "rt" "gpu" "false" "double"',
                        '  run_xhd "graphics" "$root/$dataset1" "$root/$dataset2" "ply" 3 "rt" "gpu" "false" "adaptive"',
                        "}",
                        "run_all_geo",
                        "run_all_graphics",
                        "$PROG_ROOT/hd_exec -repeat 1 -check=false",
                    ]
                ),
                encoding="utf-8",
            )
            (author_repo / "expr" / "draw_tune_radius.py").write_text(
                "\n".join(
                    [
                        'TUNE_VARIANTS = ("rt_gpu_radius_add", "rt_gpu_radius_double", "rt_gpu_radius_adaptive",)',
                        'TUNE_LABELS = ("Add by Diagonal", "Double Radius", "Our Method",)',
                        'df = load_json_to_df(f"logs/tune_radius/{variant}/{base_dir}")',
                        'draw_bar_chart(ax, base_dir="geo", title="geo", legend_pos="upper right")',
                        'draw_bar_chart(ax, base_dir="graphics", title="graphics", legend_pos="upper left")',
                        "df['Running.AvgTime']",
                        'fig.savefig("tune_radius.pdf")',
                    ]
                ),
                encoding="utf-8",
            )

            artifact = module.build_figure8_audit(
                author_repo=author_repo,
                mapping_path=MAPPING,
                target_matrix_path=TARGET_MATRIX,
                date="2026-07-09",
            )

        self.assertEqual(
            artifact["status"],
            "figure8_radius_strategy_audit_ready__figure8_not_reproduced__tune_radius_logs_missing",
        )
        self.assertTrue(artifact["author_script_contract"]["script_draw_contract_aligned"])
        run_contract = artifact["author_script_contract"]["run_radius_tuning"]
        self.assertEqual(run_contract["radius_values"], ["add", "double", "adaptive"])
        self.assertEqual(run_contract["variant"], "rt")
        self.assertEqual(run_contract["execution"], "gpu")
        self.assertTrue(run_contract["calls_run_all_geo"])
        self.assertTrue(run_contract["calls_run_all_graphics"])
        self.assertFalse(artifact["decision"]["figure8_reproduced"])
        self.assertFalse(artifact["decision"]["tune_radius_numeric_matrix_available"])
        self.assertEqual(artifact["checked_in_log_evidence"]["tune_radius"]["total_json_count"], 0)

    def test_artifact_records_current_figure8_author_side_blocker(self):
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(
            payload["status"],
            "figure8_radius_strategy_audit_ready__figure8_not_reproduced__tune_radius_logs_missing",
        )
        self.assertFalse(payload["decision"]["figure8_reproduced"])
        self.assertTrue(payload["decision"]["author_script_available"])
        self.assertFalse(payload["decision"]["tune_radius_numeric_matrix_available"])
        self.assertFalse(payload["decision"]["run_all_radius_strategy_evidence_available"])
        self.assertTrue(payload["author_script_contract"]["script_draw_contract_aligned"])
        self.assertEqual(
            payload["checked_in_log_evidence"]["run_all_mapping"]["coverage_status"],
            "not_covered_by_run_all_timing_logs",
        )
        self.assertEqual(payload["checked_in_log_evidence"]["tune_radius"]["total_json_count"], 0)
        self.assertFalse(
            payload["checked_in_log_evidence"]["tune_radius"][
                "complete_variant_category_matrix_present"
            ]
        )
        self.assertIn("logs/tune_radius has no JSON records", payload["decision"]["current_blocker"])

    def test_claim_boundary_forbids_figure8_parity_and_substitute_claims(self):
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        for value in payload["claim_boundary"].values():
            self.assertFalse(value)
        self.assertFalse(payload["claim_boundary"]["figure8_reproduction_claimed"])
        self.assertFalse(payload["claim_boundary"]["performance_ratio_claimed"])
        self.assertFalse(payload["claim_boundary"]["rtdl_author_radius_strategy_parity_claimed"])
        self.assertFalse(payload["claim_boundary"]["run_all_logs_claimed_as_figure8"])
        next_steps = "\n".join(payload["decision"]["next_allowed_steps"])
        self.assertIn("run author run_radius_tuning.sh", next_steps)
        self.assertIn("Level-B radius-strategy diagnostic", next_steps)
        self.assertIn("Only after", next_steps)


if __name__ == "__main__":
    unittest.main()
