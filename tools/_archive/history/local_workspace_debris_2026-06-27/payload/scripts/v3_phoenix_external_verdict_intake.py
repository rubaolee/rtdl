#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]

VALID_VERDICT_LABELS = (
    "release_ready",
    "approve_blocked_not_release",
    "block_p0",
    "block_p1",
)

DEFAULT_CANDIDATES = (
    {
        "candidate_id": "claude_after_dossier_release_ready",
        "path": ROOT
        / "docs"
        / "reviews"
        / "claude_phoenix_v3_aggregate_release_readiness_13_row_after_dossier_review_2026-06-22.md",
    },
    {
        "candidate_id": "latest_external_blocked_record",
        "path": ROOT
        / "docs"
        / "reviews"
        / "external_ai_blocked_phoenix_v3_aggregate_release_readiness_13_row_after_dossier_2026-06-22.md",
    },
    {
        "candidate_id": "codex_subagent_review",
        "path": ROOT
        / "docs"
        / "reviews"
        / "codex_subagent_phoenix_v3_aggregate_release_readiness_13_row_review_2026-06-22.md",
    },
    {
        "candidate_id": "codex_fallback_consensus",
        "path": ROOT
        / "docs"
        / "reviews"
        / "codex_phoenix_v3_aggregate_release_readiness_13_row_2ai_fallback_consensus_2026-06-22.md",
    },
)

VERDICT_RE = re.compile(r"(?im)^\s*(?:[-*]\s*)?Verdict\s*:\s*`?([A-Za-z0-9_-]+)`?\b")
EXTERNAL_REVIEWER_RE = re.compile(
    r"(?im)^\s*(?:[-*]\s*)?(?:External\s+reviewer|Reviewer)\s*:\s*(Claude|Gemini|Human external reviewer|External reviewer)\b"
)

DISQUALIFYING_PHRASES = (
    ("external_review_not_obtained", "external_review_not_obtained_marker"),
    ("external ai blocked", "external_ai_blocked_record"),
    ("codex subagent", "codex_subagent_or_internal_reviewer"),
    ("fallback consensus", "fallback_consensus_not_external_verdict"),
    ("cannot substitute", "cannot_substitute_for_external_authorization"),
    ("does not replace the required external", "does_not_replace_external_authorization"),
    ("substantive verdict returned: false", "no_substantive_verdict_returned"),
    ("process stopped by bounded timeout: true", "bounded_timeout_record"),
    ("not a release verdict", "explicit_not_release_verdict"),
    ("does not satisfy the external-ai side", "does_not_satisfy_external_ai_rule"),
    ("this is not a release-readiness review", "explicit_not_release_readiness_review"),
)


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _candidate_from_path(path: Path) -> dict[str, Any]:
    return {"candidate_id": path.stem, "path": path}


def _normalize_verdict(raw: str) -> str:
    return raw.strip().lower().replace("-", "_")


def _find_verdict(text: str) -> tuple[str | None, str | None]:
    match = VERDICT_RE.search(text)
    if not match:
        return None, None
    raw = match.group(1)
    verdict = _normalize_verdict(raw)
    return verdict, raw


def _has_external_reviewer_provenance(text: str) -> bool:
    return EXTERNAL_REVIEWER_RE.search(text) is not None


def _find_external_reviewer(text: str) -> str | None:
    match = EXTERNAL_REVIEWER_RE.search(text)
    if not match:
        return None
    return match.group(1).strip().lower().replace(" ", "_")


