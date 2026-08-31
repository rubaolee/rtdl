from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
EXPECTED = ROOT / "history/internal_docs/goal5757_frozen_v4_capability_vocabulary_20260811.json"


def main() -> None:
    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(ROOT / "src")
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/goal5757_introspect_frozen_v4_capability.py")],
        cwd=ROOT,
        env=environment,
        check=True,
        capture_output=True,
        text=True,
    )
    observed = json.loads(result.stdout)
    expected = json.loads(EXPECTED.read_text(encoding="utf-8"))
    if observed != expected:
        print(json.dumps({
            "schema": "rtdl.goal5757.capability_vocabulary_check.v1",
            "status": "FAIL_CLOSED__VOCABULARY_DRIFT",
            "expected": expected,
            "observed": observed,
        }, sort_keys=True, indent=2))
        raise SystemExit(1)
    print(json.dumps({
        "schema": "rtdl.goal5757.capability_vocabulary_check.v1",
        "status": "PASS",
        "callback_role_count": len(expected["callback_roles"]),
        "effect_kind_count": len(expected["effect_kinds"]),
        "geometry_family_count": len(expected["physical_schema"]["geometry_families"]),
        "canonical_template_count": len(expected["physical_schema"]["canonical_reference_templates"]),
        "closed_world_absence_count": len(expected["closed_world_absences"]),
    }, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
