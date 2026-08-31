#!/usr/bin/env python3
"""Independent stdlib-only verifier for the Goal5795 Linux smoke result."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re


SHA256 = re.compile(r"[0-9a-f]{64}")


def digest(value) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"),
        ensure_ascii=True, allow_nan=False,
    ).encode("utf-8")).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def verify(path: Path) -> dict[str, object]:
    raw = path.read_bytes()
    document = json.loads(raw)
    require(document["schema"] == "rtdl.goal5795.public_linux_smoke.v1",
            "wrong result schema")
    require(document["status"] == "PASS", "smoke did not pass")
    require(document["registered_performance_timing_count"] == 0,
            "functional smoke contains registered performance timings")
    require(document["performance_claimed"] is False,
            "functional smoke claims performance")
    require(SHA256.fullmatch(document["native_sha256"]) is not None,
            "native identity malformed")

    checked_receipts = []
    for family in ("bounded", "triangle"):
        result = document[family]
        require(result["double_close_pass"] is True,
                f"{family} double close did not pass")
        require(all(
            row["first_error_claimed"] == 0 and row["error_code"] == 0
            for row in result["launch_status"]),
            f"{family} exposed device error")
        require(SHA256.fullmatch(result["program_identity_sha256"]) is not None,
                f"{family} program identity malformed")
        require(SHA256.fullmatch(result["executable_identity_sha256"]) is not None,
                f"{family} executable identity malformed")
        receipt = dict(result["traversal_receipt"])
        receipt_sha = receipt.pop("receipt_sha256")
        require(digest(receipt) == receipt_sha,
                f"{family} traversal receipt self-digest mismatch")
        require(receipt["physical_executor_classification"]
                == "optix_traversal_observed",
                f"{family} is not behavioral OptiX")
        require(receipt["provider_library_sha256"] == document["native_sha256"],
                f"{family} receipt/native mismatch")
        require(receipt["output_digest"] == result["output_sha256"],
                f"{family} receipt/output mismatch")
        require(receipt["expected_program_observed_at_receipt_edge"] is True,
                f"{family} expected program was not observed")
        checked_receipts.append(receipt_sha)

    bounded = document["bounded"]
    require(bounded["observed"] == bounded["expected"]
            == [[100, 10], [101, 20]], "bounded CPU/GPU result mismatch")
    require(digest(bounded["observed"]) == bounded["output_sha256"],
            "bounded output digest mismatch")

    triangle = document["triangle"]
    require(triangle["per_ray_observed"] == triangle["per_ray_expected"]
            == [3, 2, 0, 1], "triangle per-ray CPU/GPU mismatch")
    require(triangle["weighted_observed"] == triangle["weighted_expected"] == 16,
            "triangle checked reduction mismatch")
    require(digest(triangle["weighted_observed"]) == triangle["output_sha256"],
            "triangle output digest mismatch")

    return {
        "schema": "rtdl.goal5795.public_linux_smoke_recount.v1",
        "status": "PASS",
        "input_sha256": hashlib.sha256(raw).hexdigest(),
        "native_sha256": document["native_sha256"],
        "receipt_sha256": checked_receipts,
        "bounded_rows": bounded["observed"],
        "triangle_per_ray": triangle["per_ray_observed"],
        "triangle_weighted": triangle["weighted_observed"],
        "registered_performance_timing_count": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("result", type=Path)
    print(json.dumps(verify(parser.parse_args().result), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
