# Historical and current-tree custody checks

Date: 2026-09-05

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
