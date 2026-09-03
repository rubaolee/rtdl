#!/usr/bin/env python3
"""Build and verify the pre-inspection Goal5839 field-census protocol."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import tarfile
import tempfile
from collections import defaultdict
from pathlib import Path, PurePosixPath
from typing import Any

from scripts import goal5753_build_held_out_universe as legacy_universe
from scripts import goal5793_x1_build_exposure_registry as survey_registry


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_ROOT = (
    ROOT
    / "history"
    / "internal_docs"
    / "goal5839_real_artifact_protocol_census_20260903"
)
AUTHORITY_PATH = EVIDENCE_ROOT / "GOAL5839_PREREGISTRATION.json"

SCHEMA = "rtdl.goal5839.real_artifact_protocol_census_preregistration.v1"
AUTHORITY_DOMAIN = "rtdl.goal5839.real_artifact_protocol_census_preregistration.v1"
FROZEN_AT_UTC = "2026-09-03T06:56:46Z"
PRE_REGISTRATION_PARENT_COMMIT = "cc1c5052f09bbf468650181d442a85907924609e"

SURVEY_URL = "https://arxiv.org/abs/2603.28771"
SURVEY_SOURCE_URL = "https://export.arxiv.org/e-print/2603.28771"
SURVEY_ARCHIVE_BYTES = 752_766
SURVEY_ARCHIVE_SHA256 = (
    "bfe852a1425b01b63ee0298f75646c824e9daf67429184211d446ba7f3643857"
)
SAMPLE_BIB_SHA256 = (
    "9e394f5712478c5b84f8dd88b80490e009a033dffd1e17773f24aadb0c2eb26a"
)
PROB_CSV_SHA256 = (
    "88749ea23e465c972afb9c6efa1553bc1a4e0a25b6faa5f00c1c5b9c27979e95"
)
LEGACY_UNIVERSE_EXPECTED_BYTES = 43_892
LEGACY_UNIVERSE_EXPECTED_SHA256 = (
    "fb89d1da0e9b7bc18ce3333eb11a5920ffdef9f23ba227f4ecbf96e898234b05"
)

ALLOWED_LABELS = (
    "ENFORCED",
    "UNCHECKED_BUT_APPARENTLY_CONSISTENT",
    "VIOLATED",
    "UNRESOLVED_WITH_REASON",
)

PROPERTIES: tuple[dict[str, Any], ...] = (
    {
        "id": "CP001_ROLE_EFFECT_CLOSURE",
        "question": (
            "Does the artifact machine-check the allowed callback-role effects and "
            "required cross-role effect topology before creating or launching the route?"
        ),
        "required_evidence": (
            "role entry points, effect-producing statements, consumers, and the exact "
            "rejecting check or explicit absence of such a check"
        ),
        "boundary": (
            "A language-legal callback, successful compilation, or reviewer inference "
            "does not count as protocol enforcement."
        ),
    },
    {
        "id": "CP002_SEMANTIC_ABI_OWNERSHIP",
        "question": (
            "Does the artifact machine-check the nominal meaning and producer/consumer "
            "ownership of payload, attribute, SBT, and result channels rather than only "
            "their bit widths?"
        ),
        "required_evidence": (
            "every relevant channel slot, its producer expression, consumer expression, "
            "declared meaning, and the exact rejecting check or explicit absence"
        ),
        "boundary": (
            "Matching C/CUDA types or manually consistent comments do not establish "
            "nominal semantic ownership."
        ),
    },
    {
        "id": "CP003_PHYSICAL_BINDING",
        "question": (
            "Does the artifact machine-check callback assumptions against geometry kind, "
            "GAS/SBT association, buffer layout, field-to-geometry mapping, output/reducer, "
            "and target binding before launch?"
        ),
        "required_evidence": (
            "host construction, device declarations, launch bindings, layout definitions, "
            "and the exact rejecting check or explicit absence"
        ),
        "boundary": (
            "A route that happens to bind the expected buffers is apparently consistent, "
            "not enforced, unless incompatible bindings are rejected by a relevant check."
        ),
    },
    {
        "id": "CP004_STATUS_GATED_CONTINUATION_AND_COMPLETENESS",
        "question": (
            "Does the artifact represent failure, overflow, truncation, or incompleteness "
            "and prevent result exposure or host/device continuation until status is "
            "accepted?"
        ),
        "required_evidence": (
            "capacity/completeness contract, status production, status read order, output "
            "exposure, and continuation behavior"
        ),
        "boundary": (
            "Reading a status without suppressing invalid or partial output does not count "
            "as enforcement. A route with no bounded output may be unresolved or "
            "not-applicable only through the frozen reason taxonomy."
        ),
    },
    {
        "id": "CP005_EXECUTABLE_IDENTITY_CHAIN",
        "question": (
            "Does the artifact bind the intended protocol and physical plan to the exact "
            "generated source/PTX, native/provider objects, target, and launched executable "
            "so substitution is rejected?"
        ),
        "required_evidence": (
            "program construction, module/pipeline loading, cache selection, identity "
            "checks, and execution receipt or explicit absence"
        ),
        "boundary": (
            "This is chain-of-custody evidence, not application correctness; build success "
            "or a filename convention alone is not enforcement."
        ),
    },
)

UNRESOLVED_REASONS = (
    "NO_ELIGIBLE_PUBLIC_AUTHOR_ARTIFACT_FOUND_UNDER_FROZEN_DISCOVERY_PROTOCOL",
    "PUBLIC_ARTIFACT_UNAVAILABLE_AT_ACQUISITION",
    "NO_STATICALLY_INSPECTABLE_OPTIX_ROUTE",
    "RELEVANT_GENERATED_OR_HOST_SOURCE_MISSING",
    "MULTIPLE_ROUTES_WITH_NO_FROZEN_CANONICAL_ROUTE",
    "SEMANTIC_INTENT_AMBIGUOUS_IN_EXACT_SOURCE_AND_PAPER",
    "BUILD_OR_GENERATION_STEP_REQUIRED_TO_OBSERVE_PROPERTY_BUT_NOT_REPRODUCIBLE",
    "PROPERTY_NOT_APPLICABLE_ONLY_AFTER_INDEPENDENT_ADJUDICATION",
    "INDEPENDENT_EXTRACTION_OR_ADJUDICATION_PENDING",
    "RESPONSIBLE_DISCLOSURE_GATE_PENDING",
)


class PreregistrationError(RuntimeError):
    """Fail-closed Goal5839 preregistration error."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise PreregistrationError(message)


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def _authority_seal(value: dict[str, Any]) -> str:
    body = dict(value)
    body["authority_sha256"] = ""
    return _sha256(AUTHORITY_DOMAIN.encode("ascii") + b"\0" + _canonical_bytes(body))


