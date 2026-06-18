from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
for _path in (ROOT, SRC):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

import rtdsl as rt


PACKET_VERSION = "rtdl.v3_0.neutral_buffer_protocol_gate.goal4606.v1"
OUT_JSON = Path("docs/reports/goal4606_v3_0_m207_neutral_buffer_protocol_gate_2026-06-17.json")
OUT_REPORT = Path("docs/reports/goal4606_v3_0_m207_neutral_buffer_protocol_gate_2026-06-17.md")
MATRIX_DOC = Path("docs/learn/v3_0_binding_and_device_interop_matrix.md")
ZERO_COPY_DOC = Path("docs/learn/v3_0_zero_copy_interop_contract.md")
BENCHMARK_INDEX = Path("docs/learn/benchmark_evidence_index.md")
SEAM = Path("src/rtdsl/neutral_buffer_seam.py")


class FakeCuPyColumn:
    __module__ = "cupy.synthetic"

    dtype = "int64"
    shape = (3,)
    strides = (1,)

    @property
    def __cuda_array_interface__(self) -> dict[str, object]:
        return {
            "shape": self.shape,
            "typestr": "<i8",
            "data": (0xCAFE, False),
            "version": 3,
        }

    def __dlpack__(self) -> object:
        return object()

    def __dlpack_device__(self) -> tuple[int, int]:
        return (2, 0)

    def data_ptr(self) -> int:
        return 0xCAFE


class FakeDLPackColumn:
    dtype = "float64"
    shape = (2,)
    strides = (1,)

    @property
    def __cuda_array_interface__(self) -> dict[str, object]:
        return {
            "shape": self.shape,
            "typestr": "<f8",
            "data": (0xBEEF, False),
            "version": 3,
        }

    def __dlpack__(self) -> object:
        return object()

    def __dlpack_device__(self) -> tuple[int, int]:
        return (2, 0)

    def data_ptr(self) -> int:
        return 0xBEEF


class FakeCudaArrayColumn:
    @property
    def __cuda_array_interface__(self) -> dict[str, object]:
        return {
            "shape": (4,),
            "typestr": "<u4",
            "data": (0x1234, False),
            "version": 3,
        }


class FakeHostArray:
    @property
    def __array_interface__(self) -> dict[str, object]:
        return {
            "shape": (5,),
            "typestr": "<f8",
            "data": (0x5678, False),
            "version": 3,
        }


def _descriptor_metadata() -> dict[str, Any]:
    cupy_priority = rt.neutral_buffer_descriptor_from_object(
        "group_ids",
        FakeCuPyColumn(),
        producer="cupy_union_find",
        consumer="numba_segmented_sum",
    ).to_metadata()
    dlpack = rt.neutral_buffer_descriptor_from_object(
        "values",
        FakeDLPackColumn(),
        producer="framework_dlpack",
        consumer="cupy_rawkernel",
    ).to_metadata()
    cuda = rt.neutral_buffer_descriptor_from_object(
        "row_ids",
        FakeCudaArrayColumn(),
        producer="native_optix_future",
        consumer="raw_cuda",
        lifetime_state="producer_retained",
        native_producer=True,
    ).to_metadata()
    host = rt.neutral_buffer_descriptor_from_object(
        "host_reference",
        FakeHostArray(),
        producer="cpu_reference",
        consumer="numpy",
    ).to_metadata()
    measured = rt.neutral_buffer_descriptor_from_object(
        "row_ids",
        FakeCudaArrayColumn(),
        producer="native_optix_future",
        consumer="cupy",
        transfer_status="zero_copy_measured",
        lifetime_state="producer_retained",
        native_producer=True,
        measured_same_pointer=True,
        measured_no_host_stage=True,
        measured_evidence={"probe": "synthetic_same_pointer_fixture"},
    ).to_metadata()
    return {
        "cupy_priority": cupy_priority,
        "dlpack": dlpack,
        "cuda_array_interface": cuda,
        "array_interface": host,
        "measured_zero_copy_candidate": measured,
    }


