#!/usr/bin/env python3
"""Build the exact Goal5793 X2 result/report/self-review and sole CFR."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.goal5793_x1_canonical import canonical_json_bytes, seal_document, sha256_bytes
from scripts import goal5793_x2_build_offline_review_capsule as capsule_builder
from scripts import goal5793_x2_verify_offline_review_capsule as capsule_verifier


ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "history/internal_docs"
DATE = "2026-08-22"
RESULT_NAME = "goal5793_x2_offline_implementation_review_result_20260822.json"
REPORT_NAME = "goal5793_x2_offline_implementation_review_report_20260822.md"
SELF_REVIEW_NAME = "self_review_goal5793_x2_offline_implementation_review_20260822.md"
CFR_NAME = "call_for_review_goal5793_x2_offline_implementation_and_x3_search_entry_20260822.md"
RESULT_DOMAIN = "rtdl.goal5793.x2.offline_implementation_review_result"

CAPSULE_ROOTS = {
    capsule_builder.ARCHIVE_NAME: (7_221_120, "4c64a48a0da52b393b6868a8770be6d3766369d235698132b5f2001f5a429841"),
    capsule_builder.TWIN_NAME: (7_221_120, "4c64a48a0da52b393b6868a8770be6d3766369d235698132b5f2001f5a429841"),
    capsule_builder.MANIFEST_NAME: (22_440, "51cbcaa1a4ed2b9be4f25769f35445a16e6dc08da9163c80bf0decb466048fd8"),
    capsule_builder.AUDIT_NAME: (2_526, "24b7baeae00e6baf3e6927ee0195f5052579544f546c473653eef9e84bc9262f"),
}


def _identity(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {"path": path.relative_to(ROOT).as_posix(), "bytes": len(data), "sha256": sha256_bytes(data)}


def _check_capsule() -> dict[str, Any]:
    for name, (size, digest) in CAPSULE_ROOTS.items():
        data = (HISTORY / name).read_bytes()
        if len(data) != size or sha256_bytes(data) != digest:
            raise RuntimeError(f"X2_CAPSULE_IDENTITY_MISMATCH:{name}")
    if (HISTORY / capsule_builder.ARCHIVE_NAME).read_bytes() != (HISTORY / capsule_builder.TWIN_NAME).read_bytes():
        raise RuntimeError("X2_CAPSULE_TWIN_MISMATCH")
    fresh = capsule_builder.build_outputs()
    for name in CAPSULE_ROOTS:
        if fresh[name] != (HISTORY / name).read_bytes():
            raise RuntimeError(f"X2_CAPSULE_FRESH_REBUILD_MISMATCH:{name}")
    audit = capsule_verifier.verify_archive(HISTORY / capsule_builder.ARCHIVE_NAME)
    if audit.get("audit_sha256") != "2e9f41d6ce601af3924d9299c889dbda1bfa58eb85a28e201b184ede46b77c29":
        raise RuntimeError("X2_CAPSULE_AUDIT_SEAL_MISMATCH")
    return audit


def _report() -> str:
    return """# Goal5793 X2 offline implementation report

## Outcome

X2 is ready for exact-byte external review at **offline implementation only** scope. The compact deterministic capsule is 7,221,120 bytes, its twin is byte-identical, and its standalone standard-library verifier reconstructs the manifest, predecessor identities, generated authorities, synthetic fixtures, hostile cases, and frozen claim boundary.

This result does **not** authorize a live provider search, NIST beacon request, entropy draw, selection, candidate implementation, GPU/SSH/POD work, timing, product change, publication, or submission.

## What is implemented and frozen

