from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "goal75_oracle_trust_audit.py"
SPEC = importlib.util.spec_from_file_location("goal75_oracle_trust_audit", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class Goal75OracleTrustAuditTest(unittest.TestCase):
    def test_build_case_inventory_is_deterministic(self) -> None:
        left = MODULE.build_case_inventory(
            mini_random_seed=1,
            small_random_seed=2,
            mini_random_cases=2,
            small_random_cases=3,
        )
        right = MODULE.build_case_inventory(
            mini_random_seed=1,
            small_random_seed=2,
            mini_random_cases=2,
            small_random_cases=3,
        )
        self.assertEqual(left, right)
        self.assertEqual(len(left["mini_lsi"]), 5)
        self.assertEqual(len(left["mini_pip"]), 5)
        self.assertEqual(len(left["mini_overlay"]), 5)
        self.assertEqual(len(left["small_lsi"]), 3)
        self.assertEqual(len(left["small_pip"]), 3)
        self.assertEqual(len(left["small_overlay"]), 3)

    def test_render_markdown_includes_envelope_summary(self) -> None:
        summary = {
            "host_label": "linux",
            "db_name": "rtdl_postgis",
            "mini_python": {
                "all_pass": True,
                "lsi": {"case_count": 4, "python_pass_count": 4},
                "pip": {"case_count": 5, "python_full_pass_count": 5, "python_positive_pass_count": 5},
                "overlay": {"case_count": 3, "python_pass_count": 3},
            },
            "small_native": {
                "all_pass": True,
                "lsi": {"case_count": 6, "native_pass_count": 6},
                "pip": {"case_count": 7, "native_full_pass_count": 7, "native_positive_pass_count": 7},
                "overlay": {"case_count": 2, "native_pass_count": 2},
            },
        }
        markdown = MODULE.render_markdown(summary)
        self.assertIn("# Goal 75 Oracle Trust Audit", markdown)
        self.assertIn("mini Python all-pass: `True`", markdown)
        self.assertIn("small native all-pass: `True`", markdown)

    def test_summarize_workload_tracks_pip_python_and_native(self) -> None:
        pip_cases = [
            {
                "python": {
                    "full": {"parity_vs_postgis": True},
                    "positive": {"parity_vs_postgis": True},
                },
                "native": {
                    "full": {"parity_vs_postgis": True},
                    "positive": {"parity_vs_postgis": False},
                },
            }
        ]
        python_summary = MODULE.summarize_workload(pip_cases, oracle_key="pip_python")
        native_summary = MODULE.summarize_workload(pip_cases, oracle_key="pip_native")
        self.assertTrue(python_summary["python_all_pass"])
        self.assertFalse(native_summary["native_all_pass"])


if __name__ == "__main__":
    unittest.main()
