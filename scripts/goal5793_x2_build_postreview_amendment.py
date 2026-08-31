#!/usr/bin/env python3
"""Build the append-only X2 postreview repair authority and sole CFR."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tempfile
from typing import Any

if __package__ in (None, ""):
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.goal5793_x1_canonical import canonical_json_bytes, seal_document, sha256_bytes
from scripts import goal5793_x2_preentropy_enumerator as enum_v1
from scripts import goal5793_x2_preentropy_enumerator_v2 as enum_v2
from scripts import goal5793_x2_structural_friction as friction_v1
from scripts import goal5793_x2_structural_friction_v2 as friction_v2


ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "history/internal_docs"
DATE = "2026-08-22"
AUTHORITY_NAME = "goal5793_x2_postreview_amendment_authority_20260822.json"
REPORT_NAME = "goal5793_x2_postreview_amendment_report_20260822.md"
CFR_NAME = "call_for_review_goal5793_x2_postreview_amendment_and_x3_search_entry_20260822.md"
AUTHORITY_DOMAIN = "rtdl.goal5793.x2.postreview_amendment_authority"

PINNED_ROOTS = {
    "history/internal_docs/call_for_review_goal5793_x2_offline_implementation_and_x3_search_entry_20260822.md": (13661, "669265526798dc56d8aaf76acbbb7c5669f4b1ed34cde56a1923eed3cb515927"),
    "history/internal_docs/review_goal5793_x2_offline_implementation_and_x3_search_entry_20260822.md": (40444, "1135ff6dfdfa744fab2b16b2a84175e0a9c66988c64fb651ffaed48bcf173f52"),
    "history/internal_docs/goal5793_x2_offline_review_capsule_20260822.tar.gz": (7221120, "4c64a48a0da52b393b6868a8770be6d3766369d235698132b5f2001f5a429841"),
    "history/internal_docs/goal5793_x2_offline_review_capsule_manifest_20260822.json": (22440, "51cbcaa1a4ed2b9be4f25769f35445a16e6dc08da9163c80bf0decb466048fd8"),
    "history/internal_docs/goal5793_x2_offline_review_capsule_audit_20260822.json": (2526, "24b7baeae00e6baf3e6927ee0195f5052579544f546c473653eef9e84bc9262f"),
    "history/internal_docs/goal5793_x2_exposure_alias_authority_v2_20260822.json": (461251, "72a30e8b2a8998507ca2f27517346006f62ef6b370f9777a54bddf9dd8edae8b"),
}

SOURCE_ROOTS = (
    "scripts/goal5793_x2_preentropy_enumerator_v2.py",
    "tests/goal5793_x2_preentropy_enumerator_v2_test.py",
    "scripts/goal5793_x2_structural_friction_v2.py",
    "tests/goal5793_x2_structural_friction_v2_test.py",
    "scripts/goal5793_x2_build_exposure_alias_authority_v2.py",
    "tests/goal5793_x2_exposure_alias_authority_v2_test.py",
    "scripts/goal5793_x2_build_postreview_amendment.py",
    "tests/goal5793_x2_postreview_amendment_test.py",
)


def _identity(relative: str) -> dict[str, Any]:
    path = ROOT / relative
    data = path.read_bytes()
    return {"path": relative, "bytes": len(data), "sha256": sha256_bytes(data)}


def _verify_roots() -> None:
    for relative, (size, digest) in PINNED_ROOTS.items():
        data = (ROOT / relative).read_bytes()
        if len(data) != size or sha256_bytes(data) != digest:
            raise RuntimeError(f"PINNED_ROOT_IDENTITY_MISMATCH:{relative}")


def _science(candidate: str, vector: dict[str, str], family: str) -> dict[str, Any]:
    return {
        "schema": "rtdl.goal5793.x2.preentropy_science_row.v1",
        "candidate_id": candidate,
        "canonical_work_identity": f"doi:10.9999/{candidate.lower()}",
        "normalized_problem_family": family,
        "source_basis_exact": True,
        "oracle_exact": True,
        "stock_rt": True,
        "existing_registered_family": True,
        "expected_disposition": "COMPATIBLE" if candidate == "A" else "UNKNOWN",
        "public_admit_compile_run_reachable": True,
        "no_core_change_predicted": True,
        "structural_vector": vector,
        "risk_flags": {key: key == "continuation" and candidate == "C" for key in ("multiplicity", "tie_boundary", "continuation", "ownership_epoch", "global_composition")},
        "identity_stage_selection_eligible": True,
    }


def _p1_evidence() -> dict[str, Any]:
    positives, _ = enum_v1.load_positive_vectors()
    fixture = {
        "schema": "rtdl.goal5793.x2.preentropy_science_fixture.v1",
        "mode": "OFFLINE_SYNTHETIC_FIXTURES_ONLY",
        "synthetic_fixture": True,
        "network_call_count": 0,
        "examiner_invocation_count": 0,
        "candidate_implementation_count": 0,
        "rows": [
            _science("A", dict(positives[0], ray_construction="FINITE_SEGMENT"), "problem_a"),
            _science("B", dict(positives[1], geometry_family="INSTANCED_CURVE_OR_SPHERE_PRIMITIVE"), "problem_b"),
            _science("C", dict(positives[2], composition="COMMUTATIVE_CHECKED_REDUCTION"), "problem_c"),
        ],
    }
    result = enum_v2.build_fixture_result(fixture)
    unmapped = next(row for row in result["validated_rows"] if row["candidate_id"] == "B")
    return {
        "input_rows": result["counts"]["input_rows"],
        "validated_rows": len(result["validated_rows"]),
        "mapped_rows": result["counts"]["mapped_rows"],
        "unmapped_rows": result["counts"]["unmapped_rows"],
        "unmapped_by_axis": result["counts"]["unmapped_by_axis"],
        "unmapped_values_by_axis": result["counts"]["unmapped_values_by_axis"],
        "unmapped_control_row": unmapped,
        "batch_aborted": False,
        "unrecorded_manual_deletion_needed": False,
        "all_input_rows_accounted": result["counts"]["input_rows"] == len(result["validated_rows"]),
        "result_sha256": result["result_sha256"],
    }


def _lineage(path: str, raw: bytes) -> dict[str, Any]:
    pin = {"path": path, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
    return {
        "schema": friction_v1.SCHEMA,
        "lineage_id": "postreview-friction-control",
        "predecessor_lineage_ids": [],
        "app_owned_files": [pin],
        "generated_paths": [],
        "authority_scalar_paths": {"manual": [], "defaulted": [], "derived": [], "unresolved": []},
        "stage_records": [{"stage": "SOURCE_PROJECTION", "status": "PRESENT", "artifact": pin, "reason": None}],
        "failures": [],
        "baseline": {"status": "NA", "reason": "NO_EXACT_FUNCTIONALLY_MATCHED_BASELINE", "source_pins": []},
    }


def _friction_evidence() -> dict[str, Any]:
    python_source = b"""import rtdsl.v4_semantically_admitted_compiler\n\ndef run(x):\n    # CUDA_SUCCESS OPTIX_SUCCESS optixAccelBuild\n    message = \"cudaMalloc optixTrace\"\n    n=len([1,2]); print(n); d=dict()\n    for i in range(3): value=str(i).upper()\n    return rtdsl.v4_semantically_admitted_compiler.run_semantically_admitted_builtin_triangle(x)\n"""
    c_source = b"""#include <optix_stubs.h>\n#include <cuda_runtime_api.h>\nif (res != CUDA_SUCCESS) return;\nif (r != OPTIX_SUCCESS) return;\nOPTIX_CHECK(optixAccelBuild(ctx));\ncuda_stream_t s;\nchar *p = \"no cuda mention here\"; // CUDA optixTrace\noptixTrace(h);\ncudaMalloc(&p, 4);\n"""
    with tempfile.TemporaryDirectory(prefix="goal5793_x2_postreview_friction_") as temp:
        root = Path(temp)
        (root / "app.py").write_bytes(python_source)
        py_result = friction_v2.measure_lineage(root, _lineage("app.py", python_source))
        (root / "app.cu").write_bytes(c_source)
        c_result = friction_v2.measure_lineage(root, _lineage("app.cu", c_source))
    return {
        "dotted_import_public_rtdl_calls": py_result["metrics"]["public_rtdl_api_call_sites"]["value"],
        "ordinary_python_unresolved_rtdl_calls": py_result["metrics"]["unresolved_rtdl_api_call_sites"]["value"],
        "ordinary_python_calls_excluded_from_rtdl_metric": py_result["metrics"]["non_rtdl_call_sites_excluded_from_api_metric"]["value"],
        "python_comment_and_string_cuda_optix_code_tokens": py_result["metrics"]["raw_cuda_optix_code_tokens"]["value"],
        "c_cuda_optix_code_tokens": [row["token"] for row in c_result["details"]["raw_cuda_optix_code_token_sites"]],
        "prose_counted": False,
        "direct_cuda_optix_public_private_unresolved_comparison_allowed": False,
        "supports_usability_or_productivity_claim": False,
        "python_measurement_sha256": py_result["measurement_sha256"],
        "c_measurement_sha256": c_result["measurement_sha256"],
    }


