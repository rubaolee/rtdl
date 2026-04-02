# Goal 29 Diagnosis Report (Codex)

Round result:
- no safe parity fix was proven in this round
- the round closes as a diagnosis-only goal

What was established:
1. the larger exact-source `k=5` mismatch is real and reproducible
2. the mismatch can be reduced to a 4-left / 4-right exact-source segment reproducer
3. the current float-based native geometry ABI is a confirmed contributing factor
4. the current Embree `lsi` broad phase still shows unresolved false-negative behavior beyond that precision issue

What was attempted locally and then discarded:
- double-precision native segment refine
- broader segment bounds
- robust-scene mode
- normalized ray parameterization
- scene-collision broad phase
- wider local ABI prototype

Why these changes were discarded:
- none of them produced a trustworthy, regression-clean parity fix in this round
- publishing partial runtime changes here would have reduced repo integrity

Closure recommendation:
- accept Goal 29 as an honest diagnosis round
- keep runtime code unchanged
- start a new redesign round for exact-source `lsi` broad phase plus double-precision ABI policy
