from __future__ import annotations

from pathlib import Path
import argparse
import sys


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "docs" / "rtdl_primitive_catalog.md"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate the RTDL primitive catalog from Python hierarchy nodes.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true", help="Fail if the output file differs from generated content.")
    args = parser.parse_args(argv)

    sys.path[:0] = [str(ROOT / "src"), str(ROOT)]
    from rtdsl.primitive_catalog import render_primitive_catalog_markdown

    output_path = args.output if args.output.is_absolute() else ROOT / args.output
    rendered = render_primitive_catalog_markdown()
    if args.check:
        current = output_path.read_text(encoding="utf-8") if output_path.exists() else ""
        if current != rendered:
            print(f"primitive catalog drift detected: {output_path}", file=sys.stderr)
            return 1
        print(f"primitive catalog up to date: {output_path}")
        return 0

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered, encoding="utf-8", newline="\n")
    print(f"wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