def build_authority() -> dict[str, Any]:
    _verify_roots()
    alias = json.loads((HISTORY / "goal5793_x2_exposure_alias_authority_v2_20260822.json").read_text(encoding="utf-8"))
    if alias.get("authority_sha256") != "55fdfb156781652ea4fb913f8539931e7ff1aea45ab2b94ff6f4e523b616b98d":
        raise RuntimeError("ALIAS_V2_INTERNAL_IDENTITY_MISMATCH")
    authority: dict[str, Any] = {
        "schema": "rtdl.goal5793.x2.postreview_amendment_authority.v1",
        "date": DATE,
        "status": "POSTREVIEW_REPAIRS_FROZEN_FOR_EXTERNAL_REVIEW__X3_NOT_AUTHORIZED",
        "review": _identity("history/internal_docs/review_goal5793_x2_offline_implementation_and_x3_search_entry_20260822.md"),
        "review_verdict": {"P0": 0, "P1": 1, "P2": 5, "P3": 2, "x3_provider_search_cleared": False},
        "immutable_reviewed_roots": [_identity(relative) for relative in PINNED_ROOTS if "exposure_alias_authority_v2" not in relative],
        "successor_roots": [_identity(relative) for relative in SOURCE_ROOTS] + [_identity("history/internal_docs/goal5793_x2_exposure_alias_authority_v2_20260822.json")],
        "p1_1_unmapped_denominator_repair": _p1_evidence(),
        "p2_dispositions": {
            "P2_1_raw_token_lexer": {"status": "TECHNICALLY_CLOSED_PENDING_EXTERNAL_REVIEW", "evidence": _friction_evidence()},
            "P2_2_call_classification": {
                "status": "TECHNICALLY_CLOSED_PENDING_EXTERNAL_REVIEW",
                "unresolved_scope": "RTDSL_AND_SCRIPTS_GOAL5793_ONLY",
                "direct_baseline_call_metric_comparison_allowed": False,
            },
            "P2_3_cross_platform_crypto_tcb": {
                "status": "ACCEPTED_AS_MANDATORY_PRE_BEACON_GATE__NOT_REQUIRED_FOR_X3_PROVIDER_SEARCH",
                "before_any_live_pulse_request": [
                    "REBUILD_ON_FROZEN_X1_LINUX_ENVIRONMENT",
                    "PIN_LINUX_INTERPRETER_STDLIB_CRYPTOGRAPHY_RUST_ABI3_SO_OPENSSL_AND_HOST_CRYPTO",
                    "COMPARE_AUTHORITY_BYTES_TO_WINDOWS_GENERATED_AUTHORITY",
                    "EXTERNALLY_REVIEW_ANY_DIFFERENCE_BEFORE_OBSERVING_A_PULSE",
                ],
                "live_beacon_authorized": False,
            },
            "P2_4_alias_projection": {
                "status": "CLOSED_BY_EXPLICIT_V2_LEGIBILITY_AUTHORITY",
                "correction": "V1_FIELDS_WERE_NOT_REDACTED__THEY_WERE_NESTED_UNDER_PROTOCOL_ALIASES",
                "exact_split": {"strong_identifier_rows": 7, "weak_author_year_fallback_rows": 176, "weak_exact_title_only_rows": 3},
                "alias_v2": _identity("history/internal_docs/goal5793_x2_exposure_alias_authority_v2_20260822.json"),
            },
            "P2_5_role_claim_language": {"status": "CLOSED_BY_PRECORPUS_LITERAL_CLAIM_CEILING", **enum_v2.CLAIM_LANGUAGE},
        },
        "p3_dispositions": {
            "P3_1_identity_label": {
                "status": "ACCEPTED_FOR_FUTURE_X3_OUTPUT",
                "required_fields": {"identity_screen_passed": True, "science_screen_pending": True, "selection_eligible_after_all_screens": False},
            },
            "P3_2_near_duplicate_without_strong_id": {
                "status": "ACCEPTED_RESIDUAL__MUST_BE_REPORTED",
                "selection_measure_is_over_identity_components_not_proven_underlying_works": True,
                "population_inflation_from_UNMERGED_NEAR_DUPLICATES_possible": True,
                "arbitrary_manual_merge_allowed": False,
            },
        },
        "test_evidence": {
            "focused_postreview_tests": 18,
            "focused_postreview_passes": 18,
            "breakdown": {
                "unmapped_denominator_v2": "4/4",
                "structural_friction_v2": "4/4",
                "exposure_alias_authority_v2": "4/4",
                "postreview_amendment_determinism_and_single_cfr": "6/6",
            },
        },
        "claim_boundary": {
            "p1_technically_repaired": True,
            "external_amendment_review_pending": True,
            "x3_provider_search_authorized": False,
            "generalization_exam_count": 0,
            "usability_study_count": 0,
            "functionally_matched_direct_cuda_optix_baseline_count": 0,
        },
        "authorization": {
            "x3_provider_search": False, "live_nist_beacon": False, "entropy": False,
            "selection": False, "candidate_work": False, "gpu_ssh_pod": False,
            "timing": False, "product_change": False, "publication": False, "submission": False,
        },
        "sole_cfr_forward_pointer": f"history/internal_docs/{CFR_NAME}",
        "authority_sha256": "",
    }
    authority["authority_sha256"] = seal_document(authority, seal_field="authority_sha256", domain=AUTHORITY_DOMAIN, version=1)
    return authority


