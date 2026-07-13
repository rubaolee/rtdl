from __future__ import annotations

import argparse
from pathlib import Path


FULL_BBOX_ANCHORS = (
    ("999999001 2 1 2 0 0", "-1.7914890900e+02 -1.4548692000e+01", "-1.7914890800e+02 -1.4548691000e+01"),
    ("999999002 2 3 4 0 0", "1.7977846400e+02 7.1390481000e+01", "1.7977846500e+02 7.1390482000e+01"),
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--start-id", type=int, required=True)
    parser.add_argument("--end-id", type=int, required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--append-full-bbox-anchors", action="store_true")
    args = parser.parse_args()

    source = Path(args.source)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    kept = 0
    with source.open("r", encoding="utf-8", errors="replace") as src, output.open("w", encoding="utf-8") as out:
        while True:
            header = src.readline()
            if not header:
                break
            p1 = src.readline()
            p2 = src.readline()
            if not p1 or not p2:
                raise RuntimeError(f"truncated CDB record near: {header!r}")
            fields = header.split()
            if not fields:
                continue
            try:
                record_id = int(fields[0])
            except ValueError:
                continue
            if args.start_id <= record_id <= args.end_id:
                out.write(header)
                out.write(p1)
                out.write(p2)
                kept += 1
        if args.append_full_bbox_anchors:
            for header, p1, p2 in FULL_BBOX_ANCHORS:
                out.write(header + "\n")
                out.write(p1 + "\n")
                out.write(p2 + "\n")
    print(f"kept={kept} output={output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
