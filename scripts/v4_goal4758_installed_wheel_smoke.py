#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WHEEL = ROOT / "dist" / "goal4758_v4_release_candidate" / "rtdl_source_tree-4.0.0-py3-none-any.whl"
DEFAULT_OUT_DIR = ROOT / "future" / "v4" / "evidence" / "v4_goal4758_wheel_install_smoke_2026-06-26"


SMOKE_CODE = r"""
import json
import rtdsl.v4 as v4

boundary = v4.claim_boundary_v4()
component_union = v4.plan_operator_request_v4("component_union", partner="numba")
grouped_sum = v4.plan_operator_request_v4("grouped_vector_sum_f64x2", partner="cupy")
payload = {
    "status": "ok",
    "front_door_status": boundary["status"],
    "matrix_apps": boundary["complete_rt_core_app_matrix_app_count"],
    "matrix_rows": boundary["complete_rt_core_app_matrix_row_count"],
    "measured_partners": boundary["measured_partners"],
    "formal_release_authorized": boundary["formal_release_authorized"],
    "numba_component_union_status": component_union.status,
    "numba_component_union_surface": component_union.api_surface,
    "cupy_grouped_vector_sum_status": grouped_sum.status,
    "cupy_grouped_vector_sum_surface": grouped_sum.api_surface,
}
print(json.dumps(payload, sort_keys=True))
"""


def _run(command: list[str], *, cwd: Path, stdout: Path, stderr: Path) -> int:
    proc = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    stdout.write_text(proc.stdout, encoding="utf-8")
    stderr.write_text(proc.stderr, encoding="utf-8")
    return proc.returncode


def _render_report(summary: dict[str, Any]) -> str:
    lines = [
        "# V4 Goal4758 Installed Wheel Smoke",
        "",
        f"Status: `{summary['status']}`",
        "",
        "This smoke validates the current V4.0 wheel from an installed package path.",
        "It is intentionally no-CUDA: it checks the public V4 front door and planner",
        "boundary after wheel installation rather than source-tree imports.",
        "",
        "## Result",
        "",
        f"- wheel: `{summary['wheel']}`",
        f"- install status: `{summary['install_status']}`",
        f"- smoke status: `{summary['smoke_status']}`",
        f"- venv removed: `{summary['venv_removed']}`",
        f"- matrix apps: `{summary.get('matrix_apps')}`",
        f"- matrix rows: `{summary.get('matrix_rows')}`",
        f"- measured partners: `{', '.join(summary.get('measured_partners', []))}`",
        f"- CuPy grouped-vector-sum plan: `{summary.get('cupy_grouped_vector_sum_status')}`",
        f"- Numba component-union plan: `{summary.get('numba_component_union_status')}`",
        "",
        "## Non-Authorization",
        "",
        "This smoke does not authorize public V4.0 tagging, broad speedup wording,",
        "blanket CuPy performance claims, arbitrary Numba callbacks, or true-zero-copy claims.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Install the V4 wheel into a temporary venv and smoke-test V4 front door.")
    parser.add_argument("--wheel", type=Path, default=DEFAULT_WHEEL)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--keep-venv", action="store_true")
    args = parser.parse_args()

    wheel = args.wheel.resolve()
    out_dir = args.out_dir.resolve()
    venv_dir = out_dir / ".venv"
    out_dir.mkdir(parents=True, exist_ok=True)
    if not wheel.exists():
        raise FileNotFoundError(wheel)
    if venv_dir.exists():
        shutil.rmtree(venv_dir)

    summary: dict[str, Any] = {
        "schema": "rtdl.v4.goal4758.installed_wheel_smoke.v1",
        "status": "started",
        "wheel": str(wheel),
        "out_dir": str(out_dir),
        "no_cuda_required": True,
        "release_authorized": False,
        "public_tag_authorized": False,
        "broad_speedup_claim_authorized": False,
    }

    create_rc = _run(
        [sys.executable, "-m", "venv", str(venv_dir)],
        cwd=ROOT,
        stdout=out_dir / "venv_create.stdout.txt",
        stderr=out_dir / "venv_create.stderr.txt",
    )
    summary["venv_create_returncode"] = create_rc
    if create_rc != 0:
        summary["status"] = "failed_venv_create"
    else:
        python = venv_dir / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
        install_rc = _run(
            [str(python), "-m", "pip", "install", "--force-reinstall", str(wheel)],
            cwd=ROOT,
            stdout=out_dir / "wheel_install_with_deps.log",
            stderr=out_dir / "wheel_install_with_deps.stderr.txt",
        )
        summary["install_returncode"] = install_rc
        summary["install_status"] = "passed" if install_rc == 0 else "failed"
        smoke_rc = 1
        smoke_payload: dict[str, Any] = {}
        if install_rc == 0:
            smoke_rc = _run(
                [str(python), "-c", SMOKE_CODE],
                cwd=ROOT,
                stdout=out_dir / "import_claim_boundary_after_install.log",
                stderr=out_dir / "import_claim_boundary_after_install.stderr.txt",
            )
            summary["smoke_returncode"] = smoke_rc
            smoke_text = (out_dir / "import_claim_boundary_after_install.log").read_text(encoding="utf-8").strip()
            if smoke_text:
                smoke_payload = json.loads(smoke_text.splitlines()[-1])
                summary.update(smoke_payload)
        summary["smoke_status"] = "passed" if smoke_rc == 0 and smoke_payload.get("status") == "ok" else "failed"
        summary["status"] = "passed" if summary["install_status"] == "passed" and summary["smoke_status"] == "passed" else "failed"

    if args.keep_venv:
        summary["venv_removed"] = False
    elif venv_dir.exists():
        shutil.rmtree(venv_dir)
        summary["venv_removed"] = not venv_dir.exists()
    else:
        summary["venv_removed"] = True

    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "summary.md").write_text(_render_report(summary), encoding="utf-8")
    print(out_dir / "summary.json")
    print(summary["status"])
    return 0 if summary["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
