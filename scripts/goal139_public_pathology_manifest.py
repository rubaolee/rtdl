from __future__ import annotations

import argparse
import json

import rtdsl as rt


def main() -> None:
    parser = argparse.ArgumentParser(description="Write Goal 139 public pathology dataset manifest.")
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    artifacts = rt.write_goal139_artifacts(args.output_dir)
    print(json.dumps({"artifacts": {key: str(value) for key, value in artifacts.items()}}, indent=2))


if __name__ == "__main__":
    main()
