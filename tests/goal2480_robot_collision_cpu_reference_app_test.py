from __future__ import annotations

import json
import os
import pathlib
import re
import subprocess
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
APP = (
    ROOT
    / "examples"
    / "v2_0"
    / "research_benchmarks"
    / "robot_collision"
    / "rtdl_robot_collision_benchmark_app.py"
)
README = ROOT / "examples" / "v2_0" / "research_benchmarks" / "robot_collision" / "README.md"
RESEARCH_README = ROOT / "examples" / "v2_0" / "research_benchmarks" / "README.md"
REPORT = ROOT / "docs" / "reports" / "goal2480_robot_collision_cpu_reference_app_2026-05-21.md"
GEMINI_REVIEW = ROOT / "docs" / "reviews" / "goal2480_gemini_review_robot_collision_cpu_reference_2026-05-21.md"
CLAUDE_REVIEW = ROOT / "docs" / "reviews" / "goal2480_claude_review_robot_collision_cpu_reference_2026-05-21.md"
CONSENSUS = (
    ROOT
    / "docs"
    / "reviews"
    / "goal2480_codex_gemini_claude_consensus_robot_collision_cpu_reference_2026-05-21.md"
)
NATIVE_DIR = ROOT / "src" / "native"


class Goal2480RobotCollisionCpuReferenceAppTest(unittest.TestCase):
    def test_tiny_cpu_reference_matches_expected_compact_flags(self) -> None:
        from examples.v2_0.research_benchmarks.robot_collision.rtdl_robot_collision_benchmark_app import (
            run_robot_collision_benchmark,
        )

        payload = run_robot_collision_benchmark(dataset="tiny", include_rows=True)

        self.assertEqual(payload["app"], "robot_collision_benchmark")
        self.assertEqual(payload["mode"], "cpu_reference")
        self.assertTrue(payload["matches_expected"])
        self.assertEqual(payload["pose_count"], 5)
        self.assertEqual(payload["link_count"], 2)
        self.assertEqual(payload["compact_link_flags"], [0, 0, 0, 1, 1, 1, 0, 0, 0, 1])
        pose_flags = {row["pose_id"]: row["any_hit"] for row in payload["pose_summaries"]}
        self.assertEqual(pose_flags, {1: False, 2: True, 3: True, 4: False, 5: True})
        rotated = next(row for row in payload["pose_summaries"] if row["pose_id"] == 5)
        self.assertEqual(rotated["colliding_link_ids"], [2])
        self.assertIn("hit_pairs", payload)
        self.assertGreater(len(payload["hit_pairs"]), 0)

    def test_scaled_cpu_reference_is_configurable_and_keeps_compact_contract(self) -> None:
        from examples.v2_0.research_benchmarks.robot_collision.rtdl_robot_collision_benchmark_app import (
            run_robot_collision_benchmark,
        )

        payload = run_robot_collision_benchmark(
            dataset="scaled",
            pose_count=12,
            obstacle_count=5,
            link_count=3,
        )

        self.assertEqual(payload["pose_count"], 12)
        self.assertEqual(payload["link_count"], 3)
        self.assertEqual(len(payload["link_flags"]), 36)
        self.assertEqual(len(payload["compact_link_flags"]), 36)
        self.assertGreater(payload["static_obstacle_triangle_count"], 0)
        self.assertEqual(payload["query_triangle_count"], 72)
        self.assertIsNone(payload["matches_expected"])
        self.assertNotIn("hit_pairs", payload)

    def test_cli_emits_json_and_claim_boundary(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(APP),
                "--dataset",
                "tiny",
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONPATH": "src:."},
        )
        payload = json.loads(completed.stdout)

        self.assertTrue(payload["matches_expected"])
        boundary = payload["claim_boundary"]
        self.assertFalse(boundary["paper_reproduction_claim_authorized"])
        self.assertFalse(boundary["authors_code_comparison_claim_authorized"])
        self.assertFalse(boundary["public_speedup_claim_authorized"])
        self.assertFalse(boundary["native_robot_abi_added"])
        self.assertFalse(boundary["native_collision_abi_added"])
        self.assertFalse(boundary["native_engine_touched"])
        self.assertFalse(boundary["continuous_collision_supported"])
        self.assertTrue(boundary["cpu_reference_only"])
        self.assertFalse(payload["paper_status"]["official_code_verified"])
        self.assertFalse(payload["paper_status"]["official_data_verified"])

    def test_docs_record_goal2480_scope_and_next_gate(self) -> None:
        readme = README.read_text(encoding="utf-8")
        research_readme = RESEARCH_README.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("static obstacle triangles + batched transformed query meshes", readme)
        self.assertIn("No robot-specific native ABI is added", readme)
        self.assertIn("Goal2481 must decide the native/partner compact output representation", readme)
        self.assertIn("robot_collision/", research_readme)
        self.assertIn("No native code was changed", report)
        self.assertIn("Official implementation was not verified", report)
        self.assertIn("Goal2481 should design the generic RTDL contract", report)
        self.assertIn("paper_reproduction_claim_authorized = false", report)
        self.assertIn("CPU reference is intentionally 2D", report)
        self.assertIn("Goal2481 must explicitly decide whether", readme)
        self.assertIn("official code, and official data must be", report)

    def test_external_reviews_and_consensus_approve_goal2480(self) -> None:
        gemini = GEMINI_REVIEW.read_text(encoding="utf-8")
        claude = CLAUDE_REVIEW.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("Verdict: Approved", gemini)
        self.assertIn("Blocking Issues: None", gemini)
        self.assertIn("## Verdict: Approved", claude)
        self.assertIn("Blocking Issues", claude)
        self.assertIn("None", claude)
        self.assertIn("## Consensus: Approved", consensus)
        self.assertIn("Goal2481 generic contract design", consensus)

    def test_no_native_robot_or_collision_abi_was_added(self) -> None:
        pattern = re.compile(r"\brtdl_[a-z0-9_]*(robot|collision)[a-z0-9_]*\b", re.IGNORECASE)
        hits = []
        for path in NATIVE_DIR.rglob("*"):
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            if pattern.search(text):
                hits.append(str(path.relative_to(ROOT)))
        self.assertEqual(hits, [])


if __name__ == "__main__":
    unittest.main()
