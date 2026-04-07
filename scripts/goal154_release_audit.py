from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _exists(relpath: str) -> bool:
    return (REPO_ROOT / relpath).exists()


def main() -> int:
    required_release_docs = [
        "docs/release_reports/v0_2/README.md",
        "docs/release_reports/v0_2/release_statement.md",
        "docs/release_reports/v0_2/support_matrix.md",
        "docs/release_reports/v0_2/audit_report.md",
        "docs/release_reports/v0_2/tag_preparation.md",
    ]
    required_goal_packages = [
        "docs/reports/goal148_v0_2_scope_status_package_2026-04-07.md",
        "docs/reports/goal149_front_door_and_example_consistency_freeze_2026-04-07.md",
        "docs/reports/goal150_v0_2_release_readiness_and_stability_2026-04-07.md",
        "docs/reports/goal151_final_front_door_status_freeze_2026-04-07.md",
        "docs/reports/goal152_v0_2_release_statement_and_support_matrix_2026-04-07.md",
        "docs/reports/goal153_backend_loader_robustness_2026-04-07.md",
    ]
    required_external_reviews = [
        "docs/reports/goal148_scope_decision_claude_2026-04-07.md",
        "docs/reports/goal148_scope_decision_gemini_2026-04-07.md",
        "docs/reports/goal149_external_review_claude_2026-04-07.md",
        "docs/reports/goal150_external_review_claude_2026-04-07.md",
        "docs/reports/goal151_external_review_claude_2026-04-07.md",
        "docs/reports/goal152_external_review_claude_2026-04-07.md",
        "docs/reports/goal153_external_review_claude_2026-04-07.md",
    ]
    required_consensus = [
        "history/ad_hoc_reviews/2026-04-07-codex-consensus-goal148-v0_2-scope-decision.md",
        "history/ad_hoc_reviews/2026-04-07-codex-consensus-goal149-front-door-example-freeze.md",
        "history/ad_hoc_reviews/2026-04-07-codex-consensus-goal150-release-readiness.md",
        "history/ad_hoc_reviews/2026-04-07-codex-consensus-goal151-front-door-status-freeze.md",
        "history/ad_hoc_reviews/2026-04-07-codex-consensus-goal152-release-statement-and-support-matrix.md",
        "history/ad_hoc_reviews/2026-04-07-codex-consensus-goal153-backend-loader-robustness.md",
    ]

    groups = [
        ("release_docs", required_release_docs),
        ("goal_packages", required_goal_packages),
        ("external_reviews", required_external_reviews),
        ("consensus", required_consensus),
    ]

    overall_ok = True
    for label, items in groups:
        all_present = all(_exists(item) for item in items)
        overall_ok = overall_ok and all_present
        print(f"{label} = {str(all_present).lower()}")
        for item in items:
            print(f"  {item}: {str(_exists(item)).lower()}")

    print(f"overall_release_audit = {str(overall_ok).lower()}")
    return 0 if overall_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