def _safe_archive_members(archive_payload: bytes) -> dict[str, bytes]:
    contents: dict[str, bytes] = {}
    with tarfile.open(fileobj=io.BytesIO(archive_payload), mode="r:*") as archive:
        members = archive.getmembers()
        _require(len(members) <= 1_024, "SURVEY_ARCHIVE_MEMBER_LIMIT_EXCEEDED")
        for member in members:
            path = PurePosixPath(member.name)
            _require(
                member.name
                and not path.is_absolute()
                and "\\" not in member.name
                and all(part not in ("", ".", "..") for part in path.parts),
                "UNSAFE_SURVEY_ARCHIVE_PATH",
            )
            _require(not member.issym() and not member.islnk(), "SURVEY_ARCHIVE_LINK_FORBIDDEN")
            _require(member.isdir() or member.isfile(), "SURVEY_ARCHIVE_SPECIAL_MEMBER_FORBIDDEN")
            if member.isfile():
                stream = archive.extractfile(member)
                _require(stream is not None, "SURVEY_ARCHIVE_MEMBER_UNREADABLE")
                payload = stream.read()
                _require(len(payload) == member.size, "SURVEY_ARCHIVE_MEMBER_SIZE_MISMATCH")
                contents[path.as_posix()] = payload
    return contents


