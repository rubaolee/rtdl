# Historical and current-tree custody checks

Date: 2026-09-06

This repository retains historical authorities whose source bytes were later
changed by explicitly named successor work. Their historical conclusions must
be verified at the bound snapshot, not by pretending that a current-tree hash
comparison should still pass.

This file documents expected failures. It does not authorize resealing,
rewriting an old manifest, or hiding a failed test.

## Goal5838 frozen-core exam

Historical authority:

- evidence commit:
  `7da68056550818d8e2f6cdb4d7aa3e9029cc4524`;
- authority:
  `history/internal_docs/goal5838_generic_core_exam_20260902/FINAL_AUTHORITY.json`;
- historical conclusion:
  `PASS__GOAL5838_COMPLETE_AT_PREREGISTERED_BOUNDED_SCOPE`.

At that commit, the focused current-file seal test passes `9/9`:

```bash
git clone --no-checkout . /tmp/rtdl-goal5838-replay
git -C /tmp/rtdl-goal5838-replay checkout \
  7da68056550818d8e2f6cdb4d7aa3e9029cc4524
cd /tmp/rtdl-goal5838-replay
PYTHONPATH=src:. python -m unittest \
  tests.goal5838_core_seal_and_selection_test
```

The current branch intentionally contains later changes to all three sealed
files. Goal5844 added generic lifecycle memoization; Goals5846 and 5847 added
successor deployment/AOT functionality. Consequently this current-tree command
is expected to fail with a sealed-file drift error:

```bash
PYTHONPATH=src:. python -m unittest \
  tests.goal5838_core_seal_and_selection_test
```

That failure means only that the current source is not byte-identical to the
Goal5838 exam snapshot. It does not retroactively change the result at the
evidence commit. Current prose must describe Goal5838 in the past tense and
bind it to that commit.

The Goal5838 authority records a 7,181,936-byte native provider with SHA-256
`c91a22edbd7855824c6ad111a11c77aa599bdbb767b54b0d2e3f4355a1932076` and
`committed_to_git: false`. The repository can replay source and seal checks at
the commit, but it cannot rehash that exact DSO unless the external evidence
byte is supplied. A rebuild is new reproducibility evidence, not proof that it
recreated the absent historical binary byte for byte.

## Goal5840 independent refinement evidence

Historical authority:

- evidence commit:
  `79fdbb61c2afd602a16e8fc01b27d0cf8a576e7b`;
- authority:
  `history/internal_docs/goal5840_independent_lowering_refinement_20260903/FINAL_AUTHORITY.json`;
- historical conclusion:
  `PASS__GOAL5840_COMPLETE_AT_PREREGISTERED_BOUNDED_REFINEMENT_SCOPE`.

The authority records both its 7,181,936-byte native provider and its
3,170,210-byte raw capsule as outside Git. Their exact SHA-256 values remain in
the authority. Repository-only replay can inspect the verifier and committed
derived evidence, but cannot independently rehash absent raw bytes. The public
artifact must either include those bytes or disclose this limit and provide a
separate source-rebuild/functional-replay path.

## Goal5832 protocol-shape algebra

The Goal5832 historical manifest explicitly records:

```text
git_object_status = BROKEN_BAD_OBJECT_HEAD_NO_COMMIT_CLAIM
```

It therefore has no valid historical Git commit to which its complete file set
can be checked out. Its manifest also binds documentation and a PDF that were
not carried into the recovery branch. The current test fails while rehashing
later-changed Goal5831 files, currently first at
`goal5831.source_authorities[1]`.

Do not invent an evidence commit for Goal5832. Its safe use is the declared
terminology, denominator, and schema specification at the recorded file-hash
scope. A public artifact must not promise repository-only replay of its full
historical manifest.

## Goal5837 owner-grouped classification

Historical authority:

- evidence commit:
  `0f5c9d4297f73e412732e5a8ab133423fe4cfd21`;
- evidence tree:
  `5b80f7f07807679a7ea9eae5e7b29b303ab387ed`;
- authority:
  `history/internal_docs/goal5837_owner_grouped_classification_20260902/GOAL5837_AUTHORITY.json`;
- authority SHA-256:
  `962fe108326b51fe9ca1c31e5192aab2699d941a7ea0f733d39e718d15bae271`;
- authority self-seal:
  `025090252ac60b722cc398402297656877405a998024d221592e18aa888f0465`.

At that commit, a fresh detached clone passes:

```bash
PYTHONPATH=src:. python \
  scripts/goal5837_freeze_owner_grouped_classification.py --verify-stored
```

The current branch intentionally has a different root `AGENTS.md` identity.
Goal5837's historical authority records that then-current root file as one of
its inputs. The current-tree rebuild therefore differs only in the recorded
current-root byte count, SHA-256, and derived authority seal, and this command
fails closed with `Goal5837Error: AUTHORITY_CURRENT_INPUT_MISMATCH`.

Do not regenerate or overwrite the stored authority to make the current-tree
command green. Verify the historical classification at the exact evidence
commit; use current source tests separately for successor behavior.

## Goal5843 fair post-R1 baseline

Historical final authority:

- sealing commit:
  `75b2b34fad1f0280a43ce6cbc00e99d4b9d9d937`;
- sealing tree:
  `50fc7f1b60fbbf1ecbf65cd99c02f5c39b6717f8`;
- formal source commit recorded by the authority:
  `c2662603c4d24902361fbd70325832ee7d98a0a4`;
- authority:
  `history/internal_docs/goal5843_post_r1_fair_baseline_20260904/GOAL5843_FINAL_INTERNAL_AUTHORITY.json`;
- authority SHA-256:
  `dbf86d19083fdba6adee26ca216aae8dc00fe1d836c1afbff37aafc28e3d48a0`;
- authority self-seal:
  `c40b9fe5d3ace2f58fe29a1a39363ce25373332f774f3c36ffa839ce650bdba8`.

At the sealing commit, a fresh detached clone passes:

```bash
PYTHONPATH=src:. python \
  scripts/goal5843_build_final_authority.py --verify-stored
```

The current branch contains legitimate successor changes to nine files pinned
by Goal5843's preregistration, including its family schema/lifecycle and
prepared runtimes. The unchanged current-tree command consequently fails with
`Goal5843ContractError: preregistration differs from canonical builder` before
comparing the stored final authority.

This is an exact-snapshot refusal, not evidence that the historical transaction
failed. Do not rebuild Goal5843's preregistration from current files or reseal
its final authority. Run it only at the sealing commit, and classify current
Goal5848/Goal5851 tests as a separate current-source layer.

## Goal5807 recovered-branch support files

`tests/goal5807_provider_ready_formal_test.py` refers to two historical support
files that are absent from the recovery branch and from every object reachable
through the current repository refs:

- `history/internal_docs/goal5806_same_source_postimport_target_20260826.json`;
- `history/internal_docs/goal5807_provider_ready_confirmatory_formal_contract_20260827.json`.

Consequently five tests in that module currently terminate with
`FileNotFoundError` before exercising current runtime code. This behavior is
already present at the pre-Goal5848 `HEAD`; it is not a Goal5848 regression.
One separate v2-contract test skips when its historical input is absent.

Do not fabricate either file from a remembered schema or expected digest. The
safe current regression set excludes those byte-dependent historical tests and
reports the exclusion. If the exact historical bytes are recovered, restore
them with provenance and rerun the original hash assertions unchanged.

## Curated current verification

Current regression commands should run current-source suites and separately
label historical replay suites. Do not present a broad discovery run containing
the expected historical errors as a clean current regression. Conversely, do
not skip them silently: reference this file and report the exact expected
failures.
