from __future__ import annotations

from enum import Enum
import re
from typing import Mapping


PROBE_SCHEMA = "rtdl.goal5757.lane_probe_result.v1"


class LaneClassification(str, Enum):
    SUPPORTED_NOW = "SUPPORTED_NOW"
    PARTNER_ONLY_GAP = "PARTNER_ONLY_GAP"
    MISSING_GENERIC_SEMANTIC = "MISSING_GENERIC_SEMANTIC"


class LaneProbeContractError(ValueError):
    def __init__(self, code: str, path: str, message: str) -> None:
        self.code = code
        self.path = path
        self.message = message
        super().__init__(f"Goal5757 lane probe rejected: {code}@{path}: {message}")


COMMON_KEYS = {
    "schema", "app_id", "lane_id", "qualification", "classification",
    "contract_freeze_sha256", "callback_source_sha256", "callback_ir_sha256",
    "cpu_oracle_sha256", "cpu_differential_case_count",
    "cpu_differential_mismatch_count", "typed_schema_sha256",
    "canonical_plan_sha256", "canonical_plan_count", "partner_preflight_sha256",
    "target_compile_preflight_sha256", "forbidden_identity_dispatch_hits",
    "fail_closed_stage", "fail_closed_code", "minimal_counterexample_sha256",
    "required_missing_contract", "paper_semantic_evidence_sha256",
    "existing_composition_insufficient_reason", "cross_app_reuse_candidates",
}


def _fail(code: str, path: str, message: str) -> None:
    raise LaneProbeContractError(code, path, message)


def _sha(value: object, path: str, *, optional: bool = False) -> str | None:
    if optional and value is None:
        return None
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        _fail("sha256", path, "lowercase SHA-256 required")
    return value


