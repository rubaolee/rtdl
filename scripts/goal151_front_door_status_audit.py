from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DOCS = (
    ROOT / "README.md",
    ROOT / "docs" / "README.md",
    ROOT / "docs" / "v0_2_user_guide.md",
    ROOT / "docs" / "rtdl_feature_guide.md",
    ROOT / "docs" / "handoff" / "PROJECT_MEMORY_BOOTSTRAP.md",
)

REQUIRED_WORKLOADS = (
    "segment_polygon_hitcount",
    "segment_polygon_anyhit_rows",
    "polygon_pair_overlap_area_rows",
    "polygon_set_jaccard",
)

REQUIRED_PHRASES = (
    "frozen v0.2",
    "Linux",
    "Mac",
)

JACCARD_BOUNDARY_PHRASE = "native CPU/oracle fallback"


def audit_doc(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    return {
        "path": str(path),
        "all_workloads_present": all(workload in text for workload in REQUIRED_WORKLOADS),
        "all_required_phrases_present": all(phrase in text for phrase in REQUIRED_PHRASES),
        "jaccard_boundary_present": JACCARD_BOUNDARY_PHRASE in text,
    }


def main() -> None:
    docs = [audit_doc(path) for path in DOCS]
    payload = {
        "all_docs_cover_frozen_scope": all(item["all_workloads_present"] for item in docs),
        "all_docs_cover_platform_split": all(item["all_required_phrases_present"] for item in docs),
        "all_docs_cover_jaccard_boundary": all(item["jaccard_boundary_present"] for item in docs),
        "docs": docs,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
