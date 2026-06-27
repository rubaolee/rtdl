from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROBE = ROOT / "scripts" / "v4_rt_barneshut_native_benchmark_ready_probe.py"


class V4Goal4766RtBarnesHutBenchmarkReadyProbeTest(unittest.TestCase):
    def test_probe_cli_exposes_cold_warm_and_author_binary_controls(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(PROBE), "--help"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        help_text = proc.stdout
        self.assertIn("--repeat", help_text)
        self.assertIn("--author-binary", help_text)
        self.assertIn("--trimmed-dataset", help_text)
        self.assertIn("--goal-label", help_text)
        self.assertIn("cold/warm", help_text)

    def test_probe_preserves_non_release_boundaries(self) -> None:
        text = PROBE.read_text(encoding="utf-8")

        self.assertIn("public_speedup_claim_authorized", text)
        self.assertIn("paper_reproduction_claim_authorized", text)
        self.assertIn("v2_v3_v4_author_speed_table_authorized", text)
        self.assertIn("input_columns_downloaded_for_tree_build", text)
        self.assertIn("warm_checksum_stable", text)


if __name__ == "__main__":
    unittest.main()