def _zero_copy_without_evidence_rejected() -> bool:
    try:
        rt.neutral_buffer_descriptor_from_object(
            "row_ids",
            FakeCudaArrayColumn(),
            producer="native_optix_future",
            consumer="cupy",
            transfer_status="zero_copy_measured",
            lifetime_state="producer_retained",
            native_producer=True,
        )
    except ValueError as exc:
        return "zero_copy_measured requires" in str(exc)
    return False


def _lifetime_probe() -> dict[str, Any]:
    lease = rt.create_neutral_buffer_lease(
        rt.neutral_buffer_descriptor_from_object(
            "row_ids",
            FakeCudaArrayColumn(),
            producer="native_optix_future",
            consumer="numba",
            lifetime_state="producer_retained",
            native_producer=True,
        )
    )
    borrowed = lease.begin_partner_borrow()
    returned = borrowed.complete_partner_borrow()
    invalid_rejected = False
    try:
        rt.validate_neutral_buffer_lifetime_transition(
            "released",
            "partner_borrowed",
            event="handoff_begin",
        )
    except ValueError as exc:
        invalid_rejected = "invalid neutral buffer lifetime transition" in str(exc)
    pending = rt.neutral_buffer_lifetime_plan(
        producer="native_optix_future",
        consumer="numba",
        state="native_owned_pending_state_machine",
        retain_until="state_machine_defined",
    )
    return {
        "borrowed": borrowed.to_metadata(),
        "returned": returned.to_metadata(),
        "invalid_transition_rejected": invalid_rejected,
        "pending_native_state_machine_required": pending.requires_native_state_machine,
    }


