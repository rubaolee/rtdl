from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import subprocess
from pathlib import Path, PurePosixPath
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-08-22"

SOURCE_PATH = ROOT / "history/internal_docs/goal5793_s0_source_and_admission_freeze_20260822.json"
CANDIDATE_PATH = ROOT / "history/internal_docs/goal5793_s0_known_universe_requalification_20260822.json"
PROTOCOL_PATH = ROOT / "history/internal_docs/goal5793_s0_protocol_and_stage_authority_20260822.json"
REPORT_PATH = ROOT / "history/internal_docs/goal5793_s0_preregistration_technical_report_20260822.md"
SELF_REVIEW_PATH = ROOT / "history/internal_docs/self_review_goal5793_s0_preregistration_20260822.md"
RESULT_PATH = ROOT / "history/internal_docs/goal5793_s0_preregistration_result_20260822.json"
AUDIT_PATH = ROOT / "history/internal_docs/goal5793_s0_independent_audit_20260822.json"
CFR_PATH = ROOT / "history/internal_docs/call_for_review_goal5793_s0_preregistration_and_generic_examiner_entry_20260822.md"

GOAL5753_UNIVERSE = ROOT / "history/internal_docs/goal5753_held_out_candidate_universe_20260811.json"
GOAL5753_PROTOCOL = ROOT / "history/internal_docs/goal5753_core_freeze_and_selection_protocol_20260811.json"
A2_CLOSURE = ROOT / "history/internal_docs/goal5789_a2_postreview_closure_and_goal5793_s0_entry_20260822.json"

COMPLETE_SUMMARY = {
    "file_count": 326,
    "total_bytes": 14587884,
    "rows_canonical_bytes": 46672,
    "rows_sha256": "f26b55e6d9a120a34882e9c7ada44df5503f1f90f83db893d1d6957ab0202f97",
}
CRITICAL_SUMMARY = {
    "file_count": 41,
    "total_bytes": 3559681,
    "rows_sha256": "f2a8887ac279e71f5425b9ec5ad12b5ce0c258a2e219f254322d101866797138",
}
EXPECTED_COUNTS = {
    "survey_rows": 35,
    "excluded_rows": 30,
    "source_gap_analyzed_permanently_ineligible_rows": 5,
    "selection_eligible_rows": 0,
    "qualified_role_a_rows": 0,
    "qualified_role_b_rows": 0,
    "qualified_role_c_rows": 0,
    "eligible_ordered_triplets": 0,
}
SOURCE_GAP_IDS = {
    "Zhang2025RTSpMSpMHR::spmm",
    "Hashinoki2023ImplementationOR::radio_wave_propagation",
    "Morrical2019EfficientSS::space_skipping",
    "Liu2025RayTC::infrared_radiation",
    "Salmon2019ExploitingHR::particle_transport",
}
EXPECTED_SOURCE_GAPS = {
    "Zhang2025RTSpMSpMHR::spmm": ["publisher paper bytes unavailable; code must not substitute for paper semantics"],
    "Hashinoki2023ImplementationOR::radio_wave_propagation": ["exact target paper unavailable", "no author code located", "oracle not frozen"],
    "Morrical2019EfficientSS::space_skipping": ["no author code located", "exact bounded discrete oracle not frozen"],
    "Liu2025RayTC::infrared_radiation": ["exact paper unavailable", "no author code located", "statistical oracle not frozen"],
    "Salmon2019ExploitingHR::particle_transport": ["exact author OptiX/OpenMC port not found", "deterministic oracle not frozen"],
}
HISTORICAL_WORKLOAD_FAMILIES = (
    "ANN", "BFS", "Barnes-Hut", "Binary Search", "Continuous CD", "DBSCAN", "Discrete CD", "FRNN",
    "Graph Drawing", "Index Scan", "Infrared Radiation", "Line-Segment Intersection",
    "Non-euclidean kNN", "Outlier Detection", "Particle Simulation", "Particle Tracking",
    "Particle Transport", "Particle-Mesh Coupling", "Penetration Depth", "Point Location", "Point Queries",
    "Point in Polygon", "RMQ", "Radio Wave Propagation", "Range Queries", "Segmentation",
    "Set Intersection", "SpMM", "Space Skipping", "Triangle Counting", "Voxelization", "kNN",
)
EXPECTED_HISTORICAL_ROOTS = [
    {
        "commit": "89079f4c0d60b8a8517b8b302170868de1e3e4a7",
        "path": "docs/reports/goal519_rt_workload_universe_from_2603_28771_2026-04-17.md",
        "bytes": 10800,
        "sha256": "972403628507c9655acd5fdaf20349feb859c46929b6dd3431bc4af37dbe6437",
        "meaning": "the 32 normalized workload families later represented by the Goal5753 rows were catalogued and discussed at roadmap/feasibility level; this is not paper-specific source review",
    },
    {
        "commit": "ccd86697daa54467ab256aeba49798bf9ee06d64",
        "path": "docs/reports/goal521_v0_8_workload_scope_decision_matrix_2026-04-17.md",
        "bytes": 8165,
        "sha256": "590de7ef35aea6244949f187498fb3f45a90e4fc3a59ee0b538f6ba8910169ac",
        "meaning": "the same 32 normalized workload families received workload-scope feasibility/risk treatment; this is not paper-specific source review",
    },
]

# Filled from independently rehashed, prewrite-stable builder output.  These
# constants make coordinated resealing insufficient: the auditor does not trust
# a document merely because its self-seal was recomputed.
EXPECTED_SOURCE_AUTHORITY_SHA256 = "5107d019ff5c583645e3c101021678e84381546c32310b0027ec9220ee1b4dd3"
EXPECTED_CANDIDATE_AUTHORITY_SHA256 = "5567828708f4af7d0029880af71783cec8c267c7c9100fee949311586ebce4a0"
EXPECTED_PROTOCOL_AUTHORITY_SHA256 = "bcdef49272ec413334edc3c9b5d3f201c8b3586f943ab2d87c032f316cfe8a4e"
EXPECTED_CANDIDATE_ROWS_SHA256 = "15da2365bfff3ded0dd6a3e763a3044c3255a8699afdd02b5c3c2e9182209289"
EXPECTED_REPORT_FILE_SHA256 = "27d4d5167832ddc7d1a39f21e26f46f13bd27324e22c936937096d2fa8116868"
EXPECTED_SELF_REVIEW_FILE_SHA256 = "6b5e59b259d882763a2a22bed680031dc36a5ffab295a6021dc6908e7367a458"
EXPECTED_PROTOCOL_SUBTREE_SHA256: dict[str, str] = {
    "stage_transition_guards": "3226e397e1888c6f6d0ccacc588377ebdbed4ca4f4ab1b47a2201442c0158a20",
    "x1_generic_examiner_contract": "dce4cccfdbdad96075af42bf816cbde22683764efb26e0ec2a2144b968161009",
    "x1_environment_and_shared_native_contract": "b3a20720cdaaca681033ebe10966210060082aca4e31877df6fa41682bfa4052",
    "x2_systematic_expansion": "dad2dbdafbae8cdfbee0c51750b29cc5e9a4b34ba5c84b261a1f891be45a532e",
    "x3_preentropy_science_projection": "c9281faac38a3fba29ef6b21ad9d54ebb6725075356d10e4998dd438cfc9773b",
    "x3_triplet_enumeration": "5b9bac15a086fee5fa4a9a36615f60f9e4799a861aeca20658374c3407a49d72",
    "deferred_entropy": "ee6a6113fb0e6954ca200722f53e948509123707d1155302401420ba04d8ccb9",
    "postselection_input_and_implementation_freeze": "cfc241b89ea298985339e57a26be3576f697dff184449a795b02be476d3c0605",
    "structural_friction_ledger": "4386aa60f87ebac0c949716fb6182856c3fef911bf0fcf6513d3f2c63dce4fda",
    "claim_lint": "c29d06e93e902c4dbae22f9ed7d4043012217fae6415123099e5acd223133571",
    "external_review_and_absorption_dag": "a1a16892a592e5c7d83dfbb3d97cfa088c460a302df1ceaaea08982e7e46c8da",
}
EXPECTED_QUERY_TERMS = [
    "ray tracing core", "ray tracing cores", "ray tracing unit", "ray tracing units",
    "ray tracing accelerator", "ray tracing accelerators", "hardware ray tracing",
    "DirectX Raytracing", "Vulkan ray tracing", "OptiX", "HIPRT",
]
ENTROPY_FIELD_ORDER = [
    "domain",
    "s0_protocol_authority_file_sha256",
    "complete_source_rows_sha256",
    "x1_examiner_closure_file_sha256",
    "x2_harvester_entropy_closure_file_sha256",
    "x3_science_triplet_owner_closure_file_sha256",
    "expanded_append_only_row_table_file_sha256",
    "preentropy_science_projection_rows_sha256",
    "ordered_triplets_rows_sha256",
    "ordered_triplet_count",
    "anchor_chain_index",
    "anchor_pulse_index",
    "anchor_timestamp_ms",
    "anchor_certificate_id",
    "anchor_output_value",
    "target_chain_index",
    "target_pulse_index",
    "target_timestamp_ms",
    "target_certificate_id",
    "target_output_value",
    "counter",
]

FAIL_IDS = {
    "ZERO_DRIFT_AUTHORITY_MISMATCH",
    "EXPLANATORY_SUBMANIFEST_OVERCLAIM",
    "UNIVERSE_ROW_SET_MISMATCH",
    "SOURCE_GAP_HYGIENE_FAILURE",
    "EXPOSURE_AUTHORITY_MISMATCH",
    "FORBIDDEN_SELECTION_FEATURE_DEPENDENCE",
    "ROLE_REQUALIFICATION_MISMATCH",
    "TRIPLET_SET_MISMATCH",
    "PREMATURE_ENTROPY_OR_SELECTION",
    "STAGE_PREDECESSOR_UNSATISFIED",
    "SEARCH_BEFORE_EXAMINER_FREEZE",
    "EXPANSION_PROTOCOL_DRIFT",
    "EXAMINER_METADATA_DEPENDENCE",
    "REGISTRY_DERIVATION_OR_CORE_DRIFT",
    "ENTROPY_DOMAIN_OR_TARGET_MISMATCH",
    "POST_OUTCOME_RESCUE",
    "OUTCOME_DEPENDENT_VALIDITY",
    "FRICTION_LEDGER_MISMATCH",
    "USABILITY_OVERCLAIM",
    "EXPOSURE_CLAIM_OVERREACH",
    "RESULT_OR_BINDING_MISMATCH",
}


