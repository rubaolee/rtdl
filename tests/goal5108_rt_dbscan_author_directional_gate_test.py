from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "Paper-reproduction-apps" / "rt-dbscan-paper"
RUNNER = APP_DIR / "scripts" / "run_authorofficial_component_signature_gate.py"
INPUT_1K = APP_DIR / "data" / "fixtures" / "uci_3droad_1k_author_2d_zero_z.csv"
AUTHOR_1K = APP_DIR / "results" / "uci_3droad_1k_author_goal5107_clean.jsonl"


def _load_runner():
    spec = importlib.util.spec_from_file_location("rt_dbscan_author_directional_gate", RUNNER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5108RtDbscanAuthorDirectionalGateTest(unittest.TestCase):
    def test_conventional_reference_still_mismatches_uci_3droad_author_payload(self) -> None:
        runner = _load_runner()
        summary = runner.run_gate(
            input_path=INPUT_1K,
            epsilon=0.05,
            min_points=100,
            backend="cpu_reference",
            author_payload_path=AUTHOR_1K,
        )

        self.assertFalse(summary["matched"])
        self.assertFalse(summary["signature_matched"])
        self.assertFalse(summary["component_partition_matched"])
        self.assertTrue(summary["core_flags_matched"])
        self.assertEqual(
            summary["rtdl"]["signature"],
            {
                "core_count": 329,
                "component_count": 3,
                "component_sizes": [102, 168, 181],
                "noise_count": 549,
            },
        )
        self.assertEqual(
            summary["author_signature"],
            {
                "core_count": 329,
                "component_count": 3,
                "component_sizes": [90, 168, 181],
                "noise_count": 561,
            },
        )

    def test_author_directional_reference_matches_uci_3droad_author_payload(self) -> None:
        runner = _load_runner()
        summary = runner.run_gate(
            input_path=INPUT_1K,
            epsilon=0.05,
            min_points=100,
            backend="author_directional_cpu_reference",
            author_payload_path=AUTHOR_1K,
        )

        self.assertTrue(summary["matched"])
        self.assertTrue(summary["signature_matched"])
        self.assertTrue(summary["component_partition_matched"])
        self.assertTrue(summary["core_flags_matched"])
        self.assertTrue(summary["bounded_component_partition_reproduction_claim_authorized"])
        self.assertFalse(summary["paper_reproduction_claim_authorized"])
        self.assertFalse(summary["performance_claim_authorized"])
        self.assertEqual(summary["rtdl"]["signature"], summary["author_signature"])
        self.assertEqual(summary["rtdl"]["metadata"]["border_assignment_policy"], "author_call2_xid_greater_than_primid_only")
        self.assertIn("not a generic RTDL core semantic", summary["rtdl"]["metadata"]["claim_boundary"])

    def test_author_directional_backend_is_app_runner_only(self) -> None:
        runner_source = RUNNER.read_text(encoding="utf-8")
        self.assertIn("author_directional_cpu_reference", runner_source)
        self.assertIn("app_side_author_directional_border_assignment_reference_3d", runner_source)
        self.assertIn("optix_cupy_component_signature", runner_source)

        core_init = (ROOT / "src" / "rtdsl" / "__init__.py").read_text(encoding="utf-8")
        component_partition = (ROOT / "src" / "rtdsl" / "component_partition.py").read_text(encoding="utf-8")
        self.assertNotIn("author_directional_cpu_reference", core_init)
        self.assertNotIn("author_directional_cpu_reference", component_partition)
        self.assertNotIn("xID > primID", component_partition)


if __name__ == "__main__":
    unittest.main()
