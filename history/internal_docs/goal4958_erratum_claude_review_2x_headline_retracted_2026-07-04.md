# Goal4958 Erratum: 2.04x Headline Retracted

Date: 2026-07-04

## Trigger

Claude reviewed the Goal4958 status/report and identified a denominator
mismatch:

```text
Goal4957 fresh device-columnar route: ~0.90s
Goal4958 split:
  prepare_lsi_session_sec      ~0.26s
  lsi_public_rows_warmup_sec   ~0.51s
  cached/replay body           ~0.086s
  total                        ~0.86s ~= Goal4957 ~0.90s
```

The apparent improvement from ~0.90s to ~0.086s was not a new fresh-overlay
speedup. It came from excluding the first exact LSI computation and session
preparation as warmup/replay.

## Correction

The previous headline:

```text
RTDL writer-free binary route is about 2.04x slower than AuthorPatch overlay compute.
```

is retracted as a same-denominator performance claim.

Correct classification:

```text
fresh writer-free binary route: ~0.90s
AuthorPatch overlay compute:    0.0421s
fresh comparison:               ~21x slower

cached/replay body after exact LSI already computed once: ~0.086s
cached/replay arithmetic ratio vs AuthorPatch:            ~2.04x
```

The cached/replay ratio is not an authorized headline because the RTDL numerator
excludes first LSI computation while the author baseline includes overlay
compute.

## Files Amended

- `history/internal_docs/goal4958_prepared_hot_lsi_replay_and_exact_device_output_audit_2026-07-04.md`
- `history/internal_docs/v2_14_3_rayjoin_binary_operator_status_problem_solution_progress_plan_2026-07-04.md`
- `Paper-reproduction-apps/rayjoin-paper/README.md`

## Allowed Claim After Erratum

RTDL's v2.14.3 RayJoin writer-free binary route has achieved a real fresh-route
improvement:

```text
~2.92s -> ~0.90s
```

This is approximately a 3x improvement over the original numeric binary route.
It remains about 21x slower than the patched author overlay compute baseline on
a fresh same-denominator comparison.

The cached/replay body is about 0.086s after exact LSI pair ids have already
been computed once. This is useful diagnostic evidence for repeated execution
on the same prepared pair, but not a fresh overlay result.

## Next Honest Bottleneck

The next real bottleneck is exact LSI computation / exact pair-id output:

```text
lsi_public_rows_warmup_sec ~= 0.51s
```

Candidate device columns and left-id count device columns cannot substitute for
exact `{left_id, right_id}` pair rows. Any further route toward author-level
fresh performance should address generic exact planar-map LSI device pair
columns or deeper fusion, under separate review.
