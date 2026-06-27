import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v3_phoenix_aabb_prepare_reuse_serious_pod_evidence.py"
PACKET_JSON = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_aabb_prepare_reuse_serious_rtx_evidence_2026-06-21.json"
)
PACKET_MD = PACKET_JSON.with_suffix(".md")
EVIDENCE_DIR = ROOT / "docs" / "rebuild" / "v3" / "evidence" / "phoenix_v3_aabb_prepare_reuse_serious_20260621"


class V3PhoenixAabbPrepareReuseSeriousPodEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
        cls.text = PACKET_MD.read_text(encoding="utf-8")

    def test_packet_is_serious_evidence_but_not_m7(self):
        payload = self.payload
        self.assertEqual(payload["status"], "aabb_prepare_reuse_serious_rtx_evidence_not_m7_low_margin")
        self.assertEqual(payload["generic_capability"], "aabb_candidate_stream")
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(payload["m7_promotion_authorized"])
        self.assertFalse(payload["m7_reopen_candidate_pending_2ai_review"])
        self.assertEqual(payload["m7_qualified_release_rows_added"], 0)
        self.assertEqual(payload["failed_checks"], [])
        self.assertTrue(all(payload["checks"].values()))

    def test_hardware_scale_and_phase_table_are_serious(self):
        payload = self.payload
        self.assertEqual(payload["hardware"]["gpu"], "NVIDIA RTX 4000 Ada Generation")
        self.assertEqual(payload["hardware"]["rt_hardware_gate"], "pass")
        self.assertEqual(payload["parameters"]["grid_count"], 32768)
        self.assertEqual(payload["parameters"]["repeat"], 50)
        self.assertEqual(payload["parameters"]["backends"], ["embree", "optix"])
        for backend in ("embree", "optix"):
            row = payload["phase_rows"][backend]
            self.assertTrue(row["matches_cpu_reference"])
            self.assertTrue(row["complete_candidate_coverage"])
            self.assertEqual(row["valid_rows"], 32768)
            for field in (
                "prepare_aabb_index_2d_sec",
                "emit_aabb_intersection_pair_rows_2d_total_sec",
                "collect_k_bounded_rows_sec",
                "cold_plus_collect_wall_sec",
            ):
                self.assertGreater(row[field], 0.0)

    def test_low_margin_result_blocks_m7(self):
        comparisons = self.payload["comparisons"]
        self.assertAlmostEqual(
            comparisons["optix_over_embree_cold_plus_collect_wall_speedup"],
            1.1400086912394385,
        )
        self.assertAlmostEqual(comparisons["material_wall_speedup_floor"], 1.2)
        self.assertGreater(comparisons["optix_over_embree_cold_plus_collect_wall_speedup"], 1.0)
        self.assertLess(
            comparisons["optix_over_embree_cold_plus_collect_wall_speedup"],
            comparisons["material_wall_speedup_floor"],
        )
        self.assertAlmostEqual(comparisons["optix_over_embree_prepare_speedup"], 0.6235016572276956)
        self.assertIn("below the runner's 1.20 material-speedup floor", self.payload["interpretation"])

    def test_markdown_and_raw_evidence_files_are_present(self):
        for name in (
            "summary.json",
            "environment.json",
            "aabb_prepare_reuse_embree.json",
            "aabb_prepare_reuse_optix.json",
            "run.log",
        ):
            self.assertTrue((EVIDENCE_DIR / name).exists(), name)
        for phrase in (
            "M7 rows added by this packet: 0",
            "OptiX / Embree cold-plus-collect wall speedup: `1.140x`",
            "Material wall-speedup floor: `1.200x`",
            "Do not promote this row to M7.",
            "Do not claim V3 AABB is faster from a 1.140x low-margin wall result.",
            "Was I foolish?",
        ):
            self.assertIn(phrase, self.text)

    def test_script_rebuilds_packet(self):
        with tempfile.TemporaryDirectory() as tmp:
            json_out = Path(tmp) / "packet.json"
            md_out = Path(tmp) / "packet.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--json-out",
                    str(json_out),
                    "--md-out",
                    str(md_out),
                    "--pretty",
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            rebuilt = json.loads(json_out.read_text(encoding="utf-8"))
            self.assertEqual(rebuilt["status"], self.payload["status"])
            self.assertEqual(rebuilt["comparisons"], self.payload["comparisons"])
            self.assertIn("AABB Prepare-Reuse Serious RTX Evidence", md_out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
