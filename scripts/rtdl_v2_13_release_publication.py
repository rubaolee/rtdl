#!/usr/bin/env python3
"""Emit the v2.13 source-tree release publication package."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rtdsl.v2_13_release_publication import (  # noqa: E402
    markdown_v2_13_public_rt_vs_embree_comparison,
    markdown_v2_13_publication,
    markdown_v2_13_release_readme,
    markdown_v2_13_tag_preparation,
    v2_13_release_publication_packet,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit JSON instead of Markdown README")
    parser.add_argument(
        "--release-dir",
        type=Path,
        default=ROOT / "docs" / "release_reports" / "v2_13",
        help="write the release package to this directory",
    )
    args = parser.parse_args(argv)

    payload = v2_13_release_publication_packet()
    release_dir = args.release_dir
    release_dir.mkdir(parents=True, exist_ok=True)

    (release_dir / "release_publication.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (release_dir / "README.md").write_text(markdown_v2_13_release_readme(payload), encoding="utf-8")
    (release_dir / "publication.md").write_text(markdown_v2_13_publication(payload), encoding="utf-8")
    (release_dir / "tag_preparation.md").write_text(
        markdown_v2_13_tag_preparation(payload),
        encoding="utf-8",
    )
    (release_dir / "public_rt_vs_embree_comparison.json").write_text(
        json.dumps(
            {
                "version": payload["version"],
                "status": payload["status"],
                "source_artifacts": payload["source_artifacts"],
                "summary": payload["summary"],
                "rows": payload["rows"],
                "blocked_wording": payload["blocked_wording"],
                "pip_interpretation": payload["pip_interpretation"],
                "validation": payload["validation"],
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    (release_dir / "public_rt_vs_embree_comparison.md").write_text(
        markdown_v2_13_public_rt_vs_embree_comparison(payload),
        encoding="utf-8",
    )

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(markdown_v2_13_release_readme(payload), end="")
    return 0 if payload["validation"]["status"] == "accept" else 1


if __name__ == "__main__":
    raise SystemExit(main())
