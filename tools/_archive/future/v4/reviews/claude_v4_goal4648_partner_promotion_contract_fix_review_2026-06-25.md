**accept_goal4648_complete**

All three items the third reviewer flagged are confirmed fixed:

**Blocker (fail-open bug) — FIXED.**
`v4_partner_promotion_candidate_allowed` (line 186-188) now opens with an explicit guard:
```python
if normalized_partner not in {"cupy", "numba"}:
    return False
```
The old path would have iterated all contracts and returned `True` if a candidate_id happened to match any entry under an unsupported partner. The guard closes that before the loop runs.

**Negative tests for torch/unknown — PRESENT.**
`test_unsupported_contract_requests_fail_closed` (lines 56-86) covers all required cases: `torch` partner returns `False` for `candidate_allowed`, `unknown` partner returns `False`, and bare `numba` without `fixed=True` raises `ValueError`.

**`partner_parity_counts_as_v4_speed_win=False` — PRESENT.**
Set in both the `cupy` contract (line 121) and `numba_fixed` contract (line 160). Asserted in the cupy test (line 33), numba test (line 47), and front-door sweep (line 141). Present in the JSON evidence (line 35).

**Other checks pass cleanly:**
- All six claim-boundary flags are `False` across both contracts and confirmed in tests.
- Planner still returns `tier2_declared_unmeasured_partner` for CuPy until Goal4649.
- Front-door exports all four symbols; `V4_GOAL4648_PARTNER_PROMOTION_CONTRACT_STATUS` re-exported (v4.py lines 19-22, 125-127).
- Numeric bars frozen before measurement: correctness 1.0, speedup floor 1.20x, parity floor 0.98x.
- Non-authorization scope is intact — no CuPy performance claims, no broad V4 speedup, no release wording, no POD spend.

Goal4649 may start.
