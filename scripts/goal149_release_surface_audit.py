from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

RELEASE_EXAMPLES = {
    "segment_polygon_hitcount": ROOT / "examples" / "rtdl_segment_polygon_hitcount.py",
    "segment_polygon_anyhit_rows": ROOT / "examples" / "rtdl_segment_polygon_anyhit_rows.py",
    "polygon_pair_overlap_area_rows": ROOT / "examples" / "rtdl_polygon_pair_overlap_area_rows.py",
    "polygon_set_jaccard": ROOT / "examples" / "rtdl_polygon_set_jaccard.py",
    "road_hazard_screening": ROOT / "examples" / "rtdl_road_hazard_screening.py",
    "generate_only_script": ROOT / "scripts" / "rtdl_generate_only.py",
}

RELEASE_DOCS = (
    ROOT / "README.md",
    ROOT / "docs" / "README.md",
    ROOT / "docs" / "quick_tutorial.md",
    ROOT / "docs" / "v0_2_user_guide.md",
    ROOT / "docs" / "rtdl_feature_guide.md",
    ROOT / "docs" / "release_facing_examples.md",
)
RELEASE_EXAMPLE_DOC = ROOT / "docs" / "release_facing_examples.md"


def run_goal149_release_surface_audit() -> dict[str, object]:
    example_results = {
        name: {"path": str(path), "exists": path.exists()}
        for name, path in RELEASE_EXAMPLES.items()
    }
    doc_results = []
    for path in RELEASE_DOCS:
        text = path.read_text(encoding="utf-8")
        doc_results.append(
            {
                "path": str(path),
                "mentions_release_examples": "Release-Facing Examples" in text or "release_facing_examples.md" in text,
            }
        )
    return {
        "all_examples_exist": all(item["exists"] for item in example_results.values()),
        "examples": example_results,
        "all_docs_link_release_examples": all(item["mentions_release_examples"] for item in doc_results),
        "docs": doc_results,
        "release_example_doc_has_no_machine_local_links": not re.search(
            r"\]\(/Users/rl2025/",
            RELEASE_EXAMPLE_DOC.read_text(encoding="utf-8"),
        ),
    }


def main() -> None:
    print(json.dumps(run_goal149_release_surface_audit(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