- The pinned survey component registers all 186 bibliography entries. Seven have strong identifiers; 179 use conservative normalized title/author/year aliases and remain permanently ineligible as historical exposures. No weak identity is promoted into a selectable candidate.
- The offline harvester, source resolver, author-code resolver, controlled taxonomy, deduplication, role derivation, ordered-triplet enumeration, structural-friction ledger, and selection-frame logic are candidate-agnostic and operate only on synthetic/offline fixtures.
- Exact recovered NISTIR 8213 and Beacon 2.0 XSD bytes are included. Three contradictions are explicit: noninteger length prefix, external status serialization, and certificate-ID preimage. The preregistered interpretation uses NISTIR for cryptographic preimages and XSD only for transport/schema; no post-observation variant choice is allowed.
- The cipher-suite-0 verifier implements uint64 framing, exact PEM-byte certificate IDs, RSA PKCS#1 v1.5/SHA-512 signatures, output recomputation, certificate path/validity/key-usage checks, previous-output and precommitment links, and exact-target rejection of the API's possible next-closest response.
- A 1,442-pulse synthetic predecessor/anchor/target chain is fully authenticated. A coherently re-signed middle-link attack and next-closest substitution are rejected. No live NIST trust bundle or pulse was observed.
- Before create-only writes, the capsule-bound Goal5793 X2 test selection ran 107/107 successfully. Four additional prewrite review-entry tests validate deterministic document construction, the result seal, all-false authorization, embedded exact bytes, and the single-CFR rule: 111/111 prewrite. After the capsule write, the phase-specific "outputs absent" test is intentionally no longer applicable; stored bytes are instead checked by fresh byte replay and the independent archive audit.

## Scientific boundary

This stage produces **zero generalization results** and **zero usability results**. It closes infrastructure needed for a future prospective test; it does not make the test succeed. The old 35-row catalog remains permanently selection-ineligible, and X2 performs no live expansion search.

The strongest future claim remains limited to query-defined, post-examiner-frozen, existing-family compositional reuse. Even a future three-exam success will not prove soundness, completeness, a false-rejection rate, arbitrary-workload generalization, or third-family generalization.

For usability, the current evidence remains negative/bounded: there is no user study, no developer-time measurement, and no claim that RTDL is easier or more productive than direct CUDA/OptiX. A separate submission gate must still establish at least one non-toy public GPU path and an independent clean-machine cold reproduction; otherwise the paper must avoid positive usability claims.

## Remaining live boundary

The offline synthetic trust root is not a NIST trust root. Before any future beacon request, a separately reviewed exact live NIST root/intermediate trust bundle and a no-variant-switch interpretation authority are required. The crypto replay is non-hermetic: Python, the standard library, cryptography, and host OS crypto APIs are disclosed TCB components and are not embedded in the capsule.

The only requested next permission is owner closure after a clean returned review, allowing **X3 provider search only** under the already frozen query protocol. Beacon, entropy, selection, candidate work, execution, GPU/SSH/POD, timing, product changes, and publication remain false.
"""


def _self_review() -> str:
    return """# Self-review: Goal5793 X2 offline implementation

## Adversarial conclusion

No positive generalization or usability claim is earned here. X2 is only the frozen, reviewable machinery that prevents future candidate selection and NIST mapping from being steered after outcomes are visible.

The strongest checks are: all 186 historical bibliography entries remain registered; weak identifiers fail toward ineligibility; removal/relabeling/authorization escalation fails; PDF identity runs in a fresh process with a pinned vendored parser; the NISTIR/XSD contradictions are preserved; the 21-field selection KAT and rejection boundary are exact; all 1,442 synthetic pulses are authenticated; a coherently re-signed middle-link attack fails; and next-closest target substitution fails.

## Known ceilings

1. There is no exact live NIST signing trust bundle and no live pulse evidence. The synthetic authority cannot be relabelled as live.
2. The cryptographic runtime is not hermetic. Its Python/stdlib/cryptography/OS TCB is recorded; the capsule does not embed those bytes.
3. Only 7/186 survey entries have strong identifiers. The other 179 are conservatively blocked, not resolved by optimistic matching.
4. No provider search, entropy, selection, candidate implementation, GPU run, timing, generalization exam, user task, or usability study occurred.
5. Passing 107 capsule-bound tests plus 4 prewrite review-entry tests is implementation evidence, not scientific generalization or user productivity evidence.

## Kill conditions for review

