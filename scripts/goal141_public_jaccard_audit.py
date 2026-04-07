from __future__ import annotations

import argparse
import json
from pathlib import Path

import rtdsl as rt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--zip-path", default="build/goal141_monuseg_train.zip")
    parser.add_argument("--xml-name", default=rt.MONUSEG_DEFAULT_XML)
    parser.add_argument("--db-name", default="rtdl_postgis")
    parser.add_argument("--db-user", default=None)
    parser.add_argument("--polygon-limit", type=int, default=64)
    parser.add_argument("--copies", default="1,4")
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    zip_path = Path(args.zip_path)
    if not zip_path.exists():
        rt.download_monuseg_training_zip(zip_path)
    payload = rt.run_goal141_public_jaccard_audit(
        zip_path=zip_path,
        db_name=args.db_name,
        db_user=args.db_user,
        xml_name=args.xml_name,
        polygon_limit=args.polygon_limit,
        copies=tuple(int(value) for value in args.copies.split(",") if value),
    )
    artifacts = rt.write_goal141_artifacts(payload, args.output_dir)
    print(json.dumps({"artifacts": {key: str(value) for key, value in artifacts.items()}}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
