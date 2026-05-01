ACCEPT

## Findings:

1.  **100 ms minimum phase-duration rule:** The 100 ms minimum phase-duration rule is a reasonable and conservative measure to prevent fragile microbenchmark wording. It helps ensure that only significant and stable performance improvements are considered for public claims, reducing the risk of misleading results from very short or highly variable measurements.

2.  **`service_coverage_gaps / prepared_gap_summary` as sole public-review-ready row:** Based on the information provided in the document and assuming the `scripts/goal1006_public_rtx_claim_wording_gate.py` correctly implements the specified policy criteria (Goal1005 candidate status, fastest-baseline/RTX ratio >= 1.20, comparable RTX phase >= 0.10 s, no whole-app wording), it is correct that only `service_coverage_gaps / prepared_gap_summary` is identified as public-review-ready.

3.  **Wording bounded to measured query phase and avoidance of whole-app claims:** The policy explicitly states that "Goal1006 does not authorize public speedup claims. It only identifies rows mature enough to send to a later 2-AI public wording review," and mandates "no whole-app wording." This clearly indicates that the allowed wording is intended to be bounded to measured query phases, effectively preventing broad, unverified whole-app claims. The policy's intent is well-articulated to avoid such claims.

4.  **Conservative handling of held/rejected rows:** The handling of held and rejected rows appears appropriately conservative:
    *   "7 candidates held for larger-scale repeat because their RTX phases are under 10 ms" is a sound approach. Insufficiently short phase durations warrant further investigation and larger-scale testing to ensure reliability before any claims are considered.
    *   "9 non-candidate rows" are correctly excluded as they do not meet the initial criteria from Goal1005, which is a foundational requirement.
    The overall policy design, including the performance ratio and phase duration requirements, contributes to a conservative and responsible process for evaluating potential public claims.