Return P1 or worse if the capsule cannot be rebuilt byte-identically; if any source conflict is hidden; if a live authorization becomes true; if weak historical identities can enter selection; if expected outcome/candidate identity controls the offline decision path; if next-closest or unauthenticated pulses can influence the mapping; or if the report converts infrastructure readiness into a generalization/usability claim.
"""


def build_documents() -> dict[str, bytes]:
    audit = _check_capsule()
    report = _report().encode("utf-8")
    self_review = _self_review().encode("utf-8")
    report_id = {"path": f"history/internal_docs/{REPORT_NAME}", "bytes": len(report), "sha256": sha256_bytes(report)}
    self_id = {"path": f"history/internal_docs/{SELF_REVIEW_NAME}", "bytes": len(self_review), "sha256": sha256_bytes(self_review)}
    result: dict[str, Any] = {
        "schema": "rtdl.goal5793.x2.offline_implementation_review_result.v1",
        "date": DATE,
        "status": "READY_FOR_OWNER_CONTROLLED_EXACT_BYTE_EXTERNAL_REVIEW__X2_NOT_YET_ACCEPTED__NO_LIVE_AUTHORIZATION",
        "predecessors": {
            "x1_closure": _identity(HISTORY / "goal5793_x1_postreview_closure_and_x2_offline_entry_20260822.json"),
            "normative_recovery_review": _identity(HISTORY / "review_goal5793_x2_normative_source_recovery_preaction_amendment_v2_20260822.md"),
            "normative_recovery_owner_closure": _identity(HISTORY / "goal5793_x2_normative_source_recovery_owner_closure_20260822.json"),
        },
        "capsule": {
            "archive": _identity(HISTORY / capsule_builder.ARCHIVE_NAME),
            "twin": _identity(HISTORY / capsule_builder.TWIN_NAME),
            "manifest": _identity(HISTORY / capsule_builder.MANIFEST_NAME),
            "audit": _identity(HISTORY / capsule_builder.AUDIT_NAME),
            "archive_twin_byte_identical": True,
            "fresh_rebuild_byte_identical": True,
            "independent_audit_sha256": audit["audit_sha256"],
        },
        "evidence": {
            "prewrite_capsule_bound_x2_test_count": 107,
            "prewrite_capsule_bound_x2_test_pass_count": 107,
            "prewrite_review_entry_test_count": 4,
            "prewrite_review_entry_test_pass_count": 4,
            "prewrite_total_x2_test_count": 111,
            "prewrite_total_x2_test_pass_count": 111,
            "postwrite_phase_specific_absence_tests_applicable": False,
            "postwrite_fresh_capsule_rebuild_byte_identical": True,
            "postwrite_independent_capsule_audit_pass": True,
            "survey_exposure_rows": 186,
            "strong_identifier_rows": 7,
            "conservative_weak_identifier_rows": 179,
            "normative_source_file_count": 2,
            "normative_source_recovery_http_get_count": 2,
            "synthetic_authenticated_pulse_count": 1442,
            "live_provider_search_call_count": 0,
            "live_beacon_call_count": 0,
            "entropy_draw_count": 0,
            "scientific_selection_count": 0,
            "candidate_work_count": 0,
            "gpu_ssh_pod_action_count": 0,
            "registered_or_performance_timing_count": 0,
            "generality_exam_count": 0,
            "usability_study_count": 0,
        },
        "claim_boundary": {
            "x2_offline_implementation_ready_for_review": True,
            "x2_externally_accepted": False,
            "x2_owner_closed": False,
            "exact_live_nist_trust_authority_issued": False,
            "x3_live_search_authorized": False,
            "beacon_entropy_selection_authorized": False,
            "generalization_claim_earned": False,
            "usability_claim_earned": False,
            "public_gpu_path_proven": False,
        },
        "authorization": {
            "x3_provider_search": False,
            "live_nist_beacon": False,
            "entropy": False,
            "selection": False,
            "candidate_implementation": False,
            "candidate_execution": False,
            "gpu_ssh_pod": False,
            "timing": False,
            "product_change": False,
            "publication": False,
            "submission": False,
        },
        "supporting_documents": {"report": report_id, "self_review": self_id},
        "sole_cfr_forward_pointer": f"history/internal_docs/{CFR_NAME}",
        "result_sha256": "",
    }
    result["result_sha256"] = seal_document(result, seal_field="result_sha256", domain=RESULT_DOMAIN, version=1)
    result_bytes = canonical_json_bytes(result) + b"\n"
    result_id = {"path": f"history/internal_docs/{RESULT_NAME}", "bytes": len(result_bytes), "sha256": sha256_bytes(result_bytes)}
    root_rows = [result_id, report_id, self_id]
    for name in CAPSULE_ROOTS:
        root_rows.append(_identity(HISTORY / name))
    root_rows += [
        _identity(ROOT / "scripts/goal5793_x2_build_offline_review_capsule.py"),
        _identity(ROOT / "scripts/goal5793_x2_verify_offline_review_capsule.py"),
        _identity(ROOT / "scripts/goal5793_x2_build_external_review_entry.py"),
        _identity(ROOT / "tests/goal5793_x2_offline_review_capsule_test.py"),
    ]
    table = "\n".join(f"| `{row['path']}` | {row['bytes']} | `{row['sha256']}` |" for row in root_rows)
    cfr = f"""# Call for external review: Goal5793 X2 offline implementation and X3-search entry