def _extract_source(archive_path: Path) -> tuple[bytes, bytes, bytes]:
    payload = archive_path.read_bytes()
    _require(len(payload) == SURVEY_ARCHIVE_BYTES, "SURVEY_ARCHIVE_BYTES_MISMATCH")
    _require(_sha256(payload) == SURVEY_ARCHIVE_SHA256, "SURVEY_ARCHIVE_SHA256_MISMATCH")
    contents = _safe_archive_members(payload)
    _require("sample.bib" in contents, "SURVEY_SAMPLE_BIB_MISSING")
    _require("prob.csv" in contents, "SURVEY_PROB_CSV_MISSING")
    sample_bib = contents["sample.bib"]
    prob_csv = contents["prob.csv"]
    _require(_sha256(sample_bib) == SAMPLE_BIB_SHA256, "SAMPLE_BIB_SHA256_MISMATCH")
    _require(_sha256(prob_csv) == PROB_CSV_SHA256, "PROB_CSV_SHA256_MISMATCH")
    return payload, sample_bib, prob_csv


def _legacy_rebuild_identity(
    archive_path: Path,
    sample_bib: bytes,
    prob_csv: bytes,
) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="goal5839-legacy-rebuild-") as tmp:
        tmp_root = Path(tmp)
        prob_path = tmp_root / "prob.csv"
        bib_path = tmp_root / "sample.bib"
        prob_path.write_bytes(prob_csv)
        bib_path.write_bytes(sample_bib)
        value = legacy_universe.build(prob_path, bib_path, archive_path)
    rebuilt = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")
    return {
        "expected_historical_artifact": {
            "bytes": LEGACY_UNIVERSE_EXPECTED_BYTES,
            "sha256": LEGACY_UNIVERSE_EXPECTED_SHA256,
        },
        "current_generator_rebuild_from_exact_source": {
            "bytes": len(rebuilt),
            "sha256": _sha256(rebuilt),
        },
        "byte_identical_reproduction": (
            len(rebuilt) == LEGACY_UNIVERSE_EXPECTED_BYTES
            and _sha256(rebuilt) == LEGACY_UNIVERSE_EXPECTED_SHA256
        ),
        "disposition": (
            "LEGACY_GOAL5753_ARTIFACT_UNAVAILABLE_AND_NOT_REPRODUCED_BYTE_IDENTICALLY__"
            "DO_NOT_USE_AS_GOAL5839_SOURCE_AUTHORITY"
        ),
    }


def _build_denominator(sample_bib: bytes, prob_csv: bytes) -> dict[str, Any]:
    bibliography_rows = survey_registry.parse_bibtex(sample_bib.decode("utf-8"))
    _require(len(bibliography_rows) == 186, "SURVEY_BIBLIOGRAPHY_COUNT_MISMATCH")
    bibliography = {row["citation_key"]: row for row in bibliography_rows}
    _require(len(bibliography) == 186, "SURVEY_BIBLIOGRAPHY_KEYS_NOT_UNIQUE")

    with io.StringIO(prob_csv.decode("utf-8-sig")) as stream:
        table_rows = list(csv.DictReader(stream))
    _require(len(table_rows) == 35, "SURVEY_PROBLEM_ROW_COUNT_MISMATCH")

    problem_rows: list[dict[str, Any]] = []
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for source_index, row in enumerate(table_rows):
        raw_problem = row["Problem"].strip()
        match = re.fullmatch(r"(.+?)~\\cite\{([^}]+)\}", raw_problem)
        _require(match is not None, f"SURVEY_PROBLEM_ROW_UNPARSEABLE:{source_index}")
        assert match is not None
        problem, citation_key = match.group(1).strip(), match.group(2).strip()
        _require(citation_key in bibliography, f"SURVEY_CITATION_KEY_MISSING:{citation_key}")
        projected = {
            "source_index": source_index,
            "problem": problem,
            "citation_key": citation_key,
            "survey_measurements": {
                "best_speedup": row["Best Speedup"],
                "worst_speedup": row["Worst Speedup"],
                "improves_count": row["Improves?"],
                "average": row["Avg"],
            },
        }
        problem_rows.append(projected)
        grouped[citation_key].append(projected)

    _require(len(grouped) == 29, "SURVEY_UNIQUE_WORK_COUNT_MISMATCH")
    _require(len({row["problem"] for row in problem_rows}) == 32, "SURVEY_PROBLEM_COUNT_MISMATCH")

    works: list[dict[str, Any]] = []
    for citation_key in sorted(grouped, key=lambda value: value.encode("utf-8")):
        bib = bibliography[citation_key]
        fields = bib["fields"]
        works.append(
            {
                "work_id": f"survey_bib:{citation_key}",
                "citation_key": citation_key,
                "entry_type": bib["entry_type"],
                "title": fields.get("title"),
                "author": fields.get("author"),
                "year": fields.get("year"),
                "doi": fields.get("doi"),
                "url": fields.get("url"),
                "raw_bibtex_entry_sha256": bib["raw_sha256"],
                "survey_problem_rows": grouped[citation_key],
                "artifact_discovery_status": "NOT_STARTED_AT_PREREGISTRATION",
                "classification_cell_count": 0,
            }
        )

    return {
        "unit": (
            "all_29_unique_cited_works_represented_by_the_exact_35_row_survey_problem_table, "
            "plus every distinct eligible public author artifact discovered for each work"
        ),
        "complete_under_scope": True,
        "paper_problem_row_count": len(problem_rows),
        "distinct_problem_label_count": len({row["problem"] for row in problem_rows}),
        "unique_work_count": len(works),
        "expected_minimum_property_cell_count_after_census": len(works) * len(PROPERTIES),
        "problem_rows": problem_rows,
        "works": works,
    }


