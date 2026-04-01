from __future__ import annotations

from pathlib import Path

from rtdsl.rayjoin_artifacts import generate_goal22_artifacts


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    output_dir = ROOT / "build" / "goal22_reproduction"
    artifacts = generate_goal22_artifacts(output_dir)
    for key, path in artifacts.items():
        print(f"{key}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
