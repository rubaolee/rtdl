"""Build deterministic, non-self-referential Goal5790-A1 evidence twins.

This packages only the six raw case records, their small audit inputs, the CPU
contract, the Home execution spec, and the independent verification tools.  It
does not package an expanded source tree, target native, cache cubin, or timing.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import tarfile

from goal5790_a1_independent_recount import (
    ACTUAL_ARMS,
    ADAPTED_RAW_SCHEMA,
    CASE_IDS,
    EXECUTED_INPUT_DELTA_BY_CASE,
    EXECUTION_CASE_SCHEMA,
    EXECUTION_SPEC_SCHEMA,
    POSTRUN_OBSERVATION_FIELDS,
    PRODUCT_RULE_BY_CASE_RULE,
    _expected_home_machine,
    _verify_controller_result,
    _verify_source_members,
    canonical_bytes,
    digest,
    expected_executed_input,
    home_toolchain_identity,
    recount,
    sha_file,
    safe_relative,
    strict_load,
    verify_cpu_suite,
    verify_execution_spec,
    verify_home_machine_authority,
)


MANIFEST_SCHEMA = "rtdl.goal5790_a1.evidence_manifest.v1"
BOUNDARY_SCHEMA = "rtdl.goal5790_a1.evidence_boundary.v1"
FORBIDDEN_SUFFIXES = {".cubin", ".fatbin", ".so", ".dll", ".dylib"}
DEFAULT_DIAGNOSTIC_ENTRYPOINT = "scripts/goal5790_a1_home_worker.py"
DEFAULT_PRODUCT_SOURCES = (
    "src/rtdsl/v4_semantic_physical_admission.py",
    "src/rtdsl/v4_semantically_admitted_compiler.py",
    "src/rtdsl/v4_typed_physical_schema.py",
)
PARTICLE_GATE_AUTHORITY = (
    "history/internal_docs/"
    "goal5790_a1_amendment_a1_particle_earliest_product_gate_20260816.md")
CONTROLLING_PLAN_AUTHORITY = (
    "history/internal_docs/goal5790_a1_rejected_program_suite_plan_20260816.md")
GOVERNANCE_AUTHORITIES = (
    (CONTROLLING_PLAN_AUTHORITY,
     "goal5790_a1_controlling_plan_authority"),
    (PARTICLE_GATE_AUTHORITY,
     "particle_earliest_product_gate_authority"),
)


def _safe_member(name: str) -> str:
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts or "." in path.parts \
            or "" in path.parts:
        raise ValueError(f"unsafe evidence member: {name!r}")
    lowered = {part.lower() for part in path.parts}
    if ".codex" in lowered:
        raise ValueError(f"private .codex member forbidden: {name}")
    if path.suffix.lower() in FORBIDDEN_SUFFIXES:
        raise ValueError(f"binary/cache payload forbidden: {name}")
    return path.as_posix()


def _json_bytes(value: object) -> bytes:
    return json.dumps(
        value, indent=2, sort_keys=True, ensure_ascii=True, allow_nan=False,
    ).encode("utf-8") + b"\n"


def _read_required(path: Path, label: str) -> bytes:
    if not path.is_file():
        raise FileNotFoundError(f"missing {label}: {path}")
    return path.read_bytes()


def _add(payloads: dict[str, bytes], name: str, data: bytes) -> None:
    member = _safe_member(name)
    if member in payloads:
        raise ValueError(f"duplicate evidence member: {member}")
    payloads[member] = data


def _seal(value: dict[str, object], field: str) -> dict[str, object]:
    result = json.loads(json.dumps(value, allow_nan=False))
    result.pop(field, None)
    result[field] = digest(result)
    return result


def _source_evidence_path(logical: str) -> str:
    return _safe_member("AUDIT/PRE_RUN_SOURCE/" + logical)


def capture_pre_run_case_authorities(
    *, cpu_suite: Path, native_library: Path, optix_sdk: str,
    compute_capability: str = "6.1",
) -> tuple[dict[str, dict[str, object]], str, dict[str, object]]:
    """Capture inert live-authority snapshots without compiling or launching.

    The private registry issuer remains inside the compiler/test classifier;
    this packaging tool receives only ``to_dict()`` snapshots.  Those snapshots
    cannot recreate a process-local authority and therefore cannot become a
    public bypass.
    """

    if compute_capability != "6.1":
        raise ValueError("Goal5790-A1 authority capture is Home CC6.1 only")
    suite_payload = strict_load(cpu_suite.resolve())
    if not isinstance(suite_payload, dict):
        raise ValueError("CPU suite must be an object")
    suite, cases = verify_cpu_suite(
        suite_payload, str(suite_payload.get("suite_sha256")))
    native_library = native_library.resolve()
    if not native_library.is_file():
        raise FileNotFoundError(native_library)
    # Import the test harness without importing ``rtdsl``.  Preseed a minimal
    # namespace before the first rtdsl submodule import so the broad package
    # initializer cannot eagerly load Numba, CUDA, or an OptiX runtime.
    from scripts.goal5790_a1_home_worker import (
        _forbidden_reject_imports,
        _install_test_only_rtdsl_namespace,
        _process_audit_snapshot,
        build_pre_run_case_authorities,
    )
    import sys
    before_names = set(sys.modules)
    before = _process_audit_snapshot()
    _install_test_only_rtdsl_namespace()
    from rtdsl.v4_typed_physical_schema import ReferenceTargetProfile

    target = ReferenceTargetProfile(
        provider="optix", optix_sdk=optix_sdk,
        compute_capability=compute_capability,
        native_sha256=sha_file(native_library),
        supports_custom_aabb=True, supports_builtin_triangle=True)
    snapshots = {
        case_id: build_pre_run_case_authorities(cases[case_id], target)
        for case_id in CASE_IDS
    }
    after_names = set(sys.modules)
    after = _process_audit_snapshot()
    imported = sorted(after_names - before_names)
    forbidden = list(_forbidden_reject_imports(imported))
    if forbidden or before["relevant_memory_maps"] \
            != after["relevant_memory_maps"]:
        raise RuntimeError(
            "pre-run authority capture imported a low-level GPU/compiler path")
    # The helper itself records all low-level counters as zero.  Check here as
    # well so a future helper expansion cannot silently turn authority capture
    # into execution.
    for case_id, snapshot in snapshots.items():
        if any(snapshot.get(field) != 0 for field in (
                "low_level_compiler_call_count", "native_prepare_call_count",
                "native_execute_call_count", "traversal_launch_count")):
            raise RuntimeError(
                f"pre-run authority capture executed work: {case_id}")
    audit: dict[str, object] = {
        "schema": "rtdl.goal5790_a1.pre_run_capture_audit.v1",
        "process_audit_before": before,
        "process_audit_after": after,
        "new_module_names": imported,
        "forbidden_low_level_imports": forbidden,
        "rtdsl_namespace_preseeded": "rtdsl" in imported,
        "broad_rtdsl_initializer_executed": False,
        "low_level_compiler_call_count": 0,
        "native_prepare_call_count": 0,
        "native_execute_call_count": 0,
        "traversal_launch_count": 0,
    }
    audit = _seal(audit, "audit_sha256")
    return snapshots, target.target_sha256, audit


def build_pre_run_execution_spec(
    *,
    cpu_suite: Path,
    home_authority: Path,
    repository_root: Path,
    scientific_identity: dict[str, object],
    case_authority_snapshots: dict[str, dict[str, object]],
    pre_run_capture_audit: dict[str, object],
    output_root: Path,
    diagnostic_entrypoint: str = DEFAULT_DIAGNOSTIC_ENTRYPOINT,
    product_sources: tuple[str, ...] = DEFAULT_PRODUCT_SOURCES,
) -> dict[str, object]:
    """Create the immutable execution authority before any Home arm runs.

    ``case_authority_snapshots`` must be captured from live compiler-owned
    authorities by the Home worker's inert pre-run helper.  This function does
    not compile a callback, prepare a native program, launch OptiX, or inspect
    a postrun result.  In particular, executable/program/receipt identities are
    deliberately absent from this authority.
    """

    cpu_suite = cpu_suite.resolve()
    home_authority = home_authority.resolve()
    repository_root = repository_root.resolve()
    output_root = output_root.resolve()
    if output_root.exists():
        raise FileExistsError("pre-run execution-spec root is create-only")
    suite_payload = strict_load(cpu_suite)
    if not isinstance(suite_payload, dict):
        raise ValueError("CPU suite must be an object")
    suite, cases = verify_cpu_suite(
        suite_payload, str(suite_payload.get("suite_sha256")))
    authority = verify_home_machine_authority(home_authority)
    if set(scientific_identity) != {
        "execution_source_archive_sha256", "execution_source_tree_sha256",
        "native_library_sha256", "target_provider", "optix_sdk",
        "compute_capability", "target_identity_sha256",
    }:
        raise ValueError("scientific identity shape mismatch")
    if scientific_identity["target_provider"] != "optix" \
            or scientific_identity["compute_capability"] != "6.1":
        raise ValueError("Goal5790-A1 pre-run spec is Home OptiX/CC6.1 only")

    if set(case_authority_snapshots) != set(CASE_IDS):
        raise ValueError("pre-run authority snapshots do not cover six cases")
    source_roles: dict[str, set[str]] = {}
    entrypoint = _safe_member(diagnostic_entrypoint)
    source_roles.setdefault(entrypoint, set()).update({
        "trusted_test_classifier", "diagnostic_entrypoint",
        "unsafe_transform_implementation", "unchecked_u64_kernel_source",
    })
    for logical in product_sources:
        source_roles.setdefault(_safe_member(logical), set()).add(
            "product_public_facade_source")
    snapshots: dict[str, dict[str, object]] = {}
    for case_id in CASE_IDS:
        raw_snapshot = case_authority_snapshots[case_id]
        snapshot = json.loads(json.dumps(raw_snapshot, allow_nan=False))
        snapshot.pop("snapshot_sha256", None)
        if snapshot.get("case_id") != case_id \
                or snapshot.get("case_sha256") != cases[case_id]["case_sha256"]:
            raise ValueError(f"pre-run authority case mismatch: {case_id}")
        if snapshot.get("classifier_source_sha256") \
                != sha_file(repository_root / entrypoint):
            raise ValueError("trusted classifier source changed during spec build")
        registry = snapshot.get("physical_registry")
        if not isinstance(registry, dict):
            raise ValueError(f"physical registry absent: {case_id}")
        for entry in registry.get("entries", []):
            guarantee = entry.get("guarantee") if isinstance(entry, dict) else None
            manifest = guarantee.get("source_manifest") \
                if isinstance(guarantee, dict) else None
            if not isinstance(manifest, dict) or not manifest:
                raise ValueError(f"registry source manifest absent: {case_id}")
            for logical in manifest:
                source_roles.setdefault(_safe_member(logical), set()).add(
                    "physical_guarantee_source")
        oracle_path = _safe_member(str(
            cases[case_id]["semantic_authority"]["oracle_source_path"]))
        if sha_file(repository_root / oracle_path) != cases[case_id][
                "semantic_authority"]["oracle_source_sha256"]:
            raise ValueError(f"semantic oracle source drift: {case_id}")
        source_roles.setdefault(oracle_path, set()).add(
            "independent_semantic_oracle")
        snapshots[case_id] = _seal(snapshot, "snapshot_sha256")

    output_root.mkdir(parents=True)
    source_rows: list[dict[str, object]] = []
    for logical in sorted(source_roles):
        source = repository_root / logical
        if not source.is_file():
            raise FileNotFoundError(f"pre-run source is absent: {logical}")
        evidence = _source_evidence_path(logical)
        destination = output_root / evidence
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(source.read_bytes())
        source_rows.append({
            "logical_path": logical,
            "evidence_path": evidence,
            "sha256": sha_file(source),
            "roles": sorted(source_roles[logical]),
        })

    home_evidence = output_root / "AUTHORITIES/HOME_MACHINE_AUTHORITY.json"
    home_evidence.parent.mkdir(parents=True, exist_ok=True)
    home_evidence.write_bytes(home_authority.read_bytes())
    governance_rows: list[dict[str, object]] = []
    for logical, role in GOVERNANCE_AUTHORITIES:
        governance_source = repository_root / logical
        if not governance_source.is_file():
            raise FileNotFoundError(f"governance authority is absent: {logical}")
        governance_evidence = "AUTHORITIES/" + Path(logical).name
        governance_destination = output_root / governance_evidence
        governance_destination.write_bytes(governance_source.read_bytes())
        governance_rows.append({
            "logical_path": logical,
            "evidence_path": governance_evidence,
            "sha256": sha_file(governance_source),
            "role": role,
        })
    cases_rows: list[dict[str, object]] = []
    for case_id in CASE_IDS:
        case = cases[case_id]
        case_row: dict[str, object] = {
            "schema": EXECUTION_CASE_SCHEMA,
            "case_id": case_id,
            "upstream_case_sha256": case["case_sha256"],
            "shared_case_identity": {
                "semantic_request_sha256": digest(case["semantic_authority"]),
                "input_sha256": digest(case["minimal_witness"]),
                "oracle_authority_sha256": digest(case["independent_oracle"]),
                "source_authority_sha256": case["source_authority"][
                    "authority_sha256"],
            },
            "pre_run_case_authorities": snapshots[case_id],
            "expected_product_rejection": {
                "verdict": "INCOMPATIBLE",
                "expected_rule_id": case["expected_rule_id"],
                "required_stable_product_rule_ids": [
                    PRODUCT_RULE_BY_CASE_RULE[case["expected_rule_id"]]],
                "executable": False,
                "execution_authorized": False,
            },
            "accepted_control_expected_disposition": (
                "FAIL_CLOSED_OVERFLOW" if case_id == CASE_IDS[2] else "VALUE"),
            "accepted_executed_input_sha256": digest(
                expected_executed_input(case, diagnostic=False)),
            "diagnostic_executed_input_sha256": digest(
                expected_executed_input(case, diagnostic=True)),
            "declared_executed_input_differences": list(
                EXECUTED_INPUT_DELTA_BY_CASE[case_id]),
            "allowed_postrun_observation_fields": list(
                POSTRUN_OBSERVATION_FIELDS),
        }
        cases_rows.append(_seal(case_row, "case_execution_spec_sha256"))

    diagnostic_sha = sha_file(repository_root / entrypoint)
    product_rows = [{
        "logical_path": logical,
        "evidence_path": _source_evidence_path(logical),
        "sha256": sha_file(repository_root / logical),
    } for logical in product_sources]
    spec: dict[str, object] = {
        "schema": EXECUTION_SPEC_SCHEMA,
        "upstream_suite_sha256": suite["suite_sha256"],
        "home_machine_authority_sha256": authority["receipt_sha256"],
        "home_machine_authority_file_sha256": sha_file(home_authority),
        "home_machine_authority_evidence_path":
            "AUTHORITIES/HOME_MACHINE_AUTHORITY.json",
        "home_toolchain_identity_sha256": home_toolchain_identity(authority),
        "cupy_version": "14.0.1",
        "scientific_identity": scientific_identity,
        "pre_run_capture_audit": json.loads(json.dumps(
            pre_run_capture_audit, allow_nan=False)),
        "pre_run_source_members": source_rows,
        "governance_authority_members": governance_rows,
        "case_count": len(cases_rows),
        "cases": cases_rows,
        "diagnostic_api_audit": {
            "diagnostic_entrypoint_path": entrypoint,
            "diagnostic_entrypoint_sha256": diagnostic_sha,
            "diagnostic_entrypoint_evidence_path": _source_evidence_path(
                entrypoint),
            "diagnostic_symbol": "diagnostic_builtin_program",
            "product_source_members": product_rows,
            "diagnostic_symbol_absent_from_product_api": True,
            "test_only_entrypoint_not_imported_by_product": True,
            "production_bypass_parameter_present": False,
        },
        "claim_boundary": {
            "home_only": True,
            "pod_authorized": False,
            "performance_timing_authorized": False,
            "performance_claimed": False,
            "formal_worker": False,
            "diagnostic_is_product_bypass": False,
        },
    }
    spec = _seal(spec, "execution_spec_sha256")
    spec_path = output_root / "HOME_EXECUTION_SPEC.json"
    spec_path.write_bytes(_json_bytes(spec))
    return {
        "execution_spec": spec,
        "execution_spec_path": spec_path.as_posix(),
        "execution_spec_file_sha256": sha_file(spec_path),
        "execution_spec_sha256": spec["execution_spec_sha256"],
        "source_member_count": len(source_rows),
    }


def _worker_filename(case_id: str, arm: str) -> str:
    slug = case_id.replace(".", "__").replace("-", "_")
    return f"{slug}__{arm}.json"


def adapt_controller_result(
    *, cpu_suite: Path, execution_spec: Path, pre_run_root: Path,
    controller_root: Path, expected_suite_sha256: str, output_root: Path,
) -> dict[str, object]:
    """Create strict manifests over the exact controller/worker bytes.

    The adapter does not manufacture an execution receipt.  It copies the
    exact sealed controller result and all 18 exact worker files, then emits
    six small manifests whose only job is to bind those original bytes to the
    pre-run case authorities.  The stdlib-only recount reopens and validates
    every original worker after this function returns.
    """

    cpu_suite = cpu_suite.resolve()
    execution_spec = execution_spec.resolve()
    pre_run_root = pre_run_root.resolve()
    controller_root = controller_root.resolve()
    output_root = output_root.resolve()
    resolved = {cpu_suite, execution_spec, pre_run_root, controller_root,
                output_root}
    if len(resolved) != 5:
        raise ValueError("adapter inputs/output must be distinct")
    if output_root.exists():
        raise FileExistsError("adapted evidence root is create-only")
    suite_payload = strict_load(cpu_suite)
    if not isinstance(suite_payload, dict):
        raise ValueError("CPU suite must be an object")
    suite, cases = verify_cpu_suite(suite_payload, expected_suite_sha256)
    spec_payload = strict_load(execution_spec)
    spec, spec_cases = verify_execution_spec(
        spec_payload, suite, cases, pre_run_root)
    source_members = _verify_source_members(
        spec["pre_run_source_members"], pre_run_root)
    authority_relative = safe_relative(
        spec["home_machine_authority_evidence_path"],
        "Home-machine authority evidence path")
    authority = verify_home_machine_authority(
        pre_run_root / authority_relative)
    expected_machine = _expected_home_machine(authority)
    controller_path = controller_root / "RESULT.json"
    controller_payload = strict_load(controller_path)
    controller, controller_cases = _verify_controller_result(
        controller_payload, suite=suite, spec=spec,
        suite_file_sha256=sha_file(cpu_suite),
        spec_file_sha256=sha_file(execution_spec),
        expected_home_machine=expected_machine)

    pending: dict[str, bytes] = {
        "AUTHORITIES/CPU_SUITE.json": cpu_suite.read_bytes(),
        "AUTHORITIES/HOME_EXECUTION_SPEC.json": execution_spec.read_bytes(),
        authority_relative: (pre_run_root / authority_relative).read_bytes(),
        "CONTROLLER/RESULT.json": controller_path.read_bytes(),
    }
    for row in spec["pre_run_source_members"]:
        relative = safe_relative(row["evidence_path"], "pre-run source path")
        pending[relative] = (pre_run_root / relative).read_bytes()
    for row in spec["governance_authority_members"]:
        relative = safe_relative(row["evidence_path"], "governance path")
        pending[relative] = (pre_run_root / relative).read_bytes()

    raw_manifests: dict[str, dict[str, object]] = {}
    for case_id in CASE_IDS:
        case = cases[case_id]
        case_spec = spec_cases[case_id]
        controller_case = controller_cases[case_id]
        worker_refs: dict[str, dict[str, object]] = {}
        for arm in ACTUAL_ARMS:
            filename = _worker_filename(case_id, arm)
            source = controller_root / "RAW" / filename
            if not source.is_file():
                raise FileNotFoundError(f"controller worker is absent: {source}")
            worker = strict_load(source)
            if worker != controller_case["arms"][arm]:
                raise ValueError(
                    f"controller nested worker differs from raw bytes: {case_id}/{arm}")
            relative = f"CONTROLLER/RAW/{filename}"
            pending[relative] = source.read_bytes()
            worker_refs[arm] = {
                "path": relative,
                "file_sha256": sha_file(source),
                "worker_result_sha256": worker.get("worker_result_sha256"),
                "parent_pid": worker.get("parent_pid"),
            }
        raw: dict[str, object] = {
            "schema": ADAPTED_RAW_SCHEMA,
            "status": "PASS",
            "upstream_suite_sha256": suite["suite_sha256"],
            "execution_spec_sha256": spec["execution_spec_sha256"],
            "case_id": case_id,
            "case_sha256": case["case_sha256"],
            "case_execution_spec_sha256": case_spec[
                "case_execution_spec_sha256"],
            "controller_result_path": "CONTROLLER/RESULT.json",
            "controller_result_file_sha256": sha_file(controller_path),
            "controller_result_sha256": controller["result_sha256"],
            "controller_case_sha256": digest(controller_case),
            "source_workers": worker_refs,
            "source_worker_set_sha256": digest(worker_refs),
        }
        raw = _seal(raw, "raw_result_sha256")
        raw_manifests[case_id] = raw
        pending[f"raw/{case_id}.json"] = _json_bytes(raw)

    output_root.mkdir(parents=True)
    for relative, data in sorted(pending.items()):
        destination = output_root / _safe_member(relative)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
    recount_result = recount(
        output_root / "AUTHORITIES/CPU_SUITE.json",
        output_root / "AUTHORITIES/HOME_EXECUTION_SPEC.json",
        output_root, expected_suite_sha256)
    return {
        "status": "PASS",
        "adapted_root": output_root.as_posix(),
        "upstream_suite_sha256": suite["suite_sha256"],
        "execution_spec_sha256": spec["execution_spec_sha256"],
        "controller_result_file_sha256": sha_file(controller_path),
        "controller_result_sha256": controller["result_sha256"],
        "case_count": len(raw_manifests),
        "worker_count": len(raw_manifests) * len(ACTUAL_ARMS),
        "recount_sha256": recount_result["recount_sha256"],
    }


def _collect_audit_files(raw_root: Path, execution_spec: dict,
                         raw_records: list[dict]) -> set[str]:
    result: set[str] = set()
    for row in execution_spec["pre_run_source_members"]:
        result.add(row["evidence_path"])
    for row in execution_spec["governance_authority_members"]:
        result.add(row["evidence_path"])
    api = execution_spec["diagnostic_api_audit"]
    result.add(api["diagnostic_entrypoint_evidence_path"])
    for row in api["product_source_members"]:
        result.add(row["evidence_path"])
    for raw in raw_records:
        if raw.get("schema") == ADAPTED_RAW_SCHEMA:
            result.add(raw["controller_result_path"])
            for row in raw["source_workers"].values():
                result.add(row["path"])
        else:
            for row in raw["product_admission_reject"]["raw_audit_artifacts"]:
                result.add(row["path"])
    for relative in result:
        _safe_member(relative)
        if not (raw_root / relative).is_file():
            raise FileNotFoundError(f"referenced audit file absent: {relative}")
    return result


def _tar_gz(payloads: dict[str, bytes]) -> tuple[bytes, dict[str, object]]:
    rows = [
        {"path": name, "sha256": hashlib.sha256(data).hexdigest(),
         "size_bytes": len(data)}
        for name, data in sorted(payloads.items())
    ]
    manifest: dict[str, object] = {
        "schema": MANIFEST_SCHEMA,
        "manifest_is_non_self_referential": True,
        "payload_count": len(rows),
        "payload_bytes": sum(row["size_bytes"] for row in rows),
        "payloads": rows,
    }
    manifest["manifest_sha256"] = digest(manifest)
    all_members = dict(payloads)
    all_members["MANIFEST.json"] = _json_bytes(manifest)

    tar_buffer = io.BytesIO()
    with tarfile.open(fileobj=tar_buffer, mode="w", format=tarfile.PAX_FORMAT) as archive:
        for name, data in sorted(all_members.items()):
            info = tarfile.TarInfo(name)
            info.size = len(data)
            info.mode = 0o644
            info.mtime = 0
            info.uid = 0
            info.gid = 0
            info.uname = ""
            info.gname = ""
            archive.addfile(info, io.BytesIO(data))
    compressed = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=compressed,
                       mtime=0, compresslevel=9) as stream:
        stream.write(tar_buffer.getvalue())
    return compressed.getvalue(), manifest


def _verify_archive(path: Path, expected_manifest: dict[str, object]) -> None:
    seen: set[str] = set()
    observed: dict[str, bytes] = {}
    with tarfile.open(path, "r:gz") as archive:
        for member in archive.getmembers():
            name = _safe_member(member.name)
            if name in seen:
                raise AssertionError(f"duplicate archive member: {name}")
            seen.add(name)
            if not member.isfile():
                raise AssertionError(f"non-regular archive member: {name}")
            stream = archive.extractfile(member)
            if stream is None:
                raise AssertionError(f"unreadable archive member: {name}")
            observed[name] = stream.read()
    if "MANIFEST.json" not in observed:
        raise AssertionError("archive manifest absent")
    manifest = json.loads(observed.pop("MANIFEST.json").decode("utf-8"))
    if manifest != expected_manifest:
        raise AssertionError("archive manifest bytes/semantics drift")
    unsigned = dict(manifest)
    claimed = unsigned.pop("manifest_sha256", None)
    if claimed != digest(unsigned):
        raise AssertionError("archive manifest digest mismatch")
    rows = manifest.get("payloads")
    if not isinstance(rows, list):
        raise AssertionError("archive manifest rows malformed")
    if manifest.get("payload_count") != len(rows) \
            or manifest.get("payload_bytes") != sum(
                row.get("size_bytes", -1) for row in rows
                if isinstance(row, dict)):
        raise AssertionError("archive manifest accounting mismatch")
    expected_names: set[str] = set()
    for row in rows:
        if not isinstance(row, dict) \
                or set(row) != {"path", "sha256", "size_bytes"}:
            raise AssertionError("archive manifest row malformed")
        name = _safe_member(row["path"])
        if name in expected_names:
            raise AssertionError("duplicate manifest path")
        expected_names.add(name)
        data = observed.get(name)
        if data is None or len(data) != row["size_bytes"] \
                or hashlib.sha256(data).hexdigest() != row["sha256"]:
            raise AssertionError(f"archive payload mismatch: {name}")
    if set(observed) != expected_names:
        raise AssertionError("archive membership differs from non-self manifest")


def build(*, cpu_suite: Path, execution_spec: Path, raw_root: Path,
          expected_suite_sha256: str, output: Path, twin: Path) -> dict[str, object]:
    resolved = [path.resolve() for path in (cpu_suite, execution_spec, raw_root,
                                             output, twin)]
    if len(set(resolved)) != len(resolved):
        raise ValueError("all input/output paths must be distinct")
    if output.exists() or twin.exists():
        raise FileExistsError("evidence output is create-only")

    recount_result = recount(cpu_suite, execution_spec, raw_root,
                             expected_suite_sha256)
    spec = strict_load(execution_spec)
    raw_records: list[dict] = []
    payloads: dict[str, bytes] = {}
    _add(payloads, "AUTHORITIES/CPU_SUITE.json", _read_required(cpu_suite, "CPU suite"))
    _add(payloads, "AUTHORITIES/HOME_EXECUTION_SPEC.json",
         _read_required(execution_spec, "execution spec"))
    home_authority_relative = _safe_member(
        spec["home_machine_authority_evidence_path"])
    _add(payloads, home_authority_relative,
         _read_required(raw_root / home_authority_relative,
                        "frozen Home-machine authority"))
    for case_id in CASE_IDS:
        path = raw_root / "raw" / f"{case_id}.json"
        raw = strict_load(path)
        if not isinstance(raw, dict):
            raise ValueError(f"raw record is not an object: {case_id}")
        raw_records.append(raw)
        # Preserve the verifier's root-relative schema so extraction is
        # directly recountable with ``--raw-root .``.
        _add(payloads, f"raw/{case_id}.json", path.read_bytes())
    for relative in sorted(_collect_audit_files(raw_root, spec, raw_records)):
        _add(payloads, relative, (raw_root / relative).read_bytes())

    here = Path(__file__).resolve()
    recount_path = here.with_name("goal5790_a1_independent_recount.py")
    _add(payloads, "TOOLS/goal5790_a1_build_evidence.py", here.read_bytes())
    _add(payloads, "TOOLS/goal5790_a1_independent_recount.py",
         recount_path.read_bytes())
    _add(payloads, "INDEPENDENT_RECOUNT.json", _json_bytes(recount_result))
    boundary = {
        "schema": BOUNDARY_SCHEMA,
        "home_only": True,
        "pod_used": False,
        "formal_worker": False,
        "registered_performance_timing_count": 0,
        "performance_claimed": False,
        "cache_cubin_included": False,
        "cache_cubin_is_authority": False,
        "prebuilt_target_native_included": False,
        "expanded_execution_source_included": False,
        "native_identity_is_digest_only": True,
        "manifest_is_non_self_referential": True,
    }
    boundary["boundary_sha256"] = digest(boundary)
    _add(payloads, "EVIDENCE_BOUNDARY.json", _json_bytes(boundary))

    archive_bytes, manifest = _tar_gz(payloads)
    output.parent.mkdir(parents=True, exist_ok=True)
    twin.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(archive_bytes)
    twin.write_bytes(archive_bytes)
    archive_sha = hashlib.sha256(archive_bytes).hexdigest()
    if sha_file(output) != archive_sha or sha_file(twin) != archive_sha:
        raise AssertionError("evidence twin byte mismatch")
    _verify_archive(output, manifest)
    _verify_archive(twin, manifest)
    return {
        "archive_sha256": archive_sha,
        "twin_sha256": archive_sha,
        "payload_count": manifest["payload_count"],
        "payload_bytes": manifest["payload_bytes"],
        "manifest_sha256": manifest["manifest_sha256"],
        "recount_sha256": recount_result["recount_sha256"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    pre_run = commands.add_parser(
        "pre-run-spec", help="freeze authorities before Home worker zero")
    pre_run.add_argument("--cpu-suite", type=Path, required=True)
    pre_run.add_argument("--home-authority", type=Path, required=True)
    pre_run.add_argument("--repository-root", type=Path, required=True)
    pre_run.add_argument("--native", type=Path, required=True)
    pre_run.add_argument("--execution-source-archive-sha256", required=True)
    pre_run.add_argument("--execution-source-tree-sha256", required=True)
    pre_run.add_argument("--optix-sdk", required=True)
    pre_run.add_argument("--cc", default="6.1", choices=("6.1",))
    pre_run.add_argument("--output-root", type=Path, required=True)
    pre_run.add_argument("--receipt", type=Path)
    adapt = commands.add_parser(
        "adapt-controller",
        help="bind exact controller/18-worker bytes into strict raw manifests")
    adapt.add_argument("--cpu-suite", type=Path, required=True)
    adapt.add_argument("--execution-spec", type=Path, required=True)
    adapt.add_argument("--pre-run-root", type=Path, required=True)
    adapt.add_argument("--controller-root", type=Path, required=True)
    adapt.add_argument("--expected-suite-sha256", required=True)
    adapt.add_argument("--output-root", type=Path, required=True)
    adapt.add_argument("--receipt", type=Path)
    archive = commands.add_parser(
        "archive", help="recount and package completed Home evidence")
    archive.add_argument("--cpu-suite", type=Path, required=True)
    archive.add_argument("--execution-spec", type=Path, required=True)
    archive.add_argument("--raw-root", type=Path, required=True)
    archive.add_argument("--expected-suite-sha256", required=True)
    archive.add_argument("--output", type=Path, required=True)
    archive.add_argument("--twin", type=Path, required=True)
    archive.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    if args.command == "pre-run-spec":
        snapshots, target_sha, capture_audit = capture_pre_run_case_authorities(
            cpu_suite=args.cpu_suite, native_library=args.native,
            optix_sdk=args.optix_sdk, compute_capability=args.cc)
        result = build_pre_run_execution_spec(
            cpu_suite=args.cpu_suite, home_authority=args.home_authority,
            repository_root=args.repository_root,
            scientific_identity={
                "execution_source_archive_sha256":
                    args.execution_source_archive_sha256,
                "execution_source_tree_sha256":
                    args.execution_source_tree_sha256,
                "native_library_sha256": sha_file(args.native),
                "target_provider": "optix", "optix_sdk": args.optix_sdk,
                "compute_capability": args.cc,
                "target_identity_sha256": target_sha,
            },
            case_authority_snapshots=snapshots,
            pre_run_capture_audit=capture_audit,
            output_root=args.output_root,
        )
    elif args.command == "adapt-controller":
        result = adapt_controller_result(
            cpu_suite=args.cpu_suite,
            execution_spec=args.execution_spec,
            pre_run_root=args.pre_run_root,
            controller_root=args.controller_root,
            expected_suite_sha256=args.expected_suite_sha256,
            output_root=args.output_root,
        )
    else:
        result = build(
            cpu_suite=args.cpu_suite,
            execution_spec=args.execution_spec,
            raw_root=args.raw_root,
            expected_suite_sha256=args.expected_suite_sha256,
            output=args.output,
            twin=args.twin,
        )
    rendered = _json_bytes(result)
    if args.receipt is None:
        print(rendered.decode("utf-8"), end="")
    else:
        if args.receipt.exists():
            raise FileExistsError("builder receipt is create-only")
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_bytes(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
