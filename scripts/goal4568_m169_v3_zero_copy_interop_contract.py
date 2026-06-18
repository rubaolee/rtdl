from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from rtdsl.neutral_buffer_seam import (
    describe_v2_5_neutral_buffer_seam_contract,
    neutral_buffer_descriptor_from_object,
)


PACKET_VERSION = "rtdl.v3_0.zero_copy_interop_contract.goal4568.v1"
OUT_JSON = Path("docs/reports/goal4568_v3_0_m169_zero_copy_interop_contract_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4568_v3_0_m169_zero_copy_interop_contract_2026-06-17.md")
DOC = Path("docs/history/v4_preparatory_embedding/v3_0_zero_copy_interop_contract.md")
EMBEDDABILITY = Path("docs/history/v4_preparatory_embedding/v3_0_embeddability_architecture_strategy.md")
LEARN_README = Path("docs/history/v4_preparatory_embedding/README.md")
SEAM = Path("src/rtdsl/neutral_buffer_seam.py")


class FakeCudaArray:
    __cuda_array_interface__ = {
        "shape": (4,),
        "typestr": "<f4",
        "data": (0x1000, False),
        "version": 3,
        "strides": None,
        "device": 0,
    }


def _zero_copy_without_evidence_rejected() -> bool:
    try:
        neutral_buffer_descriptor_from_object(
            "points",
            FakeCudaArray(),
            producer="framework",
            consumer="rtdl",
            transfer_status="zero_copy_measured",
        )
    except ValueError as exc:
        return "zero_copy_measured requires" in str(exc)
    return False


def _measured_zero_copy_descriptor() -> dict[str, Any]:
    descriptor = neutral_buffer_descriptor_from_object(
        "points",
        FakeCudaArray(),
        producer="framework",
        consumer="rtdl",
        transfer_status="zero_copy_measured",
        measured_same_pointer=True,
        measured_no_host_stage=True,
        measured_evidence={"transfer_counter_window": "unit"},
    )
    return descriptor.to_metadata()


def build_packet(root: Path = Path(".")) -> dict[str, Any]:
    contract = describe_v2_5_neutral_buffer_seam_contract()
    doc = (root / DOC).read_text(encoding="utf-8")
    embeddability = (root / EMBEDDABILITY).read_text(encoding="utf-8")
    learn = (root / LEARN_README).read_text(encoding="utf-8")
    seam = (root / SEAM).read_text(encoding="utf-8")
    borrowed = neutral_buffer_descriptor_from_object(
        "points",
        FakeCudaArray(),
        producer="framework",
        consumer="rtdl",
    ).to_metadata()
    measured = _measured_zero_copy_descriptor()
    checks = {
        "contract_prioritizes_dlpack_and_cuda_array_interface": "dlpack" in contract["protocol_priority"]
        and "cuda_array_interface" in contract["protocol_priority"],
        "contract_has_borrowed_and_measured_statuses": "borrowed_device_pointer_unmeasured"
        in contract["transfer_statuses"]
        and "zero_copy_measured" in contract["transfer_statuses"],
        "contract_blocks_public_claims": contract["true_zero_copy_public_claim_authorized"] is False
        and contract["public_speedup_claim_authorized"] is False,
        "fake_cuda_array_defaults_to_borrowed_unmeasured": borrowed["buffer"]["device"] == "cuda:0"
        and borrowed["transfer_status"] == "borrowed_device_pointer_unmeasured"
        and borrowed["zero_copy_claim_authorized"] is False,
        "zero_copy_measured_requires_evidence": _zero_copy_without_evidence_rejected(),
        "measured_zero_copy_requires_same_pointer_and_no_host_stage": measured["zero_copy_claim_authorized"]
        is True
        and measured["public_speedup_claim_authorized"] is False,
        "doc_defines_observed_borrowed_measured_public_layers": "Observed descriptor" in doc
        and "Borrowed device pointer, unmeasured" in doc
        and "Measured zero-copy candidate" in doc
        and "Public true-zero-copy claim" in doc,
        "doc_blocks_c_abi_device_query_route_claim": "does not make" in doc
        and "C ABI" in doc
        and "query route" in doc
        and "consume device" in doc
        and "buffers" in doc
        and "does not validate CUDA pointer" in doc
        and "ownership" in doc,
        "embeddability_links_zero_copy_contract": "V3.0 Zero-Copy Interop Contract" in embeddability,
        "history_archive_links_zero_copy_contract": "V3.0 Zero-Copy Interop Contract" in learn,
        "seam_keeps_native_device_output_unpromoted": "native_device_output_promotion_ready" in seam
        and "return False" in seam,
    }
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4568 / V3 M169",
        "status": "zero_copy_interop_contract_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "borrowed_descriptor": borrowed,
        "measured_descriptor": measured,
        "claim_boundary": {
            "c_abi_device_buffer_route_implemented": False,
            "dlpack_c_abi_support_implemented": False,
            "framework_adapter_runtime_validated": False,
            "public_true_zero_copy_claim_authorized": False,
            "public_speedup_claim_authorized": False,
        },
        "conclusion": (
            "Goal4568 connects the existing neutral-buffer seam to the V3 "
            "embeddability plan: DLPack and CUDA-array-interface objects can be "
            "described as borrowed device pointers, measured zero-copy remains "
            "evidence-gated, and public/C-ABI device-buffer query claims stay "
            "blocked."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Goal4568 / V3 M169 Zero-Copy Interop Contract",
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
            "- This is a descriptor/readiness contract, not C ABI device-buffer support.",
            "- No DLPack C ABI route, framework adapter runtime, public zero-copy claim, or speedup wording is authorized.",
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
