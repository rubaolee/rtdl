#!/usr/bin/env python3
"""Build the successor application-performance figure from the projection."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


EXPECTED_DATA_SHA256 = (
    "ae2cb7011f407c37b3850aa2a854d177baa4a6494d704eb2ddf68e89f574578c"
)
EXPECTED_ROWS = {
    ("particle_tracking", "complete"): (0.1854778580490768, 0.20112034732405892),
    ("particle_tracking", "prepared"): (0.7725590207607267, 0.8402604629649705),
    ("triangle_counting__com_dblp__rt_2a1", "complete"): (
        1.0548112813170818,
        1.1654245205007596,
    ),
    ("triangle_counting__com_dblp__rt_2a1", "prepared"): (
        1.0995118679029061,
        1.1828899668880144,
    ),
    ("librts__parks__point_contains", "complete"): (
        0.3231058624536087,
        0.35745412600174475,
    ),
    ("librts__parks__point_contains", "prepared"): (
        0.9987037678227315,
        1.1104287412538512,
    ),
    ("librts__parks__range_contains", "complete"): (
        0.3652028382993414,
        0.4202689821058394,
    ),
    ("librts__parks__range_contains", "prepared"): (
        0.9849218238434485,
        1.2433325860712887,
    ),
    ("triangle_counting__cit_patents__rt_2a1__4m", "complete"): (
        1.0380651560653118,
        1.0575173494954127,
    ),
    ("triangle_counting__cit_patents__rt_2a1__4m", "prepared"): (
        1.0573612349196906,
        1.0837352868818877,
    ),
}
UNITS = (
    ("particle_tracking", "Particle"),
    ("triangle_counting__com_dblp__rt_2a1", "com-dblp / 1M"),
    ("librts__parks__point_contains", "LibRTS point"),
    ("librts__parks__range_contains", "LibRTS range"),
    ("triangle_counting__cit_patents__rt_2a1__4m", "cit-Patents / 4M"),
)


def _load_projection(path: Path) -> dict:
    raw = path.read_bytes()
    observed_hash = hashlib.sha256(raw).hexdigest()
    if observed_hash != EXPECTED_DATA_SHA256:
        raise SystemExit(
            f"projection hash mismatch: expected {EXPECTED_DATA_SHA256}, "
            f"observed {observed_hash}"
        )
    projection = json.loads(raw)
    if projection.get("schema") != "rtdl.cgo2027.application_projection.v1":
        raise SystemExit("unexpected projection schema")
    if projection.get("independent_recount_projection", {}).get("status") != (
        "PASS__METHOD_AND_TARGET"
    ):
        raise SystemExit("projection does not carry the accepted recount status")
    rows = {
        (row["unit_id"], row["endpoint"]): (
            row["median_new_v4_over_pyoptix"],
            row["max_new_v4_over_pyoptix"],
        )
        for row in projection["expected_evaluations"]
    }
    if rows != EXPECTED_ROWS:
        raise SystemExit("projection rows differ from the reviewed ten-row authority")
    return projection


def _build_figure(projection: dict, output: Path) -> None:
    rows = {
        (row["unit_id"], row["endpoint"]): row
        for row in projection["expected_evaluations"]
    }
    blue = "#285b86"
    orange = "#a45118"
    red = "#9a2f2f"
    ink = "#202b35"
    grid = "#d7dee3"

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 8,
            "axes.edgecolor": "#aab5bd",
            "axes.labelcolor": ink,
            "xtick.color": "#51606c",
            "ytick.color": ink,
            "pdf.fonttype": 42,
        }
    )
    figure, axes = plt.subplots(1, 2, figsize=(7.0, 3.0), sharey=True)
    figure.subplots_adjust(left=0.205, right=0.985, bottom=0.30, top=0.755, wspace=0.13)
    figure.suptitle(
        "Successor application routes relative to public PyOptiX",
        x=0.02,
        y=0.975,
        ha="left",
        fontsize=12.0,
        fontweight="bold",
        color=ink,
    )
    figure.text(
        0.02,
        0.875,
        "RTX A4500 | 8 paired fresh-process blocks per row | lower is better",
        ha="left",
        fontsize=8.5,
        color="#586775",
    )

    y_positions = list(reversed(range(len(UNITS))))
    for axis, endpoint, title in zip(
        axes,
        ("complete", "prepared"),
        ("Setup + run after shared preprocessing", "Prepared checked action"),
    ):
        axis.set_xlim(0.0, 1.42)
        axis.set_ylim(-0.55, 4.55)
        axis.set_axisbelow(True)
        axis.grid(axis="x", color=grid, linewidth=0.6)
        axis.axvline(1.0, color=ink, linewidth=1.0, linestyle="--", zorder=1)
        axis.axvline(1.2, color=orange, linewidth=0.9, linestyle=":", zorder=1)
        axis.axvline(1.35, color=red, linewidth=0.9, linestyle=":", zorder=1)
        axis.set_title(title, fontsize=8.5, fontweight="bold", pad=8)
        axis.set_xlabel("successor RTDL / PyOptiX", fontsize=8, labelpad=4)
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)
        axis.set_xticks((0.0, 0.5, 1.0, 1.2, 1.35))
        axis.set_xticklabels(("0", ".5", "1", "1.2", "1.35"), fontsize=7.2)

        for (unit_id, _), y in zip(UNITS, y_positions):
            row = rows[(unit_id, endpoint)]
            median = row["median_new_v4_over_pyoptix"]
            maximum = row["max_new_v4_over_pyoptix"]
            axis.plot((median, maximum), (y, y), color=blue, linewidth=1.4, zorder=3)
            axis.plot(median, y, marker="D", color=blue, markersize=4.3, zorder=4)
            axis.plot(
                maximum,
                y,
                marker="o",
                markerfacecolor="white",
                markeredgecolor=blue,
                markeredgewidth=1.0,
                markersize=4.8,
                zorder=4,
            )
            axis.annotate(
                f"{median:.3f}",
                (median, y),
                xytext=(0, 8),
                textcoords="offset points",
                ha="center",
                fontsize=7.0,
                color=ink,
            )

    axes[0].set_yticks(y_positions, [label for _, label in UNITS], fontsize=7.8)
    axes[1].tick_params(axis="y", left=False, labelleft=False)
    figure.text(
        0.02,
        0.115,
        "Diamond: paired median. Open circle: largest observed block. Dashed: 1x; dotted: 1.20 / 1.35 gates.",
        ha="left",
        fontsize=7.5,
        color=ink,
    )
    figure.text(
        0.02,
        0.045,
        "All ten rows meet the registered envelope; only cit-Patents / 4M is a multi-second prepared computation.",
        ha="left",
        fontsize=7.3,
        color="#586775",
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    metadata = {
        "Title": "RTDL successor application performance",
        "Author": "Anonymous",
        "Creator": "build_successor_performance.py",
        "CreationDate": dt.datetime(2000, 1, 1, tzinfo=dt.timezone.utc),
        "ModDate": dt.datetime(2000, 1, 1, tzinfo=dt.timezone.utc),
    }
    figure.savefig(output, format="pdf", metadata=metadata, bbox_inches=None)
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--projection",
        type=Path,
        default=Path(__file__).parents[1]
        / "artifact_long_workload"
        / "data"
        / "application_projection.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("successor_application_performance.pdf"),
    )
    args = parser.parse_args()
    os.environ.setdefault("SOURCE_DATE_EPOCH", "946684800")
    _build_figure(_load_projection(args.projection), args.output)


if __name__ == "__main__":
    main()
