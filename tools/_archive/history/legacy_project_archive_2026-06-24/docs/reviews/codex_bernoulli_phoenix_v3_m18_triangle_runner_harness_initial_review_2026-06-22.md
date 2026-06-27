# Codex + Bernoulli Initial Review: Phoenix V3 M18 Triangle Runner Harness

Date: 2026-06-22

Verdict: `revise_m18_harness`

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
focused_pod_spend_authorized_now: false
all_app_pod_spend_authorized: false
m18_satisfies_runner_harness_blocker: false
triangle_counts_as_third_strict_set_a_material_probe_now: false
```

## Finding

Bernoulli found a blocking metadata/timing bug: the first M18 harness draft
claimed `hot_path_host_materialization=false`, but the runner variant
synchronized and called `weighted_hit_sum_out.get()` inside
`run_weighted_summary_device_output_stream`, which is the measured repeat body.

That makes the M16/M17 residency metadata inaccurate, or at minimum makes the
hot/finalize timing boundary unclear.

## Required Fix

Move scalar read/finalization out of the measured hot repeat path, or mark and
report it honestly as hot-path host materialization. Add a regression test that
would fail if `.get()` or host scalar materialization happens inside the
measured runner loop while metadata says false.

## Verification Bernoulli Accepted

Bernoulli accepted these as good but insufficient:

```text
19 tests OK
dry-run status OK with 3 variants and no failed checks
release wording gate passed
overclaim scan had no matches
```

## Goal-Level Decision Audit

Decision: accept the revise verdict and fix the measured-hot-path scalar read
before any POD authorization request.

1. Was I foolish?
   Yes, in the first M18 harness draft.
2. If yes, what actions made the decision foolish?
   I placed a host scalar `.get()` inside the measured runner body while also
   asserting `hot_path_host_materialization=false`.
3. Was there another path?
   Yes. Use the prepared execution runner's finalize phase so the measured
   repeat launches device work and finalization reads the scalar once after the
   measured loop.
4. Can I now try a different path?
   Yes. Move scalar finalization out of the hot repeat path, add a regression
   test, rerun local gates, and request review again.
