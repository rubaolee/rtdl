---

## Goal 372 Review — Bounded cit-Patents triangle-count probe

**Verdict: PASS with one flag**

---

### What is correct

**Scope boundary is clean.** The slice does exactly what Goal 372 claims: adds a runnable probe script and focused tests. It makes no live Linux result, benchmark, or paper-scale claims. Report and charter match.

**Script follows the established probe pattern.** The structure mirrors `goal362_wiki_talk_larger_triangle_count_eval.py` exactly: CLI args, `load_snap_simple_undirected_graph`, `triangle_count_baseline_evaluation`, tagged JSON output. No deviation from the truth-path contract.

**Loader handles the test fixtures correctly.** `load_snap_simple_undirected_graph` (graph_datasets.py:137-143) skips self-loops and deduplicates symmetric edges before the cap. The test fixture `0 1\n1 2\n2 0\n2 2\n1 0\n` yields 3 canonical edges → 1 triangle → `oracle_match: true` is a valid assertion. `expected_vertex_count` is used only as a floor for adjacency-list sizing (line 149), not as a rejection threshold, so small fixtures still load correctly.

**`max_canonical_edges_loaded` tagging is consistent.** Test 2 confirms the field echoes the CLI arg (50000), not the actual loaded count — same convention as goal362.

---

### The flag

**`expected_vertex_count=spec.vertex_count_hint` inflates test-time allocation.** Goal362's wiki-Talk script does not pass this parameter. Goal372 introduces it — causing both tests to allocate and iterate a **3,774,768-entry** adjacency list (`resolved_vertex_count = max(3, 3_774_768)`) for a 3-edge fixture. This is a test performance waste (the allocation alone takes non-trivial time and memory), though it does not affect correctness.

For triangle-count specifically, `expected_vertex_count` provides no semantic value: triangle count is purely topological, vertex numbering is irrelevant. Drop the parameter from the script or at least from the test invocation. If the intent is to preserve vertex ID fidelity for cross-goal consistency, that rationale should be documented; as it stands it looks like an accidental deviation from the wiki-Talk template.

---

### Minor observation

Neither test checks that the JSON is valid parseable JSON — only substring presence. This is consistent with prior goal tests and acceptable for a probe slice.

---

### Chain coherence

Goal 371 (plan) → Goal 372 (probe script, this slice) → Goal 373 (Linux execution) is a clean linear progression. Goal 372 delivers exactly what Goal 373 needs to pick up.
