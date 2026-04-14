# Goal 338 Consensus: v0.6 Graph Workload Charter

Date: 2026-04-13
Consensus Status: Approved

## Summary

This consensus finalizes the semantic expectations for the `v0.6` graph initiation.

## Consensus Items

1.  **BFS Semantics**: Truth-path for BFS must produce deterministic vertex-level groupings. Single-source BFS is the priority; multi-source is reserved for future expansion.
2.  **Triangle Count Semantics**: Use the "simple undirected" convention where each triangle is counted once. The runtime must explicitly avoid duplicate counting within the truth-path.
3.  **Language Surface**: Graph workloads will use a "pass-by-materialized-layout" contract. Ingestion and complexity of graph conversion remain in the application layer (Python).
4.  **Baseline Policy**: Adopt PostgreSQL as the canonical external correctness baseline for all opening `v0.6` graph workloads.

## Participants

- RTDL Core Collaborator (User)
- Gemini AI Assistant (Technical lead)
