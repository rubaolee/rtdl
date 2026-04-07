from __future__ import annotations

import argparse
import json
from pathlib import Path

import rtdsl as rt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--zip-path", default="build/goal141_monuseg_train.zip")
    parser.add_argument("--xml-name", default=rt.MONUSEG_DEFAULT_XML)
    parser.add_argument("--polygon-limit", type=int, default=16)
    parser.add_argument("--copies", default="64,128")
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    zip_path = Path(args.zip_path)
    if not zip_path.exists():
        rt.download_monuseg_training_zip(zip_path)
    payload = rt.run_goal146_jaccard_linux_stress(
        zip_path=zip_path,
        xml_name=args.xml_name,
        polygon_limit=args.polygon_limit,
        copies=tuple(int(value) for value in args.copies.split(",") if value),
    )
    artifacts = rt.write_goal146_artifacts(payload, args.output_dir)
    print(json.dumps({"artifacts": {key: str(value) for key, value in artifacts.items()}}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
