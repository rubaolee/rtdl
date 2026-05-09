**ACCEPT**

The diff is a clean v1.5→v1.6 polish pass with no blockers. Checking each criterion:

**Stale v1.0/v1.5-as-current wording**
All "current release" headings and body text updated to v1.6. v1.0 references are now marked historical ("v1.0-era app-specific native continuations", "historical app-building tutorial"). No remaining v1.5-as-current text introduced.

**Package-install claims**
README and `examples/README.md` both explicitly say "source-tree examples, not package-install examples" and require `PYTHONPATH=src:.`. The added Windows cmd.exe/PowerShell blocks follow the same pattern. No pip-install or package-install language anywhere in the diff.

**Whole-app speedup claims**
`performance_model.md` preserves "not universal whole-app speedup" as the closing rule. `quick_tutorial.md` strengthens `reduce_rows` disclaimer ("do not read it as a blanket native-backend reduction speedup claim"). No new speedup claims introduced.

**OptiX/RT-core overclaims**
`examples/README.md` adds explicit bullet: "`--backend optix` is not by itself a public NVIDIA RT-core speedup claim." Existing claim boundaries in `performance_model.md` and `quick_tutorial.md` are preserved unchanged.

**COLLECT\_K\_BOUNDED promotion**
`performance_model.md` changes "deferred to v1.5.1" to "deferred to follow-up performance work" (removes stale version, keeps it deferred). `examples/README.md` adds explicit bullet: "`COLLECT_K_BOUNDED` is not a stable v1.6 primitive." Not promoted anywhere.

**Test alignment**
Test string assertions in all three test files (`goal1231`, `goal1232`, `goal1244`) are consistently updated to match the new doc text — including the `v1.7-v2.0` roadmap language and the `v1.6 package has Windows, Linux, and OptiX validation evidence` phrase.

No new overclaims, no stale version strings left as "current", no package-install assertions, no COLLECT_K_BOUNDED stability claims.
