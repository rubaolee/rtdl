from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FEATURE_ROOT = ROOT / "docs" / "features"
TOP_LEVEL_DOCS = (
    ROOT / "README.md",
    ROOT / "docs" / "README.md",
    ROOT / "docs" / "quick_tutorial.md",
    ROOT / "docs" / "rtdl" / "README.md",
    ROOT / "docs" / "rtdl" / "dsl_reference.md",
    ROOT / "docs" / "rtdl" / "programming_guide.md",
    ROOT / "docs" / "rtdl" / "workload_cookbook.md",
    ROOT / "docs" / "rtdl_feature_guide.md",
    ROOT / "docs" / "v0_2_user_guide.md",
    ROOT / "docs" / "handoff" / "PROJECT_MEMORY_BOOTSTRAP.md",
)
REQUIRED_FEATURE_SECTIONS = (
    "## Purpose",
    "## Docs",
    "## Code",
    "## Example",
    "## Best Practices",
    "## Try",
    "## Try Not",
    "## Limitations",
)


def run_goal147_doc_audit() -> dict[str, object]:
    feature_homes = sorted(FEATURE_ROOT.glob("*/README.md"))
    feature_results = []
    for path in feature_homes:
        text = path.read_text(encoding="utf-8")
        missing = [header for header in REQUIRED_FEATURE_SECTIONS if header not in text]
        feature_results.append(
            {
                "feature": path.parent.name,
                "path": str(path),
                "missing_sections": missing,
            }
        )

    top_level_results = []
    for path in TOP_LEVEL_DOCS:
        text = path.read_text(encoding="utf-8")
        top_level_results.append(
            {
                "path": str(path),
                "mentions_feature_homes": "Feature Homes" in text or "docs/features/" in text or "features/README.md" in text,
            }
        )

    return {
        "feature_home_count": len(feature_results),
        "feature_homes": feature_results,
        "top_level_docs": top_level_results,
        "all_feature_sections_present": all(not item["missing_sections"] for item in feature_results),
        "all_top_level_docs_link_feature_homes": all(item["mentions_feature_homes"] for item in top_level_results),
    }


def main() -> None:
    print(json.dumps(run_goal147_doc_audit(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
