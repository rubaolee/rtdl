# Goal 53 Plan Report

## Summary

The next goal should be to close the bounded comparison matrix across the systems we now trust:

- PostGIS
- C oracle
- Embree
- OptiX

This is the right next step because the project has already achieved the more difficult prerequisite:

- exact correctness alignment on the accepted bounded real-data packages

## Why This Goal Is Worth Doing

It converts the current project state from a set of successful individual rounds into one coherent accepted comparison package.

That package is useful because it answers, in one place:

- which systems agree
- which workloads have been externally validated
- where Embree is stronger
- where OptiX is stronger
- where PostGIS remains structurally different

Without this closure step, the current evidence remains scattered across several goals and reports.

## Scope Choice

This plan intentionally stays bounded.

It does not expand to:

- new families
- larger nationwide runs
- new backend implementation work

Instead it consolidates the strongest already-accepted evidence on:

- `County ⊲⊳ Zipcode` `top4_tx_ca_ny_pa`
- `BlockGroup ⊲⊳ WaterBodies` `county2300_s10`

## Main Risk

The biggest risk is not correctness anymore. It is presentation honesty:

- mixing timings from non-equivalent rerun phases
- overstating fairness between PostGIS and RTDL
- hiding the fact that `pip` involves different execution models

So the report must be explicit and conservative.

## Source-Of-Truth Rule

Every matrix row must cite the accepted artifact it came from.

Preferred rule:

- if Goal 50 already contains the accepted four-system row for a package/workload, use Goal 50 directly
- do not mix in older rows from earlier reports unless a rerun or later accepted report makes them equivalent again

## Refresh-Rerun Rule

A refresh rerun is required only if:

- a needed matrix row is missing from the accepted Goal 50-style source set, or
- the candidate row comes from a different accepted code state or a materially different harness structure

Otherwise:

- do not rerun
- use the already accepted artifact directly

## OptiX Preflight

If any refresh rerun becomes necessary, first confirm:

- GPU visibility on `192.168.1.20`
- working OptiX runtime load
- the current accepted OptiX library path still resolves cleanly

## Recommendation

Proceed with Goal 53.

It is worth doing now, and it is the right bridge between:

- correctness foundation work already completed
- and broader bounded reproduction closure still to come
