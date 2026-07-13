#!/usr/bin/env python3
"""Create a bounded CDB representative by taking the first N chains."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from rtdsl.datasets import CdbDataset, load_cdb, write_cdb


def _chain_point_count(dataset: CdbDataset) -> int:
    return sum(len(chain.points) for chain in dataset.chains)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--max-chains", type=int, required=True)
    parser.add_argument("--summary", required=True)
    args = parser.parse_args()

    source = load_cdb(args.input)
    chains = source.chains[: args.max_chains]
    sliced = CdbDataset(name=Path(args.output).stem, chains=tuple(chains))
    write_cdb(sliced, args.output)

    summary = {
        "input": str(args.input),
        "output": str(args.output),
        "source_chain_count": len(source.chains),
        "source_point_count": _chain_point_count(source),
        "sliced_chain_count": len(sliced.chains),
        "sliced_point_count": _chain_point_count(sliced),
        "selection": "first_n_chains_from_current_osm_geofabrik_representative_cdb",
        "claim_boundary": "bounded LSI representative only; not exact paper CDB",
    }
    Path(args.summary).write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
