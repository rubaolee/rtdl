from __future__ import annotations

from rtdsl.optix_runtime import prepare_planar_map_lsi_2d_optix
from rtdsl.optix_runtime import prepare_segment_pair_intersection_optix


def main() -> None:
    # Two crossing segments with explicit IDs. This only checks whether the
    # public row surface is callable and what fields it returns.
    base = (
        {"id": 10, "x0": 0.0, "y0": 0.0, "x1": 1.0, "y1": 1.0},
    )
    query = (
        {"id": 20, "x0": 0.0, "y0": 1.0, "x1": 1.0, "y1": 0.0},
    )
    with prepare_planar_map_lsi_2d_optix(base) as lsi:
        print("planar_map_lsi_count", lsi.count(query), flush=True)
        print("planar_map_lsi_metadata", lsi.count_with_metadata(query), flush=True)
    with prepare_segment_pair_intersection_optix(base) as raw:
        rows = raw.run_raw(query)
        try:
            print("raw_row_count", rows.row_count, flush=True)
            print("raw_fields", rows.field_names, flush=True)
            for row in rows.to_dict_rows():
                print("raw_row", row, flush=True)
        finally:
            rows.close()


if __name__ == "__main__":
    main()
