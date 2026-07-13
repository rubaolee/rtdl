from __future__ import annotations

import argparse
import json


def _prefix_output_lines(prefix_json: str) -> list[str]:
    with open(prefix_json, "r", encoding="utf-8") as f:
        data = json.load(f)
    lines: list[str] = []
    for chain in data["chains"]:
        lines.append(
            f"{chain['id']} {chain['point_count']} {chain['first']} "
            f"{chain['last']} {chain['left']} {chain['right']}"
        )
        lines.extend(chain["points"])
    return lines


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prefix-json", required=True)
    parser.add_argument("--author-output", required=True)
    parser.add_argument("--output-json", required=True)
    args = parser.parse_args()

    expected_lines = _prefix_output_lines(args.prefix_json)
    first_mismatch = None
    with open(args.author_output, "r", encoding="utf-8", errors="replace") as author:
        for line_no, expected in enumerate(expected_lines, 1):
            got = author.readline()
            if got == "":
                first_mismatch = {
                    "line": line_no,
                    "rtdl": expected,
                    "author": "<EOF>",
                }
                break
            got = got.rstrip("\n")
            if got != expected:
                first_mismatch = {
                    "line": line_no,
                    "rtdl": expected,
                    "author": got,
                }
                break

    summary = {
        "prefix_json": args.prefix_json,
        "author_output": args.author_output,
        "generated_lines": len(expected_lines),
        "prefix_byte_line_match": first_mismatch is None,
        "first_mismatch": first_mismatch,
        "last_checked_line": len(expected_lines) if first_mismatch is None else first_mismatch["line"],
    }
    with open(args.output_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, sort_keys=True)
        f.write("\n")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if first_mismatch is None else 1


if __name__ == "__main__":
    raise SystemExit(main())
