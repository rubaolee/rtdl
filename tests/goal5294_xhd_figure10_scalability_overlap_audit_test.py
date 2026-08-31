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
    / "build_xhd_figure10_scalability_overlap_audit.py"
)
ARTIFACT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5294_figure10_scalability_overlap_audit_2026-07-09.json"
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
        "build_xhd_figure10_scalability_overlap_audit",
        SCRIPT,
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.path.insert(0, str(SCRIPT.parent))
    spec.loader.exec_module(module)
    return module


class Goal5294XhdFigure10ScalabilityOverlapAuditTest(unittest.TestCase):
    def test_builder_detects_script_contract_but_missing_scalability_logs(self):
        module = _load_script()

        with tempfile.TemporaryDirectory() as tmp:
            author_repo = Path(tmp) / "author"
            (author_repo / "expr").mkdir(parents=True)
            (author_repo / "expr" / "run_scalability.sh").write_text(
                "\n".join(
                    [
                        "function run_hd() {",
                        '  $PROG_ROOT/hd_exec -repeat 1 -check=false -input_type "wkt" -n_dims 3',
                        "}",
                        "for size in 12500000 25000000 50000000; do",
                        '  dataset="$DATASET_ROOT/geo/all_nodes.wkt"',
                        "  for variant in eb nn clover rt; do",
                        '    run_hd "scal_vary_size" "$dataset" "$dataset" "wkt" 3 $variant "gpu" $size "0.005"',
                        "  done",
                        "done",
                        "for translate in 0.0001 0.0002 0.0004; do",
                        '  dataset="$DATASET_ROOT/geo/all_nodes.wkt"',
                        "  for variant in eb nn clover rt; do",
                        '    run_hd "scal_vary_translate" "$dataset" "$dataset" "wkt" 3 $variant "gpu" 10000000 $translate',
                        "  done",
                        "done",
                    ]
                ),
                encoding="utf-8",
            )
            (author_repo / "expr" / "draw_scalability.py").write_text(
                "\n".join(
                    [
                        'VARIANTS = ("eb_gpu", "nn_gpu", "clover_gpu", "rt_gpu")',
                        'VARIANT_LABELS = ("EB", "NN-KD", "NN-Clover", "X-HD")',
                        'dir_path = f"logs/scalability/{variant}/scal_vary_size"',
                        'dir_path = f"logs/scalability/{variant}/scal_vary_translate"',
                        "df['Input.Files'].apply(lambda x: x[0]['NumPoints'])",
                        "df['Input.Translate']",
                        "df['Running.AvgTime']",
                        "draw_subfig('Count', axes[0])",
                        "draw_subfig('Translate', axes[1])",
                        'axes[0].set_title("(a) Varying the Scale of Datasets")',
                        'axes[1].set_title("(b) Sensitivity to Overlap")',
                        'fig.savefig("scalability.pdf")',
                    ]
                ),
                encoding="utf-8",
            )

            artifact = module.build_figure10_audit(
                author_repo=author_repo,
                mapping_path=MAPPING,
                target_matrix_path=TARGET_MATRIX,
                date="2026-07-09",
            )

        self.assertEqual(
            artifact["status"],
            "figure10_scalability_overlap_audit_ready__figure10_not_reproduced__scalability_logs_missing",
        )
        self.assertTrue(artifact["author_script_contract"]["script_draw_contract_aligned"])
        run_contract = artifact["author_script_contract"]["run_scalability"]
        self.assertEqual(run_contract["dataset"], "all_nodes.wkt")
        self.assertEqual(run_contract["run_variants"], ["eb", "nn", "clover", "rt"])
        self.assertEqual(run_contract["execution"], "gpu")
        self.assertGreaterEqual(run_contract["size_sweep_count"], 3)
        self.assertGreaterEqual(run_contract["translate_sweep_count"], 3)
        self.assertFalse(artifact["decision"]["figure10_reproduced"])
        self.assertFalse(artifact["decision"]["scalability_numeric_matrix_available"])
        self.assertEqual(artifact["checked_in_log_evidence"]["scalability"]["total_json_count"], 0)

    def test_artifact_records_current_figure10_author_side_blocker(self):
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(
            payload["status"],
            "figure10_scalability_overlap_audit_ready__figure10_not_reproduced__scalability_logs_missing",
        )
        self.assertFalse(payload["decision"]["figure10_reproduced"])
        self.assertTrue(payload["decision"]["author_script_available"])
        self.assertFalse(payload["decision"]["scalability_numeric_matrix_available"])
        self.assertTrue(payload["decision"]["run_all_workload_family_records_available"])
        self.assertFalse(payload["decision"]["run_all_scale_overlap_labels_available"])
        self.assertEqual(
            payload["checked_in_log_evidence"]["run_all_mapping"]["coverage_status"],
            "workload_families_present__scale_overlap_labels_missing",
        )
        self.assertEqual(payload["checked_in_log_evidence"]["run_all_mapping"]["record_count"], 4535)
        self.assertEqual(payload["checked_in_log_evidence"]["scalability"]["total_json_count"], 0)
        self.assertFalse(
            payload["checked_in_log_evidence"]["scalability"][
                "complete_variant_sweep_matrix_present"
            ]
        )
        self.assertIn("logs/scalability has no JSON records", payload["decision"]["current_blocker"])

    def test_claim_boundary_forbids_figure10_parity_and_run_all_substitution(self):
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        for value in payload["claim_boundary"].values():
            self.assertFalse(value)
        self.assertFalse(payload["claim_boundary"]["figure10_reproduction_claimed"])
        self.assertFalse(payload["claim_boundary"]["performance_ratio_claimed"])
        self.assertFalse(payload["claim_boundary"]["rtdl_author_scalability_overlap_parity_claimed"])
        self.assertFalse(payload["claim_boundary"]["run_all_workload_families_claimed_as_figure10"])
        next_steps = "\n".join(payload["decision"]["next_allowed_steps"])
        self.assertIn("run author run_scalability.sh", next_steps)
        self.assertIn("Level-B scalability/overlap diagnostic", next_steps)
        self.assertIn("Only after", next_steps)


if __name__ == "__main__":
    unittest.main()
