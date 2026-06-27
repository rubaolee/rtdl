from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


V4_GOAL4773_STATUS = (
    "external_review_approved_public_tag_under_bounded_framing__clean_wheel_smoke_passed__v4_0_0_tag_created_and_pushed"
)
V4_GOAL4773_VERDICT = "approve_close_gemini_debt_and_allow_v4_0_public_tag"


@dataclass(frozen=True)
class V4Goal4773AuthorizationStatus:
    status: str
    verdict: str
    antigravity_review: str
    review_packet: str
    release_owner_record: str
    current_status_doc: str
    public_readme: str
    future_v4_readme: str
    public_tag_externally_authorized: bool
    git_tag_created: bool
    clean_release_commit_required: bool
    clean_wheel_smoke_passed: bool
    tag_target_ready: bool
    git_tag_pushed: bool
    public_release_tag: str
    public_release_commit: str
    public_release_commit_source: str
    broad_speedup_authorized: bool
    paper_reproduction_authorized: bool
    tier3_callback_authorized: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "verdict": self.verdict,
            "antigravity_review": self.antigravity_review,
            "review_packet": self.review_packet,
            "release_owner_record": self.release_owner_record,
            "current_status_doc": self.current_status_doc,
            "public_readme": self.public_readme,
            "future_v4_readme": self.future_v4_readme,
            "public_tag_externally_authorized": self.public_tag_externally_authorized,
            "git_tag_created": self.git_tag_created,
            "clean_release_commit_required": self.clean_release_commit_required,
            "clean_wheel_smoke_passed": self.clean_wheel_smoke_passed,
            "tag_target_ready": self.tag_target_ready,
            "git_tag_pushed": self.git_tag_pushed,
            "public_release_tag": self.public_release_tag,
            "public_release_commit": self.public_release_commit,
            "public_release_commit_source": self.public_release_commit_source,
            "broad_speedup_authorized": self.broad_speedup_authorized,
            "paper_reproduction_authorized": self.paper_reproduction_authorized,
            "tier3_callback_authorized": self.tier3_callback_authorized,
        }


def _repo(root: Path | None) -> Path:
    return root or Path(__file__).resolve().parents[2]


def v4_goal4773_release_authorization_status(root: Path | None = None) -> dict[str, Any]:
    repo = _repo(root)
    return V4Goal4773AuthorizationStatus(
        status=V4_GOAL4773_STATUS,
        verdict=V4_GOAL4773_VERDICT,
        antigravity_review=(
            "tools/_archive/future/v4/reviews/antigravity_v4_gemini_full_coverage_review_2026-06-27.md"
        ),
        review_packet=(
            "tools/_archive/future/v4/reviews/"
            "v4_gemini_full_coverage_review_debt_for_antigravity_2026-06-27.md"
        ),
        release_owner_record=(
            "tools/_archive/future/v4/"
            "v4_goal4773_antigravity_review_intake_and_release_owner_status_2026-06-27.md"
        ),
        current_status_doc="docs/current_v4_status.md",
        public_readme="README.md",
        future_v4_readme="tools/_archive/future/v4/README.md",
        public_tag_externally_authorized=True,
        git_tag_created=True,
        clean_release_commit_required=True,
        clean_wheel_smoke_passed=True,
        tag_target_ready=True,
        git_tag_pushed=True,
        public_release_tag="v4.0.0",
        public_release_commit="resolved_by_git_tag_object",
        public_release_commit_source="git tag object v4.0.0",
        broad_speedup_authorized=False,
        paper_reproduction_authorized=False,
        tier3_callback_authorized=False,
    ).as_dict()