def build_packet(root: Path = Path(".")) -> dict[str, Any]:
    matrix_doc = (root / MATRIX_DOC).read_text(encoding="utf-8")
    zero_copy_doc = (root / ZERO_COPY_DOC).read_text(encoding="utf-8")
    index = (root / BENCHMARK_INDEX).read_text(encoding="utf-8")
    seam = (root / SEAM).read_text(encoding="utf-8")
    contract = rt.describe_v2_5_neutral_buffer_seam_contract()
    descriptors = _descriptor_metadata()
    lifetime = _lifetime_probe()
    checks = {
        "contract_prioritizes_adapter_then_dlpack_then_cuda_array": contract["protocol_priority"][:3]
        == (
            "registered_partner_adapter",
            "dlpack",
            "cuda_array_interface",
        ),
        "registered_adapter_wins_over_generic_protocols": rt.classify_neutral_buffer_protocol(
            FakeCuPyColumn()
        )
        == "cupy"
        and descriptors["cupy_priority"]["buffer"]["source_protocol"] == "cupy",
        "generic_dlpack_precedes_raw_cuda_array_interface": rt.classify_neutral_buffer_protocol(
            FakeDLPackColumn()
        )
        == "dlpack"
        and descriptors["dlpack"]["buffer"]["source_protocol"] == "dlpack",
        "cuda_array_interface_falls_back_to_borrowed_unmeasured": descriptors["cuda_array_interface"][
            "transfer_status"
        ]
        == "borrowed_device_pointer_unmeasured"
        and descriptors["cuda_array_interface"]["zero_copy_claim_authorized"] is False,
        "array_interface_stays_host_reference": descriptors["array_interface"]["transfer_status"]
        == "host_reference"
        and descriptors["array_interface"]["device_resident"] is False,
        "zero_copy_measured_requires_explicit_evidence": _zero_copy_without_evidence_rejected(),
        "measured_zero_copy_candidate_does_not_authorize_public_speedup": descriptors[
            "measured_zero_copy_candidate"
        ]["zero_copy_claim_authorized"]
        is True
        and descriptors["measured_zero_copy_candidate"]["public_speedup_claim_authorized"] is False,
        "lifetime_lease_borrow_and_return_work": lifetime["borrowed"]["is_borrowed"] is True
        and lifetime["returned"]["state"] == "producer_retained",
        "invalid_lifetime_transition_is_rejected": lifetime["invalid_transition_rejected"] is True,
        "pending_native_state_machine_is_explicit": lifetime["pending_native_state_machine_required"] is True,
        "experimental_symbols_importable_but_not_star_exported": all(
            hasattr(rt, name) and name not in rt.__all__
            for name in (
                "classify_neutral_buffer_protocol",
                "neutral_buffer_descriptor_from_object",
                "create_neutral_buffer_lease",
            )
        ),
        "matrix_doc_keeps_dlpack_runtime_blocked": "DLPack" in matrix_doc
        and "No implemented C ABI DLPack adapter" in matrix_doc,
        "zero_copy_doc_names_current_hook": "src/rtdsl/neutral_buffer_seam.py" in zero_copy_doc,
        "benchmark_index_links_goal4606": "Goal4606 neutral buffer protocol gate" in index,
        "seam_keeps_native_promotion_false": "def native_device_output_promotion_ready" in seam
        and "return False" in seam,
    }
    failed = tuple(name for name, passed in checks.items() if not passed)
    return {
        "version": PACKET_VERSION,
        "goal": "Goal4606 / V3 M207",
        "status": "neutral_buffer_protocol_gate_checked",
        "date": "2026-06-17",
        "checks": checks,
        "failed_checks": failed,
        "contract": contract,
        "descriptors": descriptors,
        "lifetime": lifetime,
        "status_matrix": {
            "neutral_buffer_protocol_classification": "validated_synthetic",
            "registered_adapter_priority": "validated",
            "dlpack_descriptor_path": "validated_descriptor_only",
            "cuda_array_interface_descriptor_path": "validated_descriptor_only",
            "array_interface_host_path": "validated_host_reference",
            "zero_copy_measured_gate": "validated_evidence_required",
            "lifetime_lease_state_machine": "validated_fail_closed",
            "c_abi_dlpack_adapter": "blocked",
            "device_buffer_query_route": "blocked",
            "public_true_zero_copy_claim": "blocked",
            "public_speedup_claim": "blocked",
        },
        "claim_boundary": {
            "neutral_buffer_protocol_gate_authorized": True,
            "dlpack_descriptor_metadata_authorized": True,
            "cuda_array_interface_descriptor_metadata_authorized": True,
            "host_array_interface_descriptor_authorized": True,
            "lifetime_state_machine_authorized": True,
            "c_abi_dlpack_adapter_authorized": False,
            "device_buffer_query_route_authorized": False,
            "external_cuda_stream_authorized": False,
            "native_device_output_promotion_authorized": False,
            "public_true_zero_copy_claim_authorized": False,
            "public_speedup_claim_authorized": False,
            "release_authorized": False,
        },
        "conclusion": (
            "Goal4606 promotes the neutral-buffer protocol seam into the current "
            "V3 closure gate. Synthetic objects validate protocol priority, "
            "DLPack descriptor metadata, CUDA-array-interface descriptor "
            "metadata, host array metadata, measured-zero-copy evidence gating, "
            "and fail-closed lifetime leasing. This is still descriptor/control "
            "evidence only: it does not authorize a C ABI DLPack adapter, "
            "device-buffer query route, external CUDA stream ordering, native "
            "device-output promotion, public true-zero-copy wording, or speedup "
            "wording."
        ),
    }


def write_report(packet: dict[str, Any], path: Path) -> None:
    lines = [
        "# Goal4606 / V3 M207 Neutral Buffer Protocol Gate",
        "",
        f"Status: `{packet['status']}`",
        "",
        "## Conclusion",
        "",
        packet["conclusion"],
        "",
        "## Status Matrix",
        "",
        "| Surface | Status |",
        "| --- | --- |",
    ]
    for name, status in packet["status_matrix"].items():
        lines.append(f"| `{name}` | `{status}` |")
    lines.extend(
        [
            "",
            "## Checks",
            "",
            "| Check | Passed |",
            "| --- | --- |",
        ]
    )
    for name, passed in packet["checks"].items():
        lines.append(f"| `{name}` | `{passed}` |")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This validates protocol classification, descriptor metadata, and lifetime-state behavior only.",
            "- C ABI DLPack adapters, device-buffer query routes, external CUDA stream ordering, native device-output promotion, public true-zero-copy wording, speedup wording, and release claims remain blocked.",
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
