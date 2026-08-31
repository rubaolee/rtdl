"""Result-independent NVIDIA OptiX/PyOptiX stack selection for Goal5798.

The language does not select a GPU model or demand a preferred driver.  It
observes the provided NVIDIA Linux environment and chooses the newest frozen
OptiX API whose NVIDIA-published driver floor is satisfied.  The choice is
made before any task is materialized and never depends on correctness,
performance, memory use, or the application result.
"""

from __future__ import annotations

import argparse
import json
import re
from typing import Any


PYOPTIX_REPOSITORY = "https://github.com/NVIDIA/otk-pyoptix.git"
PYOPTIX_COMMIT = "3144f224c0fd18733925faf3d8fb82c7376b8dcf"
PYOPTIX_TAG = "v1.3.0"
PYOPTIX_TREE = "0bf0ec24efb4a43f129aee25dd265aa8149374e3"

# Ordered newest first.  Commit identities and minimum drivers are from the
# NVIDIA optix-dev release entries.  The current PyOptiX source documents
# source installation against legacy OptiX releases; no PyOptiX source edit is
# permitted for any row.
COMPATIBLE_STACKS: tuple[dict[str, Any], ...] = (
    {
        "stack_id": "PYOPTIX_V1_3_OPTIX_9_1",
        "optix_api_version": "9.1.0",
        "optix_header_tag": "v9.1.0",
        "optix_header_commit": "f1f6dd803f3159992d248178f6e09421c6eb8b6d",
        "minimum_driver": "590.0",
        "minimum_driver_tuple": (590, 0),
        "pyoptix_distribution_name": "pyoptix",
        "pyoptix_distribution_version": "9.1.0",
    },
    {
        "stack_id": "PYOPTIX_V1_3_OPTIX_9_0",
        "optix_api_version": "9.0.0",
        "optix_header_tag": "v9.0.0",
        "optix_header_commit": "fff65c2a7c592f1ea5f1661ad7d2381cf965f9bd",
        "minimum_driver": "570.0",
        "minimum_driver_tuple": (570, 0),
        "pyoptix_distribution_name": "pyoptix",
        "pyoptix_distribution_version": "9.1.0",
    },
    {
        "stack_id": "PYOPTIX_V1_3_OPTIX_8_1",
        "optix_api_version": "8.1.0",
        "optix_header_tag": "v8.1.0",
        "optix_header_commit": "50021ea0af6d41609a97777ceebbdf1e1d34efe7",
        "minimum_driver": "555.0",
        "minimum_driver_tuple": (555, 0),
        "pyoptix_distribution_name": "pyoptix",
        "pyoptix_distribution_version": "9.1.0",
    },
    {
        "stack_id": "PYOPTIX_V1_3_OPTIX_8_0",
        "optix_api_version": "8.0.0",
        "optix_header_tag": "v8.0.0",
        "optix_header_commit": "f60c1e44f18426f426a2ed948f28515b3cf67b8a",
        "minimum_driver": "535.0",
        "minimum_driver_tuple": (535, 0),
        "pyoptix_distribution_name": "pyoptix",
        "pyoptix_distribution_version": "9.1.0",
    },
    {
        "stack_id": "PYOPTIX_V1_3_OPTIX_7_7",
        "optix_api_version": "7.7.0",
        "optix_header_tag": "v7.7.0",
        "optix_header_commit": "7b5c4e8608b8b4b601729f6240fc3fd53cb36d23",
        "minimum_driver": "530.41",
        "minimum_driver_tuple": (530, 41),
        "pyoptix_distribution_name": "pyoptix",
        "pyoptix_distribution_version": "9.1.0",
    },
    {
        "stack_id": "PYOPTIX_V1_3_OPTIX_7_6",
        "optix_api_version": "7.6.0",
        "optix_header_tag": "v7.6.0",
        "optix_header_commit": "56ec8542c8c828ebc3c6b64edfc9fd232943870a",
        "minimum_driver": "522.25",
        "minimum_driver_tuple": (522, 25),
        "pyoptix_distribution_name": "pyoptix",
        "pyoptix_distribution_version": "9.1.0",
    },
)


def driver_tuple(value: str) -> tuple[int, ...]:
    parts = re.findall(r"\d+", value)
    if not parts:
        raise ValueError(f"driver version contains no numeric component: {value!r}")
    return tuple(int(part) for part in parts)


def _at_least(actual: tuple[int, ...], minimum: tuple[int, ...]) -> bool:
    width = max(len(actual), len(minimum))
    return actual + (0,) * (width - len(actual)) >= minimum + (0,) * (width - len(minimum))


def public_stack(row: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in row.items() if key != "minimum_driver_tuple"}


def select_compatible_stack(driver_version: str) -> dict[str, Any]:
    """Select solely from the observed driver version, never from a result."""
    actual = driver_tuple(driver_version)
    for row in COMPATIBLE_STACKS:
        if _at_least(actual, row["minimum_driver_tuple"]):
            return public_stack(row)
    raise RuntimeError(
        "the provided driver predates OptiX 7.6/PyOptiX's frozen supported "
        "API floor (NVIDIA driver 522.25); no GPU model was rejected")


def validate_selected_stack(driver_version: str, selected: dict[str, Any]) -> list[str]:
    try:
        expected = select_compatible_stack(driver_version)
    except (RuntimeError, ValueError):
        return ["NO_SUPPORTED_OPTIX_STACK_FOR_DRIVER"]
    if selected != expected:
        return ["STACK_NOT_DETERMINISTIC_MAXIMUM_COMPATIBLE"]
    return []


def frozen_registry() -> list[dict[str, Any]]:
    return [public_stack(row) for row in COMPATIBLE_STACKS]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--driver", required=True)
    parser.add_argument("--field", choices=tuple(frozen_registry()[0]))
    args = parser.parse_args()
    selected = select_compatible_stack(args.driver)
    if args.field:
        print(selected[args.field])
    else:
        print(json.dumps(selected, sort_keys=True))


if __name__ == "__main__":
    main()
