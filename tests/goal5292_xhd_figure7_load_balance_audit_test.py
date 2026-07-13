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
    / "build_xhd_figure7_load_balance_audit.py"
)
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5292_figure7_load_balance_audit_2026-07-09.json"
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
        "build_xhd_figure7_load_balance_audit",
        SCRIPT,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.path.insert(0, str(SCRIPT.parent))
    spec.loader.exec_module(module)
    return module


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _minimal_author_log(*, lb: int, category: str) -> dict:
    return {
        "HDResult": 1.0,
        "Input": {
            "Files": [
                {"Path": f"/data/{category}_left.dat", "NumPoints": 10},
                {"Path": f"/data/{category}_right.dat", "NumPoints": 20},
            ]
        },
        "Running": {
            "AvgTime": 1.25,
            "LB": lb,
            "Repeats": [
                {
                    "Profiling": False,
                    "Iterations": [
                        {
                            "RTTime": 0.5,
                            "CUDATime": 0.25,
                            "OffloadingSize": 3,
                            "AdjustBVHTime": 0.125,
                            "Hits": 7,
                            "ComparedPoints": 11,
                        }
                    ],
                }
            ],
        },
    }


class Goal5292XhdFigure7LoadBalanceAuditTest(unittest.TestCase):
    def test_builder_detects_missing_lb_comparison_and_lb256_only_run_all(self):
        module = _load_script()

        with tempfile.TemporaryDirectory() as tmp:
            author_repo = Path(tmp) / "author"
            (author_repo / "expr").mkdir(parents=True)
            (author_repo / "expr" / "run_lb.sh").write_text(
                "\n".join(
                    [
                        'datasets1=(dragon.ply thai_statuette.ply dragon.ply thai_statuette.ply)',
                        'datasets2=(asian_dragon.ply happy_buddha.ply happy_buddha.ply asian_dragon.ply)',
                        'for lb in "0" "256"; do',
                        '  variant="rt"',
                        '  execution="gpu"',
                        '  normalize="$normalize"',
                        '  ./hd_exec -profiling -check=true',
                        "done",
                    ]
                ),
                encoding="utf-8",
            )
            (author_repo / "expr" / "draw_lb.py").write_text(
                'for family in ["geo", "graphics"]:\n'
                '    fields = ["AdjustBVHTime", "CUDATime", "RTTime", "Hits", "ComparedPoints"]\n',
                encoding="utf-8",
            )
            _write_json(
                author_repo
                / "expr"
                / "logs"
                / "end2end"
                / "rt_gpu"
                / "geo"
                / "geo_pair.json",
                _minimal_author_log(lb=256, category="geo"),
            )
            _write_json(
                author_repo
                / "expr"
                / "logs"
                / "end2end"
                / "rt_gpu"
                / "graphics"
                / "graphics_pair.json",
                _minimal_author_log(lb=256, category="graphics"),
            )

            artifact = module.build_figure7_audit(
                author_repo=author_repo,
                mapping_path=MAPPING,
                target_matrix_path=TARGET_MATRIX,
                date="2026-07-09",
            )

        self.assertEqual(
            artifact["status"],
            "figure7_load_balance_source_audit_ready__figure7_not_reproduced__lb_comparison_logs_missing",
        )
        self.assertFalse(artifact["decision"]["figure7_reproduced"])
        self.assertTrue(artifact["author_script_contract"]["script_draw_contract_mismatch"])
        self.assertFalse(artifact["author_script_contract"]["run_lb"]["script_lists_geo_pairs"])
        self.assertTrue(artifact["author_script_contract"]["draw_lb"]["expects_geo"])
        self.assertEqual(artifact["checked_in_log_evidence"]["lb_comparison"]["total_json_count"], 0)
        self.assertFalse(
            artifact["checked_in_log_evidence"]["lb_comparison"]["complete_lb0_lb256_matrix_present"]
        )
        self.assertFalse(artifact["checked_in_log_evidence"]["run_all_rt_gpu"]["has_lb0_records"])
        self.assertTrue(artifact["checked_in_log_evidence"]["run_all_rt_gpu"]["has_lb256_records"])
        self.assertTrue(artifact["checked_in_log_evidence"]["run_all_rt_gpu"]["has_iteration_metrics"])

    def test_artifact_records_current_figure7_author_side_blocker(self):
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(
            payload["status"],
            "figure7_load_balance_source_audit_ready__figure7_not_reproduced__lb_comparison_logs_missing",
        )
        self.assertFalse(payload["decision"]["figure7_reproduced"])
        self.assertFalse(payload["decision"]["lb_comparison_numeric_matrix_available"])
        self.assertFalse(payload["decision"]["run_all_lb0_counterpart_available"])
        self.assertTrue(payload["decision"]["run_all_iteration_metrics_available"])
        self.assertEqual(payload["checked_in_log_evidence"]["lb_comparison"]["total_json_count"], 0)
        self.assertEqual(payload["checked_in_log_evidence"]["run_all_rt_gpu"]["record_count"], 7)
        self.assertEqual(
            payload["checked_in_log_evidence"]["run_all_rt_gpu"]["by_category"]["geo"]["lb_values"],
            [256],
        )
        self.assertEqual(
            payload["checked_in_log_evidence"]["run_all_rt_gpu"]["by_category"]["graphics"]["lb_values"],
            [256],
        )
        self.assertIn("lb=0/lb=256 logs are absent", payload["decision"]["current_blocker"])

    def test_claim_boundary_forbids_figure7_ratio_and_substitute_claims(self):
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        for value in payload["claim_boundary"].values():
            self.assertFalse(value)
        self.assertFalse(payload["claim_boundary"]["figure7_reproduction_claimed"])
        self.assertFalse(payload["claim_boundary"]["performance_ratio_claimed"])
        self.assertFalse(payload["claim_boundary"]["rtdl_author_load_balance_parity_claimed"])
        self.assertFalse(payload["claim_boundary"]["lb2048_or_other_substitute_claimed_as_figure7"])
        next_steps = "\n".join(payload["decision"]["next_allowed_steps"])
        self.assertIn("run author run_lb.sh", next_steps)
        self.assertIn("Level-B load-balance diagnostic", next_steps)
        self.assertIn("Only after", next_steps)


if __name__ == "__main__":
    unittest.main()
