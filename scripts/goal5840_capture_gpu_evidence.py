#!/usr/bin/env python3
"""Capture Goal5840's four exact-mode true-OptiX evidence bundles."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
from typing import Mapping

from rtdsl.v4_callback_lifecycle import V4Target, V4Toolchain
from rtdsl.v4_sphere_any_hit_count import V4SphereTarget
from rtdsl.v4_target_evidence_capture import capture_real_target_evidence_bundle
from scripts.goal5840_gpu_cases import goal5840_mode_cases


ROOT = Path(__file__).resolve().parents[1]
GOAL_ROOT = (
    ROOT
    / "history/internal_docs/goal5840_independent_lowering_refinement_20260903"
)
PREREGISTRATION = GOAL_ROOT / "GOAL5840_PREREGISTRATION.json"
PRE_POD_AUTHORITY = GOAL_ROOT / "PRE_POD_INPUT_AUTHORITY.json"
CHECKER = ROOT / "scripts/goal5840_independent_target_checker.py"
MUTATION_RUNNER = ROOT / "scripts/goal5840_mutation_suite.py"
SUMMARY_DOMAIN = b"rtdl.goal5840.true_optix_target_evidence.v1\0"
TRUST_ROOT_DOMAIN = b"rtdl.goal5840.runtime_trust_roots.v1\0"
NATIVE_BUILD_DOMAIN = b"rtdl.goal5838.selected_sphere_optix_provider_build.v2\0"
GOAL5840_REQUIRED_NATIVE_SYMBOLS = (
    "rtdl_optix_get_version",
    "rtdl_optix_traversal_audit_abort",
    "rtdl_optix_traversal_audit_begin",
    "rtdl_optix_traversal_audit_finish",
    "rtdl_optix_v4_checked_u64_product_sum_host_v1",
    "rtdl_optix_v4_describe_prepared_builtin_sphere_callback_v1",
    "rtdl_optix_v4_destroy_prepared_bounded_relation_callback_v1",
    "rtdl_optix_v4_destroy_prepared_builtin_sphere_callback_v1",
    "rtdl_optix_v4_destroy_prepared_triangle_reduction_callback_v1",
    "rtdl_optix_v4_execute_prepared_bounded_relation_callback_v3",
    "rtdl_optix_v4_execute_prepared_builtin_sphere_callback_v1",
    "rtdl_optix_v4_execute_prepared_triangle_reduction_callback_v2",
    "rtdl_optix_v4_prepare_bounded_relation_callback_v1",
    "rtdl_optix_v4_prepare_builtin_sphere_callback_v1",
    "rtdl_optix_v4_prepare_triangle_reduction_callback_v1",
    "rtdl_optix_v4_rtdlexe_producer_descriptor_v1",
    "rtdl_optix_v4_runtime_compiler_attempt_count_v1",
)
NATIVE_BUILD_SOURCE_PATHS = frozenset({
    "scripts/goal5838_build_selected_sphere_optix_provider.py",
    "src/native/rtdl_optix.cpp",
    "src/native/optix/rtdl_optix_prelude.h",
    "src/native/optix/rtdl_optix_core.cpp",
    "src/native/optix/rtdl_optix_v4_callback_poc.cpp",
    "src/native/optix/rtdl_optix_api.cpp",
    "src/native/optix/rtdl_optix_v4_particle_template.h",
    "src/native/optix/rtdl_optix_v4_product_status.h",
    "src/native/optix/rtdl_optix_workloads.cpp",
    "src/native/optix/rtdl_optix_cuda_helpers.cu",
})
SOURCE_PATHS = (
    "scripts/goal5840_capture_gpu_evidence.py",
    "scripts/goal5840_freeze_gpu_inputs.py",
    "scripts/goal5840_gpu_cases.py",
    "scripts/goal5840_independent_target_checker.py",
    "scripts/goal5840_mutation_suite.py",
    "scripts/goal5840_verify_gpu_evidence.py",
    "src/rtdsl/v4_target_control_flow_evidence.py",
    "src/rtdsl/v4_target_evidence_bundle.py",
    "src/rtdsl/v4_target_evidence_capture.py",
    "history/internal_docs/goal5840_independent_lowering_refinement_20260903/"
    "GOAL5840_PREREGISTRATION.json",
    "history/internal_docs/goal5840_independent_lowering_refinement_20260903/"
    "PRE_POD_INPUT_AUTHORITY.json",
)


def _canonical(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _jsonable(value: object) -> object:
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    return value


def _git(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=ROOT, text=True, capture_output=True, check=False
    )
    if completed.returncode:
        raise RuntimeError(f"git {' '.join(args)}: {completed.stderr.strip()}")
    return completed.stdout.strip()


def _repository_custody(expected_commit: str) -> dict[str, object]:
    if len(expected_commit) != 40 or any(
        character not in "0123456789abcdef" for character in expected_commit
    ):
        raise RuntimeError("--expected-commit must be one full lowercase commit")
    if _git("rev-parse", "HEAD") != expected_commit:
        raise RuntimeError("checkout does not equal --expected-commit")
    if _git("status", "--porcelain=v1", "--untracked-files=all"):
        raise RuntimeError("GPU capture requires a clean Git worktree")
    rows = []
    for relative in SOURCE_PATHS:
        path = ROOT / relative
        working = path.read_bytes()
        committed = subprocess.run(
            ["git", "show", f"{expected_commit}:{relative}"],
            cwd=ROOT,
            capture_output=True,
            check=True,
        ).stdout
        if working != committed:
            raise RuntimeError(f"working source differs from commit: {relative}")
        rows.append({
            "path": relative,
            "bytes": len(working),
            "sha256": hashlib.sha256(working).hexdigest(),
        })
    return {
        "expected_commit": expected_commit,
        "head_before": expected_commit,
        "branch": _git("branch", "--show-current"),
        "origin": _git("remote", "get-url", "origin"),
        "clean_before": True,
        "source_files": rows,
    }


def _finish_repository_custody(
    before: dict[str, object], expected_commit: str
) -> dict[str, object]:
    if _git("rev-parse", "HEAD") != expected_commit or _git(
        "status", "--porcelain=v1", "--untracked-files=all"
    ):
        raise RuntimeError("repository changed during GPU capture")
    return {**before, "head_after": expected_commit, "clean_after": True}


def _outside_repository(path: Path) -> Path:
    result = path.expanduser().resolve()
    if result == ROOT or ROOT in result.parents:
        raise RuntimeError("GPU evidence output must be outside the Git tree")
    if result.exists():
        raise FileExistsError(result)
    result.mkdir(parents=True)
    return result


def _machine() -> dict[str, object]:
    completed = subprocess.run(
        [
            "nvidia-smi",
            "--id=0",
            "--query-gpu=name,uuid,driver_version,pci.bus_id,compute_cap,memory.total",
            "--format=csv,noheader,nounits",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        raise RuntimeError(f"nvidia-smi failed: {completed.stderr.strip()}")
    rows = [
        [part.strip() for part in line.split(",")]
        for line in completed.stdout.splitlines()
        if line.strip()
    ]
    if len(rows) != 1 or len(rows[0]) != 6:
        raise RuntimeError(f"one selected GPU required: {rows!r}")
    return dict(zip(
        ("name", "uuid", "driver", "pci_bus_id", "compute_capability", "memory_mib"),
        rows[0],
        strict=True,
    ))


def _verify_frozen_core() -> dict[str, object]:
    seal_path = (
        ROOT
        / "history/internal_docs/goal5838_generic_core_exam_20260902/"
        "GENERIC_CORE_SEAL.json"
    )
    seal = json.loads(seal_path.read_text(encoding="ascii"))
    rows = []
    for row in seal["frozen_core_files"]:
        path = ROOT / row["path"]
        observed = _sha_file(path)
        if observed != row["sha256"]:
            raise RuntimeError(f"Goal5838 frozen core changed: {row['path']}")
        rows.append({
            "path": row["path"],
            "bytes": path.stat().st_size,
            "sha256": observed,
        })
    return {
        "seal_sha256": seal["seal_sha256"],
        "files": rows,
        "changed_file_count": 0,
    }


def _verify_pre_pod_authority() -> dict[str, object]:
    authority = json.loads(PRE_POD_AUTHORITY.read_text(encoding="ascii"))
    body = dict(authority)
    observed = body.pop("authority_sha256", None)
    body["authority_sha256"] = ""
    expected = hashlib.sha256(
        b"rtdl.goal5840.pre_pod_input_authority.v1\0" + _canonical(body)
    ).hexdigest()
    if observed != expected:
        raise RuntimeError("pre-pod input authority seal differs")
    if (
        authority.get("schema")
        != "rtdl.goal5840.pre_pod_input_authority.v1"
        or authority.get("stage") != "BEFORE_ANY_GOAL5840_GPU_EXECUTION"
        or authority.get("required_mode_count") != 4
        or authority.get("route_bundle_group_count") != 3
        or authority.get("execution_counts_at_freeze")
        != {
            "goal5840_gpu_launches": 0,
            "goal5840_positive_target_bundles": 0,
            "goal5840_exact_bundle_mutations": 0,
        }
    ):
        raise RuntimeError("pre-pod input authority contract differs")
    source_rows = authority.get("source_files")
    if not isinstance(source_rows, list):
        raise RuntimeError("pre-pod input authority source inventory is absent")
    for row in source_rows:
        if not isinstance(row, dict):
            raise RuntimeError("pre-pod source inventory row is invalid")
        path = ROOT / str(row.get("path"))
        if (
            not path.is_file()
            or path.stat().st_size != row.get("bytes")
            or _sha_file(path) != row.get("sha256")
        ):
            raise RuntimeError(f"pre-pod source changed: {row.get('path')}")
    return authority


def _verify_native_build(path: Path, native: Path, expected_commit: str) -> dict[str, object]:
    manifest_path = path.expanduser().resolve(strict=True)
    document = json.loads(manifest_path.read_text(encoding="ascii"))
    repository = document.get("repository")
    output = document.get("native_output")
    if not isinstance(repository, dict) or not isinstance(output, dict):
        raise RuntimeError("native build manifest is incomplete")
    body = dict(document)
    observed_result_sha256 = body.get("result_sha256")
    body["result_sha256"] = ""
    if observed_result_sha256 != hashlib.sha256(
        NATIVE_BUILD_DOMAIN + _canonical(body)
    ).hexdigest():
        raise RuntimeError("native build manifest seal differs")
    build_input = document.get("build_input")
    source_rows = repository.get("source_files")
    if not isinstance(build_input, dict) or not isinstance(source_rows, list):
        raise RuntimeError("native build input/source custody is incomplete")
    observed_sources = set()
    for row in source_rows:
        if not isinstance(row, dict) or not isinstance(row.get("path"), str):
            raise RuntimeError("native build source row is invalid")
        relative = str(row["path"])
        source = ROOT / relative
        if (
            relative in observed_sources
            or not source.is_file()
            or source.stat().st_size != row.get("bytes")
            or _sha_file(source) != row.get("sha256")
        ):
            raise RuntimeError(f"native build source custody differs: {relative}")
        observed_sources.add(relative)
    if (
        observed_sources != NATIVE_BUILD_SOURCE_PATHS
        or document.get("build_input_sha256") != _digest(build_input)
        or build_input.get("builder_path")
        != "scripts/goal5838_build_selected_sphere_optix_provider.py"
        or build_input.get("builder_sha256")
        != _sha_file(ROOT / str(build_input["builder_path"]))
    ):
        raise RuntimeError("native build source/input identity differs")
    if (
        document.get("schema")
        != "rtdl.goal5838.selected_sphere_optix_provider_build.v2"
        or document.get("status")
        != "PASS__FRESH_PROVIDER_DSO_AND_REQUIRED_ABI_EXPORTED"
        or document.get("all_required_symbols_exported") is not True
        or repository.get("expected_commit") != expected_commit
        or repository.get("head_before") != expected_commit
        or repository.get("head_after") != expected_commit
        or output.get("sha256") != _sha_file(native)
        or output.get("bytes") != native.stat().st_size
        or Path(str(output.get("path"))).resolve() != native
    ):
        raise RuntimeError("native build manifest does not bind commit/DSO")
    return {
        "path": str(manifest_path),
        "bytes": manifest_path.stat().st_size,
        "sha256": _sha_file(manifest_path),
        "schema": document.get("schema"),
        "status": document.get("status"),
        "result_sha256": document.get("result_sha256"),
    }


def _verify_goal5840_native_symbols(native: Path) -> dict[str, object]:
    nm = shutil.which("nm")
    if nm is None:
        raise RuntimeError("nm is required for Goal5840 native ABI verification")
    completed = subprocess.run(
        [nm, "-D", "-g", "--defined-only", str(native)],
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        raise RuntimeError(f"Goal5840 nm check failed: {completed.stderr.strip()}")
    names = sorted({
        line.split()[-1]
        for line in completed.stdout.splitlines()
        if line.split()
    })
    missing = [
        symbol for symbol in GOAL5840_REQUIRED_NATIVE_SYMBOLS
        if symbol not in names
    ]
    if missing:
        raise RuntimeError(f"Goal5840 native ABI symbols are missing: {missing}")
    return {
        "schema": "rtdl.goal5840.required_native_symbols.v1",
        "method": "gnu_nm_dynamic_external_defined_exact_name",
        "required_symbols": list(GOAL5840_REQUIRED_NATIVE_SYMBOLS),
        "all_required_symbols_exported": True,
        "exported_symbol_count": len(names),
        "exported_symbol_names_sha256": _digest(names),
        "nm_path": str(Path(nm).resolve()),
    }


def _write_exclusive(path: Path, value: object) -> None:
    with path.open("x", encoding="ascii") as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True))
        stream.write("\n")


def _progress(stage: str, **fields: object) -> None:
    print(json.dumps({"stage": stage, **fields}, sort_keys=True), flush=True)


def _run_checker(
    bundle_path: Path,
    report_path: Path,
    roots: Mapping[str, str],
) -> dict[str, object]:
    completed = subprocess.run(
        [
            sys.executable,
            "-I",
            str(CHECKER),
            str(bundle_path),
            "--trusted-declaration-sha256",
            roots["declaration_sha256"],
            "--trusted-executable-identity-sha256",
            roots["executable_identity_sha256"],
            "--trusted-control-flow-manifest-sha256",
            roots["control_flow_manifest_sha256"],
            "--output",
            str(report_path),
        ],
        cwd=ROOT,
        env={"PATH": os.environ.get("PATH", "")},
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        raise RuntimeError(
            f"independent checker rejected {bundle_path.name}: "
            f"{completed.stdout}\n{completed.stderr}"
        )
    report = json.loads(report_path.read_text(encoding="ascii"))
    if report.get("verdict") != "ACCEPT" or report.get("pass_count") != 5:
        raise RuntimeError(f"independent checker result differs: {report}")
    return report


def _mode_file_stem(index: int, mode: str) -> str:
    return f"mode_{index:02d}_{mode}"


def run(args: argparse.Namespace) -> dict[str, object]:
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "0":
        raise RuntimeError("CUDA_VISIBLE_DEVICES=0 is required")
    output = _outside_repository(args.output)
    _progress("preflight_started", output=str(output))
    repository = _repository_custody(args.expected_commit)
    frozen_core = _verify_frozen_core()
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="ascii"))
    input_authority = _verify_pre_pod_authority()
    frozen_preregistration = input_authority.get("preregistration")
    if (
        not isinstance(frozen_preregistration, dict)
        or frozen_preregistration.get("file_sha256")
        != _sha_file(PREREGISTRATION)
        or frozen_preregistration.get("authority_sha256")
        != preregistration.get("authority_sha256")
    ):
        raise RuntimeError("live preregistration differs from pre-pod authority")
    native = args.native.expanduser().resolve(strict=True)
    native_build = _verify_native_build(
        args.native_build_manifest, native, args.expected_commit
    )
    native_symbols = _verify_goal5840_native_symbols(native)
    machine = _machine()
    _progress(
        "preflight_passed",
        gpu=machine["name"],
        compute_capability=machine["compute_capability"],
        native_sha256=_sha_file(native),
    )
    if machine["compute_capability"] != args.compute_capability:
        raise RuntimeError("selected GPU compute capability differs from argument")
    capability = tuple(int(item) for item in args.compute_capability.split("."))
    if len(capability) != 2:
        raise RuntimeError("compute capability must have major.minor form")
    toolchain = V4Toolchain.current(
        compute_capability=capability,
        optix_include=args.optix_include.expanduser().resolve(strict=True),
        cuda_include=args.cuda_include.expanduser().resolve(strict=True),
    )
    stable_target = V4Target.from_native(
        native,
        optix_sdk=args.optix_sdk,
        compute_capability=args.compute_capability,
    )
    sphere_target = V4SphereTarget.from_native(
        native,
        optix_sdk=args.optix_sdk,
        compute_capability=args.compute_capability,
    )
    expected_by_key = {
        row["key"]: row for row in input_authority["mode_cases"]
    }
    if len(expected_by_key) != 4:
        raise RuntimeError("pre-pod authority has duplicate or missing mode keys")
    bundles = []
    bundle_paths = []
    mode_records = []
    trust_roots: dict[str, dict[str, str]] = {}
    declaration_authority = str(preregistration["authority_sha256"])

    for index, case in enumerate(goal5840_mode_cases(), start=1):
        _progress("mode_started", index=index, key=case.key)
        frozen = expected_by_key.get(case.key)
        if not isinstance(frozen, dict):
            raise RuntimeError(f"mode absent from pre-pod authority: {case.key}")
        if frozen.get("plan_sha256") != case.route.plan.plan_sha256:
            raise RuntimeError(f"mode plan differs from pre-pod authority: {case.key}")
        fixture_sha256 = _digest(_jsonable(case.fixture_document))
        expected_output = _jsonable(case.expected_output)
        expected_output_sha256 = _digest(expected_output)
        if (
            frozen.get("fixture_sha256") != fixture_sha256
            or frozen.get("expected_output_sha256") != expected_output_sha256
            or frozen.get("expected_output") != expected_output
        ):
            raise RuntimeError(
                f"fixture/oracle differs from pre-pod authority: {case.key}"
            )
        target = sphere_target if case.target_kind == "sphere" else stable_target
        program = case.route.compile()
        materialized = program.materialize(target=target, toolchain=toolchain)
        prepared = materialized.prepare(case.static_input)
        try:
            result = prepared.execute(case.batch)
            observed_output = _jsonable(result.output)
            if observed_output != expected_output:
                raise RuntimeError(
                    f"output mismatch for {case.key}: "
                    f"{observed_output!r} != {expected_output!r}"
                )
            bundle = capture_real_target_evidence_bundle(
                route_id=case.route_id,
                mode=case.mode,
                route=case.route,
                program=program,
                materialized=materialized,
                result=result,
                target=target,
                toolchain=toolchain,
                declaration_authority_sha256=declaration_authority,
                repository_root=ROOT,
            )
        finally:
            prepared.close()
            prepared.close()

        if bundle["declaration"]["declaration_sha256"] != frozen.get(
            "declaration_sha256"
        ) or bundle["physical_evidence"]["target_control_flow_evidence"][
            "manifest_sha256"
        ] != frozen.get("control_flow_manifest_sha256"):
            raise RuntimeError(f"pre-pod trust root differs for {case.key}")
        stem = _mode_file_stem(index, case.mode)
        bundle_path = output / f"{stem}_bundle.json"
        checker_path = output / f"{stem}_independent_check.json"
        _write_exclusive(bundle_path, bundle)
        roots = {
            "declaration_sha256": bundle["declaration"]["declaration_sha256"],
            "executable_identity_sha256": bundle["physical_evidence"][
                "executable_identity"
            ]["identity_sha256"],
            "control_flow_manifest_sha256": bundle["physical_evidence"][
                "target_control_flow_evidence"
            ]["manifest_sha256"],
        }
        checker_report = _run_checker(bundle_path, checker_path, roots)
        _progress(
            "mode_passed",
            index=index,
            key=case.key,
            bundle_sha256=bundle["bundle_sha256"],
            independent_property_pass_count=checker_report["pass_count"],
        )
        trust_roots[case.key] = roots
        bundles.append(bundle)
        bundle_paths.append(bundle_path)
        mode_records.append({
            "key": case.key,
            "route_id": case.route_id,
            "mode": case.mode,
            "fixture_sha256": fixture_sha256,
            "expected_output": expected_output,
            "expected_output_sha256": _digest(expected_output),
            "observed_output": observed_output,
            "observed_output_sha256": result.output_sha256,
            "bundle_file": bundle_path.name,
            "bundle_sha256": bundle["bundle_sha256"],
            "independent_check_file": checker_path.name,
            "independent_check_sha256": checker_report["report_sha256"],
            "independent_property_pass_count": checker_report["pass_count"],
            "true_optix": (
                result.traversal_receipt.get("physical_executor_classification")
                == "optix_traversal_observed"
            ),
        })

    trust_document: dict[str, object] = {
        "schema": "rtdl.goal5840.runtime_trust_roots.v1",
        "source": (
            "captured_from_live_generic_lifecycle_objects_before_bundle_"
            "independent_check; capture_runner_remains_in_tcb"
        ),
        "trust_roots": trust_roots,
        "claim_boundary": {
            "pre_pod_declaration_and_control_roots": True,
            "post_materialization_executable_identity_root": True,
            "independent_hardware_attestation": False,
        },
        "trust_roots_sha256": "",
    }
    trust_document["trust_roots_sha256"] = hashlib.sha256(
        TRUST_ROOT_DOMAIN + _canonical(trust_document)
    ).hexdigest()
    trust_path = output / "RUNTIME_TRUST_ROOTS.json"
    _write_exclusive(trust_path, trust_document)

    mutation_path = output / "EXACT_BUNDLE_MUTATION_RESULT.json"
    mutation_command = [
        sys.executable,
        str(MUTATION_RUNNER),
        "--trust-roots",
        str(trust_path),
        "--output",
        str(mutation_path),
    ]
    for bundle_path in bundle_paths:
        mutation_command.extend(("--bundle", str(bundle_path)))
    mutation = subprocess.run(
        mutation_command,
        cwd=ROOT,
        env={**os.environ, "PYTHONPATH": "src:."},
        text=True,
        capture_output=True,
        check=False,
    )
    if mutation.returncode:
        raise RuntimeError(
            f"exact bundle mutation suite failed: {mutation.stdout}\n{mutation.stderr}"
        )
    mutation_report = json.loads(mutation_path.read_text(encoding="ascii"))
    _progress(
        "mutation_suite_passed",
        unique_claim_units=mutation_report["preregistered_claim_unit_count"],
        mode_replications=mutation_report["mode_replication_application_count"],
    )
    repository = _finish_repository_custody(repository, args.expected_commit)
    summary: dict[str, object] = {
        "schema": "rtdl.goal5840.true_optix_target_evidence.v1",
        "status": "PASS__FOUR_MODES_TRUE_OPTIX_AND_15_UNIQUE_MUTATIONS_REJECTED",
        "repository": repository,
        "machine": machine,
        "runtime": {
            "python": platform.python_version(),
            "python_executable": sys.executable,
            "numba": importlib.metadata.version("numba"),
            "numpy": importlib.metadata.version("numpy"),
            "cuda_visible_devices": os.environ["CUDA_VISIBLE_DEVICES"],
            "optix_sdk": args.optix_sdk,
            "compute_capability": args.compute_capability,
            "optix_include": str(toolchain.optix_include),
            "cuda_include": str(toolchain.cuda_include),
        },
        "native": {
            "path": str(native),
            "bytes": native.stat().st_size,
            "sha256": _sha_file(native),
            "build_manifest": native_build,
            "goal5840_required_symbol_check": native_symbols,
        },
        "preregistration": {
            "path": str(PREREGISTRATION.relative_to(ROOT)),
            "file_sha256": _sha_file(PREREGISTRATION),
            "authority_sha256": preregistration["authority_sha256"],
        },
        "pre_pod_input_authority": {
            "path": str(PRE_POD_AUTHORITY.relative_to(ROOT)),
            "file_sha256": _sha_file(PRE_POD_AUTHORITY),
            "authority_sha256": input_authority["authority_sha256"],
        },
        "frozen_core": frozen_core,
        "route_bundle_group_count": 3,
        "required_mode_bundle_count": len(mode_records),
        "true_optix_mode_count": sum(row["true_optix"] for row in mode_records),
        "independent_property_pass_count": sum(
            int(row["independent_property_pass_count"]) for row in mode_records
        ),
        "preregistered_unique_mutation_count": mutation_report[
            "preregistered_claim_unit_count"
        ],
        "mode_replication_mutation_count": mutation_report[
            "mode_replication_application_count"
        ],
        "mode_cases": mode_records,
        "runtime_trust_roots_file": trust_path.name,
        "runtime_trust_roots_sha256": trust_document["trust_roots_sha256"],
        "mutation_result_file": mutation_path.name,
        "mutation_result_sha256": mutation_report["report_sha256"],
        "claim_boundary": {
            "three_bounded_routes_only": True,
            "four_required_modes": True,
            "target_side_structural_refinement_evidence": True,
            "general_compiler_soundness": False,
            "application_correctness": False,
            "performance_or_speedup": False,
            "external_review_or_consensus": False,
        },
        "summary_sha256": "",
    }
    if (
        summary["required_mode_bundle_count"] != 4
        or summary["true_optix_mode_count"] != 4
        or summary["independent_property_pass_count"] != 20
        or summary["preregistered_unique_mutation_count"] != 15
        or summary["mode_replication_mutation_count"] != 20
    ):
        raise RuntimeError("Goal5840 positive/mutation denominator differs")
    summary["summary_sha256"] = hashlib.sha256(
        SUMMARY_DOMAIN + _canonical(summary)
    ).hexdigest()
    _write_exclusive(output / "RESULT.json", summary)
    _progress("capture_passed", summary_sha256=summary["summary_sha256"])
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--native-build-manifest", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--compute-capability", required=True)
    parser.add_argument("--optix-sdk", required=True)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(args)
    print(json.dumps({
        "status": result["status"],
        "summary_sha256": result["summary_sha256"],
        "output": str(args.output.expanduser().resolve() / "RESULT.json"),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
