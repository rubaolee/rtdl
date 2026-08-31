from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "Paper-reproduction-apps" / "rt-dbscan-paper"
RUNNER = APP_DIR / "scripts" / "run_authorofficial_component_signature_gate.py"


def _load_runner():
    spec = importlib.util.spec_from_file_location("rt_dbscan_authorofficial_component_gate", RUNNER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5094RtDbscanAuthorOfficialComponentSignatureGateTest(unittest.TestCase):
    def test_tiny3d_cpu_reference_component_signature(self):
        runner = _load_runner()
        summary = runner.run_gate(
            input_path=APP_DIR / "data" / "fixtures" / "tiny3d_core_count.csv",
            epsilon=0.35,
            min_points=3,
            backend="cpu_reference",
        )
        self.assertEqual(summary["point_count"], 8)
        self.assertEqual(
            summary["rtdl"]["signature"],
            {
                "core_count": 7,
                "component_count": 2,
                "component_sizes": [3, 4],
                "noise_count": 1,
            },
        )
        self.assertEqual(summary["rtdl"]["component_labels"], [0, 0, 0, 0, 1, 1, 1, -1])
        self.assertEqual(summary["rtdl"]["canonical_component_labels"], [0, 0, 0, 0, 1, 1, 1, -1])
        self.assertFalse(summary["author_comparator_used"])
        self.assertFalse(summary["bounded_component_signature_reproduction_claim_authorized"])
        self.assertFalse(summary["bounded_component_partition_reproduction_claim_authorized"])
        self.assertFalse(summary["paper_reproduction_claim_authorized"])

    def test_border_noise_fixture_has_border_and_noise_signature(self):
        runner = _load_runner()
        summary = runner.run_gate(
            input_path=APP_DIR / "data" / "fixtures" / "border_noise3d_component_signature.csv",
            epsilon=0.35,
            min_points=5,
            backend="cpu_reference",
        )
        self.assertEqual(summary["point_count"], 12)
        self.assertEqual(
            summary["rtdl"]["signature"],
            {
                "core_count": 10,
                "component_count": 2,
                "component_sizes": [5, 6],
                "noise_count": 1,
            },
        )
        self.assertEqual(summary["rtdl"]["core_flags"][0], 0)
        self.assertEqual(summary["rtdl"]["core_flags"][-1], 0)
        self.assertEqual(
            summary["rtdl"]["core_flags"],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        )
        self.assertEqual(
            summary["rtdl"]["component_labels"],
            [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, -1],
        )
        self.assertEqual(
            summary["rtdl"]["canonical_component_labels"],
            [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, -1],
        )

    def test_canonical_partition_detects_border_swap_that_signature_misses(self):
        runner = _load_runner()
        expected = [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, -1]
        border_swapped = [1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, -1]
        expected_signature = runner._canonical_signature_from_labels(expected, core_count=10)
        swapped_signature = runner._canonical_signature_from_labels(border_swapped, core_count=10)
        self.assertEqual(expected_signature, swapped_signature)
        self.assertEqual(expected_signature["component_sizes"], [5, 6])
        self.assertNotEqual(
            runner._canonical_partition_labels(expected),
            runner._canonical_partition_labels(border_swapped),
        )

    def test_author_patch_exposes_component_signature_without_core_primitive(self):
        patch = (APP_DIR / "author_patches" / "goal5092_authorofficial_core_count_output.patch").read_text(
            encoding="utf-8"
        )
        for phrase in (
            "\\\"component_labels\\\"",
            "\\\"component_sizes\\\"",
            "\\\"noise_count\\\"",
            "\\\"core_flags\\\"",
            "\\\"parent_roots\\\"",
        ):
            self.assertIn(phrase, patch)
        self.assertIn("post call-2 component signature", patch)
        self.assertNotIn("rtdl_optix", patch)
        self.assertNotIn("DBSCAN-native RTDL engine ABI", patch)

    def test_manifest_still_keeps_full_paper_claim_closed(self):
        manifest = json.loads((APP_DIR / "data" / "manifest.json").read_text(encoding="utf-8"))
        self.assertFalse(manifest["boundaries"]["full_paper_reproduction_claimed"])
        self.assertFalse(manifest["boundaries"]["whole_program_speedup_claimed"])


if __name__ == "__main__":
    unittest.main()
