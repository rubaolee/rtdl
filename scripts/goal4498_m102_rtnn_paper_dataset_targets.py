from __future__ import annotations

from collections import Counter
from dataclasses import asdict
import json
from pathlib import Path

import rtdsl as rt


PACKET_VERSION = "rtdl.v3_0.rtnn_paper_dataset_targets.goal4498.v1"
OUT_JSON = Path("docs/reports/goal4498_v3_0_m102_rtnn_paper_dataset_targets_2026-06-17.json")
OUT_JSONL = Path("docs/reports/goal4498_v3_0_m102_rtnn_paper_dataset_targets_2026-06-17.jsonl")
OUT_REPORT = Path("docs/reports/goal4498_v3_0_m102_rtnn_paper_dataset_targets_2026-06-17.md")
AUTHOR_REPO_URL = "https://github.com/horizon-research/rtnn"
AUTHOR_REPO_PROBE_COMMIT = "5532e7031d0c8268ffa555972f074f8882b379b5"
AUTHOR_REPO_BUNDLED_POINT_FILES = ("src/samplepc.txt",)
PAPER_URL = "https://horizon-lab.org/pubs/ppopp22.pdf"


def _rows() -> list[dict[str, object]]:
    return [asdict(target) for target in rt.rtnn_paper_dataset_targets()]


def _summary(rows: list[dict[str, object]]) -> dict[str, object]:
    by_family = Counter(str(row["family_handle"]) for row in rows)
    by_status = Counter(str(row["exact_recipe_status"]) for row in rows)
    by_priority = Counter(str(row["acquisition_priority"]) for row in rows)
    return {
        "target_count": len(rows),
        "families": dict(sorted(by_family.items())),
        "exact_recipe_statuses": dict(sorted(by_status.items())),
        "acquisition_priorities": dict(sorted(by_priority.items())),
        "all_exact_rows_blocked": all(
            str(row["exact_recipe_status"]).startswith("blocked_on_")
            for row in rows
        ),
        "largest_target_point_count": max(int(row["point_count"]) for row in rows),
        "paper_reproduction_authorized": False,
        "synthetic_distribution_substitution_authorized": False,
    }


def _write_report(packet: dict[str, object]) -> None:
    rows = packet["rows"]  # type: ignore[index]
    table_lines = [
        "| Target | Family | Points | Status | Priority |",
        "|---|---|---:|---|---|",
    ]
    for row in rows:  # type: ignore[assignment]
        row = dict(row)
        table_lines.append(
            "| "
            f"`{row['paper_label']}` | `{row['family_handle']}` | "
            f"{int(row['point_count']):,} | `{row['exact_recipe_status']}` | "
            f"`{row['acquisition_priority']}` |"
        )

    report = "\n".join(
        [
            "# Goal4498 / V3 M102 RTNN Paper Dataset Targets",
            "",
            "## Conclusion",
            "",
            "RTNN paper reproduction is not currently ready, and the reason is now precise: the paper input labels are known, but exact dataset recipes are not frozen in this repo or in the public author repository snapshot. Current uniform, shell, and clustered rows remain RTDL-internal distribution evidence only.",
            "",
            "The target set is nine paper rows: four KITTI scale labels, three Stanford scan labels, and two Millennium/N-body labels. Bounded KITTI or sampled Stanford packages are allowed only as bounded reproduction artifacts with explicit labels; they must not be reported as paper rows.",
            "",
            "## Target Matrix",
            "",
            *table_lines,
            "",
            "## Acquisition Rule",
            "",
            "- Phase 1: obtain or reconstruct an exact KITTI frame recipe for `KITTI-1M`, `KITTI-6M`, `KITTI-12M`, and `KITTI-25M` before any paper wording.",
            "- Phase 2: freeze exact Stanford scan variants and point extraction/downsample rules for Bunny, Dragon, and Buddha.",
            "- Phase 3: freeze Millennium trace/snapshot ids and coordinate extraction rules for the 9M and 10M rows.",
            "- Author RTNN code can be used as the RT-core baseline, but its public repository snapshot only includes `src/samplepc.txt` as a sample input, not the paper datasets.",
            "",
            "## Source Basis",
            "",
            f"- RTNN paper: {PAPER_URL}",
            f"- Author repository: {AUTHOR_REPO_URL}",
            f"- Author repo probe commit: `{AUTHOR_REPO_PROBE_COMMIT}`",
            "",
            "Artifacts:",
            "",
            f"- `{OUT_JSON.as_posix()}`",
            f"- `{OUT_JSONL.as_posix()}`",
        ]
    )
    OUT_REPORT.write_text(report + "\n", encoding="utf-8")


def build_packet() -> dict[str, object]:
    rows = _rows()
    packet = {
        "version": PACKET_VERSION,
        "goal": "Goal4498 / V3 M102",
        "status": "rtnn_paper_dataset_targets_defined_exact_rows_blocked",
        "date": "2026-06-17",
        "paper": {
            "title": "RTNN: Accelerating Neighbor Search Using Hardware Ray Tracing",
            "url": PAPER_URL,
            "dataset_section": "Section 6.1",
            "claimed_dataset_families": (
                "KITTI LiDAR point clouds",
                "Stanford 3D Scanning Repository models",
                "Millennium Simulation Project N-body traces",
            ),
        },
        "author_repo": {
            "url": AUTHOR_REPO_URL,
            "probe_commit": AUTHOR_REPO_PROBE_COMMIT,
            "bundled_point_files": AUTHOR_REPO_BUNDLED_POINT_FILES,
            "exact_paper_datasets_bundled": False,
            "input_format": "three comma-separated coordinates per line",
        },
        "summary": _summary(rows),
        "decision": (
            "Do not run more RTNN synthetic timing as paper-reproduction evidence. "
            "The next meaningful RTNN work is acquisition/packaging of one exact or "
            "honestly bounded paper-family dataset, followed by same-output comparison "
            "between author RTNN, RTDL OptiX, and Embree/CPU under the same radius+K contract."
        ),
        "claim_boundary": {
            "paper_dataset_targets_defined": True,
            "exact_paper_inputs_acquired": False,
            "same_output_author_rtdl_comparison_ready": False,
            "synthetic_distribution_substitution_authorized": False,
            "paper_reproduction_claim_authorized": False,
            "public_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        },
        "rows": rows,
    }
    return packet


def main() -> dict[str, object]:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    packet = build_packet()
    OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True), encoding="utf-8")
    OUT_JSONL.write_text(
        "\n".join(json.dumps(row, sort_keys=True) for row in packet["rows"]) + "\n",
        encoding="utf-8",
    )
    _write_report(packet)
    print(json.dumps(packet["summary"], indent=2, sort_keys=True), flush=True)
    return packet


if __name__ == "__main__":
    main()