def _nonempty(value: object, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        _fail("nonempty_string", path, "nonempty string required")
    return value


def _count(value: object, path: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        _fail("nonnegative_integer", path, repr(value))
    return value


def validate_lane_probe(payload: Mapping[str, object]) -> LaneClassification:
    if set(payload) != COMMON_KEYS:
        _fail("closed_shape", "probe", f"expected {sorted(COMMON_KEYS)}, got {sorted(payload)}")
    if payload["schema"] != PROBE_SCHEMA:
        _fail("schema", "schema", str(payload["schema"]))
    _nonempty(payload["app_id"], "app_id")
    _nonempty(payload["lane_id"], "lane_id")
    if payload["qualification"] not in {"AUTHORIZED_PAPER_APP", "CANDIDATE__NOT_PAPER_APP_9"}:
        _fail("qualification", "qualification", str(payload["qualification"]))
    try:
        classification = LaneClassification(payload["classification"])
    except (TypeError, ValueError):
        _fail("classification", "classification", str(payload["classification"]))
        raise AssertionError
    _sha(payload["contract_freeze_sha256"], "contract_freeze_sha256")
    dispatch_hits = _count(payload["forbidden_identity_dispatch_hits"], "forbidden_identity_dispatch_hits")
    if dispatch_hits != 0:
        _fail("identity_dispatch", "forbidden_identity_dispatch_hits", str(dispatch_hits))

    callback_source = _sha(payload["callback_source_sha256"], "callback_source_sha256", optional=True)
    callback_ir = _sha(payload["callback_ir_sha256"], "callback_ir_sha256", optional=True)
    oracle = _sha(payload["cpu_oracle_sha256"], "cpu_oracle_sha256", optional=True)
    cases = _count(payload["cpu_differential_case_count"], "cpu_differential_case_count")
    mismatches = _count(payload["cpu_differential_mismatch_count"], "cpu_differential_mismatch_count")
    typed_schema = _sha(payload["typed_schema_sha256"], "typed_schema_sha256", optional=True)
    plan = _sha(payload["canonical_plan_sha256"], "canonical_plan_sha256", optional=True)
    plan_count = _count(payload["canonical_plan_count"], "canonical_plan_count")
    partner = _sha(payload["partner_preflight_sha256"], "partner_preflight_sha256", optional=True)
    target = _sha(payload["target_compile_preflight_sha256"], "target_compile_preflight_sha256", optional=True)

    failure_fields = (
        payload["fail_closed_stage"], payload["fail_closed_code"],
        payload["minimal_counterexample_sha256"], payload["required_missing_contract"],
        payload["paper_semantic_evidence_sha256"],
        payload["existing_composition_insufficient_reason"],
    )
    reuse = payload["cross_app_reuse_candidates"]
    if not isinstance(reuse, list) or any(not isinstance(item, str) or not item.strip() for item in reuse):
        _fail("reuse_candidates", "cross_app_reuse_candidates", "string array required")

    if classification is LaneClassification.SUPPORTED_NOW:
        if None in {callback_source, callback_ir, oracle, typed_schema, plan, partner, target}:
            _fail("supported_evidence", "probe", "all executable evidence digests required")
        if cases <= 0 or mismatches != 0:
            _fail("cpu_differential", "probe", "positive cases and zero mismatches required")
        if plan_count != 1:
            _fail("canonical_plan_count", "canonical_plan_count", str(plan_count))
        if any(value is not None for value in failure_fields) or reuse:
            _fail("supported_failure_fields", "probe", "supported lane cannot carry gap fields")
        return classification

    if classification is LaneClassification.PARTNER_ONLY_GAP:
        if None in {callback_source, callback_ir, oracle, typed_schema, plan}:
            _fail("partner_gap_semantic_evidence", "probe", "callback/CPU/schema/plan evidence required")
        if cases <= 0 or mismatches != 0 or plan_count != 1:
            _fail("partner_gap_semantic_evidence", "probe", "exact CPU differential and one plan required")
        if partner is not None or target is not None:
            _fail("partner_gap_preflight", "probe", "partner/target success evidence must be absent")
        if payload["fail_closed_stage"] != "partner_boundary":
            _fail("partner_gap_stage", "fail_closed_stage", str(payload["fail_closed_stage"]))
        _nonempty(payload["fail_closed_code"], "fail_closed_code")
        _sha(payload["minimal_counterexample_sha256"], "minimal_counterexample_sha256")
        _nonempty(payload["required_missing_contract"], "required_missing_contract")
        _sha(payload["paper_semantic_evidence_sha256"], "paper_semantic_evidence_sha256")
        _nonempty(payload["existing_composition_insufficient_reason"], "existing_composition_insufficient_reason")
        return classification

    if payload["fail_closed_stage"] not in {"frontend", "verifier", "typed_schema", "canonical_plan"}:
        _fail("semantic_gap_stage", "fail_closed_stage", str(payload["fail_closed_stage"]))
    _nonempty(payload["fail_closed_code"], "fail_closed_code")
    _sha(payload["minimal_counterexample_sha256"], "minimal_counterexample_sha256")
    _nonempty(payload["required_missing_contract"], "required_missing_contract")
    _sha(payload["paper_semantic_evidence_sha256"], "paper_semantic_evidence_sha256")
    _nonempty(payload["existing_composition_insufficient_reason"], "existing_composition_insufficient_reason")
    if partner is not None or target is not None:
        _fail("semantic_gap_partner", "probe", "semantic gap cannot claim partner/target success")
    if payload["fail_closed_stage"] in {"frontend", "verifier"} and any(
        value is not None for value in (callback_ir, typed_schema, plan)
    ):
        _fail("semantic_gap_downstream_evidence", "probe", "downstream evidence after early failure is invalid")
    if payload["fail_closed_stage"] == "typed_schema" and any(value is not None for value in (typed_schema, plan)):
        _fail("semantic_gap_downstream_evidence", "probe", "schema/plan success after schema failure is invalid")
    if payload["fail_closed_stage"] == "canonical_plan" and plan is not None:
        _fail("semantic_gap_downstream_evidence", "probe", "plan success after plan failure is invalid")
    return classification

