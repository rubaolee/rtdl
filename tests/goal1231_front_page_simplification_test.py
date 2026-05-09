from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Goal1231FrontPageSimplificationTest(unittest.TestCase):
    def test_root_readme_is_a_landing_page_not_a_report_dump(self) -> None:
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        lines = text.splitlines()

        self.assertLessEqual(len(lines), 260)
        self.assertIn("## Start Fast", text)
        self.assertIn("## Current Status", text)
        self.assertIn("## NVIDIA RT-Core Claim Boundary", text)
        self.assertIn("[Docs Index](docs/README.md)", text)
        self.assertIn("[v1.0 App Acceleration Inventory](docs/v1_0_app_acceleration_inventory.md)", text)
        self.assertLessEqual(text.count("Goal"), 20)

    def test_front_page_keeps_claim_boundary_without_embedding_full_history(self) -> None:
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        compact = " ".join(text.split())

        self.assertIn("not, by itself, a public claim that NVIDIA RT cores accelerated the app", compact)
        self.assertIn("not a whole-app, default-mode, Python-postprocess", compact)
        self.assertIn("v1.6 release package/support matrix as the current release authority", compact)
        self.assertIn("v1.0 inventory preserved for app-boundary history", compact)
        self.assertIn("Detailed evidence and review trail", text)


if __name__ == "__main__":
    unittest.main()
