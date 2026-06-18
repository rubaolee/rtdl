from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


PACKET_VERSION = "rtdl.v3_0.c_abi_stability_policy.goal4565.v1"
OUT_JSON = Path("docs/reports/goal4565_v3_0_m166_c_abi_stability_policy_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4565_v3_0_m166_c_abi_stability_policy_2026-06-17.md")
POLICY = Path("docs/learn/v3_0_c_abi_stability_policy.md")
C_ABI_DRAFT = Path("docs/learn/v3_0_c_abi_draft.md")
EMBEDDABILITY = Path("docs/learn/v3_0_embeddability_architecture_strategy.md")
LEARN_README = Path("docs/learn/README.md")


def build_packet(root: Path = Path(".")) -> dict[str, Any]:
    policy = (root / POLICY).read_text(encoding="utf-8")
    c_abi = (root / C_ABI_DRAFT).read_text(encoding="utf-8")
    embeddability = (root / EMBEDDABILITY).read_text(encoding="utf-8")
    learn = (root / LEARN_README).read_text(encoding="utf-8")
    checks = {
        "policy_declares_0_1_3_not_frozen": "`0.1.3`" in policy and "not frozen" in policy,
        "policy_documents_runtime_compatibility_guard": "rtdl_abi_is_compatible" in policy
        and "patch <= RTDL_ABI_VERSION_PATCH" in policy,
        "policy_names_current_surface": "include/rtdl/rtdl.h" in policy
        and "make build-c-api" in policy
        and "src/native/rtdl_c_api.cpp" in policy,
        "policy_names_current_evidence_gates": "exported-symbol" in policy
        and "non-Python C client" in policy
        and "negative runtime" in policy
        and "`v3_current`" in policy,
        "policy_requires_version_bump_for_breaking_changes": "RTDL_ABI_VERSION_*" in policy
        and "breaking change" in policy,
        "policy_defines_1_0_freeze_requirements": "## 1.0 Freeze Requirements" in policy
        and "Cross-version compatibility tests" in policy
        and "symbol manifest" in policy,
        "policy_defines_future_compatibility_rules": "## Future Compatibility Rules" in policy
        and "Existing exported C symbols are not removed" in policy
        and "Enum values and status codes are not reused" in policy,
        "policy_keeps_claim_boundary_blocked": "does not itself freeze the ABI" in policy
        and "make performance claims" in policy,
        "c_abi_draft_links_policy": "v3_0_c_abi_stability_policy.md" in c_abi,
        "embeddability_strategy_links_policy": "V3.0 C ABI Stability Policy" in embeddability
        and "v3_0_c_abi_stability_policy.md" in embeddability,
        "learn_readme_links_policy": "V3.0 C ABI Stability Policy" in learn,
    }
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4565 / V3 M166",
        "status": "c_abi_stability_policy_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "claim_boundary": {
            "stable_abi_authorized": False,
            "packaged_sdk_authorized": False,
            "cross_version_compatibility_validated": False,
            "optix_embree_c_abi_query_authorized": False,
            "release_authorized": False,
        },
        "conclusion": (
            "Goal4565 adds an explicit V3 C ABI stability policy: the current "
            "`0.1.3` source-tree ABI remains experimental, breaking changes are "
            "allowed only with evidence refresh and versioning, and stable-SDK "
            "wording is blocked until symbol-manifest, cross-version, packaging, "
            "and runtime gates pass."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Goal4565 / V3 M166 C ABI Stability Policy",
        "",
        f"Status: `{packet['status']}`",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Checks",
        "",
        "| Check | Passed |",
        "| --- | --- |",
    ]
    for name, passed in packet["checks"].items():
        lines.append(f"| `{name}` | `{passed}` |")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- The policy does not freeze the ABI or authorize package/release wording.",
            "- No cross-version compatibility, OptiX/Embree C ABI query, or performance claim is authorized.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args(argv)
    packet = build_packet()
    if not args.no_write:
        OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
        OUT_JSON.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        write_report(packet, OUT_REPORT)
    print(
        json.dumps(
            {
                "failed_checks": packet["failed_checks"],
                "status": "accept" if not packet["failed_checks"] else "reject",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if not packet["failed_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
