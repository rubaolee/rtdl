from __future__ import annotations

from dataclasses import dataclass

from .v4_goal4749_final_rt_core_protocol import APP_ORDER
from .v4_goal4749_final_rt_core_protocol import build_protocol


V4_APP_COMPATIBILITY_STATUS = "v4_0_app_compatibility_superset_catalog_goal4751_in_progress"


@dataclass(frozen=True)
class V4AppCompatibilityPlan:
    app: str
    status: str
    v4_route_status: str
    v4_support_class: str
    v4_route: str
    blocker: str
    cupy_status: str
    numba_status: str
    release_claim_authorized: bool = False
    v4_new_speed_claim_authorized: bool = False
    inherited_compatibility_counts_as_speed: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "app": self.app,
            "status": self.status,
            "v4_route_status": self.v4_route_status,
            "v4_support_class": self.v4_support_class,
            "v4_route": self.v4_route,
            "blocker": self.blocker,
            "cupy_status": self.cupy_status,
            "numba_status": self.numba_status,
            "release_claim_authorized": self.release_claim_authorized,
            "v4_new_speed_claim_authorized": self.v4_new_speed_claim_authorized,
            "inherited_compatibility_counts_as_speed": self.inherited_compatibility_counts_as_speed,
        }


def v4_app_compatibility_rows() -> tuple[dict[str, object], ...]:
    """Return V4.0 app-level compatibility rows sourced from Goal4749.

    This is deliberately separate from the operator-pushdown planner. The
    operator planner should keep rejecting app-identity kernels; this catalog
    answers a different user question: whether V4.0 exposes or must repair the
    benchmark app capability inherited from V2.14/V3.
    """

    rows: list[dict[str, object]] = []
    for row in build_protocol()["rows"]:
        v4 = row["versions"]["v4_0"]
        blocked = v4["route_status"] == "v4_0_repair_required_before_final_timing"
        rows.append(
            {
                "app": row["app"],
                "status": (
                    "compatibility_repair_required"
                    if blocked
                    else "compatibility_route_protocol_ready"
                ),
                "v4_route_status": v4["route_status"],
                "v4_support_class": row["v4_support_class"],
                "v4_route": v4["route"],
                "blocker": v4["blocker"],
                "cupy_status": row["partner_contract"]["cupy"],
                "numba_status": row["partner_contract"]["numba"],
                "release_claim_authorized": False,
                "v4_new_speed_claim_authorized": False,
                "inherited_compatibility_counts_as_speed": False,
            }
        )
    return tuple(rows)


def plan_v4_app_compatibility(app: str) -> V4AppCompatibilityPlan:
    key = str(app).strip().lower().replace("-", "_")
    rows = {str(row["app"]): row for row in v4_app_compatibility_rows()}
    if key not in rows:
        raise ValueError(f"unknown V4 benchmark app compatibility request: {app}")
    row = rows[key]
    return V4AppCompatibilityPlan(
        app=str(row["app"]),
        status=str(row["status"]),
        v4_route_status=str(row["v4_route_status"]),
        v4_support_class=str(row["v4_support_class"]),
        v4_route=str(row["v4_route"]),
        blocker=str(row["blocker"]),
        cupy_status=str(row["cupy_status"]),
        numba_status=str(row["numba_status"]),
    )


def validate_v4_app_compatibility_catalog() -> dict[str, object]:
    rows = v4_app_compatibility_rows()
    errors: list[str] = []
    by_app = {str(row["app"]): row for row in rows}
    if tuple(by_app) != APP_ORDER:
        errors.append("app compatibility rows must preserve promoted app order")
    if len(rows) != 10:
        errors.append("app compatibility catalog must contain 10 rows")
    for row in rows:
        app = str(row["app"])
        if row["status"] == "compatibility_repair_required" and not row["blocker"]:
            errors.append(f"{app}: repair row must name blocker")
        if str(row["v4_route_status"]).lower() in {"no_v4_route", "missing"}:
            errors.append(f"{app}: V4 route must be compatibility/repair, not hidden missing")
        if row["release_claim_authorized"] is not False:
            errors.append(f"{app}: catalog cannot authorize release")
        if row["inherited_compatibility_counts_as_speed"] is not False:
            errors.append(f"{app}: inherited compatibility cannot count as speed")
    return {
        "status": "passed" if not errors else "failed",
        "error_count": len(errors),
        "errors": errors,
        "catalog_status": V4_APP_COMPATIBILITY_STATUS,
        "row_count": len(rows),
        "repair_required_apps": [
            str(row["app"]) for row in rows if row["status"] == "compatibility_repair_required"
        ],
    }


__all__ = [
    "V4_APP_COMPATIBILITY_STATUS",
    "V4AppCompatibilityPlan",
    "plan_v4_app_compatibility",
    "validate_v4_app_compatibility_catalog",
    "v4_app_compatibility_rows",
]
