from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "Paper-reproduction-apps" / "x-hd-paper"


class Goal5262XhdUserEntrypointDocsStatusTest(unittest.TestCase):
    def test_readme_promotes_hd_exec_entrypoint_without_full_paper_claim(self) -> None:
        readme = (APP_DIR / "README.md").read_text(encoding="utf-8")

        self.assertIn(
            "xhd_public_modelnet40_all400_and_graphics_representatives_hd_exec_entrypoint_complete__full_paper_incomplete",
            readme,
        )
        self.assertIn("scripts/run_xhd_rtdl_hd_exec.py", readme)
        self.assertIn("scripts/run_xhd_rtdl_hd_exec_summary_batch.py", readme)
        self.assertIn("matched_case_count = 400", readme)
        self.assertIn("per_source_witness_exact = true for all 400 cases", readme)
        self.assertIn("results/xhd_goal5260_modelnet40_all400_hd_exec_batch_exact_witness_pod.json", readme)
        self.assertIn("results/xhd_goal5261_hd_exec_entrypoint_all400_performance_matrix_2026-07-09.json", readme)
        self.assertIn("results/xhd_goal5263_dragon_happy_hd_exec_exact_witness_pod.json", readme)
        self.assertIn("results/xhd_goal5264_dragon_asian_hd_exec_exact_witness_pod.json", readme)
        self.assertIn("results/xhd_goal5265_thai_happy_hd_exec_exact_witness_pod.json", readme)
        self.assertIn("results/xhd_goal5266_thai_asian_hd_exec_exact_witness_pod.json", readme)
        self.assertIn("RTDL route / author process-wall = 1.648034759782505x slower", readme)
        self.assertIn("RTDL route / author internal AvgTime = 150.3906850953375x slower", readme)
        self.assertIn("must remain labeled", readme)
        self.assertIn("does", readme)
        self.assertIn("not prove exact original paper byte-input identity", readme)
        self.assertIn("does not claim speedup", readme)
        self.assertIn("full X-HD paper reproduction", readme)

    def test_manifest_records_goal5260_5261_evidence_and_keeps_boundaries_false(self) -> None:
        manifest = json.loads((APP_DIR / "data" / "manifest.json").read_text(encoding="utf-8"))

        self.assertEqual(
            manifest["reproduction_scope"]["status"],
            "xhd_level_b_and_hd_exec_entrypoint_complete__memory_accounting_integrated__full_paper_incomplete",
        )
        evidence = {item["path"]: item for item in manifest["evidence"]["result_artifacts"]}
        goal5260 = evidence[
            "Paper-reproduction-apps/x-hd-paper/results/xhd_goal5260_modelnet40_all400_hd_exec_batch_exact_witness_pod.json"
        ]
        goal5261 = evidence[
            "Paper-reproduction-apps/x-hd-paper/results/xhd_goal5261_hd_exec_entrypoint_all400_performance_matrix_2026-07-09.json"
        ]

        self.assertTrue(goal5260["matched"])
        self.assertIn("400 / 400", goal5260["note"])
        self.assertIn("not exact paper byte-input identity", goal5260["note"])
        self.assertIn("route/process-wall = 1.65x slower", goal5261["note"])
        self.assertIn("route/author-internal-AvgTime = 150.39x slower", goal5261["note"])
        self.assertIn("No speedup", goal5261["note"])

        boundaries = manifest["boundaries"]
        self.assertFalse(boundaries["full_paper_reproduction_claimed"])
        self.assertFalse(boundaries["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(boundaries["whole_program_speedup_claimed"])
        self.assertFalse(boundaries["author_performance_parity_claimed"])
        self.assertFalse(boundaries["existing_hausdorff_xhd_benchmark_reclassified_as_paper_reproduction"])


if __name__ == "__main__":
    unittest.main()
