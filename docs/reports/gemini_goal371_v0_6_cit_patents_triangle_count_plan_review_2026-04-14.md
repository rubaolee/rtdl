## Review of Goal 371: v0.6 bounded cit-Patents triangle-count plan

Based on the provided documentation, the proposed `cit-Patents` triangle-count transform for Goal 371 demonstrates honesty, coherence with the current truth-path contract, and appropriate boundedness for a first second-dataset triangle slice.

**1. Honesty of the Proposed Transform:**
The plan explicitly details the `simple-graph` transform applied to the raw `cit-Patents` dataset for triangle counting. This transformation involves:
- Reading the raw directed edge list.
- Dropping self-loops.
- Canonicalizing each edge to `(min(src, dst), max(src, dst))`.
- Deduplicating canonical undirected edges.
- Materializing a simple undirected CSR graph.

This transparent declaration of the data preparation steps ensures an honest representation of the workload. It clarifies that the triangle count is performed on a derived simple undirected graph, rather than directly on the raw directed graph, managing expectations for direct comparability.

**2. Coherence with the Current Truth-Path Contract:**
The chosen `simple-graph` transform is identical to the methodology successfully applied to the `wiki-Talk` dataset for triangle counting. This approach maintains consistency with the established `v0.6` truth-path contract, which assumes simple graphs, strictly ascending neighbor lists, and no self-loops. By aligning with existing, validated practices, the plan ensures coherence and leverages previous work.

**3. Appropriate Boundedness for a First Second-Dataset Triangle Slice:**
The plan outlines a clearly bounded approach:
- It specifies using the `graphalytics_cit_patents` dataset with the `simple_undirected` transform for `triangle_count`.
- It recommends starting with a conservative bound, smaller than the latest `wiki-Talk` triangle slice, determined by quick local/Linux probing rather than pre-guessing.
- The scope sections explicitly state that this is a planning slice only, not a live evaluation, full dataset closure, benchmark claim, or paper-scale reproduction.

This constrained scope and iterative approach make the initial slice appropriately bounded, allowing focused development and validation without over-committing to full-scale performance or reproduction claims at this stage.
