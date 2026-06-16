# Goal4429 V3.0 M32 Barnes-Hut Grouped Vector Partner-Dual Refresh

## Decision

M32 closes a Barnes-Hut partner-policy/front-door gap, not the full
RT-Barnes-Hut app. The current Barnes-Hut grouped-vector typed-stream route now
explicitly lists Numba as a supported no-C++ reference partner alongside the
best GPU partner path, and the evidence runner measures both CuPy and Numba
through the same app front door.

## Measured Evidence

The formal pod evidence is:

- `docs/reports/goal4429_v3_0_m32_barnes_hut_grouped_vector_partner_dual_262144x8_2026-06-16.json`

The measured workload uses 262,144 groups x 8 rows per group, for 2,097,152
grouped-vector contribution rows. The runner uses deterministic presegmented
grouped-vector rows, caller-supplied partner-owned columns, and
`validate_row_offsets=False` for the timed prepared-window calls. The timed
window therefore covers the generic typed-stream front door plus partner
grouped-vector continuation, not host row construction or host-to-device input
transfer.

| Partner | Kernel | Timed median | Timed window | Setup outside timed window | Correctness |
|---|---:|---:|---:|---:|---|
| CuPy | `cupy_grouped_vector_sum_offsets_f64x2_kernel` | 0.018767 s | 1.505450 s / 80 repeats | 0.418073 s | matches reference within 1e-9 |
| Numba | `numba_grouped_vector_sum_offsets_f64x2_kernel` | 0.022205 s | 1.790195 s / 80 repeats | 0.204628 s | matches reference within 1e-9 |

CuPy is 1.18x faster than Numba by median on this front-door continuation
measurement. That is useful policy evidence, not a public speedup claim: CuPy is
the better partner for this exact grouped-vector continuation on this pod, while
Numba is the no-C++ reference route with the same RTDL app contract.

Correctness acceptance is tolerance-based at `1e-9` absolute error for the
float64 grouped sums. Exact output signatures are still recorded as diagnostics:
CuPy and Numba are byte-identical to each other here, while both differ from the
NumPy reference only by floating-reduction ordering at max absolute error
3.55e-15.

## Architecture Boundary

This is a partner continuation benchmark for
`generic_grouped_vector_sum_typed_stream_partner_columns`. It does not execute native RT traversal, does not compare against Embree or OptiX RT cores, does not claim full RT-Barnes-Hut reproduction, and does not authorize public speedup wording.

The important V3.0 lesson is narrower but useful: for an app that needs a
complex aggregate continuation, RTDL can expose a generic primitive/typed-stream
contract and let the user choose either a fastest available partner such as CuPy
or a no-C++ Numba reference path. That keeps the system app-agnostic while still
avoiding unnecessary host materialization inside RTDL.

## Follow-Up Debt

Barnes-Hut still needs a fused or prepared device-continuation bridge that
connects RT-produced aggregate frontiers to device-side ranked/summary aggregate
and exact-force finalize windows. M32 only makes the existing grouped-vector
continuation surface honest and measured.
