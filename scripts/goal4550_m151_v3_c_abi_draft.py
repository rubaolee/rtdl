from __future__ import annotations

import json
from pathlib import Path


PACKET_VERSION = "rtdl.v3_0.c_abi_draft.goal4550.v1"
OUT_JSON = Path("docs/reports/goal4550_v3_0_m151_c_abi_draft_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4550_v3_0_m151_c_abi_draft_2026-06-17.md")
HEADER = Path("include/rtdl/rtdl.h")
DOC = Path("docs/learn/v3_0_c_abi_draft.md")
EMBED_DOC = Path("docs/learn/v3_0_embeddability_architecture_strategy.md")


def build_packet(root: Path = Path(".")) -> dict[str, object]:
    header = (root / HEADER).read_text(encoding="utf-8")
    doc = (root / DOC).read_text(encoding="utf-8")
    embed_doc = (root / EMBED_DOC).read_text(encoding="utf-8")
    forbidden_tokens = ("class ", "template<", "std::", "namespace ")
    checks = {
        "header_exists": (root / HEADER).exists(),
        "doc_exists": (root / DOC).exists(),
        "extern_c_boundary": 'extern "C"' in header,
        "opaque_handles_declared": all(
            token in header
            for token in (
                "typedef struct rtdl_context rtdl_context;",
                "typedef struct rtdl_index rtdl_index;",
                "typedef struct rtdl_query rtdl_query;",
                "typedef struct rtdl_buffer rtdl_buffer;",
            )
        ),
        "status_codes_declared": "typedef enum rtdl_status" in header
        and "RTDL_STATUS_ERROR_INVALID_ARGUMENT" in header,
        "abi_version_declared": "RTDL_ABI_VERSION_MAJOR" in header
        and "rtdl_abi_version_major" in header,
        "external_runtime_declared": "typedef struct rtdl_external_runtime" in header
        and "void* stream" in header
        and "void* context" in header,
        "neutral_buffer_view_declared": "typedef struct rtdl_buffer_view" in header
        and "shape[8]" in header
        and "strides[8]" in header
        and "rtdl_buffer_release_fn" in header,
        "c_only_surface": not any(token in header for token in forbidden_tokens),
        "doc_boundary_blocks_implementation_claims": "not an implemented shared-library ABI" in doc
        and "does not implement any exported symbols" in doc,
        "embeddability_strategy_supports_this_step": "Freeze a draft C ABI" in embed_doc,
    }
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4550 / V3 M151",
        "status": "c_abi_draft_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "header": HEADER.as_posix(),
        "doc": DOC.as_posix(),
        "claim_boundary": {
            "shared_library_symbols_implemented": False,
            "binary_compatibility_frozen": False,
            "non_python_client_validated": False,
            "dlpack_support_implemented": False,
            "external_stream_context_validated": False,
            "release_authorized": False,
        },
        "conclusion": (
            "Goal4550 creates the first V3 embeddability implementation-facing "
            "artifact: a draft C-only `rtdl.h` boundary with opaque handles, "
            "status codes, external runtime handles, and neutral buffer views. "
            "It is intentionally a reviewed design surface, not an implemented "
            "or frozen ABI."
        ),
    }


def write_report(packet: dict[str, object], path: Path) -> None:
    lines = [
        "# Goal4550 / V3 M151 C ABI Draft",
        "",
        f"Status: `{packet['status']}`",
        "",
        "## Conclusion",
        "",
        str(packet["conclusion"]),
        "",
        "## Checks",
        "",
        "| Check | Passed |",
        "| --- | --- |",
    ]
    for name, passed in dict(packet["checks"]).items():
        lines.append(f"| `{name}` | `{passed}` |")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- No shared-library symbols are implemented by this goal.",
            "- No binary compatibility, non-Python client, DLPack, or external stream/context claim is authorized.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    packet = build_packet()
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
