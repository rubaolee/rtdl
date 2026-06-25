from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


V4_GOAL4642_PACKET_STATUS = "goal4642_final_authorization_packet_ready_not_authorized"
V4_GOAL4642_REQUESTED_LABEL = "RTDL v4.0.0 formal high-performance generic RT-core operator release"


@dataclass(frozen=True)
class V4Goal4642FinalAuthorizationPacket:
    status: str
    requested_label: str
    required_reviewer_count: int
    packet: str
    call_for_review: str
    scorecard_passed: bool
    clean_tree_passed: bool
    packet_clean_tree_revalidation_commit: str
    public_docs_cleaned: bool
    release_authorized: bool
    forbidden_claims: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "requested_label": self.requested_label,
            "required_reviewer_count": self.required_reviewer_count,
            "packet": self.packet,
            "call_for_review": self.call_for_review,
            "scorecard_passed": self.scorecard_passed,
            "clean_tree_passed": self.clean_tree_passed,
            "packet_clean_tree_revalidation_commit": self.packet_clean_tree_revalidation_commit,
            "public_docs_cleaned": self.public_docs_cleaned,
            "release_authorized": self.release_authorized,
            "forbidden_claims": self.forbidden_claims,
        }


def v4_goal4642_final_authorization_packet(root: Path | None = None) -> dict[str, Any]:
    repo = root or Path(__file__).resolve().parents[2]
    packet = "future/v4/v4_goal4642_final_3ai_release_authorization_packet_2026-06-25.md"
    call = "future/v4/reviews/call_for_review_v4_goal4642_final_3ai_release_authorization_2026-06-25.md"

    return V4Goal4642FinalAuthorizationPacket(
        status=V4_GOAL4642_PACKET_STATUS,
        requested_label=V4_GOAL4642_REQUESTED_LABEL,
        required_reviewer_count=3,
        packet=packet,
        call_for_review=call,
        scorecard_passed=(repo / "future/v4/v4_goal4639_serious_release_scorecard_pod_gate_decision_2026-06-25.md").exists(),
        clean_tree_passed=(repo / "future/v4/v4_goal4641_clean_tree_reproducibility_gate_2026-06-25.md").exists(),
        packet_clean_tree_revalidation_commit="437b79a2a382082e269d0d0ee128528caf0ae112",
        public_docs_cleaned=(repo / "future/v4/v4_goal4640_public_docs_cleanup_decision_2026-06-25.md").exists(),
        release_authorized=False,
        forbidden_claims=(
            "broad V4 speedup",
            "whole-application speedup",
            "all-benchmark speedup",
            "public true-zero-copy",
            "Tier-3 callback support",
            "raw OptiX callback support",
            "CuPy performance",
            "C ABI / embedding / non-Python host",
            "app-specific native kernels",
            "Barnes-Hut covered by V4.0",
            "Spatial RayJoin covered by V4.0",
            "LibRTS paper reproduction",
        ),
    ).as_dict()


def validate_v4_goal4642_final_authorization_packet(root: Path | None = None) -> dict[str, Any]:
    repo = root or Path(__file__).resolve().parents[2]
    packet = v4_goal4642_final_authorization_packet(repo)
    if packet["status"] != V4_GOAL4642_PACKET_STATUS:
        raise ValueError("Goal4642 packet status drift")
    if packet["requested_label"] != V4_GOAL4642_REQUESTED_LABEL:
        raise ValueError("Goal4642 requested label drift")
    if packet["required_reviewer_count"] != 3:
        raise ValueError("Goal4642 requires 3-AI authorization")
    if not packet["scorecard_passed"]:
        raise ValueError("Goal4642 requires Goal4639 scorecard evidence")
    if not packet["clean_tree_passed"]:
        raise ValueError("Goal4642 requires Goal4641 clean-tree evidence")
    if not str(packet["packet_clean_tree_revalidation_commit"]).startswith("437b79a2"):
        raise ValueError("Goal4642 packet clean-tree revalidation commit drift")
    if not packet["public_docs_cleaned"]:
        raise ValueError("Goal4642 requires Goal4640 public docs cleanup")
    if packet["release_authorized"]:
        raise ValueError("Goal4642 packet alone must not authorize release")
    for path_key in ("packet", "call_for_review"):
        if not (repo / packet[path_key]).exists():
            raise ValueError(f"Goal4642 missing {path_key}")
    return packet


__all__ = [
    "V4_GOAL4642_PACKET_STATUS",
    "V4_GOAL4642_REQUESTED_LABEL",
    "V4Goal4642FinalAuthorizationPacket",
    "v4_goal4642_final_authorization_packet",
    "validate_v4_goal4642_final_authorization_packet",
]
