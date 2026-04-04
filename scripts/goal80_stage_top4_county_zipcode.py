#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import rtdsl as rt
from scripts.goal38_linux_county_zipcode_feasibility import COUNTY_LAYER
from scripts.goal38_linux_county_zipcode_feasibility import ZIPCODE_LAYER
from scripts.goal38_linux_county_zipcode_feasibility import render_state_where
from scripts.goal38_linux_county_zipcode_feasibility import stage_asset_for_states


TOP4_STATES = ("TX", "CA", "NY", "PA")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Stage and convert the top4 county/zipcode package for Goal 80.")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--host-label", default="unknown")
    parser.add_argument("--page-size", type=int, default=500)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    county_dir = output_dir / "county"
    zipcode_dir = output_dir / "zipcode"

    county_stage = stage_asset_for_states(
        COUNTY_LAYER,
        output_dir=county_dir,
        where=render_state_where("STATE_ABBR", TOP4_STATES),
        page_size=args.page_size,
    )
    zipcode_stage = stage_asset_for_states(
        ZIPCODE_LAYER,
        output_dir=zipcode_dir,
        where=render_state_where("STATE", TOP4_STATES),
        page_size=args.page_size,
    )

    county = rt.arcgis_pages_to_cdb(county_dir, name="top4_county", ignore_invalid_tail=True)
    zipcode = rt.arcgis_pages_to_cdb(zipcode_dir, name="top4_zipcode", ignore_invalid_tail=True)

    county_cdb_path = rt.write_cdb(county, output_dir / "top4_county.cdb")
    zipcode_cdb_path = rt.write_cdb(zipcode, output_dir / "top4_zipcode.cdb")

    summary = {
        "host_label": args.host_label,
        "states": list(TOP4_STATES),
        "county_stage": county_stage,
        "zipcode_stage": zipcode_stage,
        "county": {
            "feature_count": len(county.face_ids()),
            "chain_count": len(county.chains),
            "cdb_path": str(county_cdb_path),
        },
        "zipcode": {
            "feature_count": len(zipcode.face_ids()),
            "chain_count": len(zipcode.chains),
            "cdb_path": str(zipcode_cdb_path),
        },
    }

    (output_dir / "goal80_top4_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