class AuditFailure(RuntimeError):
    def __init__(self, fail_id: str, detail: str):
        if fail_id not in FAIL_IDS:
            raise ValueError(f"unknown fail id: {fail_id}")
        self.fail_id = fail_id
        self.detail = detail
        super().__init__(f"{fail_id}: {detail}")


def fail(fail_id: str, detail: str) -> None:
    raise AuditFailure(fail_id, detail)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _entropy_value_bytes(name: str, value: Any) -> bytes:
    if name == "domain":
        if not isinstance(value, str):
            fail("ENTROPY_DOMAIN_OR_TARGET_MISMATCH", "entropy domain is not text")
        return value.encode("utf-8")
    if name.endswith("_sha256"):
        if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
            fail("ENTROPY_DOMAIN_OR_TARGET_MISMATCH", f"invalid digest field {name}")
        return bytes.fromhex(value)
    if name.endswith("_certificate_id") or name.endswith("_output_value"):
        if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{128}", value):
            fail("ENTROPY_DOMAIN_OR_TARGET_MISMATCH", f"invalid 512-bit field {name}")
        return bytes.fromhex(value)
    if type(value) is not int or value < 0 or value > (1 << 64) - 1:
        fail("ENTROPY_DOMAIN_OR_TARGET_MISMATCH", f"invalid u64 field {name}")
    return value.to_bytes(8, "big")


def build_entropy_frame(inputs: dict[str, Any], field_order: list[str]) -> bytes:
    if field_order != ENTROPY_FIELD_ORDER or set(inputs) != set(field_order):
        fail("ENTROPY_DOMAIN_OR_TARGET_MISMATCH", "entropy field set/order differs")
    magic = bytes.fromhex("5254444c3537393353454c0001")
    body = bytearray(magic)
    body.extend(len(field_order).to_bytes(2, "big"))
    for name in field_order:
        try:
            name_bytes = name.encode("ascii")
        except UnicodeEncodeError:
            fail("ENTROPY_DOMAIN_OR_TARGET_MISMATCH", "non-ASCII entropy field name")
        value_bytes = _entropy_value_bytes(name, inputs[name])
        body.extend(len(name_bytes).to_bytes(2, "big"))
        body.extend(name_bytes)
        body.extend(len(value_bytes).to_bytes(8, "big"))
        body.extend(value_bytes)
    return bytes(body)


def identity(path: Path, virtual_files: dict[Path, bytes] | None = None) -> dict[str, Any]:
    data = virtual_files[path] if virtual_files is not None and path in virtual_files else path.read_bytes()
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "bytes": len(data),
        "file_sha256": sha256_bytes(data),
    }


def verify_seal(document: dict[str, Any], field: str, fail_id: str = "RESULT_OR_BINDING_MISMATCH") -> str:
    stored = document.get(field)
    if not isinstance(stored, str) or not re.fullmatch(r"[0-9a-f]{64}", stored):
        fail(fail_id, f"missing or malformed {field}")
    body = dict(document)
    body.pop(field, None)
    actual = sha256_bytes(canonical_bytes(body))
    if stored != actual:
        fail(fail_id, f"{field} mismatch")
    return stored


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def live_source_rows() -> list[dict[str, Any]]:
    paths: list[Path] = []
    for path in (ROOT / "src").rglob("*"):
        if path.is_symlink():
            fail("ZERO_DRIFT_AUTHORITY_MISMATCH", f"symlink in declared code surface: {path}")
        if not path.is_file():
            continue
        if "__pycache__" in path.parts or path.suffix.lower() in {".pyc", ".nbc", ".nbi"}:
            continue
        paths.append(path)
    declarations = [ROOT / name for name in ("Makefile", "pyproject.toml", "requirements.txt", "VERSION")]
    if any(path.is_symlink() or not path.is_file() for path in declarations):
        fail("ZERO_DRIFT_AUTHORITY_MISMATCH", "named declaration is not a regular non-symlink file")
    paths.extend(declarations)
    rows = []
    for path in paths:
        data = path.read_bytes()
        rows.append(
            {
                "path": path.relative_to(ROOT).as_posix(),
                "sha256": sha256_bytes(data),
                "size_bytes": len(data),
            }
        )
    rows.sort(key=lambda row: row["path"].encode("utf-8"))
    return rows


def _validate_rows(rows: Any, summary: Any, expected: dict[str, Any], *, compare_live: bool) -> None:
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        fail("ZERO_DRIFT_AUTHORITY_MISMATCH", "source rows are not a list of objects")
    paths = [row.get("path") for row in rows]
    if paths != sorted(paths, key=lambda value: value.encode("utf-8")) or len(paths) != len(set(paths)):
        fail("ZERO_DRIFT_AUTHORITY_MISMATCH", "source paths are not sorted unique")
    for path in paths:
        if not isinstance(path, str) or PurePosixPath(path).as_posix() != path or path.startswith("/") or ".." in PurePosixPath(path).parts:
            fail("ZERO_DRIFT_AUTHORITY_MISMATCH", f"noncanonical source path {path!r}")
    computed = {
        "file_count": len(rows),
        "total_bytes": sum(row.get("size_bytes", -1) for row in rows),
        "rows_sha256": sha256_bytes(canonical_bytes(rows)),
    }
    if "rows_canonical_bytes" in expected:
        computed["rows_canonical_bytes"] = len(canonical_bytes(rows))
    if summary != expected or computed != expected:
        fail("ZERO_DRIFT_AUTHORITY_MISMATCH", f"source summary differs: {computed}")
    if compare_live and canonical_bytes(rows) != canonical_bytes(live_source_rows()):
        fail("ZERO_DRIFT_AUTHORITY_MISMATCH", "live source/build surface differs")


def validate_source(document: dict[str, Any], *, compare_live: bool = True) -> None:
    expected_keys = {
        "schema",
        "source_authority_sha256",
        "goal",
        "date",
        "status",
        "declared_product_native_source_zero_drift_authority",
        "critical_explanatory_submanifest",
        "v26_custody",
        "controlling_scientific_verdict_path",
        "execution_environment_and_shared_native_requirements",
        "claim_boundary",
    }
    if set(document) != expected_keys:
        fail("ZERO_DRIFT_AUTHORITY_MISMATCH", "source authority top-level key set differs")
    seal_value = verify_seal(document, "source_authority_sha256", "ZERO_DRIFT_AUTHORITY_MISMATCH")
    if (
        document.get("schema") != "rtdl.goal5793.s0.source_and_admission_freeze.v1"
        or document.get("goal") != 5793
        or document.get("date") != DATE
        or document.get("status") != "FROZEN_DECLARED_PRODUCT_NATIVE_SOURCE_CODE_SURFACE__PACKAGE_BUILD_AND_EXECUTION_ENVIRONMENT_NOT_YET_FROZEN"
    ):
        fail("ZERO_DRIFT_AUTHORITY_MISMATCH", "source authority identity/status differs")
    complete = document["declared_product_native_source_zero_drift_authority"]
    if complete.get("complete_for_declared_surface") is not True or complete.get("complete_build_or_package_closure") is not False:
        fail("ZERO_DRIFT_AUTHORITY_MISMATCH", "326-file declared-surface boundary differs")
    if complete.get("scope") != "all regular non-symlink src/** files excluding cache artifacts, plus the four named declarations Makefile, pyproject.toml, requirements.txt and VERSION":
        fail("ZERO_DRIFT_AUTHORITY_MISMATCH", "declared-surface scope differs")
    _validate_rows(complete.get("rows"), complete.get("summary"), COMPLETE_SUMMARY, compare_live=compare_live)
    critical = document["critical_explanatory_submanifest"]
    if critical.get("complete_authority") is not False:
        fail("EXPLANATORY_SUBMANIFEST_OVERCLAIM", "41-file explanatory manifest marked complete")
    _validate_rows(critical.get("rows"), critical.get("summary"), CRITICAL_SUMMARY, compare_live=False)
    custody = document["v26_custody"]
    if (
        custody.get("present_and_byte_identical_count") != 324
        or custody.get("missing_paths") != ["VERSION", "requirements.txt"]
        or custody.get("mismatch_count") != 0
    ):
        fail("ZERO_DRIFT_AUTHORITY_MISMATCH", "v26 overlap boundary differs")
    verdict = document["controlling_scientific_verdict_path"]
    if verdict.get("new_candidate_controlled_by_a2_checker") is not False or verdict.get("generic_examiner_exists") is not False:
        fail("EXAMINER_METADATA_DEPENDENCE", "historical A2 checker or nonexistent examiner claimed controlling")
    environment = document["execution_environment_and_shared_native_requirements"]
    if environment.get("authority_created") is not False or environment.get("required_before_search_or_entropy") is not True:
        fail("STAGE_PREDECESSOR_UNSATISFIED", "environment/native freeze boundary differs")
    if set(document["claim_boundary"]) != {
        "all_326_files_are_scientific_tcb_claimed",
        "complete_package_or_build_closure_claimed",
        "complete_import_closure_claimed_for_41_files",
        "toolchain_frozen",
        "native_binary_frozen",
        "new_candidate_checker_exists",
        "product_change_authorized",
    } or any(value is not False for value in document["claim_boundary"].values()):
        fail("RESULT_OR_BINDING_MISMATCH", "source claim boundary contains a true flag")
    if EXPECTED_SOURCE_AUTHORITY_SHA256 != "PENDING" and seal_value != EXPECTED_SOURCE_AUTHORITY_SHA256:
        fail("ZERO_DRIFT_AUTHORITY_MISMATCH", "source authority differs from independently pinned prewrite seal")


def _verify_historical_roots(roots: Any) -> None:
    if roots != EXPECTED_HISTORICAL_ROOTS:
        fail("EXPOSURE_AUTHORITY_MISMATCH", "historical exposure roots differ")
    for row in EXPECTED_HISTORICAL_ROOTS:
        data = subprocess.check_output(["git", "show", f"{row['commit']}:{row['path']}"], cwd=ROOT)
        if len(data) != row["bytes"] or sha256_bytes(data) != row["sha256"]:
            fail("EXPOSURE_AUTHORITY_MISMATCH", f"historical blob drift: {row['path']}")


