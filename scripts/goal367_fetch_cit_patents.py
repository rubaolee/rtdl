from __future__ import annotations

import argparse
from pathlib import Path
import sys
import urllib.request

sys.path.insert(0, "src")

import rtdsl as rt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default="build/graph_datasets/cit-Patents.txt.gz",
        help="Destination path for the downloaded cit-Patents archive.",
    )
    args = parser.parse_args()

    spec = rt.graph_dataset_spec("graphalytics_cit_patents")
    if not spec.download_url:
        raise RuntimeError("graphalytics_cit_patents is missing a download_url")

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(spec.download_url, output_path)
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