def validate_v4_goal4773_release_authorization_status(
    root: Path | None = None,
) -> dict[str, Any]:
    repo = _repo(root)
    status = v4_goal4773_release_authorization_status(repo)

    for key in (
        "antigravity_review",
        "review_packet",
        "release_owner_record",
        "current_status_doc",
        "public_readme",
        "future_v4_readme",
    ):
        if not (repo / status[key]).exists():
            raise ValueError(f"Goal4773 missing required artifact: {status[key]}")

    antigravity = (repo / status["antigravity_review"]).read_text(encoding="utf-8")
    packet = (repo / status["review_packet"]).read_text(encoding="utf-8")
    owner = (repo / status["release_owner_record"]).read_text(encoding="utf-8")
    public_docs = "\n".join(
        (repo / status[key]).read_text(encoding="utf-8")
        for key in ("current_status_doc", "public_readme", "future_v4_readme")
    )

    if status["status"] != V4_GOAL4773_STATUS:
        raise ValueError("Goal4773 status drift")
    if status["verdict"] != V4_GOAL4773_VERDICT:
        raise ValueError("Goal4773 verdict drift")
    if V4_GOAL4773_VERDICT not in antigravity:
        raise ValueError("Goal4773 Antigravity review does not carry the verdict")
    if "Gemini review debt" not in packet:
        raise ValueError("Goal4773 packet must be the Gemini review-debt packet")
    if "Clean smoke summary" not in owner or "status: passed" not in owner:
        raise ValueError("Goal4773 owner record must record clean-smoke success")
    if "v4.0.0 target is resolved by the Git tag object" not in owner:
        raise ValueError("Goal4773 owner record must record tag-object target authority")
    if "published tag is `v4.0.0`" not in public_docs:
        raise ValueError("Goal4773 current docs must expose the published V4.0.0 tag")
    if "release claim boundary is locked" not in public_docs:
        raise ValueError("Goal4773 public docs must expose the locked release claim boundary")
    if "clean wheel smoke passed" not in public_docs:
        raise ValueError("Goal4773 public docs must expose clean wheel smoke success")
    if "Public V4.0 tagging still requires external release authorization" in public_docs:
        raise ValueError("Goal4773 public docs retain stale external-review blocker")
    if "That manifest is not a public tag authorization" in public_docs:
        raise ValueError("Goal4773 public docs retain stale manifest wording")

    for forbidden in (
        "all benchmark apps are faster",
        "broad V4-over-V2.14 speedup wording",
        "Tier-3 callback/PTX support claims",
        "public true-zero-copy claims",
    ):
        if forbidden not in public_docs:
            raise ValueError(f"Goal4773 public docs missing forbidden-claim boundary: {forbidden}")

    if not status["public_tag_externally_authorized"]:
        raise ValueError("Goal4773 must record external public-tag authorization")
    if not status["git_tag_created"]:
        raise ValueError("Goal4773 must record git tag creation after V4.0.0 publication")
    if not status["clean_release_commit_required"]:
        raise ValueError("Goal4773 must require clean release packaging before tag")
    if not status["clean_wheel_smoke_passed"]:
        raise ValueError("Goal4773 must record clean wheel smoke success")
    if not status["tag_target_ready"]:
        raise ValueError("Goal4773 must record tag-target readiness")
    if not status["git_tag_pushed"]:
        raise ValueError("Goal4773 must record pushed public tag state")
    if status["public_release_tag"] != "v4.0.0":
        raise ValueError("Goal4773 public release tag drift")
    if status["public_release_commit"] != "resolved_by_git_tag_object":
        raise ValueError("Goal4773 public release commit drift")
    if status["public_release_commit_source"] != "git tag object v4.0.0":
        raise ValueError("Goal4773 public release commit source drift")
    for flag in (
        "broad_speedup_authorized",
        "paper_reproduction_authorized",
        "tier3_callback_authorized",
    ):
        if status[flag]:
            raise ValueError(f"Goal4773 must not authorize {flag}")
    return status


__all__ = [
    "V4_GOAL4773_STATUS",
    "V4_GOAL4773_VERDICT",
    "V4Goal4773AuthorizationStatus",
    "v4_goal4773_release_authorization_status",
    "validate_v4_goal4773_release_authorization_status",
]
