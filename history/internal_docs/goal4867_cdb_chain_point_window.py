from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cdb", required=True)
    parser.add_argument("--start-chain-index", type=int, required=True)
    parser.add_argument("--end-chain-index", type=int, required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    from rtdsl.rayjoin_overlay import load_cdb_overlay_packed_inputs

    inputs = load_cdb_overlay_packed_inputs(args.cdb)
    points = inputs.points.owner[2]
    segments = inputs.cdb_segments.owner[1]
    records = []
    for chain_index in range(args.start_chain_index, args.end_chain_index + 1):
        p0_index = chain_index * 2
        p1_index = p0_index + 1
        records.append(
            {
                "chain_index": chain_index,
                "left_face_id": int(segments["left_face_id"][chain_index]),
                "right_face_id": int(segments["right_face_id"][chain_index]),
                "p0_index": p0_index,
                "p1_index": p1_index,
                "p0": [float(points["x"][p0_index]), float(points["y"][p0_index])],
                "p1": [float(points["x"][p1_index]), float(points["y"][p1_index])],
                "p0_text": f"{float(points['x'][p0_index]):.6f} {float(points['y'][p0_index]):.6f}",
                "p1_text": f"{float(points['x'][p1_index]):.6f} {float(points['y'][p1_index]):.6f}",
            }
        )
    for previous, current in zip(records, records[1:]):
        current["same_as_previous_p1_raw"] = current["p0"] == previous["p1"]
        current["same_as_previous_p1_text"] = current["p0_text"] == previous["p1_text"]

    payload = {
        "schema": "rtdl.goal4867.cdb_chain_point_window.v1",
        "cdb": args.cdb,
        "records": records,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
