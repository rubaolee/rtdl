from __future__ import annotations

from dataclasses import dataclass


PARTNER_COLUMN_CONTRACT_VERSION = "rtdl.partner_column_contracts.v1"

GROUP_LAYOUT_DENSE_ZERO_BASED = "dense_zero_based"
GROUP_LAYOUT_EQUAL_CONTIGUOUS_SEGMENTS = "equal_contiguous_group_segments"
GROUP_LAYOUT_CALLER_SUPPLIED_ROW_OFFSETS = "caller_supplied_row_offsets"

SUPPORTED_GROUP_ID_LAYOUTS = (
    GROUP_LAYOUT_DENSE_ZERO_BASED,
    GROUP_LAYOUT_EQUAL_CONTIGUOUS_SEGMENTS,
    GROUP_LAYOUT_CALLER_SUPPLIED_ROW_OFFSETS,
)


@dataclass(frozen=True)
class RtdlGroupIdContract:
    """Shared partner-column contract for generic grouped continuations."""

    operation: str
    group_count: int
    row_count: int
    layout: str = GROUP_LAYOUT_DENSE_ZERO_BASED
    rows_per_group: int | None = None
    validate_in_bounds: bool = True
    validation_mode: str = "partner_specific_fail_closed"

    def to_metadata(self) -> dict[str, object]:
        return {
            "partner_column_contract_version": PARTNER_COLUMN_CONTRACT_VERSION,
            "group_id_contract_operation": self.operation,
            "group_id_layout": self.layout,
            "group_count": int(self.group_count),
            "row_count": int(self.row_count),
            "rows_per_group": None if self.rows_per_group is None else int(self.rows_per_group),
            "group_id_validate_in_bounds": bool(self.validate_in_bounds),
            "group_id_validation_mode": self.validation_mode,
        }


@dataclass(frozen=True)
class RtdlPartnerClaimBoundary:
    """False-by-default public-claim boundary for partner continuations."""

    release_authorized: bool = False
    public_speedup_claim_authorized: bool = False
    whole_app_speedup_claim_authorized: bool = False
    rt_core_speedup_claim_authorized: bool = False
    direct_device_handoff_authorized: bool = False
    true_zero_copy_authorized: bool = False
    package_install_claim_authorized: bool = False
    automatic_partner_selection_authorized: bool = False
    paper_reproduction_claim_authorized: bool = False
    app_specific_native_engine_logic_authorized: bool = False

    def to_metadata(self) -> dict[str, bool]:
        return {
            "release_authorized": self.release_authorized,
            "public_speedup_claim_authorized": self.public_speedup_claim_authorized,
            "whole_app_speedup_claim_authorized": self.whole_app_speedup_claim_authorized,
            "rt_core_speedup_claim_authorized": self.rt_core_speedup_claim_authorized,
            "direct_device_handoff_authorized": self.direct_device_handoff_authorized,
            "true_zero_copy_authorized": self.true_zero_copy_authorized,
            "package_install_claim_authorized": self.package_install_claim_authorized,
            "automatic_partner_selection_authorized": self.automatic_partner_selection_authorized,
            "paper_reproduction_claim_authorized": self.paper_reproduction_claim_authorized,
            "app_specific_native_engine_logic_authorized": self.app_specific_native_engine_logic_authorized,
        }


def make_equal_contiguous_group_id_contract(
    *,
    operation: str,
    group_count: int,
    row_count: int,
    rows_per_group: int | None = None,
    validation_mode: str = "device_resident_error_flag",
) -> RtdlGroupIdContract:
    return RtdlGroupIdContract(
        operation=str(operation),
        group_count=int(group_count),
        row_count=int(row_count),
        layout=GROUP_LAYOUT_EQUAL_CONTIGUOUS_SEGMENTS,
        rows_per_group=None if rows_per_group is None else int(rows_per_group),
        validate_in_bounds=True,
        validation_mode=str(validation_mode),
    )


def make_dense_zero_based_group_id_contract(
    *,
    operation: str,
    group_count: int,
    row_count: int,
    validation_mode: str = "partner_specific_fail_closed",
) -> RtdlGroupIdContract:
    return RtdlGroupIdContract(
        operation=str(operation),
        group_count=int(group_count),
        row_count=int(row_count),
        layout=GROUP_LAYOUT_DENSE_ZERO_BASED,
        rows_per_group=None,
        validate_in_bounds=True,
        validation_mode=str(validation_mode),
    )


def validate_group_id_contract(contract: RtdlGroupIdContract) -> dict[str, object]:
    errors: list[str] = []
    if contract.layout not in SUPPORTED_GROUP_ID_LAYOUTS:
        errors.append(f"unsupported group-id layout: {contract.layout}")
    if int(contract.group_count) < 0:
        errors.append("group_count must be non-negative")
    if int(contract.row_count) < 0:
        errors.append("row_count must be non-negative")
    if contract.layout == GROUP_LAYOUT_DENSE_ZERO_BASED:
        if contract.rows_per_group is not None:
            errors.append("dense zero-based group ids do not use rows_per_group")
        if int(contract.row_count) > 0 and int(contract.group_count) <= 0:
            errors.append("non-empty dense zero-based group ids require group_count > 0")
    if contract.layout == GROUP_LAYOUT_EQUAL_CONTIGUOUS_SEGMENTS:
        if int(contract.group_count) <= 0:
            errors.append("equal contiguous group segments require group_count > 0")
        if contract.rows_per_group is None:
            if int(contract.group_count) > 0 and int(contract.row_count) % int(contract.group_count) != 0:
                errors.append("row_count must be divisible by group_count")
        else:
            if int(contract.rows_per_group) < 0:
                errors.append("rows_per_group must be non-negative")
            if int(contract.rows_per_group) * int(contract.group_count) != int(contract.row_count):
                errors.append("rows_per_group * group_count must equal row_count")
    return {
        "status": "accept" if not errors else "reject",
        "errors": tuple(errors),
        "metadata": contract.to_metadata(),
    }


def require_group_id_contract(contract: RtdlGroupIdContract) -> dict[str, object]:
    validation = validate_group_id_contract(contract)
    if validation["status"] != "accept":
        raise ValueError("; ".join(str(error) for error in validation["errors"]))
    return validation["metadata"]


def default_partner_claim_boundary_metadata() -> dict[str, bool]:
    return RtdlPartnerClaimBoundary().to_metadata()


def validate_partner_claim_boundary(metadata: dict[str, object]) -> dict[str, object]:
    expected = default_partner_claim_boundary_metadata()
    errors = []
    for key in expected:
        if metadata.get(key) is True:
            errors.append(f"{key} must remain false unless a separate release gate authorizes it")
    return {"status": "accept" if not errors else "reject", "errors": tuple(errors)}
