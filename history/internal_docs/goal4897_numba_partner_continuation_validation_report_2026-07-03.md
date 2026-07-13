# Goal4897: Numba partner continuation validation

Date: 2026-07-03

## Verdict requested

`completed_numba_partner_enabled__bounded_app_continuation_speedup`

## Goal

Enable and validate the Numba partner continuation path for the RTDL v2.14 RayJoin paper-reproduction app after Goal4896.

This goal did not change RTDL core semantics. It investigated why the representative overlay summaries reported `numba_available=false`, enabled the partner environment on the POD, and measured whether the existing Numba app-continuation kernels improved the writer/continuation stage while preserving byte equality.

## Finding: why Numba was not active

POD import probe before repair:

```json
{
  "numba": {
    "ok": false,
    "error": "ModuleNotFoundError(\"No module named 'numba'\")"
  },
  "goal4886_rayjoin_numba_overlay_kernels": {
    "ok": true,
    "numba_available_attr": false
  }
}
```

The app-layer Numba code was already wired. The partner package was simply not installed in the POD Python environment.

Repair action:

```text
python -m pip install --break-system-packages numba
```

Installed versions:

```json
{
  "numba_version": "0.66.0",
  "NUMBA_AVAILABLE": true
}
```

## Synthetic parity

Ran the existing Numba synthetic parity harness:

- midpoint pair generation: match
- consecutive point dedupe: match
- chain keep: match
- chain-has-xsects: match
- writer skip decision: match

Evidence artifact:

- `history/internal_docs/goal4897_numba_synthetic_parity_summary_2026-07-03.json`

## Representative overlay result

Representative pair:

- Australia lakes x parks current-source representative pair
- same AuthorOfficial comparator as Goal4875/Goal4896
- same public RTDL primitives route:
  - public planar-map LSI
  - public planar-map point-location/PIP
  - Python app overlay logic with Numba partner continuation enabled

Correctness:

| Metric | Value |
|---|---|
| byte-equal | true |
| generated SHA256 | `a15e0dd4f3a4ffa6a4f8595a317cb53f31979aed02c78f4de243bb40ef40493e` |
| author SHA256 | `a15e0dd4f3a4ffa6a4f8595a317cb53f31979aed02c78f4de243bb40ef40493e` |
| output lines | 276,320 |

Evidence artifacts:

- first run: `history/internal_docs/goal4897_numba_first_overlay_summary_2026-07-03.json`
- warmed repeat: `history/internal_docs/goal4897_numba_repeat_overlay_summary_2026-07-03.json`

## Performance comparison

The fair comparison is against Goal4896's same-wrapper, pair-id LSI route, before Numba was installed.

| Route | Wrapper total | Writer phase | Byte equal | Numba available |
|---|---:|---:|---|---|
| Goal4896 pair-id LSI, Numba unavailable | 14.055081s | 3.355789s | true | false |
| Goal4897 pair-id LSI, Numba enabled | 13.167668s | 2.583972s | true | true |

Bounded speedups:

- writer/app-continuation phase: about `1.30x`
- wrapper total: about `1.07x`

Interpretation:

- This confirms that the Numba partner path is live and correct.
- The effect is useful but limited because the Numba code only accelerates selected app-continuation helpers and skip-plan decisions; the remaining output-chain writer still performs Python file formatting and per-kept-chain work.
- This does not close the deeper RT traversal/in-kernel fusion gap discussed in the architecture notes.

## What is generic and what is app-layer

Generic RTDL:

- public LSI primitive,
- public point-location/PIP primitive,
- pair-id rows from Goal4896,
- packed CDB loader/cache from Goal4895.

Application layer:

- RayJoin Section 5.7 workflow,
- midpoint generation,
- output-chain writer,
- chain skip-plan logic,
- Numba kernels in `goal4886_rayjoin_numba_overlay_kernels.py`.

The Numba code is not a hidden RTDL core primitive and not a RayJoin-specific kernel embedded in RTDL core. It is a user/application-layer partner continuation.

## Boundaries

Authorized claim:

- On the representative Australia lakes x parks overlay, enabling the existing Numba partner continuation path preserves byte equality and improves the writer/app-continuation phase from about 3.36s to about 2.58s.

Not authorized:

- no full Section 5.7 eight-pair claim,
- no broad RayJoin speedup claim,
- no claim that RTDL beats AuthorOfficial overall,
- no claim that Numba is on the RTDL primitive path,
- no claim that Numba is correctness-critical,
- no claim that this solves the in-traversal callback/fusion gap.

## Next likely bottleneck

After Goal4897, the warmed representative run still spends meaningful time in:

- LSI pair-id rows: about 2.80s,
- output writer: about 2.58s,
- vertex PIP outer call: about 1.09s,
- intersection reprojection + sorting: about 0.89s combined.

Further improvement requires either:

1. a generic prepared-left/device-resident LSI query-side route, or
2. deeper app-continuation restructuring to reduce Python formatting/writer work.
