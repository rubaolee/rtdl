from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.v4_goal4640_public_docs_cleanup_decision import validate_v4_goal4640_public_docs_cleanup

PUBLIC_DOCS = (
    ROOT / "README.md",
    ROOT / "docs" / "README.md",
    ROOT / "docs" / "current_v4_status.md",
    ROOT / "docs" / "public_documentation_map.md",
    ROOT / "docs" / "learn" / "README.md",
    ROOT / "docs" / "learn" / "performance_wording.md",
    ROOT / "docs" / "learn" / "source_tree_doctor.md",
    ROOT / "tutorials" / "README.md",
    ROOT / "tutorials" / "current" / "README.md",
    ROOT / "tutorials" / "current" / "01_first_run.md",
    ROOT / "tutorials" / "current" / "02_hello_world.md",
    ROOT / "tutorials" / "current" / "03_backend_choice.md",
    ROOT / "tutorials" / "current" / "04_prepared_runtime.md",
    ROOT / "tutorials" / "current" / "05_measurement_boundaries.md",
    ROOT / "examples" / "README.md",
    ROOT / "examples" / "v4" / "README.md",
    ROOT / "future" / "v4" / "README.md",
    ROOT / "future" / "v4" / "tier2_operator_catalog.md",
)


class V4Goal4640PublicDocsCleanupTest(unittest.TestCase):
    def test_public_docs_are_v4_current_not_v3_current(self) -> None:
        forbidden = (
            "V3.0.0",
            "current V3",
            "Current V3",
            "V3 tutorial",
            "V3 checkout",
            "V3 source-tree",
            "not a release announcement",
            "development surface",
            "development guidance",
            "development catalog",
        )
        for path in PUBLIC_DOCS:
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                text = path.read_text(encoding="utf-8")
                self.assertIn("V4", text)
                for needle in forbidden:
                    self.assertNotIn(needle, text)

    def test_legacy_current_v3_status_is_not_in_public_docs(self) -> None:
        self.assertFalse((ROOT / "docs" / "current_v3_status.md").exists())
        self.assertTrue((ROOT / "docs" / "current_v4_status.md").exists())

    def test_clean_v4_example_entrypoints_run_without_cuda(self) -> None:
        commands = (
            ["examples/v4/v4_frontdoor_quickstart.py"],
            ["examples/v4/operator_callback_planning.py", "--case", "complex-callback"],
            ["examples/v4/custom_predicate_early_exit_planning.py"],
            ["examples/v4/fixed_radius_torch_device_arrays.py", "--dry-run", "--copies", "2"],
            ["examples/v4/ray_triangle_any_hit_weighted_sum_torch_device_arrays.py", "--dry-run", "--ray-count", "16"],
            ["examples/v4/aabb_index_all_ops_count.py", "--dry-run"],
        )
        for command in commands:
            with self.subTest(command=" ".join(command)):
                proc = subprocess.run(
                    [sys.executable, *command],
                    cwd=ROOT,
                    check=True,
                    text=True,
                    stdout=subprocess.PIPE,
                )
                payload = json.loads(proc.stdout)
                self.assertIn(payload["status"], {"ok", "dry_run", "rejected_action_shaped_callback_deferred"})
                self.assertFalse(payload["release_claim_authorized"])
                self.assertFalse(payload["tier3_callback_claim_authorized"])

    def test_goal4639_scorecard_is_visible_without_overclaim(self) -> None:
        text = (ROOT / "docs" / "current_v4_status.md").read_text(encoding="utf-8")
        self.assertIn("Goal4639 scorecard passed", text)
        self.assertIn("8/8", text)
        self.assertIn("4/4", text)
        self.assertIn("most measured operators are 1.2x-1.7x", text)
        self.assertIn("Baseline / denominator", text)
        self.assertIn("whole-application speedup claim", text)
        self.assertIn("V4.0.0 Python eDSL/operator-pushdown release surface available", text)
        self.assertIn("current V4 measured operator/workflow surface count is\n`10`", text)
        self.assertIn("Custom predicate early-exit", text)
        self.assertIn("broad all-app", text)

    def test_machine_decision_records_docs_cleanup_without_release_authorization(self) -> None:
        decision = validate_v4_goal4640_public_docs_cleanup(ROOT)

        self.assertEqual("complete_public_v4_docs_cleanup_pending_external_review", decision["decision"])
        self.assertTrue(decision["public_docs_current"])
        self.assertTrue(decision["examples_checked"])
        self.assertTrue(decision["v3_current_doc_archived"])
        self.assertFalse(decision["release_authorized"])
        self.assertFalse(decision["broad_v4_speedup_claim_authorized"])
        self.assertFalse(decision["whole_app_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