def validate_candidates(document: dict[str, Any]) -> None:
    expected_keys = {
        "schema",
        "candidate_authority_sha256",
        "goal",
        "date",
        "status",
        "source_universe",
        "source_universe_historical_filename_disclaimer",
        "source_protocol",
        "survey_source",
        "historical_author_exposure",
        "uniform_policy",
        "role_definitions",
        "counts",
        "ordered_triplets",
        "ordered_triplet_rows_sha256",
        "rows",
        "source_evidence_reachability",
        "claim_boundary",
    }
    if set(document) != expected_keys:
        fail("UNIVERSE_ROW_SET_MISMATCH", "candidate authority top-level key set differs")
    seal_value = verify_seal(document, "candidate_authority_sha256", "UNIVERSE_ROW_SET_MISMATCH")
    if (
        document.get("schema") != "rtdl.goal5793.s0.known_universe_requalification.v1"
        or document.get("goal") != 5793
        or document.get("date") != DATE
        or document.get("status") != "FROZEN_35_ROW_REQUALIFICATION__ZERO_QUALIFIED_ROLE_A__ZERO_TRIPLETS__NO_ENTROPY"
    ):
        fail("UNIVERSE_ROW_SET_MISMATCH", "candidate authority identity/status differs")
    source = load_json(GOAL5753_UNIVERSE)
    if document.get("source_universe") != identity(GOAL5753_UNIVERSE) or document.get("source_protocol") != identity(GOAL5753_PROTOCOL):
        fail("UNIVERSE_ROW_SET_MISMATCH", "Goal5753 source identities differ")
    if document.get("source_universe_historical_filename_disclaimer") != "the immutable path contains held_out only as a historical filename; it is not checker/calculus generalization evidence and no held-out claim is made":
        fail("EXPOSURE_CLAIM_OVERREACH", "historical held_out filename is not locally disclaimed")
    if document.get("survey_source") != source.get("source"):
        fail("UNIVERSE_ROW_SET_MISMATCH", "survey-source projection differs")
    expected_pairs = [
        (row["source_index"], row["candidate_id"], row["citation_key"])
        for row in source["source_rows"]
    ]
    rows = document.get("rows")
    if not isinstance(rows, list):
        fail("UNIVERSE_ROW_SET_MISMATCH", "candidate rows are not a list")
    actual_pairs = [(row.get("source_index"), row.get("candidate_id"), row.get("citation_key")) for row in rows]
    if actual_pairs != expected_pairs or len(set(actual_pairs)) != 35:
        fail("UNIVERSE_ROW_SET_MISMATCH", "35-row candidate identity set differs")
    exposure = document["historical_author_exposure"]
    _verify_historical_roots(exposure.get("roots"))
    if exposure != {
        "exact_35_paper_problem_identities_visible_via_goal5753_catalog": True,
        "normalized_workload_family_count": 32,
        "normalized_workload_families": list(HISTORICAL_WORKLOAD_FAMILIES),
        "normalized_workload_families_assessed_via_goal519_521": True,
        "paper_specific_source_level_feasibility_assessment_before_s0_claimed": False,
        "unseen_or_blind_wording_allowed": False,
        "strongest_allowed_description_for_old_35": "fully enumerated 35-row author-seen legacy catalog; permanently selection-ineligible for Goal5793",
        "roots": EXPECTED_HISTORICAL_ROOTS,
    }:
        fail("EXPOSURE_AUTHORITY_MISMATCH", "32-family/35-paper exposure boundary differs")
    if exposure.get("unseen_or_blind_wording_allowed") is not False:
        fail("EXPOSURE_CLAIM_OVERREACH", "unseen/blind wording enabled")
    if document.get("uniform_policy") != {
        "all_35_rows_preserved": True,
        "all_35_rows_permanently_selection_ineligible": True,
        "later_query_match_to_any_old_identity_is_duplicate_crosslink_only": True,
        "old_exclusions_preserved": True,
        "missing_primary_source_is_a_gap_not_eligibility": True,
        "same_paper_and_normalized_problem_family_contamination_excluded": True,
        "non_rt_core_and_nonstock_hardware_excluded": True,
        "performance_speedup_and_implementation_ease_ignored": True,
        "manual_fallback_allowed": False,
    }:
        fail("ROLE_REQUALIFICATION_MISMATCH", "uniform old-catalog policy differs")
    source_gap_seen: set[str] = set()
    for row in rows:
        candidate_id = row["candidate_id"]
        if (
            row.get("paper_identity_visible_via_goal5753_catalog") is not True
            or row.get("normalized_workload_family_assessed_via_goal519_521") is not True
            or row.get("paper_specific_source_level_assessment_before_s0") != "NOT_CLAIMED"
        ):
            fail("EXPOSURE_AUTHORITY_MISMATCH", f"row exposure boundary differs for {candidate_id}")
        if row.get("unseen_claimed") is not False or row.get("blind_claimed") is not False or row.get("held_out_from_design_claimed") is not False:
            fail("EXPOSURE_CLAIM_OVERREACH", f"overclaim for {candidate_id}")
        if row.get("historical_catalog_roots") != EXPECTED_HISTORICAL_ROOTS:
            fail("EXPOSURE_AUTHORITY_MISMATCH", f"row exposure roots differ for {candidate_id}")
        if row.get("performance_or_ease_used_for_eligibility") is not False:
            fail("FORBIDDEN_SELECTION_FEATURE_DEPENDENCE", f"performance/ease used for {candidate_id}")
        if row.get("selection_forbidden") is not True:
            fail("ROLE_REQUALIFICATION_MISMATCH", f"selection enabled for {candidate_id}")
        primary = row.get("primary_source_requalification")
        if not isinstance(primary, dict):
            fail("SOURCE_GAP_HYGIENE_FAILURE", f"primary-source record missing for {candidate_id}")
        if (
            primary.get("primary_or_code_bytes_embedded_in_s0_review_artifact") is not False
            or primary.get("reviewer_rehash_requires_network_refetch_or_separate_authority") is not True
            or primary.get("author_code_nonexistence_claimed") is not False
            or primary.get("source_observation_controls_selection_eligibility") is not False
        ):
            fail("SOURCE_GAP_HYGIENE_FAILURE", f"source reachability overclaim for {candidate_id}")
        status = row.get("eligibility_status")
        roles = (
            row.get("role_a_unconventional_correct_expected_admission"),
            row.get("role_b_different_geometry_or_composition"),
            row.get("role_c_non_obvious_risk"),
        )
        if candidate_id in SOURCE_GAP_IDS:
            source_gap_seen.add(candidate_id)
            if status != "SOURCE_GAP_ANALYZED__PERMANENTLY_SELECTION_INELIGIBLE" or roles != (
                "NOT_QUALIFIED__PERMANENTLY_INELIGIBLE",
                "NOT_QUALIFIED__PERMANENTLY_INELIGIBLE",
                "NOT_QUALIFIED__PERMANENTLY_INELIGIBLE",
            ):
                fail("ROLE_REQUALIFICATION_MISMATCH", f"legacy source-gap role drift for {candidate_id}")
            if primary.get("source_gaps") != EXPECTED_SOURCE_GAPS[candidate_id]:
                fail("SOURCE_GAP_HYGIENE_FAILURE", f"source gap hidden for {candidate_id}")
        else:
            if status != "EXCLUDED" or roles != ("NOT_QUALIFIED", "NOT_QUALIFIED", "NOT_QUALIFIED"):
                fail("ROLE_REQUALIFICATION_MISMATCH", f"excluded role drift for {candidate_id}")
    if source_gap_seen != SOURCE_GAP_IDS or document.get("counts") != EXPECTED_COUNTS:
        fail("ROLE_REQUALIFICATION_MISMATCH", "candidate counts or source-gap set differ")
    if document.get("ordered_triplets") != [] or document.get("ordered_triplet_rows_sha256") != sha256_bytes(canonical_bytes([])):
        fail("TRIPLET_SET_MISMATCH", "current triplet set is not exactly empty")
    boundary = document["claim_boundary"]
    if (
        boundary.get("current_pool_has_expected_admission_positive") is not False
        or boundary.get("current_pool_supports_entropy_draw") is not False
        or boundary.get("old_35_can_reenter_future_expansion") is not False
        or boundary.get("paper_specific_source_feasibility_for_all_35_claimed") is not False
    ):
        fail("ROLE_REQUALIFICATION_MISMATCH", "empty-pool boundary overclaimed")
    reachability = document["source_evidence_reachability"]
    if reachability.get("primary_pdf_or_code_archive_bytes_embedded") is not False or reachability.get("observed_hashes_are_reviewer_reachable_without_refetch") is not False:
        fail("SOURCE_GAP_HYGIENE_FAILURE", "primary-source reachability overclaimed")
    rows_digest = sha256_bytes(canonical_bytes(rows))
    if EXPECTED_CANDIDATE_ROWS_SHA256 != "PENDING" and rows_digest != EXPECTED_CANDIDATE_ROWS_SHA256:
        fail("UNIVERSE_ROW_SET_MISMATCH", "candidate rows differ from independently pinned exact requalification")
    if EXPECTED_CANDIDATE_AUTHORITY_SHA256 != "PENDING" and seal_value != EXPECTED_CANDIDATE_AUTHORITY_SHA256:
        fail("UNIVERSE_ROW_SET_MISMATCH", "candidate authority differs from independently pinned prewrite seal")


def _require_protocol_subtree(document: dict[str, Any], name: str, fail_id: str) -> None:
    expected = EXPECTED_PROTOCOL_SUBTREE_SHA256.get(name)
    if expected is not None and sha256_bytes(canonical_bytes(document[name])) != expected:
        fail(fail_id, f"exact protocol subtree drift: {name}")


