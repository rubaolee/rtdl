# Goal4151 - RT-DBSCAN Single-Pass Advisor Metadata

Date: 2026-06-09

Verdict: accept-with-boundary

## Purpose

Goal4151 makes the Goal4149/Goal4150 single-pass direct-status evidence visible
to users through the existing explicit route advisor. This is a metadata and
guidance update only; it does not execute a route or change the stable default.

## Change

For tested RT-DBSCAN direct-status rows at factor `0.25`, advisor options now
include:

- `direct_status_convergence_mode = "single_pass_candidate"`
- `direct_status_convergence_mode_status =
  "explicit_user_selected_same_signature_candidate_not_default"`
- same-signature evidence against `until_stable`
- replay and total speedup versus the stable direct-status loop
- `single_pass_promoted_default = False`

The advisor also records
`automatic_convergence_mode_selection_authorized = False` and its claim boundary
now explicitly forbids automatic convergence-mode selection.

## Boundary

This preserves the RTDL rule that route, partner, factor, and convergence mode
remain explicit user choices. The single-pass candidate is discoverable because
it is fast and matched stable signatures in Goal4149/Goal4150, but it is not a
hidden dispatcher choice and not a universal default.

This goal does not authorize release, public speedup wording, broad RT-core
wording, whole-app benchmark claims, paper reproduction, hidden dispatch,
automatic partner selection, automatic partition-cell-factor selection,
automatic convergence-mode selection, app-specific engine logic, native ABI
additions, AMD claims, or true-zero-copy claims.
