from __future__ import annotations

import argparse
import json

import rtdsl as rt


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Goal 138 polygon overlap PostGIS validation.")
    parser.add_argument("--db-name", default="rtdl_postgis")
    parser.add_argument("--db-user", default=None)
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    payload = rt.run_goal138_polygon_overlap_postgis_validation(
        db_name=args.db_name,
        db_user=args.db_user,
    )
    if args.output_dir:
        artifacts = rt.write_goal138_artifacts(payload, args.output_dir)
        print(json.dumps({"artifacts": {key: str(value) for key, value in artifacts.items()}}, indent=2))
        return
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
