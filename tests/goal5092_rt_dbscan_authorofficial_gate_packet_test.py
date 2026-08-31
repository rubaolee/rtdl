from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "Paper-reproduction-apps" / "rt-dbscan-paper"
RUNNER = APP_DIR / "scripts" / "run_authorofficial_core_count_gate.py"


def _load_runner():
    spec = importlib.util.spec_from_file_location("rt_dbscan_authorofficial_gate", RUNNER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5092RtDbscanAuthorOfficialGatePacketTest(unittest.TestCase):
    def test_tiny3d_cpu_reference_gate_is_runnable_without_author_binary(self):
        runner = _load_runner()
        summary = runner.run_gate(
            input_path=APP_DIR / "data" / "fixtures" / "tiny3d_core_count.csv",
            epsilon=0.35,
            min_points=3,
            backend="cpu_reference",
        )
        self.assertEqual(summary["point_count"], 8)
        self.assertEqual(summary["rtdl"]["core_count"], 7)
        self.assertFalse(summary["author_comparator_used"])
        self.assertIsNone(summary["matched"])
        self.assertFalse(summary["bounded_core_count_reproduction_claim_authorized"])
        self.assertFalse(summary["paper_reproduction_claim_authorized"])
        self.assertFalse(summary["whole_program_speedup_claim_authorized"])

    def test_author_patch_exposes_core_count_without_changing_kernel_identity(self):
        patch = (APP_DIR / "author_patches" / "goal5092_authorofficial_core_count_output.patch").read_text(
            encoding="utf-8"
        )
        self.assertIn("\\\"core_count\\\"", patch)
        self.assertIn("\\\"component_labels\\\"", patch)
        self.assertIn("\\\"component_sizes\\\"", patch)
        self.assertIn("\\\"noise_count\\\"", patch)
        self.assertIn("fb[i].neighCount >= minPts", patch)
        self.assertIn("samples/cmdline/s02-rtdbscan/hostCode.cpp", patch)
        self.assertIn("owl/DeviceContext.cpp", patch)
        self.assertIn("OPTIX_PRIMITIVE_TYPE_FLAGS_CUSTOM", patch)
        self.assertNotIn("paper_speedup_claim_authorized\": true", patch)

    def test_manifest_keeps_paper_claims_closed(self):
        manifest = json.loads((APP_DIR / "data" / "manifest.json").read_text(encoding="utf-8"))
        self.assertFalse(manifest["boundaries"]["full_paper_reproduction_claimed"])
        self.assertFalse(manifest["boundaries"]["whole_program_speedup_claimed"])


if __name__ == "__main__":
    unittest.main()
