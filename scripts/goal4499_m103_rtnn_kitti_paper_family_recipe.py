from __future__ import annotations

from dataclasses import asdict
import json
import os
from pathlib import Path

import rtdsl as rt


PACKET_VERSION = "rtdl.v3_0.rtnn_kitti_paper_family_recipe.goal4499.v1"
OUT_JSON = Path("docs/reports/goal4499_v3_0_m103_rtnn_kitti_paper_family_recipe_2026-06-17.json")
OUT_JSONL = Path("docs/reports/goal4499_v3_0_m103_rtnn_kitti_paper_family_recipe_2026-06-17.jsonl")
OUT_REPORT = Path("docs/reports/goal4499_v3_0_m103_rtnn_kitti_paper_family_recipe_2026-06-17.md")

DEFAULT_SOURCE_ROOT_CANDIDATES = (
    "/workspace/data/kitti/extracted",
    "/workspace/data/kitti",
    "/data/kitti",
    "data/kitti",
)


def _source_root_candidates() -> tuple[str, ...]:
    candidates: list[str] = []
    env_root = os.environ.get("RTDL_KITTI_SOURCE_ROOT")
    if env_root:
        candidates.append(env_root)
    candidates.extend(DEFAULT_SOURCE_ROOT_CANDIDATES)
    seen: set[str] = set()
    unique: list[str] = []
    for candidate in candidates:
        if candidate not in seen:
            unique.append(candidate)
            seen.add(candidate)
    return tuple(unique)


def _resolve_first_ready_source_root() -> Path | None:
    for candidate in _source_root_candidates():
        resolved = rt.resolve_kitti_source_root(candidate)
        if resolved is None:
            continue
        try:
            if rt.discover_kitti_velodyne_frames(resolved):
                return resolved
        except RuntimeError:
            continue
    return None


def _recipe_rows(source_root: Path | None) -> list[dict[str, object]]:
    if source_root is None:
        return []
    rows: list[dict[str, object]] = []
    for target in rt.rtnn_paper_dataset_targets(family_handle="kitti_velodyne_point_sets"):
        recipe = rt.plan_kitti_paper_family_recipe(
            target_handle=target.handle,
            source_root=source_root,
        )
        rows.append(asdict(recipe))
    return rows


def _summary(rows: list[dict[str, object]], source_root: Path | None) -> dict[str, object]:
    ready_rows = [row for row in rows if row["recipe_status"] == "bounded_family_recipe_ready"]
    source_ready = source_root is not None
    return {
        "source_ready": source_ready,
        "source_root": "" if source_root is None else str(source_root),
        "kitti_target_count": len(rt.rtnn_paper_dataset_targets(family_handle="kitti_velodyne_point_sets")),
        "recipe_row_count": len(rows),
        "ready_bounded_recipe_count": len(ready_rows),
        "largest_ready_target_point_count": (
            max(int(row["target_point_count"]) for row in ready_rows) if ready_rows else 0
        ),
        "bounded_same_contract_comparison_ready": bool(ready_rows),
        "paper_reproduction_authorized": False,
        "paper_equivalence_authorized": False,
    }


def build_packet() -> dict[str, object]:
    source_root = _resolve_first_ready_source_root()
    rows = _recipe_rows(source_root)
    has_ready_recipe = any(row["recipe_status"] == "bounded_family_recipe_ready" for row in rows)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4499 / V3 M103",
        "status": (
            "kitti_bounded_family_recipes_ready"
            if has_ready_recipe
            else "kitti_source_not_ready_or_insufficient"
        ),
        "date": "2026-06-17",
        "source_probe": {
            "candidate_roots": _source_root_candidates(),
            "resolved_source_root": "" if source_root is None else str(source_root),
        },
        "summary": _summary(rows, source_root),
        "decision": (
            "Use the generated KITTI recipe rows only as bounded paper-family inputs for "
            "same-contract author RTNN, RTDL OptiX, and Embree/CPU comparison. They are "
            "not exact paper rows until the paper's frame ids and merge/truncation rule are frozen."
        ),
        "claim_boundary": {
            "paper_family_dataset": True,
            "exact_paper_recipe": False,
            "bounded_same_contract_author_rtdl_comparison_allowed": has_ready_recipe,
            "paper_reproduction_wording_allowed": False,
            "synthetic_distribution_substitution_authorized": False,
        },
        "rows": rows,
    }


def _write_report(packet: dict[str, object]) -> None:
    rows = list(packet["rows"])  # type: ignore[arg-type]
    table_lines = [
        "| Target | Target Points | Selected Points | Frames | Status | Paper Equivalence |",
        "|---|---:|---:|---:|---|---|",
    ]
    if rows:
        for row in rows:
            row = dict(row)
            table_lines.append(
                "| "
                f"`{row['paper_label']}` | "
                f"{int(row['target_point_count']):,} | "
                f"{int(row['selected_point_count']):,} | "
                f"{int(row['selected_frame_count']):,} | "
                f"`{row['recipe_status']}` | "
                f"`{row['paper_equivalence_status']}` |"
            )
    else:
        table_lines.append("| no ready KITTI source root | 0 | 0 | 0 | `source_missing` | `not_paper_equivalent` |")

    summary = dict(packet["summary"])  # type: ignore[arg-type]
    if summary["bounded_same_contract_comparison_ready"]:
        conclusion = (
            "A real KITTI source root is available, and at least one bounded paper-family "
            "recipe can now feed same-contract author RTNN, RTDL OptiX, and Embree/CPU runs."
        )
    else:
        conclusion = (
            "The V3 recipe layer is ready, but this host has not yet exposed enough KITTI "
            "Velodyne data for a bounded paper-family run."
        )

    report = "\n".join(
        [
            "# Goal4499 / V3 M103 RTNN KITTI Paper-Family Recipe",
            "",
            "## Conclusion",
            "",
            conclusion,
            "",
            "This is deliberately not an exact RTNN paper reproduction. It creates an auditable KITTI-family recipe boundary so later performance packets can compare author RTNN, RTDL OptiX, and Embree/CPU on the same bounded input without pretending the paper's exact frame recipe is known.",
            "",
            "## Recipe Matrix",
            "",
            *table_lines,
            "",
            "## Claim Boundary",
            "",
            "- Bounded same-contract comparison is allowed only when a row is `bounded_family_recipe_ready`.",
            "- Paper-reproduction wording remains disallowed.",
            "- Synthetic uniform/shell/clustered rows remain distribution evidence only and are not substitutes for these KITTI recipes.",
            "",
            "Artifacts:",
            "",
            f"- `{OUT_JSON.as_posix()}`",
            f"- `{OUT_JSONL.as_posix()}`",
        ]
    )
    OUT_REPORT.write_text(report + "\n", encoding="utf-8")


def main() -> dict[str, object]:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    packet = build_packet()
    OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True), encoding="utf-8")
    rows = list(packet["rows"])  # type: ignore[arg-type]
    OUT_JSONL.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )
    _write_report(packet)
    print(json.dumps(packet["summary"], indent=2, sort_keys=True), flush=True)
    return packet


if __name__ == "__main__":
    main()
