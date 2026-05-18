"""Internal contract-family adapter namespace.

These modules are intentionally grouped by generic RTDL contract family, not by
application or domain. Public user programs should prefer the top-level RTDSL
primitive facade and examples; these re-exports are for internal migration and
compatibility while the historical flat adapter module is split safely.
"""

from __future__ import annotations

__all__ = [
    "collection",
    "columnar_payload",
    "partner_handoff",
    "prepared_handles",
    "reductions",
    "traversal",
]
