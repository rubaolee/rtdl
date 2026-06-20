#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import platform
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import run_test_matrix  # noqa: E402
from scripts.rtdl_source_tree_doctor import gather_checks  # noqa: E402


REPORT_ID = "v4_0_source_tree_runtime_preflight_2026-06-19"


def _git_value(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        return ""
    return completed.stdout.strip()


def _parse_pyproject() -> dict[str, object]:
    pyproject = ROOT / "pyproject.toml"
    text = pyproject.read_text(encoding="utf-8") if pyproject.exists() else ""

    def field(name: str) -> str:
        match = re.search(rf"^\s*{re.escape(name)}\s*=\s*\"([^\"]+)\"", text, re.MULTILINE)
        return match.group(1) if match else ""

    name = field("name")
    version = field("version")
    description = field("description")
    return {
        "path": pyproject.relative_to(ROOT).as_posix(),
        "exists": pyproject.exists(),
        "name": name,
        "version": version,
        "description": description,
        "source_tree_identity_ok": name == "rtdl-source-tree" and version == "3.0.2",
        "v4_distribution_artifact": False,
    }


def _import_smoke() -> dict[str, object]:
    try:
        import rtdsl  # type: ignore
    except Exception as exc:  # pragma: no cover - failure path is reported.
        return {
            "ok": False,
            "module": "rtdsl",
            "error_type": exc.__class__.__name__,
            "message": str(exc),
        }
    module_file = Path(getattr(rtdsl, "__file__", "") or "")
    return {
        "ok": True,
        "module": "rtdsl",
        "module_file": str(module_file),
        "from_checkout_src": SRC.resolve() in module_file.resolve().parents,
    }


def _check_by_name(doctor: dict[str, object]) -> dict[str, dict[str, object]]:
    checks = doctor.get("checks", [])
    return {str(item["name"]): item for item in checks if isinstance(item, dict) and "name" in item}


def _required_paths() -> list[dict[str, object]]:
    paths = (
        "docs/engineering/rtdl_v4_0_source_tree_runtime_story_2026-06-19.md",
        "docs/engineering/rtdl_v4_0_release_candidate_blockers_2026-06-19.json",
        "docs/engineering/rtdl_v4_0_m1_experimental_status_2026-06-19.md",
        "scripts/v4_0_m1_fixed_radius_cupy_stream_smoke.py",
        "scripts/v4_0_m1_fixed_radius_numba_partner_surface_probe.py",
        "scripts/v4_0_m1_fixed_radius_dlpack_capsule_probe.py",
        "scripts/v4_0_m1_fixed_radius_pytorch_cuda_tensor_probe.py",
        "scripts/v4_0_m1_linux_gpu_release_gate.py",
    )
    return [
        {
            "path": path,
            "exists": (ROOT / path).exists(),
        }
        for path in paths
    ]


def _gpu_runtime_checks(doctor: dict[str, object]) -> dict[str, object]:
    by_name = _check_by_name(doctor)
    names = {
        "cupy": "optional module cupy",
        "numba": "optional module numba",
        "torch": "optional module torch",
        "optix_library": "optional OptiX library",
    }
    details: dict[str, object] = {}
    for key, name in names.items():
        check = by_name.get(name, {})
        details[key] = {
            "status": check.get("status", "missing"),
            "detail": check.get("detail", ""),
            "passes": check.get("status") == "pass",
        }
    return {
        "checks": details,
        "all_required_for_v4_m1_gpu_runtime_present": all(
            bool(item["passes"]) for item in details.values() if isinstance(item, dict)
        ),
    }


def build_payload(*, require_v4_gpu_runtime: bool = False, run_smoke: bool = False) -> dict[str, object]:
    doctor = gather_checks(
        run_smoke=run_smoke,
        include_v4_active=True,
    )
    import_smoke = _import_smoke()
    pyproject = _parse_pyproject()
    paths = _required_paths()
    gpu_runtime = _gpu_runtime_checks(doctor)

    required_failures: list[dict[str, object]] = []
    if not pyproject["source_tree_identity_ok"]:
        required_failures.append(
            {
                "check": "pyproject source-tree identity",
                "message": "pyproject.toml must remain rtdl-source-tree 3.0.2 until a real V4 package flow exists",
            }
        )
    if not import_smoke["ok"] or not import_smoke.get("from_checkout_src"):
        required_failures.append(
            {
                "check": "source-tree import smoke",
                "message": "rtdsl must import from this checkout's src tree",
                "detail": import_smoke,
            }
        )
    missing_paths = [item for item in paths if not item["exists"]]
    if missing_paths:
        required_failures.append(
            {
                "check": "required V4 M1 source-tree runtime files",
                "missing": missing_paths,
            }
        )
    if doctor["required_failures"]:
        required_failures.append(
            {
                "check": "source-tree doctor required checks",
                "failures": doctor["required_failures"],
            }
        )
    if require_v4_gpu_runtime and not gpu_runtime["all_required_for_v4_m1_gpu_runtime_present"]:
        required_failures.append(
            {
                "check": "V4 M1 GPU runtime dependencies",
                "message": "CuPy, Numba, PyTorch, and the OptiX library must be present for this required GPU-runtime preflight",
                "details": gpu_runtime,
            }
        )

    payload = {
        "report_id": REPORT_ID,
        "status": "pass" if not required_failures else "fail",
        "ok": not required_failures,
        "date": "2026-06-19",
        "repo": str(ROOT),
        "git": {
            "head": _git_value("rev-parse", "HEAD"),
            "tree": _git_value("rev-parse", "HEAD^{tree}"),
        },
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "python": platform.python_version(),
        },
        "pyproject": pyproject,
        "source_tree_import_smoke": import_smoke,
        "source_tree_doctor": doctor,
        "v4_m1_gpu_runtime": gpu_runtime,
        "required_paths": paths,
        "test_matrix_policy": {
            "v4_active_group_present": "v4_active" in run_test_matrix.TEST_GROUPS,
            "v4_release_candidate_group_present": "v4_release_candidate" in run_test_matrix.TEST_GROUPS,
            "v4_release_candidate_gate_non_authorizing": True,
            "current_v4_gate": "v4_release_candidate",
        },
        "supported_source_tree_commands": [
            "PYTHONPATH=src:. python3 scripts/rtdl_source_tree_doctor.py --include-v4-active --json",
            "make build-optix",
            "PYTHONPATH=src:. python3 scripts/run_test_matrix.py --group v4_active",
            "PYTHONPATH=src:. python3 scripts/run_test_matrix.py --group v4_release_candidate",
            "PYTHONPATH=src:. python3 scripts/v4_0_m1_fixed_radius_numba_partner_surface_probe.py",
            "PYTHONPATH=src:. python3 scripts/v4_0_m1_fixed_radius_dlpack_capsule_probe.py",
            "PYTHONPATH=src:. python3 scripts/v4_0_m1_fixed_radius_pytorch_cuda_tensor_probe.py",
            "PYTHONPATH=src:. RTDL_OPTIX_LIBRARY=$PWD/build/librtdl_optix.so python3 scripts/v4_0_m1_linux_gpu_release_gate.py --benchmark-count 262144",
        ],
        "claim_boundaries": {
            "source_tree_runtime_wording_authorized": True,
            "v4_package_install_authorized": False,
            "pypi_authorized": False,
            "wheel_authorized": False,
            "stable_sdk_authorized": False,
            "generated_bindings_authorized": False,
            "v4_current_front_door_authorized": False,
        },
        "required_failures": required_failures,
    }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the V4.0 source-tree runtime preflight report.")
    parser.add_argument(
        "--output",
        default=f"docs/reports/{REPORT_ID}.json",
        help="report path relative to the repository root",
    )
    parser.add_argument(
        "--require-v4-gpu-runtime",
        action="store_true",
        help="fail unless CuPy, Numba, PyTorch, and the OptiX library are present",
    )
    parser.add_argument("--run-smoke", action="store_true", help="ask source-tree doctor to run its portable smoke")
    args = parser.parse_args()

    payload = build_payload(
        require_v4_gpu_runtime=args.require_v4_gpu_runtime,
        run_smoke=args.run_smoke,
    )
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
