# Goal 1602: v1.6 Public Docs Overclaim Audit

## Verdict

The current front-door public docs mostly preserve the required claim
boundaries, but one roadmap drift was found and fixed:

```text
docs/current_architecture.md previously described v1.6-v2.0 as the staged
partner-mechanism track.
```

That is no longer the accepted roadmap. The page now says:

```text
v1.6 is the planned first Python+RTDL architecture closure milestone, not a
performance freeze.
v1.7-v2.0 are the staged Python+partner+RTDL mechanism track.
```

This audit does not publish `v1.6` and does not authorize any new public
performance, zero-copy, partner, package-install, or release-tag claim.

## Audited Public Docs

The audit focused on current front-door/user-facing docs, not historical
handoffs or archived goal reports:

- `README.md`
- `docs/README.md`
- `docs/public_documentation_map.md`
- `docs/current_architecture.md`
- `docs/capability_boundaries.md`
- `docs/rtdl_feature_guide.md`
- `docs/quick_tutorial.md`
- `docs/tutorials/README.md`
- `docs/app_example_quickstart.md`
- `docs/application_catalog.md`
- `docs/technical_app_notes/README.md`
- `docs/technical_app_notes/app_implementation_matrix.md`
- `docs/technical_app_notes/app_primitive_classification.md`
- `docs/performance_model.md`
- `docs/current_main_support_matrix.md`
- `docs/features/engine_support_matrix.md`
- `docs/release_reports/v1_5/README.md`
- `docs/release_reports/v1_5/release_statement.md`
- `docs/release_reports/v1_5/support_matrix.md`
- `docs/release_reports/v1_5_1/README.md`
- `docs/release_reports/v1_5_2/README.md`

## Findings

### Fixed

- `docs/current_architecture.md` had stale roadmap wording that grouped
  `v1.6-v2.0` as partner-mechanism milestones. This conflicted with the
  accepted Goal 1599-1601 boundary where `v1.6` closes Python+RTDL and
  `v1.7-v2.0` starts Python+partner+RTDL. The wording is now aligned.

### Per-File Current-Docs Summary

| File | Result |
| --- | --- |
| `README.md` | Boundaries preserved; current release remains `v1.5`; `COLLECT_K_BOUNDED` candidate wording stays non-promotional. |
| `docs/README.md` | Boundaries preserved; source-tree usage and `--backend optix` limitations remain explicit. |
| `docs/public_documentation_map.md` | Boundaries preserved; user path separates current docs from historical material. |
| `docs/current_architecture.md` | Fixed stale roadmap wording; now aligns `v1.6` with Python+RTDL closure and `v1.7-v2.0` with partner work. |
| `docs/capability_boundaries.md` | No blocking `v1.6`, speedup, zero-copy, or partner overclaim found. |
| `docs/rtdl_feature_guide.md` | No blocking overclaim found; RT-core claim notes remain guarded. |
| `docs/quick_tutorial.md` | No package-install support claim found; dependency install remains requirements-only. |
| `docs/tutorials/README.md` | No blocking `v1.6` or performance overclaim found. |
| `docs/app_example_quickstart.md` | No blocking overclaim found; app runs keep NVIDIA RT-core and whole-app boundaries visible. |
| `docs/application_catalog.md` | No blocking overclaim found; app rows remain scoped to reviewed subpaths. |
| `docs/technical_app_notes/README.md` | No blocking overclaim found; technical notes are explicitly non-claiming. |
| `docs/technical_app_notes/app_implementation_matrix.md` | No blocking overclaim found; reduced-copy and whole-app boundaries remain explicit. |
| `docs/technical_app_notes/app_primitive_classification.md` | No blocking overclaim found; `COLLECT_K_BOUNDED` remains experimental and copy reduction is not zero-copy. |
| `docs/performance_model.md` | No blocking overclaim found; zero-copy/low-copy interop is framed as a future architecture target. |
| `docs/current_main_support_matrix.md` | No blocking overclaim found; current v1.5 boundary remains explicit. |
| `docs/features/engine_support_matrix.md` | No blocking overclaim found in the public engine-support contract. |
| `docs/release_reports/v1_5/README.md` | Historical v1.5 package; no edit made. |
| `docs/release_reports/v1_5/release_statement.md` | Historical v1.5 release statement; no edit made. |
| `docs/release_reports/v1_5/support_matrix.md` | Historical v1.5 support matrix; no edit made. |
| `docs/release_reports/v1_5_1/README.md` | Candidate docs remain non-promotional. |
| `docs/release_reports/v1_5_2/README.md` | Candidate docs remain non-promotional. |

### No Blocking Overclaims Found

The audited public docs preserve these boundaries:

- `--backend optix` is not by itself a NVIDIA RT-core speedup claim.
- Public speedup wording requires exact reviewed subpath evidence.
- v1.5 is not a whole-app speedup release.
- `COLLECT_K_BOUNDED` remains experimental or pending unless a later reviewed
  gate promotes it.
- v1.5.1 and v1.5.2 candidate docs do not authorize stable promotion, public
  speedup wording, zero-copy wording, whole-app claims, or release-tag action.
- Source-tree usage remains the supported usage pattern.
- Package-install support is not claimed.
- True zero-copy remains future/conditional wording, not a current release
  claim.

## Non-Blocking Notes

- Historical v1.5 release-package files still mention older roadmap language
  such as v1.6 through v2.0 partner work. Those files are release-history
  artifacts for the already-published v1.5 package and should not be rewritten
  as if they were current `v1.6` release docs.
- `docs/performance_model.md` names zero-copy or low-copy interop as a future
  v2.0 target. In context, this is framed as future architecture and not a
  current claim. No edit was required.

## Validation

The matching regression test is:

- `tests/goal1602_v1_6_public_docs_overclaim_audit_test.py`

It checks that current front-door docs:

- no longer contain the stale `v1.6-v2.0` partner-track wording;
- explicitly say `v1.6` is the planned Python+RTDL closure milestone;
- explicitly say `v1.7-v2.0` is the Python+partner+RTDL track;
- keep `--backend optix` from becoming a public NVIDIA RT-core speedup claim;
- preserve `COLLECT_K_BOUNDED` and zero-copy claim blocks.
- reject broader synonymous release-claim phrases such as "v1.6 is now
  available", "v1.6 ships", or "v1.6 public release is authorized" across the
  current user-facing docs.

## Claim Boundary

This audit closes the first local public-docs overclaim pass only. It does not
publish `v1.6`, does not authorize release/tag action, does not promote
`COLLECT_K_BOUNDED`, does not authorize public speedup wording, and does not
authorize true zero-copy or partner claims.

## Next Work

Proceed to the stable native-path app-leakage audit.
