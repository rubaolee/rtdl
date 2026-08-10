#!/usr/bin/env python3
"""Prepare exact Arkade author inputs and enable result observation.

The pinned author archive is immutable.  This tool applies one narrowly
scoped host-only observation patch to a clean extraction of
``s02-withTrueknn``: it validates the CLI, downloads the existing result
buffer, sorts each query's already-computed neighbors by (distance,item-id),
and writes them.  Device code, OptiX programs, search rounds and distances are
unchanged.
"""

from __future__ import annotations

import argparse
import hashlib
import io
from pathlib import Path
import tarfile

import numpy as np

from arkade_contract import (
    AUTHOR_ARCHIVE,
    AUTHOR_ARCHIVE_PREFIX,
    ArkadeAlgorithm,
    load_frozen_view,
)


HOST_RELATIVE_PATH = Path("src/s02-withTrueknn/hostCode.cpp")
PATCH_CONTRACT = "arkade.author_s02_result_observation_only.v1"


_INCLUDE_ANCHOR = '#include "deviceCode.h"'
_INCLUDE_REPLACEMENT = '''#include "deviceCode.h"
#include <algorithm>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <vector>'''


_ARGUMENT_ANCHOR = """int main(int ac, char **argv)\n{\n  std::string line;"""
_ARGUMENT_REPLACEMENT = """int main(int ac, char **argv)\n{\n  if (ac != 6) {\n    std::cerr << \"usage: sample02-withTrueknn input npoints nqueries radius output\" << std::endl;\n    return 2;\n  }\n  std::string line;"""

_OUTPUT_ANCHOR = """  // printf(\"Complete Search, writing output to file...\\n\");\n  // const Neigh *fb = (const Neigh*)owlBufferGetPointer(frameBuffer,0);\n  // std::ofstream outfile;\n  // outfile.open(argv[5]);\n  // // std::cout<<setprecision(6);\n\t// for(int j=0; j<nsearchpoints; j++){\n  //   for(int i = 0; i < KN; i++)\n  //   {            \n  //     outfile<<fb[j*KN+i].ind<<'\\t'<<fb[j*KN+i].dist<<endl;\n  //   }\n  // }\n  // outfile.close();"""

_OUTPUT_REPLACEMENT = """  const Neigh *fb = (const Neigh*)owlBufferGetPointer(frameBuffer,0);\n  std::ofstream outfile(argv[5], std::ios::out | std::ios::trunc);\n  if (!outfile.is_open()) {\n    std::cerr << \"cannot open Arkade result output\" << std::endl;\n    owlContextDestroy(context);\n    return 3;\n  }\n  outfile << std::setprecision(9);\n  for (int query_id = 0; query_id < nsearchpoints; ++query_id) {\n    std::vector<Neigh> ordered;\n    ordered.reserve(KN);\n    for (int slot = 0; slot < KN; ++slot)\n      ordered.push_back(fb[query_id * KN + slot]);\n    std::sort(ordered.begin(), ordered.end(), [](const Neigh &a, const Neigh &b) {\n      if (a.dist != b.dist) return a.dist < b.dist;\n      return a.ind < b.ind;\n    });\n    for (const Neigh &neighbor : ordered)\n      outfile << query_id << '\\t' << neighbor.ind << '\\t' << neighbor.dist << '\\n';\n  }\n  outfile.close();"""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def apply_observation_patch(author_root: Path) -> dict[str, object]:
    host = Path(author_root) / HOST_RELATIVE_PATH
    before = host.read_text(encoding="utf-8")
    if (
        before.count(_INCLUDE_ANCHOR) != 1
        or before.count(_ARGUMENT_ANCHOR) != 1
        or before.count(_OUTPUT_ANCHOR) != 1
    ):
        raise RuntimeError("pinned Arkade author host source does not match patch anchors")
    after = (
        before.replace(_INCLUDE_ANCHOR, _INCLUDE_REPLACEMENT)
        .replace(_ARGUMENT_ANCHOR, _ARGUMENT_REPLACEMENT)
        .replace(_OUTPUT_ANCHOR, _OUTPUT_REPLACEMENT)
    )
    if after == before:
        raise AssertionError("author observation patch made no change")
    host.write_text(after, encoding="utf-8", newline="")
    return {
        "contract": PATCH_CONTRACT,
        "relative_path": HOST_RELATIVE_PATH.as_posix(),
        "before_sha256": hashlib.sha256(before.encode("utf-8")).hexdigest(),
        "after_sha256": sha256_file(host),
        "device_source_changed": False,
        "search_algorithm_changed": False,
        "timing_region_changed": False,
        "result_observation_only": True,
    }


