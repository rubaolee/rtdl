#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect a Linux KITTI source root for RTDL v0.5 readiness.")
    parser.add_argument("source_root", help="Path to the KITTI raw root on Linux")
    parser.add_argument("--write-json", dest="write_json", help="Optional destination for the JSON readiness report")
    args = parser.parse_args()

    report = rt.inspect_kitti_linux_source_root(args.source_root)
    if args.write_json:
        path = rt.write_kitti_linux_ready_report(args.source_root, args.write_json)
        print(path)
    else:
        print(json.dumps(report.__dict__, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
