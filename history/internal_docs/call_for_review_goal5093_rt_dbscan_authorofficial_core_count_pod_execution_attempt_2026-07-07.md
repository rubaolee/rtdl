# Call For Review: Goal5093 RT-DBSCAN AuthorOfficial Core-Count POD Execution

Please review:

```text
history/internal_docs/goal5093_rt_dbscan_authorofficial_core_count_pod_execution_attempt_2026-07-07.md
Paper-reproduction-apps/rt-dbscan-paper/scripts/run_authorofficial_core_count_gate.py
Paper-reproduction-apps/rt-dbscan-paper/scripts/setup_authorofficial_core_count.sh
Paper-reproduction-apps/rt-dbscan-paper/author_patches/goal5092_authorofficial_core_count_output.patch
Paper-reproduction-apps/rt-dbscan-paper/results/authorofficial_core_count_gate_pod_cpu_summary.json
Paper-reproduction-apps/rt-dbscan-paper/results/authorofficial_core_count_gate_pod_optix_summary.json
tests/goal5092_rt_dbscan_authorofficial_gate_packet_test.py
```

## Review Questions

1. Does Goal5093 correctly classify the result as a completed bounded
   AuthorOfficial core-count comparator gate?
2. Do both POD summaries show `author_comparator_used=true`, `matched=true`,
   and `author.core_count == rtdl.core_count == 7`?
3. Does the report keep the claim boundary narrow: call-1 core-count only, not
   full DBSCAN labels, exact paper dataset reproduction, or performance?
4. Is it correct that `bounded_core_count_reproduction_claim_authorized=true`
   while `paper_reproduction_claim_authorized=false`?
5. Is the AuthorOfficial patch acceptable as a bounded comparator patch rather
   than an algorithm rewrite?
6. Is the OWL `OPTIX_PRIMITIVE_TYPE_FLAGS_CUSTOM` compatibility hunk necessary
   and sufficiently documented?
7. Does the setup script fail closed for missing build prerequisites while
   selecting the POD OptiX root and GCC 12 CUDA host compiler when available?
8. Does the RTDL OptiX route use a generic fixed-radius count-threshold device
   column primitive, rather than an RT-DBSCAN-specific native primitive?
9. Are the local tests sufficient to protect the gate packet shape and patch
   contents?
10. Should the next step be a bounded label/component-signature gate, while
    keeping full paper reproduction and performance out of scope until separately
    authorized?

## Expected Verdict Labels

Approve if valid:

```text
approve_goal5093_rt_dbscan_authorofficial_core_count_gate_pod_optix
```

Require amendments if needed:

```text
revise_goal5093_rt_dbscan_authorofficial_core_count_gate
```