def _report() -> str:
    return """# Goal5793 X2 postreview amendment report

The blocking P1 is technically repaired without editing any reviewed byte. The append-only v2 enumerator preserves every well-formed unmapped row in `validated_rows`, records every offending axis and value, publishes `unmapped_rows` and a per-axis/value denominator, assigns no A/B/C role, and excludes the row from triplets. A three-row control containing an OptiX curve/sphere category now returns all three rows as 2 mapped + 1 unmapped; no manual deletion or batch abort remains.

P2-1/P2-2 are also repaired in an append-only friction v2: comments and strings no longer count; CUDA_/OPTIX_/cuda*/optix*/Optix*/driver prefixes and CUDA/OptiX headers do count; dotted imports resolve correctly; builtins/stdlib/other third-party calls do not inflate `unresolved_rtdl`; and RTDL public/private/unresolved metrics are explicitly forbidden as a direct-CUDA/OptiX comparative measure. This remains structural evidence only and earns no usability claim.

P2-4 contained a reviewer interpretation error: the v1 alias rows already held author/year/fallback fields, nested under `protocol_aliases`; they were not redacted. The v2 legibility authority makes the operative split explicit: 7 strong-ID rows, 176 weak rows with author+year fallback, and 3 weak exact-title-only rows. All 186 remain selection-ineligible.

P2-3 is accepted as a mandatory pre-beacon gate, not hidden or waived. Before any live pulse, the crypto authority must be rebuilt in the frozen Linux environment and its interpreter/stdlib/`_rust.abi3.so`/OpenSSL/host crypto TCB externally reviewed. This does not need to precede an X3 literature provider search, but beacon authorization remains false.

P2-5 claim language is now literal and sealed: diversity means only non-identity against four frozen positives; Role A measures preregistered prediction calibration on entropy-selected instances not chosen by the authors; and future sampling may only be described as from works expressible in the pre-frozen vocabulary, alongside the unmapped denominator.

Generalization exams remain 0. Usability studies remain 0. X3 remains unauthorized until this amendment returns P0=0/P1=0 and is append-only owner-closed.
"""


