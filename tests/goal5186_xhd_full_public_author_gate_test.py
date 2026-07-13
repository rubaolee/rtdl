from __future__ import annotations

import argparse
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "run_xhd_full_public_author_gate.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("run_xhd_full_public_author_gate", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _write_bridge(path: Path, source: Path, target: Path) -> None:
    payload = {
        "target": "graphics_dragon_happy_buddha",
        "author_log_records": {
            "hd_results": [0.12572969496250153],
        },
        "public_same_source_candidates": {
            "dragon.ply": {
                "path": str(source),
            },
            "happy_buddha.ply": {
                "path": str(target),
            },
        },
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


class Goal5186XhdFullPublicAuthorGateTest(unittest.TestCase):
    def test_author_json_compares_against_paper_log_without_exact_reference(self):
        module = _load_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "dragon.ply"
            target = root / "happy.ply"
            bridge = root / "bridge.json"
            author_json = root / "author.json"
            source.write_text("placeholder\n", encoding="utf-8")
            target.write_text("placeholder\n", encoding="utf-8")
            _write_bridge(bridge, source, target)
            author_json.write_text(
                json.dumps(
                    {
                        "HDResult": 0.12572988867759705,
                        "Input": {
                            "Files": [
                                {"NumPoints": 437645},
                                {"NumPoints": 543652},
                            ]
                        },
                        "Running": {"AvgTime": 7.823},
                    }
                ),
                encoding="utf-8",
            )
            args = argparse.Namespace(
                bridge=bridge,
                author_bin=None,
                author_json=author_json,
                output=root / "summary.json",
                run_goal="Goal5186",
                n_dims=3,
                input_type="ply",
                variant="rt",
                execution="gpu",
                tolerance=1e-6,
            )

            summary = module.build_summary(args)

        self.assertEqual(summary["schema"], "rtdl.paper_reproduction.xhd.full_public_author_gate.v1")
        self.assertEqual(summary["goal"], "Goal5186")
        self.assertTrue(summary["matched"])
        self.assertAlmostEqual(summary["author_hd_result"], 0.12572988867759705, delta=1e-12)
        self.assertAlmostEqual(summary["paper_log_min_abs_diff"], 1.9371509552418863e-7, delta=1e-12)
        self.assertEqual(summary["author_input_point_counts"], [437645, 543652])
        self.assertEqual(summary["author_running_avg_time_ms"], 7.823)
        self.assertIsNone(summary["author_run"])
        self.assertFalse(summary["author_run_failed"])
        self.assertFalse(summary["claim_boundary"]["rtdl_exact_reference_claimed"])
        self.assertFalse(summary["claim_boundary"]["rtdl_all_source_route_run_claimed"])
        self.assertFalse(summary["claim_boundary"]["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(summary["claim_boundary"]["full_paper_reproduction_claimed"])

    def test_missing_author_json_fails_closed(self):
        module = _load_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "dragon.ply"
            target = root / "happy.ply"
            bridge = root / "bridge.json"
            source.write_text("placeholder\n", encoding="utf-8")
            target.write_text("placeholder\n", encoding="utf-8")
            _write_bridge(bridge, source, target)
            args = argparse.Namespace(
                bridge=bridge,
                author_bin=None,
                author_json=root / "missing.json",
                output=root / "summary.json",
                run_goal="Goal5186",
                n_dims=3,
                input_type="ply",
                variant="rt",
                execution="gpu",
                tolerance=1e-6,
            )

            with self.assertRaises(FileNotFoundError):
                module.build_summary(args)


if __name__ == "__main__":
    unittest.main()
