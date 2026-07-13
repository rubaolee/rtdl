from __future__ import annotations

import json
import os
from pathlib import Path

from rtdsl.optix_runtime import prepare_planar_map_lsi_2d_optix
from rtdsl.optix_runtime import prepare_segment_pair_intersection_optix


BASE = (
    {
        "id": 14110870,
        "x0": 151.2771671,
        "y0": -33.8512399,
        "x1": 151.2772023,
        "y1": -33.8513923,
    },
    {
        "id": 14387225,
        "x0": 151.2771671,
        "y0": -33.8512399,
        "x1": 151.2772023,
        "y1": -33.8513923,
    },
)

QUERY = (
    {
        "id": 640,
        "x0": 151.2776856,
        "y0": -33.8511451,
        "x1": 151.2772023,
        "y1": -33.8513923,
    },
)


def hidden_predicate_rows():
    old = os.environ.get("RTDL_OPTIX_SEGMENT_PAIR_PREDICATE")
    os.environ["RTDL_OPTIX_SEGMENT_PAIR_PREDICATE"] = "planar_map_lsi"
    try:
        with prepare_segment_pair_intersection_optix(BASE) as prepared:
            rows = prepared.run_raw(QUERY)
            try:
                return int(rows.row_count), rows.to_dict_rows()
            finally:
                rows.close()
    finally:
        if old is None:
            os.environ.pop("RTDL_OPTIX_SEGMENT_PAIR_PREDICATE", None)
        else:
            os.environ["RTDL_OPTIX_SEGMENT_PAIR_PREDICATE"] = old


def main() -> int:
    with prepare_planar_map_lsi_2d_optix(BASE) as lsi:
        count_meta = lsi.count_with_metadata(QUERY)
    row_count, rows = hidden_predicate_rows()
    summary = {
        "schema": "rtdl.goal4859.minimal_real_witness_probe.v1",
        "base": BASE,
        "query": QUERY,
        "public_planar_map_lsi_count": int(count_meta["count"]),
        "hidden_predicate_row_count": row_count,
        "hidden_predicate_rows": rows,
        "count_rows_match": int(count_meta["count"]) == row_count,
        "expected_bug_signature": "count=2 rows=0",
        "source": "Australia Lakes x Parks representative, query segment index 639, base witnesses 14110870 and 14387225",
    }
    out = Path("/workspace/goal4859_minimal_real_witness_probe_summary.json")
    out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