def classify_candidate(candidate: dict[str, Any] | str | Path) -> dict[str, Any]:
    if isinstance(candidate, dict):
        candidate_id = str(candidate["candidate_id"])
        path = Path(candidate["path"])
    else:
        path = Path(candidate)
        candidate_id = path.stem

    reasons: list[str] = []
    exists = path.exists()
    size_bytes = path.stat().st_size if exists else 0
    text = ""

    if not exists:
        reasons.append("missing_file")
    elif size_bytes == 0:
        reasons.append("empty_file")
    else:
        text = path.read_text(encoding="utf-8", errors="replace")

    lower_text = text.lower()
    for phrase, reason in DISQUALIFYING_PHRASES:
        if phrase in lower_text and reason not in reasons:
            reasons.append(reason)

    verdict, raw_verdict = _find_verdict(text)
    if verdict is None:
        reasons.append("missing_verdict_line")
    elif verdict not in VALID_VERDICT_LABELS:
        reasons.append(f"invalid_verdict_label:{raw_verdict}")

    external_reviewer = _find_external_reviewer(text)
    external_reviewer_provenance = external_reviewer is not None
    if not external_reviewer_provenance:
        reasons.append("missing_external_reviewer_provenance")

    accepted = not reasons and verdict in VALID_VERDICT_LABELS
    status_line = (
        f"external_verdict_obtained_{external_reviewer}_{verdict}"
        if accepted and external_reviewer and verdict
        else None
    )
    return {
        "candidate_id": candidate_id,
        "path": _display_path(path),
        "exists": exists,
        "bytes": size_bytes,
        "accepted": accepted,
        "verdict": verdict if verdict in VALID_VERDICT_LABELS else None,
        "raw_verdict": raw_verdict,
        "external_reviewer": external_reviewer,
        "external_reviewer_provenance": external_reviewer_provenance,
        "status_line": status_line,
        "scoped_packet_authorized": bool(accepted and verdict == "release_ready"),
        "release_authorized": False,
        "reasons": reasons,
    }


def build_payload(candidates: Iterable[dict[str, Any] | str | Path] | None = None) -> dict[str, Any]:
    candidate_specs = list(candidates) if candidates is not None else list(DEFAULT_CANDIDATES)
    classified = [classify_candidate(candidate) for candidate in candidate_specs]
    accepted = [candidate for candidate in classified if candidate["accepted"]]

    if len(accepted) == 1:
        status = "external_verdict_obtained"
        accepted_verdict = accepted[0]["verdict"]
        scoped_packet_authorized = accepted[0]["scoped_packet_authorized"]
        accepted_status_line = accepted[0]["status_line"]
    elif len(accepted) > 1:
        status = "ambiguous_multiple_external_verdicts"
        accepted_verdict = None
        scoped_packet_authorized = False
        accepted_status_line = None
    else:
        status = "missing_external_verdict"
        accepted_verdict = None
        scoped_packet_authorized = False
        accepted_status_line = None

    return {
        "tool": "v3_phoenix_external_verdict_intake",
        "status": status,
        "valid_external_verdict_obtained": len(accepted) == 1,
        "scoped_packet_authorized": scoped_packet_authorized,
        "release_authorized": False,
        "accepted_verdict": accepted_verdict,
        "status_line": accepted_status_line,
        "valid_verdict_labels": list(VALID_VERDICT_LABELS),
        "accepted_candidates": accepted,
        "current_rejections": [candidate for candidate in classified if not candidate["accepted"]],
        "candidate_count": len(classified),
        "decision_audit": {
            "decision": "Treat only a real external Claude/Gemini/human verdict file as scoped packet evidence, not as V3 major release authorization.",
            "was_i_foolish": "Yes. The prior intake translated a scoped release_ready verdict into release_authorized true, which skipped the major performance mandate.",
            "foolish_actions": "The foolish action was accepting a scoped external review as V3 release authorization instead of only as evidence for the 13-row packet.",
            "other_path": "A looser path could rely on prose discipline alone, but that already created release-boundary confusion.",
            "different_path_now": "Use this intake guard to record scoped packet evidence while the major V2.x performance gate remains the actual release authority.",
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--candidate",
        action="append",
        type=Path,
        default=None,
        help="Candidate verdict file to classify. Repeatable. Defaults to current Phoenix V3 review records.",
    )
    parser.add_argument("--json-out", type=Path, default=None)
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    candidates = [_candidate_from_path(path) for path in args.candidate] if args.candidate else None
    payload = build_payload(candidates)
    text = json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
