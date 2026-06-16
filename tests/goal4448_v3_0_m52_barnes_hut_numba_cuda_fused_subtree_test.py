from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v3_0_m52_barnes_hut_numba_cuda_fused_subtree.py"
DRY_RUN = ROOT / "build" / "goal4448_m52_barnes_hut_numba_cuda_fused_subtree_dry_run_test.json"
REPORT = ROOT / "docs" / "reports" / "goal4448_v3_0_m52_barnes_hut_numba_cuda_fused_subtree_2026-06-16.md"
SMOKE = ROOT / "docs" / "reports" / "goal4448_v3_0_m52_barnes_hut_numba_cuda_fused_subtree_128_smoke_2026-06-16.json"
VALIDATION_8192 = ROOT / "docs" / "reports" / "goal4448_v3_0_m52_barnes_hut_numba_cuda_fused_subtree_8192_validation_2026-06-16.json"
SCALE = ROOT / "docs" / "reports" / "goal4448_v3_0_m52_barnes_hut_numba_cuda_fused_subtree_scale_r11_2026-06-16.json"
EVIDENCE_INDEX = ROOT / "docs" / "learn" / "benchmark_evidence_index.md"
PARTNER_MATRIX = ROOT / "docs" / "learn" / "benchmark_partner_reference_matrix.md"
RT_CORE_MATRIX = ROOT / "docs" / "learn" / "rt_core_evidence_matrix.md"
PARTNER_CHOICE = ROOT / "docs" / "learn" / "partner_choice_for_custom_logic.md"


class Goal4448V30M52BarnesHutNumbaCudaFusedSubtreeTest(unittest.TestCase):
    def test_script_declares_python_source_cuda_fused_subtree_boundary(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")

        for phrase in (
            "Goal4448 / V3.0 M52",
            "numba_cuda_fused_subtree_force_sum_prototype",
            "COMPARISON_THETA = 0.5",
            "COMPARISON_MAX_DEPTH = 32",
            "@cuda.jit",
            "node_subtree_end_index",
            "source_leaf_node_index",
            "frontier_rows_materialized_on_host",
            "contribution_rows_materialized_on_host",
            "rt_core_speedup_claim_authorized",
        ):
            self.assertIn(phrase, source)
        for forbidden in (
            "import torch",
            "from torch",
            "load_inline(",
            "CPP_SOURCE",
            "CUDA_SOURCE =",
        ):
            self.assertNotIn(forbidden, source)

    def test_dry_run_has_closed_claim_flags(self) -> None:
        if DRY_RUN.exists():
            DRY_RUN.unlink()
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--dry-run",
                "--body-counts",
                "128,8192",
                "--output",
                str(DRY_RUN),
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode)
        payload = json.loads(DRY_RUN.read_text(encoding="utf-8"))

        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["version"], "rtdl.v3_0.barnes_hut_numba_cuda_fused_subtree.goal4448.v1")
        self.assertEqual(tuple(payload["body_counts"]), (128, 8192))
        flags = payload["planned_claim_flags"]
        self.assertTrue(flags["numba_cuda_python_source_used"])
        self.assertFalse(flags["cxx_cuda_extension_used"])
        self.assertFalse(flags["torch_extension_used"])
        self.assertFalse(flags["rt_cores_used"])
        self.assertFalse(flags["public_speedup_claim_authorized"])
        self.assertFalse(flags["rt_core_speedup_claim_authorized"])

    def test_pod_evidence_records_same_contract_scale_ladder(self) -> None:
        smoke = json.loads(SMOKE.read_text(encoding="utf-8"))["rows"][0]
        validation_8192 = json.loads(VALIDATION_8192.read_text(encoding="utf-8"))["rows"][0]
        scale = json.loads(SCALE.read_text(encoding="utf-8"))
        rows = {int(row["body_count"]): row for row in scale["rows"]}

        self.assertTrue(smoke["validation"]["passed"])
        self.assertEqual(smoke["vector_sum_summary"]["contribution_row_count"], 8766)
        self.assertTrue(validation_8192["validation"]["passed"])
        self.assertEqual(validation_8192["validation"]["reference_frontier_row_count"], 3_406_489)
        self.assertAlmostEqual(
            validation_8192["vector_sum_summary"]["checksum_force_x"],
            -1836.571773996123,
            places=8,
        )
        self.assertAlmostEqual(
            validation_8192["vector_sum_summary"]["checksum_force_y"],
            4948.320604887711,
            places=8,
        )

        expected_counts = {
            8192: 3_406_489,
            16384: 12_727_680,
            32768: 15_514_679,
        }
        for body_count, expected_count in expected_counts.items():
            row = rows[body_count]
            self.assertEqual(row["theta"], 0.5)
            self.assertEqual(row["max_depth"], 32)
            self.assertEqual(row["bucket_size"], 64)
            self.assertEqual(row["vector_sum_summary"]["contribution_row_count"], expected_count)
            flags = row["claim_flags"]
            self.assertTrue(flags["numba_cuda_python_source_used"])
            self.assertFalse(flags["cxx_cuda_extension_used"])
            self.assertFalse(flags["torch_extension_used"])
            self.assertFalse(flags["rt_cores_used"])
            self.assertFalse(flags["frontier_rows_materialized_on_host"])
            self.assertFalse(flags["contribution_rows_materialized_on_host"])
            self.assertFalse(flags["rt_core_speedup_claim_authorized"])

        self.assertGreater(
            rows[8192]["comparison_baselines"]["m41_optix_numba_over_m52_event_sec"],
            4.0,
        )
        self.assertGreater(
            rows[32768]["comparison_baselines"]["m41_optix_numba_over_m52_event_sec"],
            7.0,
        )
        self.assertLess(
            rows[32768]["comparison_baselines"]["m52_event_sec_over_m45_cpu_fused"],
            1.0,
        )

    def test_docs_and_current_guidance_include_m52_without_rt_claim(self) -> None:
        import rtdsl as rt

        report = REPORT.read_text(encoding="utf-8")
        evidence_index = EVIDENCE_INDEX.read_text(encoding="utf-8")
        partner_matrix = PARTNER_MATRIX.read_text(encoding="utf-8")
        rt_core_matrix = RT_CORE_MATRIX.read_text(encoding="utf-8")
        partner_choice = PARTNER_CHOICE.read_text(encoding="utf-8")
        rows = {row["app"]: row for row in rt.current_benchmark_adequacy()}
        barnes = rows["barnes_hut"]

        for text in (report, evidence_index, partner_matrix, rt_core_matrix, partner_choice):
            self.assertIn("Goal4448", text)
            self.assertIn("Numba CUDA", text)
        self.assertIn("not an RT-core primitive", report)
        self.assertEqual("adequate", barnes["adequacy"])
        self.assertIn("Goal4448", barnes["evidence_refs"])
        self.assertIn("no-C++ fused GPU partner prototype", barnes["current_recommended_path"])
        self.assertFalse(barnes["broad_rt_core_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