def build_authority(archive_path: Path) -> dict[str, Any]:
    archive_payload, sample_bib, prob_csv = _extract_source(archive_path)
    denominator = _build_denominator(sample_bib, prob_csv)
    legacy_custody = _legacy_rebuild_identity(archive_path, sample_bib, prob_csv)
    _require(not legacy_custody["byte_identical_reproduction"], "LEGACY_CUSTODY_FACT_CHANGED")

    authority: dict[str, Any] = {
        "schema": SCHEMA,
        "goal": 5839,
        "stage": "PREREGISTRATION_BEFORE_GOAL5839_CANDIDATE_SOURCE_INSPECTION",
        "status": "FROZEN_PROTOCOL__CENSUS_EXTRACTION_NOT_STARTED__NO_FIELD_RESULT",
        "frozen_at_utc": FROZEN_AT_UTC,
        "repository_state": {
            "branch": "codex/cgo-goal5836-handoff",
            "pre_registration_parent_commit": PRE_REGISTRATION_PARENT_COMMIT,
            "candidate_source_inspection_started_in_goal5839": False,
            "candidate_repository_clone_count_in_goal5839": 0,
            "candidate_property_classification_count_in_goal5839": 0,
            "prior_project_exposure_exists": True,
            "blind_corpus_or_unseen_artifact_claimed": False,
        },
        "source_authority": {
            "survey_title": "Ray Tracing Cores for General-Purpose Computing: A Literature Review",
            "survey_url": SURVEY_URL,
            "survey_source_url": SURVEY_SOURCE_URL,
            "survey_archive": {
                "bytes": len(archive_payload),
                "sha256": _sha256(archive_payload),
                "stored_in_repository": False,
                "reacquisition_requires_exact_hash": True,
            },
            "sample_bib": {"sha256": _sha256(sample_bib), "entry_count": 186},
            "prob_csv": {"sha256": _sha256(prob_csv), "row_count": 35},
            "legacy_goal5753_custody": legacy_custody,
            "goal5839_authority_choice": (
                "USE_EXACT_SURVEY_ARCHIVE_AND_EMBEDDED_DENOMINATOR_ROWS; DO_NOT CLAIM "
                "RECOVERY OF THE MISSING LEGACY GOAL5753 JSON"
            ),
        },
        "denominator": denominator,
        "artifact_discovery_and_selection_protocol": {
            "work_denominator_never_shrinks": True,
            "no_public_artifact_found_effect": (
                "retain work and emit five UNRESOLVED_WITH_REASON cells using the frozen "
                "no-artifact reason"
            ),
            "discovery_cutoff_utc": FROZEN_AT_UTC,
            "discovery_steps_in_order": [
                "inspect exact bibliography DOI/URL fields and canonical paper landing page",
                "inspect the exact paper and publisher supplement for author-declared code or artifact links",
                "run GitHub repository search for the exact paper title; preserve query and first 50 returned repository identities",
                "run general web search for the exact quoted title plus source code; preserve query and first 20 returned URLs",
                "inspect candidate repository README/citation/license metadata only to establish author/paper relation before source classification",
            ],
            "eligible_artifact": (
                "public source artifact explicitly linked by the paper/publisher or maintained "
                "by a paper author/institution with metadata that identifies the paper, and "
                "containing a buildable or statically inspectable implementation of the paper's "
                "NVIDIA OptiX RT-repurposing route at an exact revision"
            ),
            "excluded_artifacts": [
                "CUDA-only or CPU-only baselines without the paper's OptiX route",
                "rendering-only code unrelated to the surveyed repurposing workload",
                "third-party reimplementations not released by paper authors or the named institution",
                "forks or mirrors with no distinct author-maintained implementation",
                "paper prose or pseudocode without statically inspectable source",
                "binary-only releases whose relevant protocol cannot be statically inspected",
            ],
            "duplicate_or_mirror_precedence": [
                "exact artifact revision explicitly named by the paper",
                "publisher-hosted archival artifact explicitly attached to the paper",
                "first code repository URL in paper order",
                "author-or-institution repository whose metadata explicitly identifies the paper",
            ],
            "same_precedence_tie_breaker": "lexicographically smallest normalized canonical URL",
            "revision_rule": (
                "use paper-declared tag/commit when exact; otherwise pin the observed default-branch "
                "HEAD, commit, tree, submodules, and acquisition timestamp without later updating it"
            ),
            "canonical_route_rule_per_artifact": (
                "classify every distinct paper-evaluated OptiX route explicitly named by artifact "
                "docs; otherwise classify the documented default OptiX target; if neither is "
                "unique, retain the artifact but classify all cells UNRESOLVED_WITH_REASON"
            ),
            "multiple_distinct_official_artifacts": (
                "inventory and classify every distinct eligible official artifact; use precedence "
                "only to collapse byte-identical mirrors or duplicate releases, and never choose "
                "based on observed labels"
            ),
            "completeness_boundary": (
                "complete for 29 survey works under this finite discovery protocol, not a claim "
                "that all code ever published on the internet was found"
            ),
        },
        "protocol_properties": list(PROPERTIES),
        "classification_contract": {
            "allowed_labels_only": list(ALLOWED_LABELS),
            "label_definitions": {
                "ENFORCED": (
                    "An exact, relevant machine check observes independently sourced protocol "
                    "facts and rejects the incompatible route before launch or result consumption."
                ),
                "UNCHECKED_BUT_APPARENTLY_CONSISTENT": (
                    "No complete relevant enforcing check was found, but the exact canonical "
                    "route's inspected producers, consumers, bindings, and continuation appear "
                    "mutually consistent; this is not proof and not a defect count."
                ),
                "VIOLATED": (
                    "Exact source evidence establishes a concrete reachable mismatch in the "
                    "canonical declared route; public naming additionally requires independent "
                    "adjudication and the responsible-disclosure gate."
                ),
                "UNRESOLVED_WITH_REASON": (
                    "Available exact evidence is insufficient, ambiguous, unavailable, or needs "
                    "a missing build/generated artifact. The reason must be one frozen token."
                ),
            },
            "allowed_unresolved_reasons": list(UNRESOLVED_REASONS),
            "absence_of_explicit_check_is_violation": False,
            "successful_build_or_output_is_enforcement": False,
            "matching_machine_types_are_semantic_ownership": False,
            "ambiguity_default": "UNRESOLVED_WITH_REASON",
            "favorable_imputation_allowed": False,
            "not_applicable_is_standalone_label": False,
        },
        "required_extraction_record": {
            "identity_fields": [
                "work_id",
                "artifact_url",
                "artifact_revision",
                "artifact_tree_identity",
                "license_identity",
                "source_inventory_identity",
                "canonical_route",
                "extractor_identity",
                "extracted_at_utc",
            ],
            "per_property_fields": [
                "property_id",
                "proposed_label",
                "evidence_file",
                "evidence_lines_or_symbol",
                "producer",
                "consumer",
                "enforcement_or_gap",
                "unresolved_reason",
                "notes",
            ],
            "route_evidence_fields": [
                "callback_roles",
                "payload_and_attribute_meanings",
                "physical_bindings",
                "status_and_continuation",
                "executable_construction",
            ],
            "source_inventory": (
                "all relevant regular source/build/documentation paths with byte count and SHA-256; "
                "generated/vendor/build outputs separately identified"
            ),
        },
        "independence_and_adjudication": {
            "paper_claim_requires": (
                "two independent extractions, or one extraction plus external adjudication, "
                "for every reported property cell"
            ),
            "same_codex_session_repeated_extraction_counts_as_independent": False,
            "project_author_may_resolve_ambiguity_favorably": False,
            "disagreement_resolution": "UNRESOLVED_WITH_REASON unless independent adjudicator resolves it",
            "current_independent_extractor_count": 0,
            "current_external_adjudicator_count": 0,
            "external_review_currently_available": False,
            "paper_ready_census_claim_authorized": False,
        },
        "responsible_disclosure": {
            "concrete_violation_public_naming_allowed_before_notification": False,
            "required_before_public_naming": [
                "independent adjudication of exact evidence",
                "private notice to the upstream artifact maintainers",
                "an offered minimal patch or precise repair suggestion",
                "a recorded response window of at least 14 calendar days unless authors consent earlier",
                "corrections or maintainer disagreement preserved adjacent to the finding",
            ],
            "public_repository_rule": (
                "Do not commit or push a named VIOLATED evidence row before the notification gate; "
                "retain a private local potential-finding packet instead."
            ),
        },
        "reporting_rules": {
            "always_report": [
                "all 29 work rows",
                "all unavailable and unresolved rows",
                "all zero-violation outcomes",
                "artifact discovery failures",
                "all disagreements",
                "prior project exposure and lack of blindness",
            ],
            "primary_counts": [
                "work denominator, artifact denominator, route denominator, and artifact availability",
                "property cells by the four labels",
                "unresolved cells by frozen reason",
            ],
            "forbidden_aggregation": [
                "treating five correlated properties as independent defect observations",
                "treating UNCHECKED_BUT_APPARENTLY_CONSISTENT as VIOLATED",
                "dropping works with no source",
                "reporting percentages without numerator and denominator",
            ],
        },
        "execution_state": {
            "network_artifact_discovery_count": 0,
            "candidate_source_file_inspection_count": 0,
            "candidate_source_inventory_count": 0,
            "property_extraction_count": 0,
            "adjudicated_property_cell_count": 0,
            "upstream_notification_count": 0,
            "gpu_or_pod_use_count": 0,
            "performance_timing_count": 0,
        },
        "claim_boundary": {
            "field_prevalence_result": False,
            "real_artifact_violation_found": False,
            "absence_of_enforcement_found": False,
            "paper_ready_complete_denominator_table": False,
            "external_review_or_consensus": False,
            "performance_or_application_correctness": False,
            "preregistration_only": True,
        },
        "authority_sha256": "",
    }
    authority["authority_sha256"] = _authority_seal(authority)
    validate_authority(authority)
    return authority


