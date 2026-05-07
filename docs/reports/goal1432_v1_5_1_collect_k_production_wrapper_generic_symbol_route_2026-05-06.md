# Goal 1432 v1.5.1 COLLECT_K_BOUNDED Production Wrapper Generic Symbol Route

## Verdict

ACCEPTED for the measured production-wrapper route package.

The Embree and OptiX polygon candidate wrappers now route native candidate rows through the built app-name-free generic i64 symbols, `rtdl_embree_collect_k_bounded_i64` and `rtdl_optix_collect_k_bounded_i64`, before returning the `COLLECT_K_BOUNDED` result object.

## Evidence

- Linux Embree wrapper route: `docs/reports/goal1432_v1_5_1_collect_k_production_wrapper_generic_symbol_linux_embree_2026-05-06.md`
- Linux Embree JSON: `docs/reports/goal1432_v1_5_1_collect_k_production_wrapper_generic_symbol_linux_embree_2026-05-06.json`
- RTX A5000 pod OptiX wrapper route: `docs/reports/goal1432_v1_5_1_collect_k_production_wrapper_generic_symbol_pod_optix_2026-05-06.md`
- RTX A5000 pod OptiX JSON: `docs/reports/goal1432_v1_5_1_collect_k_production_wrapper_generic_symbol_pod_optix_2026-05-06.json`
- Guard test: `tests/goal1432_v1_5_1_collect_k_production_wrapper_generic_symbol_test.py`

## Run Scope

- Cases: empty zero-capacity, exact-fit two rows, one-short fail-closed overflow, zero-capacity positive fail-closed overflow
- Embree required run: `pass=4, fail=0, skipped=0`
- OptiX required run on NVIDIA RTX A5000 pod: `pass=4, fail=0, skipped=0`
- Wrapper route: native polygon candidate rows are passed to the built generic i64 symbol for canonicalization, deduplication, capacity checking, and result materialization
- Clean rerun note: the measured Linux and pod artifacts were refreshed after `8025d689d0b9b4b8b9ec9e86871b2d09601378d2` was pushed to `origin/main`

## Claim Boundary

This closes the production-wrapper generic-symbol route blocker for the measured Embree and OptiX package. It does not authorize stable `COLLECT_K_BOUNDED` primitive promotion, speedup wording, zero-copy wording, whole-app claims, broad workload claims, release tags, or release action. Stable promotion still requires the separate 3-AI stable-promotion review.
