# Goal 135 External Review

Date: 2026-04-06
Reviewer: Claude
Status: accepted

## Verdict

Accepted. The Goal 135 package accurately describes current `main` whole-system status,
states platform boundaries honestly, and the Linux green result is traceable. The one real
integration gap was genuine, found, and fixed before close.

## Findings

**Commit hash is real.** The report claims Linux whole-system work was done on a clean
checkout at `68075bab222877b6f3dd3635e1bbe06015d67cae`. That commit exists in the log as
"Add Goal 134 v0.2 process audit" — the commit immediately before the Goal 135 repair
commit (`4f1f4f6`). Sequence is correct.

**Integration repair is verified.** The report says `baseline_integration_test.py` was
missing `segment_polygon_anyhit_rows` from its kernel map. The current file at
`tests/baseline_integration_test.py:35` has
`"segment_polygon_anyhit_rows": segment_polygon_anyhit_rows_reference` present. The fix
is real and in the repo.

**Linux 281-test green is consistent with the evidence chain.** The `v0_2_full` and
`full` results are consistent with the v0.2 runner groups added in Goal 130 and the x4096
parity-true numbers from Goal 131. No fabrication.

**Mac geos_c failure is reported honestly.** The 193-test `unit` group failure is
attributed to missing `geos_c` linkage, not misrepresented as a code regression. Platform
boundary is correctly maintained.

**Doc updates are present and accurate.** `README.md` now has a "Current Main Position"
section distinguishing the archived v0.1 anchor from the live v0.2 midterm state.
`docs/README.md` puts `v0_2_user_guide.md` first and names the two segment/polygon
families in its Live State Summary.

**Minor stale claim in both front-door docs.** Both `README.md` ("Strongest Current
Backend Story") and `docs/README.md` ("Live State Summary") still name the v0.1 long
exact-source `county_zipcode` positive-hit `pip` surface as "the strongest current
performance closure." Goal 131 published x4096 evidence showing all RTDL backends beating
PostGIS by 7–8x on the v0.2 segment/polygon families — comparable or stronger evidence.
The claim is not wrong, but it is incomplete given the current state of `main`. Goal 135
did not catch or fix this.

## Summary

The package is honest and accurate. The Linux green result is real, the integration gap
was genuine and fixed, and the platform boundary language is correct throughout. The one
remaining gap is that both front-door docs still point to the v0.1 pip/lsi surface as the
strongest performance story without mentioning the v0.2 x4096 evidence from Goal 131.
That is an omission rather than a false claim, but it slightly undersells where `main`
actually stands.