def audit_public_author_source(
    archive_path: Path = AUTHOR_ARCHIVE,
) -> dict[str, object]:
    """Classify the paper theorem separately from the public artifact gaps."""

    names = {
        "host": AUTHOR_ARCHIVE_PREFIX + "src/s02-withTrueknn/hostCode.cpp",
        "device": AUTHOR_ARCHIVE_PREFIX + "src/s02-withTrueknn/deviceCode.cu",
        "readme": AUTHOR_ARCHIVE_PREFIX + "README.md",
    }
    archive_bytes = Path(archive_path).read_bytes()
    with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:gz") as archive:
        sources = {}
        source_hashes = {}
        for key, name in names.items():
            handle = archive.extractfile(name)
            if handle is None:
                raise RuntimeError(f"pinned Arkade archive lacks {name}")
            payload = handle.read()
            sources[key] = payload.decode("utf-8")
            source_hashes[key] = hashlib.sha256(payload).hexdigest()
    host = sources["host"]
    device = sources["device"]
    readme = sources["readme"]
    required_facts = {
        "paper_declares_filter_refine_and_monotone_transform": (
            "Arkade Filter-Refine" in readme and "Arkade Monotone Transformation" in readme
        ),
        "fr_linf_device_metric_present": "#elif (NORM == 0) //linfty" in device,
        "mt_cosine_device_metric_present": "#if (NORM == -1)  //dot" in device,
        "true_knn_radius_doubles": "radius *= 2;" in host,
        "true_knn_refits_acceleration": (
            "owlGroupRefitAccel(spheresGroup);" in host
            and "owlGroupRefitAccel(world);" in host
        ),
        "true_knn_relaunches_queries": "owlLaunch2D(rayGen,nsearchpoints,1,lp);" in host,
        "public_result_output_is_commented": (
            '// const Neigh *fb = (const Neigh*)owlBufferGetPointer(frameBuffer,0);'
            in host
        ),
        "public_topk_uses_strict_distance_only": (
            "if (distance < param.res[max_idx].dist)" in device
        ),
        "public_topk_has_no_item_id_tie_break": (
            "distance == param.res[max_idx].dist" not in device
            and "distance_key" not in device
        ),
        "public_true_knn_has_no_round_bound": (
            "// while(repeat && round < in_rounds)" in host and "while(repeat)" in host
        ),
    }
    if not all(required_facts.values()):
        missing = sorted(name for name, value in required_facts.items() if not value)
        raise RuntimeError(f"Arkade public-source audit lost required facts: {missing}")
    return {
        "schema": "rtdl.goal5745.arkade_public_author_source_audit.v1",
        "goal": 5745,
        "author_archive_sha256": hashlib.sha256(archive_bytes).hexdigest(),
        "source_sha256": source_hashes,
        "required_source_facts": required_facts,
        "paper_algorithmic_reductions_implementable": True,
        "paper_theorem_declared_wrong": False,
        "public_artifact_complete_exact_output_oracle": False,
        "public_artifact_performance_or_correctness_ratio_claim_eligible_now": False,
        "reasons": [
            "public_s02_result_download_and_write_path_is_commented",
            "public_binary32_topk_has_no_deterministic_item_id_tie_break",
            "public_true_knn_loop_has_no_fail_closed_round_bound",
            "mt_dot_key_and_transformed_l2_key_are_mathematically_monotone_but_can_round_differently_in_binary32",
        ],
        "rtdl_implementation_policy": {
            "implement_paper_fr_linf": True,
            "implement_paper_mt_unit_normalization_then_l2": True,
            "implement_persistent_gas_refit_radius_doubling": True,
            "add_deterministic_binary32_metric_then_u32_id_order": True,
            "add_bounded_round_fail_closed": True,
            "do_not_relabel_stricter_rtdl_output_as_public_author_byte_output": True,
        },
        "performance_claimed": False,
    }


