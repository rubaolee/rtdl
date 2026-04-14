# Goal 339 Consensus: v0.6 Graph Data / Layout Contract

Date: 2026-04-13
Consensus Status: Approved

## Summary

This consensus establishes the technical layout boundary for the `v0.6` graph expansion.

## Consensus Items

1.  **Canonical Layout**: Adopt **CSR (Compressed Sparse Row)** as the mandatory internal and external layout for all graph traversal and counting workloads.
2.  **Indexing Boundary**: Standardize on `uint32_t` for vertex IDs and edge indices. This establishes a "bounded scale" limit of roughly 4 billion elements for the `v0.6` research line.
3.  **Topology Assumption**: Commencing with "Simple Graphs" (no self-loops, no multiedges). Triangle counting assumes undirected graphs; BFS assumes directed graphs (modeled in CSR).
4.  **In-Order Adjacency**: Adjacency lists (column indices) within CSR rows must be stored in strictly ascending order. This is a requirement for the Triangle Count truth-path and native oracle.

## Participants

- RTDL Core Collaborator (User)
- Gemini AI Assistant (Technical lead)
