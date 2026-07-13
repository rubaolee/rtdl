from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def _load_runner():
    script = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "scripts" / "run_cell_mbr_backend_assisted_gate.py"
    spec = importlib.util.spec_from_file_location("run_cell_mbr_backend_assisted_gate", script)
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load cell-MBR backend gate runner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Goal5144CellMbrBackendAssistedGateRunnerTest(unittest.TestCase):
    def test_cpu_gate_runner_writes_matching_summary(self) -> None:
        runner = _load_runner()
        with tempfile.TemporaryDirectory() as tmp:
            summary = Path(tmp) / "summary.json"
            code = runner.main(["--backend", "cpu", "--summary", str(summary)])

            self.assertEqual(code, 0)
            text = summary.read_text(encoding="utf-8")
            self.assertIn('"matched": true', text)
            self.assertIn('"backend": "cpu"', text)
            self.assertIn('"native_goal5140_backend_claim": false', text)
            self.assertIn('"paper_reproduction_claim": false', text)


if __name__ == "__main__":
    unittest.main()