def build_documents() -> dict[str, bytes]:
    authority = build_authority()
    authority_bytes = canonical_json_bytes(authority) + b"\n"
    report = _report().encode("utf-8")
    embedded_paths = list(SOURCE_ROOTS) + [
        "history/internal_docs/goal5793_x2_exposure_alias_authority_v2_20260822.json",
    ]
    rows = [
        {"path": f"history/internal_docs/{AUTHORITY_NAME}", "bytes": len(authority_bytes), "sha256": sha256_bytes(authority_bytes)},
        {"path": f"history/internal_docs/{REPORT_NAME}", "bytes": len(report), "sha256": sha256_bytes(report)},
    ] + [_identity(path) for path in embedded_paths]
    table = "\n".join(f"| `{row['path']}` | {row['bytes']} | `{row['sha256']}` |" for row in rows)
    # The builder source itself contains ordinary triple-backtick examples.
    # Use a longer fence so every embedded byte sequence is mechanically
    # extractable from the one Markdown entrypoint without fence collision.
    fence = "`" * 8
    blocks = [
        f"## Embedded `{AUTHORITY_NAME}`\n\n{fence}json\n{authority_bytes.decode('utf-8').rstrip()}\n{fence}",
        f"## Embedded `{REPORT_NAME}`\n\n{fence}markdown\n{report.decode('utf-8').rstrip()}\n{fence}",
    ]
    for path in embedded_paths:
        data = (ROOT / path).read_bytes().decode("utf-8", errors="strict").rstrip("\n")
        language = "json" if path.endswith(".json") else "python"
        blocks.append(f"## Embedded `{path}`\n\n{fence}{language}\n{data}\n{fence}")
    embedded = "\n\n".join(blocks)
    sole_send_marker = "SEND ONLY " + "THIS FILE"
    cfr = f"""# Call for external review: Goal5793 X2 postreview amendment and X3-search entry

**{sole_send_marker}.** It embeds every new authority, source, test, and report byte. Do not send a second packet.

## Requested ruling

Please return P0/P1/P2/P3 and answer:

1. Does the v2 enumerator close P1-1 by preserving and sealing every unmapped row and its denominator before any X3 corpus exists, with no manual deletion or vocabulary extension?
2. Do friction v2's code-only token lexer, dotted-import repair, RTDL-only unresolved scope, and non-comparability ceiling close P2-1/P2-2 without creating a usability claim?
3. Does alias authority v2 correctly establish 7 strong / 176 weak author-year-fallback / 3 weak exact-title-only rows, and correct the prior "redacted" characterization while keeping all 186 ineligible?
4. Is the Linux cryptographic TCB requirement sufficiently frozen as a mandatory pre-beacon gate while remaining nonblocking for X3 provider search?
5. Are the Role A/diversity/sampling-frame claim ceilings strong enough to prevent novelty, coverage, arbitrary-literature, or unqualified-random-sample overclaims?
6. If and only if P0=0/P1=0, may append-only owner closure authorize **X3 provider search only**? Beacon, entropy, selection, candidate work, GPU/SSH/POD, timing, product change, publication, and submission must remain false.

Generalization evidence = 0. Usability evidence = 0. Functionally matched direct CUDA/OptiX baseline count = 0.

## Exact new roots

| Path | Bytes | SHA-256 |
|---|---:|---|
{table}

{embedded}
""".encode("utf-8")
    return {AUTHORITY_NAME: authority_bytes, REPORT_NAME: report, CFR_NAME: cfr}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--write-create-only", action="store_true")
    parser.add_argument("--verify-stored", action="store_true")
    args = parser.parse_args()
    if args.write_create_only and args.verify_stored:
        parser.error("write and verify are mutually exclusive")
    if args.output_dir is None and (args.write_create_only or args.verify_stored):
        parser.error("output dir required")
    documents = build_documents()
    if args.write_create_only:
        targets = [args.output_dir / name for name in documents]
        if any(path.exists() or path.is_symlink() for path in targets):
            raise SystemExit("CREATE_ONLY_OUTPUT_EXISTS")
        args.output_dir.mkdir(parents=True, exist_ok=True)
        for name, data in documents.items(): (args.output_dir / name).write_bytes(data)
        status = "CREATE_ONLY_WRITE_PASS__SOLE_CFR_READY__X3_UNAUTHORIZED"
    elif args.verify_stored:
        for name, data in documents.items():
            path = args.output_dir / name
            if not path.is_file() or path.is_symlink() or path.read_bytes() != data:
                raise SystemExit(f"STORED_OUTPUT_MISMATCH:{name}")
        status = "POSTWRITE_STORED_BYTES_PASS__X3_UNAUTHORIZED"
    else:
        status = "DRY_RUN_PASS__SOLE_CFR_READY__X3_UNAUTHORIZED"
    print(json.dumps({"status": status, "documents": [{"path": name, "bytes": len(data), "sha256": sha256_bytes(data)} for name, data in documents.items()]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
