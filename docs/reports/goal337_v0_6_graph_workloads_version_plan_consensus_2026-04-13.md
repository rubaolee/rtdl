# Goal 337 Consensus: v0.6 Graph Workloads Version Plan

Date: 2026-04-13
Consensus Status: Approved

## Summary

The `v0.5.0` release is now complete. This consensus establishes the `v0.6` roadmap anchored on graph applications.

## Consensus Items

1.  **Paper Anchor**: Adopt the SIGMETRICS 2025 graph case-study paper (DOI: `10.1145/3727108`) as the primary external validation target for the `v0.6` line.
2.  **Initial Workloads**: Finalize `bfs` and `triangle_count` as the two opening workloads for the `v0.6` development ladder.
3.  **Boundary Policy**: Maintain strict truth-path/oracle/backend separation. Focus on Linux as the primary performance platform while maintaining correctness on Windows and macOS.
4.  **Version Shielding**: All `v0.6` work should be marked as "Real-data bounded" or "Research baseline" until paper-reproducibility benchmarks are verified.

## Participants

- RTDL Core Collaborator (User)
- Gemini AI Assistant (Technical lead)