def write_author_input(
    *,
    algorithm: ArkadeAlgorithm,
    view_id: str,
    output_path: Path,
) -> dict[str, object]:
    if output_path.exists():
        raise FileExistsError(f"refusing to replace author input: {output_path}")
    payload = load_frozen_view(view_id)
    data = np.asarray(payload["data_points"], dtype=np.float32)
    queries = np.asarray(payload["query_points"], dtype=np.float32)
    if algorithm is ArkadeAlgorithm.MT_COSINE:
        # Arkade MT maps cosine to Euclidean traversal after unit
        # normalization.  Binary32 is the author's device-input precision.
        data64 = data.astype(np.float64)
        query64 = queries.astype(np.float64)
        data = np.asarray(data64 / np.linalg.norm(data64, axis=1)[:, None], dtype=np.float32)
        queries = np.asarray(
            query64 / np.linalg.norm(query64, axis=1)[:, None], dtype=np.float32
        )
    rows = np.concatenate((data, queries), axis=0)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("x", encoding="ascii", newline="\n") as handle:
        for row in rows:
            handle.write("{:.9g}\t{:.9g}\t{:.9g}\n".format(*(float(value) for value in row)))
    return {
        "algorithm": algorithm.value,
        "view_id": view_id,
        "data_count": int(data.shape[0]),
        "query_count": int(queries.shape[0]),
        "binary32_input": True,
        "unit_normalized_for_mt": algorithm is ArkadeAlgorithm.MT_COSINE,
        "input_sha256": sha256_file(output_path),
    }


def load_author_observed_ids(path: Path, *, query_count: int, k: int) -> np.ndarray:
    rows = np.loadtxt(path, dtype=np.float64)
    if rows.shape != (query_count * k, 3):
        raise RuntimeError("Arkade author output row count or schema mismatch")
    query_ids = rows[:, 0].astype(np.int64)
    item_ids = rows[:, 1].astype(np.int64)
    if not np.array_equal(query_ids, np.repeat(np.arange(query_count), k)):
        raise RuntimeError("Arkade author output query order mismatch")
    if np.any(item_ids < 0) or np.any(item_ids > (1 << 32) - 1):
        raise RuntimeError("Arkade author output contains an invalid item id")
    return item_ids.astype(np.uint32).reshape(query_count, k)


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    audit_parser = subparsers.add_parser("audit")
    audit_parser.add_argument("--output", type=Path)
    patch_parser = subparsers.add_parser("patch")
    patch_parser.add_argument("author_root", type=Path)
    input_parser = subparsers.add_parser("input")
    input_parser.add_argument("--algorithm", choices=tuple(a.value for a in ArkadeAlgorithm), required=True)
    input_parser.add_argument("--view", required=True)
    input_parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "audit":
        result = audit_public_author_source()
    elif args.command == "patch":
        result = apply_observation_patch(args.author_root)
    else:
        result = write_author_input(
            algorithm=ArkadeAlgorithm(args.algorithm),
            view_id=args.view,
            output_path=args.output,
        )
    import json

    if args.command == "audit" and args.output is not None:
        if args.output.exists():
            raise FileExistsError(f"refusing to replace audit: {args.output}")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")

    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
