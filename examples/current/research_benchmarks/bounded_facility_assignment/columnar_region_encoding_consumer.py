"""Non-paper consumer of exact dense integral column encoding."""

from __future__ import annotations

from collections import defaultdict

import numpy as np

from rtdsl.columnar_encoding import exact_dense_ordinal_encode_integral


def run_authored_facility_region_consumer() -> dict[str, object]:
    """Group authored facility capacities by signed administrative region."""

    region_codes = np.asarray(
        [-4, -4, 2, 7, 2, 7, 7, 19, -4, 19],
        dtype=np.int32,
    )
    capacities = np.asarray(
        [5, 8, 3, 11, 7, 2, 13, 17, 4, 6],
        dtype=np.int64,
    )
    encoded = exact_dense_ordinal_encode_integral(
        region_codes,
        ordinal_dtype=np.uint32,
    )
    observed = defaultdict(int)
    for ordinal, capacity in zip(encoded.ordinals, capacities):
        observed[int(ordinal)] += int(capacity)
    actual = tuple(
        (
            int(encoded.unique_values[ordinal]),
            int(observed[ordinal]),
        )
        for ordinal in range(len(encoded.unique_values))
    )
    reference = defaultdict(int)
    for region, capacity in zip(region_codes, capacities):
        reference[int(region)] += int(capacity)
    expected = tuple(sorted(reference.items()))
    if actual != expected:
        raise RuntimeError("facility region dense encoding changed exact groups")
    return {
        "schema": "rtdl.nonpaper.facility_region_dense_encoding.v1",
        "consumer": "bounded_facility_assignment",
        "input_row_count": len(region_codes),
        "actual_region_capacity_rows": actual,
        "expected_region_capacity_rows": expected,
        "matched": True,
        "encoding": encoded.to_metadata(),
        "paper_or_app_identity_used_for_encoding": False,
        "performance_claimed": False,
    }


if __name__ == "__main__":
    print(run_authored_facility_region_consumer())