def validate_authority(authority: dict[str, Any]) -> None:
    _require(authority.get("schema") == SCHEMA, "AUTHORITY_SCHEMA_MISMATCH")
    _require(authority.get("authority_sha256") == _authority_seal(authority), "AUTHORITY_SEAL_MISMATCH")
    _require(authority.get("status") == "FROZEN_PROTOCOL__CENSUS_EXTRACTION_NOT_STARTED__NO_FIELD_RESULT", "AUTHORITY_STATUS_MISMATCH")
    denominator = authority.get("denominator")
    _require(isinstance(denominator, dict), "DENOMINATOR_MISSING")
    _require(denominator.get("paper_problem_row_count") == 35, "DENOMINATOR_ROW_COUNT_MISMATCH")
    _require(denominator.get("distinct_problem_label_count") == 32, "DENOMINATOR_PROBLEM_COUNT_MISMATCH")
    _require(denominator.get("unique_work_count") == 29, "DENOMINATOR_WORK_COUNT_MISMATCH")
    works = denominator.get("works")
    _require(isinstance(works, list) and len(works) == 29, "DENOMINATOR_WORK_ROWS_MISMATCH")
    _require(len({row["citation_key"] for row in works}) == 29, "DENOMINATOR_WORK_KEYS_NOT_UNIQUE")
    source_rows = denominator.get("problem_rows")
    _require(isinstance(source_rows, list) and len(source_rows) == 35, "DENOMINATOR_SOURCE_ROWS_MISMATCH")
    _require([row["source_index"] for row in source_rows] == list(range(35)), "DENOMINATOR_SOURCE_ORDER_MISMATCH")
    _require(
        authority.get("classification_contract", {}).get("allowed_labels_only")
        == list(ALLOWED_LABELS),
        "CLASSIFICATION_LABELS_MISMATCH",
    )
    properties = authority.get("protocol_properties")
    _require(
        isinstance(properties, list)
        and [row["id"] for row in properties] == [row["id"] for row in PROPERTIES],
        "PROTOCOL_PROPERTIES_MISMATCH",
    )
    execution = authority.get("execution_state")
    _require(isinstance(execution, dict), "EXECUTION_STATE_MISSING")
    _require(all(value == 0 for value in execution.values()), "PREREGISTRATION_HAS_POSTFREEZE_RESULT")
    boundary = authority.get("claim_boundary")
    _require(isinstance(boundary, dict) and boundary.get("preregistration_only") is True, "CLAIM_BOUNDARY_MISMATCH")
    _require(
        all(value is False for key, value in boundary.items() if key != "preregistration_only"),
        "PREREGISTRATION_OVERCLAIM",
    )
    legacy = authority.get("source_authority", {}).get("legacy_goal5753_custody", {})
    _require(legacy.get("byte_identical_reproduction") is False, "LEGACY_CUSTODY_MISMATCH")
    _require(
        legacy.get("expected_historical_artifact")
        == {"bytes": LEGACY_UNIVERSE_EXPECTED_BYTES, "sha256": LEGACY_UNIVERSE_EXPECTED_SHA256},
        "LEGACY_EXPECTED_IDENTITY_MISMATCH",
    )


