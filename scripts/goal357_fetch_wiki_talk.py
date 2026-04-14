from __future__ import annotations

import argparse
from pathlib import Path
import sys
import urllib.request


WIKI_TALK_URL = "https://snap.stanford.edu/data/wiki-Talk.txt.gz"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default="build/graph_datasets/wiki-Talk.txt.gz",
        help="Destination path for the downloaded SNAP wiki-Talk archive.",
    )
    args = parser.parse_args()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(WIKI_TALK_URL, output_path)
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
