from __future__ import annotations

import hashlib
import json
import sys
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import goal5789_independent_compatibility_checker as checker


CERTIFICATE = (
    ROOT
    / "history/internal_docs/goal5789_contract_evidence_20260816/certificates/triangle__com_dblp__rt_2a1.json"
)
AUTHORITY = (
    ROOT
    / "history/internal_docs/goal5789_contract_evidence_20260816/AUTHORITY_BUNDLE.json"
)
STORED_RESULT = (
    ROOT
    / "history/internal_docs/goal5789_contract_evidence_20260816/results/triangle__com_dblp__rt_2a1.json"
)
CHECKER = ROOT / "scripts/goal5789_independent_compatibility_checker.py"

EXPECTED = {
    CERTIFICATE: "cf20c8e1235e73ae2501a4783a96326911575af77ebc4bd267eda376aa723e2e",
    AUTHORITY: "dc38719058133c30052ccfad0087522999c46f07e0d52d25a5b5520b93bd776f",
    STORED_RESULT: "c742f959c6c60ffb74646e4021b5943234b33c51e7c684f436cd6c93be3d5a02",
    CHECKER: "abb1f1575af824cc37e9d9984aff8679f79cb89f4ad7ed2792ede5a3db75ac2e",
}


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"JSON object required: {path}")
    return value


def _decision_projection(result: dict[str, object]) -> dict[str, object]:
    return {
        key: result[key]
        for key in (
            "target_capable",
            "semantic_compatible",
            "instance_admissible",
            "performance",
            "canonical_resolution",
            "reference_admission_complete",
            "executable",
            "execution_authorized",
            "authority_boundary",
        )
    }


def main() -> None:
    for path, expected in EXPECTED.items():
        if _sha(path.read_bytes()) != expected:
            raise RuntimeError(f"frozen input identity mismatch: {path}")

    certificate = _load(CERTIFICATE)
    authority = _load(AUTHORITY)
    stored_result = _load(STORED_RESULT)
    baseline = checker.evaluate_certificate(certificate, authority)
    if baseline != stored_result:
        raise RuntimeError("baseline checker replay differs from stored result")

    mutated = deepcopy(certificate)
    observed_roles: list[str] = []
    original_effects: dict[str, list[str]] = {}
    for row in mutated["callback_contract"]["roles"]:
        role = row["role"]
        effects = row["effects"]
        if not isinstance(role, str) or not isinstance(effects, list) or not effects:
            raise RuntimeError("unexpected frozen role/effect shape")
        observed_roles.append(role)
        original_effects[role] = list(effects)
        row["effects"] = []
    mutated["certificate_sha256"] = checker.certificate_digest(mutated)
    mutated_result = checker.evaluate_certificate(mutated, authority)
    if _decision_projection(mutated_result) != _decision_projection(baseline):
        raise RuntimeError("empty role effects unexpectedly changed a judgment")
    if mutated_result["semantic_compatible"]["verdict"] != checker.COMPATIBLE:
        raise RuntimeError("empty role effects did not remain compatible")
    if mutated_result["reference_admission_complete"] is not True:
        raise RuntimeError("empty role effects did not remain admitted")

    missing_role = deepcopy(certificate)
    missing_role["callback_contract"]["roles"] = [
        row
        for row in missing_role["callback_contract"]["roles"]
        if row["role"] != "make_ray"
    ]
    missing_role["certificate_sha256"] = checker.certificate_digest(missing_role)
    missing_result = checker.evaluate_certificate(missing_role, authority)
    if missing_result["reference_admission_complete"] is not False:
        raise RuntimeError("missing required role unexpectedly remained admitted")
    if not any(
        "missing_geometry_role:make_ray" in reason
        for reason in missing_result["semantic_compatible"]["reasons"]
    ):
        raise RuntimeError("missing role did not fail for the expected rule")

    print(
        json.dumps(
            {
                "status": "PASS__CALLBACK_ROLE_NAMES_ARE_DECISIVE_BUT_ALLOWED_EFFECT_CONTENT_IS_NOT_INDEPENDENTLY_BOUND",
                "mutated_roles": observed_roles,
                "original_effects": original_effects,
                "mutated_effects": {role: [] for role in observed_roles},
                "ir_sha256_unchanged": True,
                "effect_digest_unchanged": True,
                "certificate_resealed": True,
                "baseline_and_mutated_decision_projection_equal": True,
                "mutated_reference_admission_complete": True,
                "missing_required_role_rejected": True,
                "technical_gap": "CERTIFICATE_ROLE_EFFECT_SUMMARY_IS_NOT_CROSS_BOUND_TO_AN_INDEPENDENT_CALLBACK_IR_AUTHORITY",
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
