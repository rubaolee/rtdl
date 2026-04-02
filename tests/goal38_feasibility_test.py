from __future__ import annotations

import argparse
import json
import tempfile
import unittest
from pathlib import Path

from scripts.goal38_linux_county_zipcode_feasibility import FROZEN_STATE_GROUPS
from scripts.goal38_linux_county_zipcode_feasibility import load_existing_summary
from scripts.goal38_linux_county_zipcode_feasibility import load_manifest_if_complete
from scripts.goal38_linux_county_zipcode_feasibility import parse_args
from scripts.goal38_linux_county_zipcode_feasibility import render_state_where
from scripts.goal38_linux_county_zipcode_feasibility import write_summary


class Goal38FeasibilityTest(unittest.TestCase):
    def test_render_state_where_quotes_each_state(self) -> None:
        self.assertEqual(
            render_state_where("STATE", ("TX", "CA", "NY")),
            "STATE IN ('TX', 'CA', 'NY')",
        )

    def test_frozen_groups_end_with_nationwide(self) -> None:
        self.assertEqual(FROZEN_STATE_GROUPS[-1][0], "nationwide")
        self.assertIn("TX", FROZEN_STATE_GROUPS[-1][1])
        self.assertIn("CA", FROZEN_STATE_GROUPS[-1][1])

    def test_default_validation_mode_is_embree_only(self) -> None:
        original = argparse._sys.argv
        argparse._sys.argv = ["goal38_linux_county_zipcode_feasibility.py", "--output-dir", "out"]
        try:
            args = parse_args()
        finally:
            argparse._sys.argv = original
        self.assertEqual(args.validation_mode, "embree-only")

    def test_load_manifest_if_complete_requires_all_pages(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            page_path = output_dir / "page_000000.json"
            page_path.write_text("{}", encoding="utf-8")
            manifest = {
                "asset_id": "zipcode_feature_layer",
                "expected_feature_count": 1,
                "downloaded_feature_count": 1,
                "page_paths": [str(page_path)],
                "where": "STATE IN ('TX')",
            }
            (output_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            self.assertEqual(
                load_manifest_if_complete(
                    output_dir,
                    asset_id="zipcode_feature_layer",
                    where="STATE IN ('TX')",
                ),
                manifest,
            )
            page_path.unlink()
            self.assertIsNone(
                load_manifest_if_complete(
                    output_dir,
                    asset_id="zipcode_feature_layer",
                    where="STATE IN ('TX')",
                )
            )

    def test_load_manifest_if_complete_rejects_mismatched_filter(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            page_path = output_dir / "page_000000.json"
            page_path.write_text("{}", encoding="utf-8")
            manifest = {
                "asset_id": "zipcode_feature_layer",
                "expected_feature_count": 1,
                "downloaded_feature_count": 1,
                "page_paths": [str(page_path)],
                "where": "STATE IN ('TX')",
            }
            (output_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            self.assertIsNone(
                load_manifest_if_complete(
                    output_dir,
                    asset_id="zipcode_feature_layer",
                    where="STATE IN ('CA')",
                )
            )

    def test_load_existing_summary_reuses_matching_header(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            summary = {
                "host_label": "linux",
                "validation_mode": "embree-only",
                "points": [{"label": "top1_tx"}],
            }
            (output_dir / "goal38_summary.json").write_text(json.dumps(summary), encoding="utf-8")
            self.assertEqual(
                load_existing_summary(output_dir, host_label="linux", validation_mode="embree-only"),
                summary,
            )

    def test_write_summary_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            summary = {
                "host_label": "linux",
                "validation_mode": "embree-only",
                "points": [{
                    "label": "top1_tx",
                    "states": ["TX"],
                    "validation_mode": "embree-only",
                    "county": {"feature_count": 1, "chain_count": 1, "segment_count": 1, "convert_sec": 1.0},
                    "zipcode": {"feature_count": 1, "chain_count": 1, "segment_count": 1, "convert_sec": 1.0},
                    "lsi": {"embree_sec": 1.0},
                    "pip": {"embree_sec": 2.0},
                }],
            }
            write_summary(output_dir, summary)
            self.assertTrue((output_dir / "goal38_summary.json").exists())
            self.assertTrue((output_dir / "goal38_summary.md").exists())
            self.assertEqual(
                load_existing_summary(output_dir, host_label="linux", validation_mode="embree-only"),
                summary,
            )


if __name__ == "__main__":
    unittest.main()
