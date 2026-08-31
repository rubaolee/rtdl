from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path

from scripts import goal5789_independent_compatibility_checker as checker


ROOT = Path(__file__).resolve().parents[1]
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
        observed = _sha(path.read_bytes())
        if observed != expected:
            raise RuntimeError(f"frozen input identity mismatch: {path}")

    certificate = _load(CERTIFICATE)
    authority = _load(AUTHORITY)
    stored_result = _load(STORED_RESULT)
    baseline = checker.evaluate_certificate(certificate, authority)
    if baseline != stored_result:
        raise RuntimeError("baseline checker replay differs from stored result")
    if certificate["callback_contract"]["total_static_iterations"] != 64:
        raise RuntimeError("unexpected frozen total_static_iterations value")

    mutated = deepcopy(certificate)
    mutated["callback_contract"]["total_static_iterations"] = 1_000_000_000
    mutated["certificate_sha256"] = checker.certificate_digest(mutated)
    mutated_result = checker.evaluate_certificate(mutated, authority)
    if _decision_projection(mutated_result) != _decision_projection(baseline):
        raise RuntimeError("large nonnegative metadata value unexpectedly changed a judgment")
    if mutated_result["semantic_compatible"]["verdict"] != checker.COMPATIBLE:
        raise RuntimeError("large nonnegative metadata value did not remain compatible")
    if mutated_result["reference_admission_complete"] is not True:
        raise RuntimeError("large nonnegative metadata value did not remain admitted")

    negative = deepcopy(certificate)
    negative["callback_contract"]["total_static_iterations"] = -1
    negative["certificate_sha256"] = checker.certificate_digest(negative)
    negative_result = checker.evaluate_certificate(negative, authority)
    if negative_result["reference_admission_complete"] is not False:
        raise RuntimeError("negative value unexpectedly remained admitted")
    if not any(
        "invalid_callback_budget:total_static_iterations" in reason
        for reason in negative_result["semantic_compatible"]["reasons"]
    ):
        raise RuntimeError("negative value did not fail for the expected shape rule")

    print(
        json.dumps(
            {
                "status": "PASS__TOTAL_STATIC_ITERATIONS_IS_NONNEGATIVE_SHAPE_CHECKED_BUT_NOT_DECISION_BOUNDED",
                "baseline_value": 64,
                "adversarial_nonnegative_value": 1_000_000_000,
                "baseline_and_adversarial_decision_projection_equal": True,
                "adversarial_reference_admission_complete": True,
                "negative_value_rejected": True,
                "classification": "AUDIT_METADATA__NOT_A_SEMANTIC_PHYSICAL_TARGET_OR_INSTANCE_JUDGMENT_OBLIGATION",
                "technical_residual": "NO_INDEPENDENT_AUTHORITY_OR_TARGET_UPPER_BOUND_IN_GOAL5789_CHECKER",
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
