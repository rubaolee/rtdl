"""Build the Goal5788 lifecycle-stratified performance evidence chart.

The chart contains only immutable Goal5785 row counts.  It deliberately avoids
novelty scores, cross-row speedup aggregation, and a visual implication that an
uncertain row is a win or a loss.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = (
    ROOT
    / "history"
    / "internal_docs"
    / "goal5788_v4_cgo_performance_evidence_20260816.png"
)


def main() -> None:
    labels = ["Overall (34)", "Cold (15)", "Prepared (19)"]
    clear_win = [11, 4, 7]
    uncertain = [13, 2, 11]
    clear_loss = [10, 9, 1]

    width, height = 1840, 900
    image = Image.new("RGB", (width, height), "#FAFAF8")
    draw = ImageDraw.Draw(image)
    regular_path = Path("C:/Windows/Fonts/arial.ttf")
    bold_path = Path("C:/Windows/Fonts/arialbd.ttf")
    regular = lambda size: ImageFont.truetype(str(regular_path), size)
    bold = lambda size: ImageFont.truetype(str(bold_path), size)
    colors = {"win": "#217A4B", "uncertain": "#7B828C", "loss": "#B6403A"}

    draw.text(
        (70, 55),
        "RTDL V4 vs V2-direct on RTX 4000 Ada",
        fill="#182027",
        font=bold(42),
    )
    draw.text(
        (70, 112),
        "Mixed, lifecycle-sensitive performance; no cross-row compensation",
        fill="#39434C",
        font=regular(27),
    )
    draw.text(
        (70, 157),
        "Classification uses the frozen paired V2/V4 95% bootstrap CI around 1.0.",
        fill="#59636D",
        font=regular(22),
    )

    bar_left, bar_right = 360, 1740
    bar_width = bar_right - bar_left
    max_rows = 34
    row_y = [280, 440, 600]
    bar_height = 76
    for index, label in enumerate(labels):
        y = row_y[index]
        draw.text((70, y + 18), label, fill="#202A31", font=bold(27))
        values = [clear_win[index], uncertain[index], clear_loss[index]]
        keys = ["win", "uncertain", "loss"]
        x = bar_left
        for value, key in zip(values, keys):
            segment = bar_width * value / max_rows
            draw.rectangle((x, y, x + segment, y + bar_height), fill=colors[key])
            if value:
                text_value = str(value)
                box = draw.textbbox((0, 0), text_value, font=bold(28))
                text_width = box[2] - box[0]
                draw.text(
                    (x + (segment - text_width) / 2, y + 20),
                    text_value,
                    fill="white",
                    font=bold(28),
                )
            x += segment

    legend_y = 735
    legend = [
        ("win", "CI-clear V4 win"),
        ("uncertain", "95% CI crosses 1"),
        ("loss", "CI-clear V4 loss"),
    ]
    x = 260
    for key, text_value in legend:
        draw.rectangle((x, legend_y, x + 32, legend_y + 32), fill=colors[key])
        draw.text((x + 45, legend_y + 1), text_value, fill="#26313A", font=regular(23))
        x += 455

    draw.text(
        (70, 835),
        "Source: Goal5785 raw-worker reconstruction and Goal5787 claim matrix. Hardware scope: one RTX 4000 Ada (CC 8.9).",
        fill="#59636D",
        font=regular(19),
    )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT, format="PNG", optimize=True)


if __name__ == "__main__":
    main()