**SEND ONLY THIS FILE. Do not send the capsule as a second attachment.** The capsule and all supporting material are local evidence paths named below.

## Requested ruling

Please independently return P0/P1/P2/P3 and answer:

1. Does the exact capsule rebuild byte-identically and verify from a fresh extraction without Git or the mutable repository?
2. Do the frozen offline harvester, source/code resolution, controlled taxonomy, deduplication, role derivation, triplet enumeration, friction ledger, and selection mapping prevent candidate/outcome-directed steering?
3. Does the 186-row exposure authority handle its 179 weak identifiers conservatively, without promoting them into the future selection pool?
4. Are the exact NISTIR/XSD sources, their three contradictions, the chosen pre-observation precedence, cipher-suite-0 implementation, 1,442-pulse synthetic chain, next-closest rejection, and non-hermetic/runtime/live ceilings accurately represented?
5. If and only if P0=0/P1=0 after review absorption, may owner closure accept X2 at offline-only scope and authorize **X3 provider search only**? Beacon, entropy, selection, candidate work, GPU/SSH/POD, timing, product changes, publication, and submission must remain unauthorized.

This review must not treat X2 as generalization or usability evidence. Both counts remain zero.

## Exact roots

| Path | Bytes | SHA-256 |
|---|---:|---|
{table}

The capsule archive and twin are byte-identical at `{CAPSULE_ROOTS[capsule_builder.ARCHIVE_NAME][1]}`. Its standalone audit seal is `2e9f41d6ce601af3924d9299c889dbda1bfa58eb85a28e201b184ede46b77c29`.

## Embedded result

```json
{result_bytes.decode('utf-8').rstrip()}
```

## Embedded technical report

```markdown
{report.decode('utf-8').rstrip()}
```

## Embedded self-review

```markdown
{self_review.decode('utf-8').rstrip()}
```
""".encode("utf-8")
    return {RESULT_NAME: result_bytes, REPORT_NAME: report, SELF_REVIEW_NAME: self_review, CFR_NAME: cfr}


def summary(documents: dict[str, bytes]) -> dict[str, Any]:
    return {
        "status": "DRY_RUN_PASS__SOLE_CFR_READY__NO_LIVE_AUTHORIZATION",
        "documents": [
            {"path": name, "bytes": len(data), "sha256": sha256_bytes(data)}
            for name, data in documents.items()
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--write-create-only", action="store_true")
    parser.add_argument("--verify-stored", action="store_true")
    args = parser.parse_args()
    if args.write_create_only and args.verify_stored:
        parser.error("write and stored verification are mutually exclusive")
    if args.output_dir is None and (args.write_create_only or args.verify_stored):
        parser.error("write or stored verification requires --output-dir")
    if args.output_dir is not None and not (args.write_create_only or args.verify_stored):
        parser.error("--output-dir requires --write-create-only or --verify-stored")
    documents = build_documents()
    result = summary(documents)
    if args.verify_stored:
        for name, data in documents.items():
            path = args.output_dir / name
            if not path.is_file() or path.is_symlink() or path.read_bytes() != data:
                raise SystemExit(f"STORED_OUTPUT_MISMATCH:{name}")
        result["status"] = "POSTWRITE_STORED_BYTES_PASS__SOLE_CFR_EXACT__NO_LIVE_AUTHORIZATION"
    elif args.output_dir is not None:
        targets = [args.output_dir / name for name in documents]
        if any(path.exists() or path.is_symlink() for path in targets):
            raise SystemExit("CREATE_ONLY_OUTPUT_EXISTS")
        args.output_dir.mkdir(parents=True, exist_ok=True)
        for name, data in documents.items():
            (args.output_dir / name).write_bytes(data)
        result["status"] = "CREATE_ONLY_WRITE_PASS__SOLE_CFR_READY__NO_LIVE_AUTHORIZATION"
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