def validate_protocol(document: dict[str, Any]) -> None:
    expected_keys = {
        "schema", "protocol_authority_sha256", "goal", "date", "status", "state_machine", "stage_transition_guards", "current_state",
        "current_literals", "x1_generic_examiner_contract", "x1_environment_and_shared_native_contract",
        "x2_systematic_expansion", "x3_preentropy_science_projection", "x3_triplet_enumeration",
        "deferred_entropy", "postselection_input_and_implementation_freeze", "structural_friction_ledger",
        "claim_lint", "external_review_and_absorption_dag", "permanent_goal5793_invariants", "authorization",
    }
    if set(document) != expected_keys:
        fail("EXPANSION_PROTOCOL_DRIFT", "protocol top-level key set differs")
    seal_value = verify_seal(document, "protocol_authority_sha256", "EXPANSION_PROTOCOL_DRIFT")
    if document.get("schema") != "rtdl.goal5793.s0.protocol_and_stage_authority.v1" or document.get("goal") != 5793 or document.get("date") != DATE:
        fail("EXPANSION_PROTOCOL_DRIFT", "protocol identity differs")
    expected_states = [
        "A2_CLOSED",
        "S0_35ROW_FROZEN__EXTERNAL_REVIEW_PENDING",
        "S0_35ROW_TERMINAL_REVIEWED",
        "X1_GENERIC_EXAMINER_REGISTRY_ENV_SHARED_NATIVE_IMPLEMENTED_REVIEWED",
        "X2_HARVESTER_ENTROPY_CLIENT_AND_EXPANSION_PROTOCOL_IMPLEMENTED_OFFLINE_REVIEWED",
        "X3_FIRST_LIVE_SEARCH_EXECUTED__SCIENCE_PROJECTED__TRIPLETS_FROZEN_REVIEWED",
        "E0_DEFERRED_NIST_ANCHOR_AND_FUTURE_TARGET",
        "E1_SELECTED_TRIPLET",
        "P1_SELECTED_SCIENCE_PREREG_REVIEWED",
        "P2_CANDIDATE_IMPLEMENTATION_FREEZE",
        "P3_EXAMS",
        "RESULT",
        "TERMINAL_SINGLE_EXPANSION_EMPTY_CONTAMINATED_OR_PROTOCOL_INVALID",
        "TERMINAL_SEARCH_INFRASTRUCTURE_FAILURE",
        "TERMINAL_ENTROPY_OR_COUNTER_INFRASTRUCTURE_FAILURE",
        "TERMINAL_VALID_SCIENTIFIC_RESULT",
    ]
    if document.get("state_machine") != expected_states or document.get("current_state") != "S0_35ROW_FROZEN__EXTERNAL_REVIEW_PENDING":
        fail("SEARCH_BEFORE_EXAMINER_FREEZE", "exact stage machine/current state differs")
    expected_transition_guards = {
        "S0_TO_X1": "exact returned S0 review with P0=0/P1=0 plus append-only owner absorption/closure that authorizes X1 only",
        "X1_TO_X2": "exact generic examiner, registry derivation, environment and shared-native authorities; hostile tests; returned external review P0=0/P1=0; append-only owner closure",
        "X2_TO_X3": "exact offline harvester, taxonomy, enumerator, NIST verifier, trust bundle and selection client; zero live calls; returned external review P0=0/P1=0; append-only owner closure",
        "X3_TO_E0": "one complete live search with all pages/responses preserved; complete append-only row table and all preentropy science projections frozen; zero preselection decision invocations; exact triplet manifest nonempty; returned external review P0=0/P1=0; append-only owner closure",
        "E0_TO_E1": "authenticated first-next anchor and exact future target satisfy the frozen NIST verifier and selection mapping; no alternate pulse",
        "E1_TO_P1": "selected triplet identity is the exact indexed member of the reviewed ordered-triplet manifest",
        "P1_TO_P2": "selected rows retain preentropy science projections; exact bounded inputs, allowed paths and outcome consequences are separately reviewed and owner-closed",
        "P2_TO_P3": "candidate app-only implementation and all mechanical identity slots are frozen; zero 326-source drift; functional execution separately authorized; no POD/SSH or timing",
        "P3_TO_RESULT": "all three lineages retained, including rejection/UNKNOWN/failure/invalid successors, with no replacement or rescue",
        "state_label_alone_never_authorizes_transition": True,
        "every_transition_requires_exact_predecessor_artifact_and_internal_seal": True,
        "transition_receipt_exact_schema": {
            "required_keys": [
                "schema",
                "from_state",
                "to_state",
                "predecessor_root_path_bytes_file_sha256_internal_seal",
                "single_cfr_path_bytes_file_sha256",
                "returned_review_path_bytes_file_sha256_verdict_p0_p1",
                "owner_closure_path_bytes_file_sha256_internal_seal",
                "authorization_exact_keyset_and_values",
                "transition_receipt_sha256",
            ],
            "returned_review_required_p0": 0,
            "returned_review_required_p1": 0,
            "missing_unknown_or_extra_field": "FAIL_CLOSED__TRANSITION_NOT_AUTHORIZED",
            "authorization_is_never_inferred_from_state_label": True,
        },
        "terminal_sink_states": [
            "TERMINAL_SINGLE_EXPANSION_EMPTY_CONTAMINATED_OR_PROTOCOL_INVALID",
            "TERMINAL_SEARCH_INFRASTRUCTURE_FAILURE",
            "TERMINAL_ENTROPY_OR_COUNTER_INFRASTRUCTURE_FAILURE",
            "TERMINAL_VALID_SCIENTIFIC_RESULT",
        ],
    }
    if document.get("stage_transition_guards") != expected_transition_guards:
        fail("STAGE_PREDECESSOR_UNSATISFIED", "stage transition guard table differs")
    literals = document["current_literals"]
    expected_literals = {
        "known_universe_rows": 35,
        "old_catalog_selection_eligible_count": 0,
        "qualified_role_a_count": 0,
        "eligible_ordered_triplet_count": 0,
        "generic_examiner_exists": False,
        "systematic_search_execution_count": 0,
        "live_provider_call_count": 0,
        "entropy_draw_count": 0,
        "anchor": None,
        "target_output": None,
        "selected_triplet": None,
        "candidate_implementation_count": 0,
        "exam_count": 0,
    }
    if literals != expected_literals:
        fail("PREMATURE_ENTROPY_OR_SELECTION", "current S0 literals differ")

    examiner = document["x1_generic_examiner_contract"]
    expected_forbidden_inputs = [
        "candidate_id", "citation_key", "source_index", "role_assignment", "expected_disposition",
        "selected_index", "performance_expectation", "implementation_ease",
    ]
    if examiner.get("implementation_authorized_now") is not False or examiner.get("search_or_entropy_authorized_by_x1") is not False:
        fail("STAGE_PREDECESSOR_UNSATISFIED", "X1 prematurely authorized")
    if examiner.get("decision_code_forbidden_inputs") != expected_forbidden_inputs:
        fail("EXAMINER_METADATA_DEPENDENCE", "examiner metadata prohibition differs")
    registry = examiner.get("registry_derivation", {})
    if registry.get("must_be_frozen_before_expansion_search") is not True or registry.get("forbidden_postfreeze_changes") != [
        "semantic obligation", "physical guarantee", "geometry family", "role or opcode", "rule", "registry template", "facade"
    ]:
        fail("REGISTRY_DERIVATION_OR_CORE_DRIFT", "registry freeze differs")
    exposure_registry = examiner.get("pre_x1_declared_project_exposure_registry", {})
    if (
        exposure_registry.get("must_be_complete_and_reviewed_before_x2_implementation_or_first_live_call") is not True
        or exposure_registry.get("all_matches_permanently_selection_ineligible_and_crosslink_only") is not True
        or exposure_registry.get("absence_means_only_not_matched_to_the_frozen_declared_registry") is not True
        or exposure_registry.get("complete_author_mental_exposure_claimed") is not False
        or exposure_registry.get("archive_member_path_or_index_only_is_sufficient") is not False
        or exposure_registry.get("registry_coverage_gap_allows_unseen_claim") is not False
        or "every PDF through the frozen parser" not in exposure_registry.get("archive_scan_rule", "")
        or exposure_registry.get("unseen_blind_or_held_out_claim_allowed") is not False
        or "NO_REPLACEMENT_OR_REUSE" not in exposure_registry.get("later_discovered_preexisting_project_exposure", "")
    ):
        fail("EXPOSURE_AUTHORITY_MISMATCH", "pre-X1 declared project-exposure registry weakened")
    _require_protocol_subtree(document, "x1_generic_examiner_contract", "EXAMINER_METADATA_DEPENDENCE")
    _require_protocol_subtree(document, "x1_environment_and_shared_native_contract", "REGISTRY_DERIVATION_OR_CORE_DRIFT")

    expansion = document["x2_systematic_expansion"]
    if expansion.get("implementation_or_query_execution_authorized_now") is not False or expansion.get("harvester_implementation_network_access_allowed") is not False:
        fail("SEARCH_BEFORE_EXAMINER_FREEZE", "search or network access prematurely authorized")
    if (
        expansion.get("entropy_client_or_verifier_implementation_authorized_now") is not False
        or expansion.get("entropy_client_or_verifier_network_access_during_implementation_allowed") is not False
        or expansion.get("entropy_client_and_verifier_must_be_frozen_reviewed_and_owner_closed_before_first_live_search") is not True
    ):
        fail("ENTROPY_DOMAIN_OR_TARGET_MISMATCH", "entropy client/verifier pre-search freeze differs")
    if expansion.get("live_provider_call_count_before_x2_owner_closure_required") != 0 or expansion.get("logical_search_terms") != EXPECTED_QUERY_TERMS:
        fail("EXPANSION_PROTOCOL_DRIFT", "query terms or pre-live-call gate differs")
    query_order = expansion.get("global_query_execution_order", {})
    if (
        query_order.get("provider_order") != ["OpenAlex Works API", "arXiv API"]
        or query_order.get("term_order") != EXPECTED_QUERY_TERMS
        or query_order.get("concurrent_or_interleaved_requests_allowed") is not False
        or query_order.get("worker_count") != 1
        or "finish and validate every page" not in query_order.get("loop_order", "")
    ):
        fail("EXPANSION_PROTOCOL_DRIFT", "global provider/term/pagination execution order differs")
    if expansion.get("publication_date_window") != {"from": "2018-01-01", "through": DATE}:
        fail("EXPANSION_PROTOCOL_DRIFT", "publication date window differs")
    if expansion.get("single_expansion_only") is not True or expansion.get("manual_fallback_or_second_query_round") is not False:
        fail("EXPANSION_PROTOCOL_DRIFT", "single expansion/no fallback weakened")
    if expansion.get("old_35_duplicate_policy", {}).get("old_rows_can_become_selection_eligible") is not False:
        fail("ROLE_REQUALIFICATION_MISMATCH", "old catalog may reenter future selection")
    if expansion.get("request_failure_policy", {}).get("partial_results_eligible") is not False:
        fail("EXPANSION_PROTOCOL_DRIFT", "partial search results enabled")
    resolution = expansion.get("uniform_full_text_resolution", {})
    if (
        resolution.get("applies_to_every_deduplicated_row_before_any_role_decision") is not True
        or resolution.get("general_web_search_author_homepage_search_or_manual_extra_attempt_allowed") is not False
        or resolution.get("first_success_controls_primary_full_text") is not True
        or resolution.get("source_resolution_outcome_cannot_drop_a_row_from_the_append_only_universe") is not True
    ):
        fail("SOURCE_GAP_HYGIENE_FAILURE", "uniform full-text resolution policy differs")
    code_policy = expansion.get("author_code_policy", {})
    direct_code = code_policy.get("direct_link_extraction_and_resolution", {})
    code_materialization = code_policy.get("repository_materialization", {})
    if (
        code_policy.get("author_code_required_for_selection_eligibility") is not False
        or code_policy.get("general_repository_search_allowed") is not False
        or direct_code.get("crawl_depth") != 1
        or direct_code.get("repository_page_link_following_allowed") is not False
        or direct_code.get("all_direct_links_are_attempted_in_order") is not True
        or direct_code.get("first_success_short_circuit_allowed") is not False
        or direct_code.get("multiple_distinct_repository_or_ref_candidates") != "NA_AMBIGUOUS_AUTHOR_CODE__NO_MANUAL_CHOICE"
        or code_materialization.get("missing_or_unmaterializable_code_affects_scientific_eligibility") is not False
        or code_materialization.get("conflicting_ref_or_tree") != "NA_AMBIGUOUS_AUTHOR_CODE__NO_MANUAL_CHOICE"
        or "gitlink path+commit" not in code_materialization.get("submodules", "")
        or "pointer bytes, oid and size" not in code_materialization.get("git_lfs", "")
    ):
        fail("FORBIDDEN_SELECTION_FEATURE_DEPENDENCE", "author-code availability/search can influence eligibility")
    dedup = expansion.get("deduplication_algorithm", {})
    if (
        dedup.get("provider_or_input_order_can_change_components_or_representative") is not False
        or dedup.get("unresolved_conflict_human_fallback_allowed") is not False
        or dedup.get("all_aliases_preserved_and_crosslinked") is not True
        or dedup.get("edge_rules_in_order") != [
            "same non-null normalized DOI",
            "same non-null versionless arXiv identifier",
            "same non-null canonical OpenAlex work identifier",
        ]
        or dedup.get("fallback_identity_is_never_an_equivalence_edge") is not True
        or "transitive closure" not in dedup.get("component_algorithm", "")
        or "IDENTITY_CONFLICT__SELECTION_INELIGIBLE" not in dedup.get("strong_identifier_conflict", "")
        or "FALLBACK_IDENTITY_AMBIGUOUS__SELECTION_INELIGIBLE" not in dedup.get("fallback_cross_component_rule", "")
        or "all-fallback/no-strong-ID collision" not in dedup.get("fallback_cross_component_rule", "")
        or "rerun the full closure/conflict/old-exposure checks" not in dedup.get("post_full_text_closure_rule", "")
    ):
        fail("EXPANSION_PROTOCOL_DRIFT", "deduplication equivalence/conflict protocol differs")
    crosscheck = resolution.get("authoritative_work_identity_crosscheck", {})
    if (
        crosscheck.get("manual_paper_or_version_choice_allowed") is not False
        or crosscheck.get("missing_ambiguous_or_conflicting_identity") != "SOURCE_GAP__SELECTION_INELIGIBLE__NO_MANUAL_VERSION_SUBSTITUTION"
    ):
        fail("SOURCE_GAP_HYGIENE_FAILURE", "primary-document work identity crosscheck weakened")
    _require_protocol_subtree(document, "x2_systematic_expansion", "EXPANSION_PROTOCOL_DRIFT")

    projection = document["x3_preentropy_science_projection"]
    if (
        projection.get("projection_change_after_x3_closure_allowed") is not False
        or projection.get("role_a_categorical_expected_compatible_required") is not True
        or projection.get("within_role_ranking_by_success_probability_allowed") is not False
        or "VALID_SCIENTIFIC" not in projection.get("actual_core_change_discovered_after_selection", "")
    ):
        fail("ROLE_REQUALIFICATION_MISMATCH", "preentropy science/role freeze weakened")
    role_quantifiers = projection.get("role_predicate_quantifiers", {})
    if role_quantifiers != {
        "A": "all(any(candidate[axis] != positive[axis] for axis in structural_axis_vocabulary) for positive in x1_frozen_positive_vectors)",
        "B": "all(any(candidate[axis] != positive[axis] for axis in role_b_difference_axes) for positive in x1_frozen_positive_vectors)",
        "C": "any(candidate_risk_flags[flag] is true for flag in risk_flag_vocabulary)",
        "empty_x1_positive_vector_set": "INFRA_INVALID__ROLE_DIVERSITY_UNDEFINED",
    }:
        fail("ROLE_REQUALIFICATION_MISMATCH", "role predicate quantifiers differ")
    isolation = projection.get("preselection_decision_isolation", {})
    zero_isolation_fields = [
        "future_candidate_examiner_invocation_count_before_selection",
        "future_candidate_authority_materializer_invocation_count_before_selection",
        "future_candidate_product_evaluate_admit_compile_run_invocation_count_before_selection",
        "future_candidate_app_implementation_count_before_selection",
        "future_candidate_execution_receipt_count_before_selection",
    ]
    if (
        any(isolation.get(field) != 0 for field in zero_isolation_fields)
        or isolation.get("science_projection_route_may_import_or_call_generic_examiner_product_evaluate_admit_compile_run_or_candidate_app") is not False
        or "TERMINATE_SINGLE_EXPANSION" not in isolation.get("violation", "")
    ):
        fail("EXAMINER_METADATA_DEPENDENCE", "preselection decision isolation differs")
    family_rule = projection.get("normalized_problem_family_rule", {})
    if (
        family_rule.get("controlled_vocabulary_frozen_before_first_live_call") is not True
        or family_rule.get("new_split_merge_or_label_after_first_live_call_allowed") is not False
        or family_rule.get("postentropy_split_merge_or_rename_allowed") is not False
        or family_rule.get("unresolved_or_reviewer_disputed_assignment") != "SELECTION_INELIGIBLE__NO_HUMAN_FALLBACK"
    ):
        fail("ROLE_REQUALIFICATION_MISMATCH", "problem-family taxonomy can change after search")
    product_path = projection.get("product_path_classification", {})
    if (
        product_path.get("exact_enum") != [
            "PUBLIC_FACADE_AND_PUBLIC_AUTHORITY_ISSUANCE",
            "PUBLIC_FACADE_WITH_PRIVATE_REGISTRY_ISSUER",
            "REFERENCE_ADMISSION_ONLY",
        ]
        or product_path.get("private_registry_issuer_must_be_disclosed") is not True
        or product_path.get("only_public_facade_and_public_authority_issuance_supports_end_user_product_path") is not True
        or product_path.get("private_or_reference_path_supports_usability_claim") is not False
        or product_path.get("classification_change_after_x3_closure_allowed") is not False
    ):
        fail("USABILITY_OVERCLAIM", "product-path classification or usability boundary differs")
    _require_protocol_subtree(document, "x3_preentropy_science_projection", "ROLE_REQUALIFICATION_MISMATCH")
    triplets = document["x3_triplet_enumeration"]
    if triplets.get("manual_pruning_allowed") is not False or triplets.get("citation_key_used_for_uniqueness_or_probability") is not False:
        fail("TRIPLET_SET_MISMATCH", "triplet enumeration permits manual or citation-key weighting")
    if "never by delimiter-free concatenation" not in triplets.get("enumerator", ""):
        fail("TRIPLET_SET_MISMATCH", "triplet tuple order is ambiguous")
    conflicts = triplets.get("conflict_group_derivation", {})
    if (
        conflicts.get("manual_conflict_group_ids_allowed") is not False
        or conflicts.get("additional_conflict_types") != []
        or conflicts.get("pairwise_distinctness_uses_only_same_work_and_same_problem_conflicts") is not True
    ):
        fail("TRIPLET_SET_MISMATCH", "triplet conflict derivation differs")
    _require_protocol_subtree(document, "x3_triplet_enumeration", "TRIPLET_SET_MISMATCH")

    entropy = document["deferred_entropy"]
    if entropy.get("authorized_now") is not False or entropy.get("current_anchor") is not None or entropy.get("current_target") is not None or entropy.get("current_selection") is not None:
        fail("PREMATURE_ENTROPY_OR_SELECTION", "entropy state is non-null")
    if entropy.get("target_offset_pulses") != 1440 or entropy.get("alternate_or_next_available_target_allowed") is not False:
        fail("ENTROPY_DOMAIN_OR_TARGET_MISMATCH", "future target rule weakened")
    target_rule = entropy.get("target_rule", {})
    target_checks = target_rule.get("required_exact_response", [])
    if "parsed RFC3339 timeStamp in Unix milliseconds equals target_ms exactly; next-closest response is rejected" not in target_checks:
        fail("ENTROPY_DOMAIN_OR_TARGET_MISMATCH", "exact target timestamp check missing")
    if (
        target_rule.get("poll_schedule_seconds_after_target_ms") != [0, 15, 30, 60, 120, 300, 600, 1200, 1800, 3600]
        or target_rule.get("poll_request_count_max") != 10
        or target_rule.get("poll_deadline_ms") != "target_ms + 3600000"
        or target_rule.get("response_or_error_for_every_attempt_preserved") is not True
        or "NO_ALTERNATE_OR_DELAYED_RETRY" not in target_rule.get("after_final_scheduled_attempt_without_exact_valid_pulse", "")
    ):
        fail("ENTROPY_DOMAIN_OR_TARGET_MISMATCH", "target polling/deadline protocol differs")
    response_schema = entropy.get("pulse_response_schema", {})
    if (
        response_schema.get("top_level_exact_keys") != ["pulse"]
        or response_schema.get("timeStamp_raw_encoding") != "strict RFC3339 UTC with exactly millisecond precision and terminal Z"
        or response_schema.get("statusCode_required") != 0
        or response_schema.get("external_statusCode_required") != 0
        or response_schema.get("version_required") != "2.0"
        or response_schema.get("cipherSuite_required") != 0
        or response_schema.get("period_required_ms") != 60000
    ):
        fail("ENTROPY_DOMAIN_OR_TARGET_MISMATCH", "pulse schema or timestamp normalization differs")
    authentication = entropy.get("authentication_and_chain_verification", {})
    normative = entropy.get("normative_source_authority", {})
    if normative != {
        "nist_ir_8213_draft": {
            "url": "https://nvlpubs.nist.gov/nistpubs/ir/2019/NIST.IR.8213-draft.pdf",
            "doi": "10.6028/NIST.IR.8213-draft",
            "bytes_observed_2026_08_22": 762001,
            "sha256_observed_2026_08_22": "6fee39f6cd82d6c1ab219e29bdec77cbf3e07075324ac3202661d7578ee8f183",
            "status": "DRAFT",
        },
        "nist_beacon_2_xsd": {
            "url": "https://csrc.nist.gov/csrc/media/Projects/interoperable-randomness-beacons/documents/certificate/beacon-2.0.xsd",
            "bytes_observed_2026_08_22": 19033,
            "sha256_observed_2026_08_22": "24c5b5b6508c0c33db2cda1902ea7f3b2009224895ba4e3fe275b7f4511675d6",
        },
        "service_status": "NIST Beacon 2.0 Beta / work in progress",
        "x2_must_preserve_exact_source_bytes_and_hashes": True,
        "refetch_drift_can_be_silently_adopted": False,
        "refetch_drift_consequence": "INFRA_INVALID__SEPARATE_SUCCESSOR_PROTOCOL_REVIEW_REQUIRED__NO_SELECTION",
    }:
        fail("ENTROPY_DOMAIN_OR_TARGET_MISMATCH", "NIST draft/schema source authority differs")
    if (
        authentication.get("verifier_implementation_must_be_frozen_before_first_live_search") is not True
        or authentication.get("trust_bundle_exact_bytes_reviewed_before_first_live_search") is not True
        or authentication.get("certificate_change_between_anchor_and_target_allowed") is not True
        or "both certificateIds enter the selection frame" not in authentication.get("certificate_change_rule", "")
        or "independently recompute" not in authentication.get("output_recomputation_rule", "")
        or "exact DER bytes" not in authentication.get("trust_bundle_required_contents", "")
        or not authentication.get("x2_required_offline_vectors")
        or authentication.get("tls_and_nist_service_remain_external_tcb") is not True
    ):
        fail("ENTROPY_DOMAIN_OR_TARGET_MISMATCH", "beacon authentication or TCB boundary differs")
    anchor = entropy.get("anchor_rule", {})
    if (
        "strictly greater" not in anchor.get("acceptance", "")
        or "previous parsed timeStamp <= not_before_ms < anchor parsed timeStamp" not in anchor.get("acceptance", "")
        or "exactly one entry whose type is previous" not in anchor.get("previous_link_rule", "")
        or "equals the fetched previous pulse outputValue" not in anchor.get("previous_link_rule", "")
    ):
        fail("ENTROPY_DOMAIN_OR_TARGET_MISMATCH", "first-next anchor or previous-output binding differs")
    mapping = entropy.get("selection_encoding", {})
    if (
        mapping.get("hash") != "SHA-256"
        or mapping.get("frame_magic_hex") != "5254444c3537393353454c0001"
        or mapping.get("field_order") != ENTROPY_FIELD_ORDER
        or mapping.get("counter_start") != 0
        or mapping.get("counter_step") != 1
        or mapping.get("counter_max") != (1 << 64) - 1
    ):
        fail("ENTROPY_DOMAIN_OR_TARGET_MISMATCH", "selection mapping differs")
    kat = entropy.get("known_answer_test", {})
    inputs = kat.get("inputs")
    if not isinstance(inputs, dict):
        fail("ENTROPY_DOMAIN_OR_TARGET_MISMATCH", "entropy known-answer inputs missing")
    frame = build_entropy_frame(inputs, mapping.get("field_order"))
    digest = sha256_bytes(frame)
    expected = kat.get("expected", {})
    n = expected.get("n")
    if type(n) is not int or n != 7:
        fail("ENTROPY_DOMAIN_OR_TARGET_MISMATCH", "known-answer N differs")
    limit = ((1 << 256) // n) * n
    x = int(digest, 16)
    if (
        kat.get("kat_id") != "goal5793-selection-tlv-v1-counter0"
        or kat.get("synthetic_not_beacon_entropy") is not True
        or expected.get("field_count") != len(ENTROPY_FIELD_ORDER)
        or expected.get("frame_bytes") != len(frame)
        or expected.get("frame_sha256") != digest
        or expected.get("x_decimal") != str(x)
        or expected.get("threshold_hex") != f"{limit:064x}"
        or expected.get("accepted") is not True
        or x >= limit
        or expected.get("selected_zero_based_index") != x % n
    ):
        fail("ENTROPY_DOMAIN_OR_TARGET_MISMATCH", "entropy known-answer test differs")
    boundary = entropy.get("rejection_boundary_test", {})
    sequence = boundary.get("synthetic_digest_sequence")
    if (
        boundary.get("n") != 7
        or boundary.get("threshold_hex") != f"{limit:064x}"
        or sequence != [f"{limit:064x}", f"{10:064x}"]
        or boundary.get("expected") != ["REJECT_X_EQUALS_THRESHOLD", "ACCEPT_INDEX_3"]
        or int(sequence[0], 16) < limit
        or int(sequence[1], 16) >= limit
        or int(sequence[1], 16) % 7 != 3
    ):
        fail("ENTROPY_DOMAIN_OR_TARGET_MISMATCH", "rejection-boundary test differs")
    cardinality = entropy.get("cardinality_known_answer_tests", {})
    if cardinality != {
        "n_zero": {
            "input_triplet_count": 0,
            "beacon_request_count": 0,
            "hash_evaluation_count": 0,
            "selected_index": None,
            "terminal": "TERMINAL_NEGATIVE__NO_BEACON_REQUEST__NO_HASH__NO_SELECTION__NO_RESCUE",
        },
        "n_one": {
            "input_triplet_count": 1,
            "anchor_and_exact_target_authentication_required": True,
            "counter": 0,
            "hash_evaluation_count": 1,
            "selected_index": 0,
            "returned_digest_must_be_recorded": True,
        },
        "counter_exhaustion": {
            "last_counter": (1 << 64) - 1,
            "next_counter_allowed": False,
            "selected_index": None,
            "terminal": "TERMINAL_INFRASTRUCTURE_FAILURE__NO_FALLBACK",
        },
    }:
        fail("ENTROPY_DOMAIN_OR_TARGET_MISMATCH", "N=0/N=1/counter-exhaustion KAT differs")
    _require_protocol_subtree(document, "deferred_entropy", "ENTROPY_DOMAIN_OR_TARGET_MISMATCH")

    post = document["postselection_input_and_implementation_freeze"]
    if post.get("replacement_row_or_candidate_allowed") is not False or post.get("selected_candidate_science_projection_change_allowed") is not False:
        fail("POST_OUTCOME_RESCUE", "candidate replacement or science mutation enabled")
    if post.get("result_dependent_validity_allowed") is not False:
        fail("OUTCOME_DEPENDENT_VALIDITY", "result-dependent invalidity enabled")
    _require_protocol_subtree(document, "postselection_input_and_implementation_freeze", "POST_OUTCOME_RESCUE")

    friction = document["structural_friction_ledger"]
    record_schema = friction.get("per_metric_record_schema", {})
    if (
        friction.get("measurement_spec_and_implementation_must_be_frozen_reviewed_and_owner_closed_in_x2_before_first_live_search") is not True
        or "private API call count and exact call sites" not in friction.get("required_for_all_three_rows_including_failures", [])
        or friction.get("required_for_every_attempt_successor_and_abandoned_lineage") is not True
        or friction.get("append_only_lineage_ids_and_predecessor_successor_links_required") is not True
        or "every attempt, successor and abandoned lineage" not in friction.get("denominator", "")
        or "no dropped or replaced lineage" not in friction.get("denominator", "")
        or set(record_schema) != {"VALUE", "NA", "bool_int_float_aliases_allowed", "extra_or_missing_keys_allowed"}
        or record_schema.get("bool_int_float_aliases_allowed") is not False
        or record_schema.get("extra_or_missing_keys_allowed") is not False
        or record_schema.get("VALUE", {}).get("reason") is not None
        or record_schema.get("NA", {}).get("value") is not None
        or "available_count, na_count and total_lineage_count" not in friction.get("per_metric_denominator_rule", "")
        or friction.get("cross_metric_aggregation_over_different_availability_sets_allowed") is not False
        or "NA_AMBIGUOUS_AUTHOR_CODE" not in friction.get("missingness_rules", {}).get("multiple_or_ambiguous_author_baselines", "")
    ):
        fail("FRICTION_LEDGER_MISMATCH", "friction ledger denominator/fields weakened")
    if friction.get("usability_study_count") != 0 or friction.get("supports_easy_or_better_than_cuda_claim") is not False:
        fail("USABILITY_OVERCLAIM", "usability claim enabled")
    _require_protocol_subtree(document, "structural_friction_ledger", "FRICTION_LEDGER_MISMATCH")
    lint = document["claim_lint"]
    if not {"unseen", "blind", "held-out", "held out", "literature-complete", "awkward", "simpler", "less code", "lower friction", "reduces burden"}.issubset(set(lint.get("forbidden_unqualified_terms", []))):
        fail("EXPOSURE_CLAIM_OVERREACH", "claim lint weakened")
    _require_protocol_subtree(document, "claim_lint", "EXPOSURE_CLAIM_OVERREACH")

    review_dag = document["external_review_and_absorption_dag"]
    if (
        review_dag.get("current_formal_output_count") != 8
        or review_dag.get("single_cfr_path") != CFR_PATH.relative_to(ROOT).as_posix()
        or review_dag.get("reviewer_receives_exactly_one_file") is not True
        or review_dag.get("separate_packet_exists_or_is_sent") is not False
        or review_dag.get("returned_review_required") != {"verdict_p0": 0, "verdict_p1": 0, "review_file_identity_pinned": True}
        or "owner send receipt" not in review_dag.get("dependency_order", [])
        or set(review_dag.get("owner_closure_required_exact_bindings", [])) != {"CFR", "root result", "independent audit", "owner send receipt", "returned review"}
        or review_dag.get("owner_closure_may_authorize") != "X1 generic-examiner, registry-derivation, environment and shared-native work only"
        or review_dag.get("state_or_filename_alone_never_authorizes_transition") is not True
    ):
        fail("STAGE_PREDECESSOR_UNSATISFIED", "external-review/owner-absorption DAG differs")
    _require_protocol_subtree(document, "external_review_and_absorption_dag", "STAGE_PREDECESSOR_UNSATISFIED")

    permanent = document["permanent_goal5793_invariants"]
    if permanent != {
        "goal5793_pod_or_ssh_allowed_ever": False,
        "registered_or_performance_timing_count_required": 0,
        "product_src_native_family_role_opcode_rule_facade_change_allowed": False,
        "candidate_app_code_must_remain_outside_src": True,
        "home_gpu_if_ever_requires_separate_external_review_and_owner_authorization": True,
        "home_gpu_scope_if_ever_authorized": "functional true-OptiX only; zero registered or performance timing",
        "valid_scientific_failure_can_relax_an_invariant": False,
    }:
        fail("REGISTRY_DERIVATION_OR_CORE_DRIFT", "permanent Goal5793 invariants differ")
    expected_authorization_keys = {
        "authorizes_generic_examiner_implementation", "authorizes_environment_or_shared_native_materialization",
        "authorizes_systematic_search", "authorizes_entropy_anchor_or_draw", "authorizes_candidate_selection",
        "authorizes_candidate_implementation", "authorizes_candidate_execution", "authorizes_product_or_src_change",
        "authorizes_gpu_home_pod_ssh", "authorizes_worker_or_timing", "authorizes_external_contact",
        "authorizes_publication_or_submission",
    }
    if set(document["authorization"]) != expected_authorization_keys or any(value is not False for value in document["authorization"].values()):
        fail("STAGE_PREDECESSOR_UNSATISFIED", "protocol authorization keyset/value differs")
    if EXPECTED_PROTOCOL_AUTHORITY_SHA256 != "PENDING" and seal_value != EXPECTED_PROTOCOL_AUTHORITY_SHA256:
        fail("EXPANSION_PROTOCOL_DRIFT", "protocol differs from independently pinned prewrite seal")


def validate_result(
    document: dict[str, Any],
    source: dict[str, Any],
    candidates: dict[str, Any],
    protocol: dict[str, Any],
    *,
    virtual_files: dict[Path, bytes] | None = None,
) -> None:
    expected_keys = {
        "schema", "result_sha256", "goal", "date", "status", "predecessor",
        "predecessor_internal_seal", "supporting_artifacts", "authoring_tools", "current_result",
        "transaction_commit_marker", "next_gate_requested_not_authorized", "single_external_review_entrypoint",
        "claim_boundary", "authorization", "permanent_goal5793_invariants",
    }
    if set(document) != expected_keys:
        fail("RESULT_OR_BINDING_MISMATCH", "root result top-level key set differs")
    verify_seal(document, "result_sha256")
    if (
        document.get("schema") != "rtdl.goal5793.s0.preregistration_result.v1"
        or document.get("goal") != 5793
        or document.get("date") != DATE
        or document.get("status") != "FROZEN_35_ROW_REQUALIFICATION__ZERO_QUALIFIED_ROLE_A__ZERO_TRIPLETS__SYSTEMATIC_EXPANSION_REQUIRED__NO_ENTROPY__EXTERNAL_REVIEW_PENDING"
    ):
        fail("RESULT_OR_BINDING_MISMATCH", "root result identity/status differs")
    expected_predecessor = identity(A2_CLOSURE, virtual_files)
    if document.get("predecessor") != expected_predecessor or document.get("predecessor_internal_seal") != "650de991134431cebe1b9d66273a6283116209e6d1363a4cbf98421bfad03aa4":
        fail("RESULT_OR_BINDING_MISMATCH", "A2 closure binding differs")
    expected_support = [identity(path, virtual_files) for path in (SOURCE_PATH, CANDIDATE_PATH, PROTOCOL_PATH, REPORT_PATH, SELF_REVIEW_PATH)]
    if document.get("supporting_artifacts") != expected_support:
        fail("RESULT_OR_BINDING_MISMATCH", "supporting artifact identities differ")
    tool_paths = [
        ROOT / "scripts/goal5793_build_s0_preregistration.py",
        ROOT / "scripts/goal5793_audit_s0_preregistration.py",
        ROOT / "tests/goal5793_s0_preregistration_test.py",
    ]
    if document.get("authoring_tools") != [identity(path, virtual_files) for path in tool_paths]:
        fail("RESULT_OR_BINDING_MISMATCH", "authoring tool identities differ")
    expected_current = {
        "declared_product_native_source_zero_drift_file_count": 326,
        "known_candidate_rows": 35,
        "excluded_rows": 30,
        "source_gap_analyzed_permanently_ineligible_rows": 5,
        "qualified_role_a_rows": 0,
        "eligible_ordered_triplets": 0,
        "systematic_search_execution_count": 0,
        "entropy_draw_count": 0,
        "selected_candidate_count": 0,
        "candidate_implementation_count": 0,
        "exam_count": 0,
    }
    if document.get("current_result") != expected_current:
        fail("RESULT_OR_BINDING_MISMATCH", "root result counts differ")
    if document.get("transaction_commit_marker") != {
        "result_is_last_create_only_output": True,
        "supporting_artifact_count": 5,
        "complete_transaction_requires_result_and_all_supporting_identities": True,
    }:
        fail("RESULT_OR_BINDING_MISMATCH", "transaction marker differs")
    if document.get("next_gate_requested_not_authorized") != "external review P0=0/P1=0 plus owner absorption may authorize X1 generic-examiner/registry/environment/shared-native work only":
        fail("STAGE_PREDECESSOR_UNSATISFIED", "next-gate request differs")
    expected_claim_boundary = {
        "generalization_claimed": False,
        "held_out_or_unseen_claimed": False,
        "usability_claimed": False,
        "soundness_or_completeness_claimed": False,
        "third_family_claimed": False,
        "all_path_gate_claimed": False,
        "production_claimed": False,
        "performance_claimed": False,
        "goal5793_scientific_result_claimed": False,
        "literature_complete_claimed": False,
        "geometry_family_generalization_claimed": False,
    }
    if document.get("claim_boundary") != expected_claim_boundary:
        fail("USABILITY_OVERCLAIM", "root claim boundary contains true")
    expected_authorization = {
        "authorizes_generic_examiner_implementation": False,
        "authorizes_registry_or_environment_materialization": False,
        "authorizes_systematic_search": False,
        "authorizes_entropy": False,
        "authorizes_candidate_selection": False,
        "authorizes_candidate_implementation": False,
        "authorizes_candidate_execution": False,
        "authorizes_product_checker_native_app_change": False,
        "authorizes_gpu_home_pod_ssh": False,
        "authorizes_worker_or_timing": False,
        "authorizes_external_reviewer_contact": False,
        "authorizes_public_release_publication_or_submission": False,
    }
    if document.get("authorization") != expected_authorization:
        fail("STAGE_PREDECESSOR_UNSATISFIED", "root authorization contains true")
    if document.get("permanent_goal5793_invariants") != {
        "goal5793_pod_or_ssh_allowed_ever": False,
        "registered_or_performance_timing_count_required": 0,
        "product_src_native_family_role_opcode_rule_facade_change_allowed": False,
    }:
        fail("REGISTRY_DERIVATION_OR_CORE_DRIFT", "root permanent invariants differ")
    if document.get("single_external_review_entrypoint") != CFR_PATH.relative_to(ROOT).as_posix():
        fail("RESULT_OR_BINDING_MISMATCH", "single CFR path differs")
    # Cross-document scientific counts are checked directly rather than trusted.
    if source["declared_product_native_source_zero_drift_authority"]["summary"] != COMPLETE_SUMMARY:
        fail("RESULT_OR_BINDING_MISMATCH", "source/result crossbind differs")
    if candidates["counts"] != EXPECTED_COUNTS or protocol["current_literals"]["qualified_role_a_count"] != 0:
        fail("RESULT_OR_BINDING_MISMATCH", "candidate/protocol/result crossbind differs")


def validate_claim_text(report_text: str, self_review_text: str) -> None:
    if sha256_bytes(report_text.encode("utf-8")) != EXPECTED_REPORT_FILE_SHA256:
        fail("EXPOSURE_CLAIM_OVERREACH", "technical report differs from the independently pinned exact claim surface")
    if sha256_bytes(self_review_text.encode("utf-8")) != EXPECTED_SELF_REVIEW_FILE_SHA256:
        fail("EXPOSURE_CLAIM_OVERREACH", "self-review differs from the independently pinned exact claim surface")
    combined = report_text + "\n" + self_review_text
    forbidden_positive = [
        r"\b159 rejections\b",
        r"\b159 negative attacks\b",
        r"\b(candidates?|catalog) (are|is) unseen\b",
        r"\bblind evaluation\b",
        r"\bheld[- ]out from (the )?(checker )?design\b",
        r"\bheld[- ]out\b",
        r"\bliterature[- ]complete\b",
        r"\bcomplete literature\b",
        r"\bgeometry-family generalization\b",
        r"\beasier than (CUDA|OptiX)\b",
        r"\bproduction[- ]ready\b",
    ]
    for pattern in forbidden_positive:
        if re.search(pattern, combined, flags=re.IGNORECASE):
            fail("EXPOSURE_CLAIM_OVERREACH", f"forbidden claim text: {pattern}")
    required = [
        "zero qualified Role-A",
        "zero valid ordered triplets",
        "fully enumerated 35-row author-seen legacy catalog; permanently selection-ineligible",
        "not a human usability study",
        "A2's five-program checker is a historical regression mechanism",
        "permanently selection-ineligible",
        "query-defined, post-examiner-frozen, existing-family bounded compositional generalization experiment",
        "Goal5793 permanently allows no POD/SSH",
    ]
    for phrase in required:
        if phrase not in combined:
            fail("RESULT_OR_BINDING_MISMATCH", f"required disclosure missing: {phrase}")


def validate_documents(
    source: dict[str, Any],
    candidates: dict[str, Any],
    protocol: dict[str, Any],
    result: dict[str, Any],
    report_text: str,
    self_review_text: str,
    *,
    compare_live_source: bool = True,
    virtual_files: dict[Path, bytes] | None = None,
) -> None:
    validate_source(source, compare_live=compare_live_source)
    validate_candidates(candidates)
    validate_protocol(protocol)
    validate_result(result, source, candidates, protocol, virtual_files=virtual_files)
    validate_claim_text(report_text, self_review_text)


def load_documents(
    virtual_files: dict[Path, bytes] | None = None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], str, str]:
    def read(path: Path) -> bytes:
        return virtual_files[path] if virtual_files is not None and path in virtual_files else path.read_bytes()

    return (
        json.loads(read(SOURCE_PATH).decode("utf-8")),
        json.loads(read(CANDIDATE_PATH).decode("utf-8")),
        json.loads(read(PROTOCOL_PATH).decode("utf-8")),
        json.loads(read(RESULT_PATH).decode("utf-8")),
        read(REPORT_PATH).decode("utf-8"),
        read(SELF_REVIEW_PATH).decode("utf-8"),
    )


