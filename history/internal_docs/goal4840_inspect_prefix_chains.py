from __future__ import annotations

import argparse
import json


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prefix-json", required=True)
    parser.add_argument("--start", type=int, required=True)
    parser.add_argument("--end", type=int, required=True)
    args = parser.parse_args()

    with open(args.prefix_json, "r", encoding="utf-8") as f:
        data = json.load(f)
    print("chain_count", len(data["chains"]))
    for idx in range(args.start, args.end + 1):
        print("IDX", idx)
        print("chain", json.dumps(data["chains"][idx - 1], sort_keys=True))
        print("pre", json.dumps(data["pre_finalize_chains"][idx - 1], sort_keys=True))
        print("events", json.dumps(data["chain_events"][idx - 1], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