def _serialized(authority: dict[str, Any]) -> bytes:
    return (json.dumps(authority, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode("ascii")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--survey-archive", type=Path)
    parser.add_argument("--output", type=Path, default=AUTHORITY_PATH)
    parser.add_argument("--verify-stored", action="store_true")
    args = parser.parse_args()

    if args.verify_stored:
        authority = json.loads(args.output.read_text(encoding="ascii"))
        validate_authority(authority)
        if args.survey_archive is not None:
            rebuilt = build_authority(args.survey_archive)
            _require(_serialized(rebuilt) == args.output.read_bytes(), "STORED_AUTHORITY_REBUILD_MISMATCH")
        print(
            json.dumps(
                {
                    "authority_sha256": authority["authority_sha256"],
                    "file_sha256": _sha256(args.output.read_bytes()),
                    "status": "PASS__GOAL5839_PREREGISTRATION_VERIFIED",
                    "survey_archive_rebuilt": args.survey_archive is not None,
                },
                sort_keys=True,
            )
        )
        return

    if args.survey_archive is None:
        parser.error("--survey-archive is required when building")
    authority = build_authority(args.survey_archive)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(_serialized(authority))
    print(
        json.dumps(
            {
                "authority_sha256": authority["authority_sha256"],
                "file_sha256": _sha256(args.output.read_bytes()),
                "status": authority["status"],
                "work_count": authority["denominator"]["unique_work_count"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