def json_bytes(document: dict[str, Any]) -> bytes:
    return json.dumps(
        document,
        sort_keys=True,
        indent=2,
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8") + b"\n"


def build_audit_document(virtual_files: dict[Path, bytes] | None = None) -> dict[str, Any]:
    source, candidates, protocol, result, report_text, self_review_text = load_documents(virtual_files)
    validate_documents(
        source,
        candidates,
        protocol,
        result,
        report_text,
        self_review_text,
        virtual_files=virtual_files,
    )
    document = {
        "schema": "rtdl.goal5793.s0.independent_audit.v1",
        "goal": 5793,
        "date": DATE,
        "status": "PASS__326_SOURCE_ROWS__35_CANDIDATES__ZERO_ROLE_A__ZERO_TRIPLETS__NO_ENTROPY_OR_AUTHORIZATION",
        "inputs": [identity(path, virtual_files) for path in (SOURCE_PATH, CANDIDATE_PATH, PROTOCOL_PATH, REPORT_PATH, SELF_REVIEW_PATH, RESULT_PATH)],
        "checks": {
            "source_rows_rehashed": 326,
            "source_rows_mismatch": 0,
            "critical_explanatory_rows_rehashed": 41,
            "critical_manifest_claimed_complete": False,
            "candidate_rows_reconstructed": 35,
            "candidate_identity_mismatch": 0,
            "historical_git_blobs_rehashed": 2,
            "goal5753_exact_35_identity_exposure_preserved": True,
            "goal519_521_32_family_roadmap_exposure_preserved": True,
            "excluded_rows": 30,
            "source_gap_analyzed_permanently_ineligible_rows": 5,
            "qualified_role_a_rows": 0,
            "eligible_ordered_triplets": 0,
            "systematic_search_execution_count": 0,
            "entropy_draw_count": 0,
            "selected_triplet": None,
            "candidate_implementation_count": 0,
            "exam_count": 0,
            "hostile_fail_id_count": 20,
        },
        "next_gate": "owner-selected external review of the single CFR; P0=0/P1=0 plus append-only owner closure may authorize X1 examiner/environment work only",
        "claim_boundary": {
            "generalization_claimed": False,
            "usability_claimed": False,
            "unseen_or_blind_claimed": False,
            "source_complete_candidate_pool_claimed": False,
            "scientific_exam_result_claimed": False,
        },
        "authorization": {
            "authorizes_external_contact": False,
            "authorizes_x1_implementation": False,
            "authorizes_search": False,
            "authorizes_entropy_or_selection": False,
            "authorizes_candidate_implementation_or_execution": False,
            "authorizes_product_gpu_pod_worker_timing": False,
            "authorizes_publication_or_submission": False,
        },
    }
    body = dict(document)
    document["audit_sha256"] = sha256_bytes(canonical_bytes(body))
    return document


def render_cfr(audit_data: bytes, virtual_files: dict[Path, bytes] | None = None) -> bytes:
    paths = [SOURCE_PATH, CANDIDATE_PATH, PROTOCOL_PATH, REPORT_PATH, SELF_REVIEW_PATH, RESULT_PATH]
    rows = [identity(path, virtual_files) for path in paths]
    audit_identity = {
        "path": AUDIT_PATH.relative_to(ROOT).as_posix(),
        "bytes": len(audit_data),
        "file_sha256": sha256_bytes(audit_data),
    }
    rows.append(audit_identity)
    table = "\n".join(f"| `{row['path']}` | {row['bytes']} | `{row['file_sha256']}` |" for row in rows)
    text = f"""# Call for review: Goal5793 S0 preregistration and generic-examiner entry

**SEND ONLY THIS FILE TO THE REVIEWER.** It is the single review entrypoint. There is no separate packet to send.

## Requested ruling

Does exact S0 honestly freeze the complete declared 326-file product/native-source zero-drift code surface (not a complete package/build closure), preserve all 35 pre-exposed legacy rows as permanently selection-ineligible, mechanically reproduce zero qualified Role-A expected-admission candidates and zero ordered triplets, therefore forbid entropy and manual rescue, and request only candidate-agnostic examiner plus exact environment/shared-native work before any systematic expansion search?

Please return one review at:
`history/internal_docs/review_goal5793_s0_preregistration_and_generic_examiner_entry_20260822.md`

Required verdict fields: `P0`, `P1`, `P2`, `P3`; whether S0 is accepted; and whether **X1 only** may be considered after append-only owner absorption. Acceptance must not authorize search, entropy, candidate selection, candidate implementation/execution, GPU/POD, publication or submission.

## Exact reviewed roots

| Path | Bytes | SHA-256 |
|---|---:|---|
{table}

## Facts the review must independently reconstruct

1. Rehash the 326 exact rows (14,587,884 bytes; row digest `f26b55e6d9a120a34882e9c7ada44df5503f1f90f83db893d1d6957ab0202f97`). Confirm this is complete only for the declared `src/**` plus four-file code surface, not package/build/toolchain closure; confirm that the 41-row digest `f2a8887ac279e71f5425b9ec5ad12b5ce0c258a2e219f254322d101866797138` is explicitly non-complete.
2. Rebuild the 35 exact paper/problem identities from Goal5753, then rehash the Goal519 and Goal521 Git blobs and independently confirm their 32 normalized workload-family projection. Goal5753 proves paper-identity exposure; Goal519/521 prove family-level roadmap/feasibility treatment, not paper-specific source review. Reject unseen/blind or unqualified historical-evaluation wording.
3. Reproduce 30 excluded rows, five source-gap-analyzed rows that are nevertheless permanently selection-ineligible, zero qualified Role A, zero selection-eligible rows and an empty ordered-triplet set. Missing source must remain visible and no old row may reenter after a later query match.
4. Confirm the current state has no generic examiner, no exact environment/shared-native authority, zero search executions, zero entropy draws, no anchor, no selection, zero implementations and zero exams.
5. Confirm the only defensible successor ordering: external S0 closure -> candidate-agnostic examiner/registry/environment/shared-native review -> offline harvester plus NIST verifier/selection-client review -> one full search -> every row's pre-entropy science projection plus triplet review -> future exact NIST anchor/target -> selected-input preregistration -> implementation -> exams.
6. Confirm that A2's hard-coded five-program checker is historical regression evidence only and cannot decide a new candidate.
7. Confirm that candidate identity, role and expected disposition are forbidden examiner inputs, and that product/independent disagreement becomes infrastructure-invalid rather than a favorable verdict choice.
8. Confirm the structural-friction ledger covers failures and private calls but supports no usability or better-than-CUDA/OptiX claim.
9. Confirm all future eligible rows must freeze source/oracle, semantic obligations, physical guarantees, categorical expected disposition and role projection before triplet enumeration or entropy, and that Goal5793 permanently forbids POD/SSH, product/core changes and registered/performance timing.
10. Confirm X1 must freeze a declared project-exposure registry from repository history, predecessor archive contents and owner disclosures; a nonmatch means only “not matched to that registry,” never unseen/blind/held out. Any match is permanently ineligible.
11. Confirm X2 freezes a single-threaded 22-query order, complete pagination, uniform full-text identity checking and deterministic transitive DOI/arXiv/OpenAlex deduplication. A fallback digest is never an equivalence edge: every repeated fallback-only or cross-component identity is selection-ineligible, not silently merged or manually resolved.
12. Independently reconstruct the 21-field TLV selection KAT (`1345` bytes, SHA-256 `a5904e12a9795bdc984b73095cc38cc670328fbb074a8db5e736c1fff0d4d92e`, N=7, index=2), the rejection-boundary vector and the N=0/N=1 branches. Confirm selection binds the X1, X2 and X3 closures, complete row table, complete pre-entropy science table and ordered-triplet table.
13. Confirm the NIST verifier is frozen before live search, independently verifies trust path, certificate identifier/validity, signature serialization, output recomputation and previous/precommitment chain; the time endpoint’s next-closest response is rejected unless the timestamp equals the exact target. Polling uses one exact URI and the fixed one-hour schedule only.
14. Confirm the reviewer receives exactly this one CFR file, with no separate packet. A later owner send receipt must pin this CFR's exact bytes and SHA-256; returned review and append-only owner closure must bind the CFR, result, audit and receipt and may authorize X1 only.

## Required hostile mutations

Run or independently reproduce all 20 stable fail classes:

- H01 `ZERO_DRIFT_AUTHORITY_MISMATCH`: remove/change/add a 326-row source.
- H02 `EXPLANATORY_SUBMANIFEST_OVERCLAIM`: mark the 41-row list complete.
- H03 `UNIVERSE_ROW_SET_MISMATCH`: delete or replace a candidate row.
- H04 `SOURCE_GAP_HYGIENE_FAILURE`: hide a source gap or substitute an abstract for unavailable full source.
- H05 `EXPOSURE_AUTHORITY_MISMATCH`: hide catalog/feasibility exposure or replace historical blobs with moving files.
- H06 `FORBIDDEN_SELECTION_FEATURE_DEPENDENCE`: make performance/ease affect eligibility.
- H07 `ROLE_REQUALIFICATION_MISMATCH`: fabricate Role A, relax its expected-COMPATIBLE predicate or enable selection.
- H08 `TRIPLET_SET_MISMATCH`: add a current triplet.
- H09 `PREMATURE_ENTROPY_OR_SELECTION`: set anchor/output/selection non-null.
- H10 `STAGE_PREDECESSOR_UNSATISFIED`: enable X1/search/entropy prematurely.
- H11 `SEARCH_BEFORE_EXAMINER_FREEZE`: reorder search before examiner closure.
- H12 `EXPANSION_PROTOCOL_DRIFT`: change query/date/dedup/screening or allow a second round.
- H13 `EXAMINER_METADATA_DEPENDENCE`: allow candidate identity/expected outcome in decision code.
- H14 `REGISTRY_DERIVATION_OR_CORE_DRIFT`: permit post-search semantic/family/template/core changes.
- H15 `ENTROPY_DOMAIN_OR_TARGET_MISMATCH`: change the pre-search-frozen verifier/mapping, accept a next-closest timestamp, wrong chain/index/URI/certificate, old pulse, alternate pulse or changed target.
- H16 `POST_OUTCOME_RESCUE`: permit replacement, row drop or valid-result rescue.
- H17 `OUTCOME_DEPENDENT_VALIDITY`: let expected/verdict mismatch define infrastructure invalidity.
- H18 `FRICTION_LEDGER_MISMATCH`: omit failures/private API or alter the denominator.
- H19 `USABILITY_OVERCLAIM`: claim easy/productive/better-than-CUDA without a study.
- H20 `EXPOSURE_CLAIM_OVERREACH`: call the catalog unseen, blind or held out from design.

## Claim boundary to preserve

This is a preregistered path to a query-defined, post-examiner-frozen, existing-family bounded compositional generalization experiment, not generalization evidence. It proves no soundness, completeness, false-rejection rate, third family, all-path gating, usability, performance or production result. A valid rejection, UNKNOWN, failure or 0/3 is publishable and terminal; it cannot trigger candidate replacement or product rescue. Goal5793 permanently permits no POD/SSH, product/core changes or registered/performance timing.
"""
    return text.encode("utf-8")


def build_outputs(virtual_files: dict[Path, bytes] | None = None) -> dict[Path, bytes]:
    audit = build_audit_document(virtual_files)
    audit_data = json_bytes(audit)
    cfr_data = render_cfr(audit_data, virtual_files)
    return {AUDIT_PATH: audit_data, CFR_PATH: cfr_data}


def write_create_only(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(data)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="create audit and the single CFR")
    args = parser.parse_args()
    outputs = build_outputs()
    if args.write:
        for path in outputs:
            if path.exists():
                raise FileExistsError(f"create-only output already exists: {path}")
        for path, data in outputs.items():
            write_create_only(path, data)
    print(
        json.dumps(
            {
                "outputs": [
                    {
                        "path": path.relative_to(ROOT).as_posix(),
                        "bytes": len(data),
                        "sha256": sha256_bytes(data),
                    }
                    for path, data in outputs.items()
                ],
                "write_performed": args.write,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
    )


if __name__ == "__main__":
    main()
