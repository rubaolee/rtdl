# Goal3069 Final v2.6 Release 3-AI Consensus

Date: 2026-06-02

Status: final 3-AI consensus authorizing the `v2.6` source-tree release tag.

## Inputs

| AI | Artifact | Verdict |
| --- | --- | --- |
| Codex | `docs/reports/goal3066_v2_6_release_action_2026-06-02.md` | `accept-with-boundary` |
| Claude | `docs/reviews/goal3067_claude_final_v2_6_release_review_2026-06-02.md` | `accept-with-boundary` |
| Gemini | `docs/reviews/goal3068_gemini_final_v2_6_release_review_2026-06-02.md` | `accept-with-boundary` |

## Consensus Verdict

`accept-with-boundary`

The three-AI release consensus agrees that the committed tree is ready to tag as
`v2.6`, with the release boundaries below preserved.

## Why The Release Can Proceed

- The user explicitly authorized the release with: "we can release. Go!"
- `VERSION` reads `v2.6`.
- The current learner/front-door docs describe v2.6 as the released source-tree
  surface rather than release-candidate or pre-release.
- The v2.6 release package exists at `docs/release_reports/v2_6/README.md`.
- The release package is source-tree-only and evidence-linked.
- The documentation cleanup gate has 3-AI consensus in Goal3061.
- The native tutorial/example pod validation gate has 3-AI consensus in
  Goal3065, including `21/21` passing commands on the configured pod.
- The final release-action gate passed:

```text
Ran 18 tests in 0.733s

OK
```

- The final release consensus gate passed:

```text
Ran 21 tests in 0.744s

OK
```

## External Review Agreement

Claude explicitly accepted that:

- `VERSION` is exactly `v2.6`;
- `README.md` and `docs/README.md` use released language;
- current-facing docs are free of release-candidate/pre-release wording;
- the release package stays source-tree-only and evidence-linked;
- the five release boundaries are intact;
- the committed tree may be tagged `v2.6` after this final consensus.

Gemini explicitly accepted that:

- `VERSION` is exactly `v2.6`;
- current learner/front-door docs describe v2.6 as released;
- the release package is source-tree-only and evidence-linked;
- the release boundaries remain explicit;
- the final release gate protects release wording and current-doc cleanup;
- it is acceptable to proceed to final 3-AI consensus and tag `v2.6`.

## Release Boundaries

This consensus authorizes tagging and publishing the source-tree release as
`v2.6`.

This consensus does not authorize:

- package-install or PyPI claims;
- broad RT-core speedup claims;
- whole-application speedup claims;
- arbitrary PyTorch, CuPy, Numba, or Triton acceleration claims;
- automatic partner-selection claims;
- general zero-copy/device-residency claims;
- full paper-reproduction claims beyond exact reviewed subpaths;
- v3.0 user-defined shader injection or custom engine-extension claims.

## Release Action

After this consensus file and its regression test are committed, create and push
the `v2.6` tag on that committed tree.
