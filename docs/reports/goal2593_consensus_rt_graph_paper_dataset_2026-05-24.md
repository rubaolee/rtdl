# Goal2593 Consensus: RT-Graph Paper-Dataset Evaluation

Date: 2026-05-24

## Verdict

3-AI consensus accepts the Goal2593 conclusion:

The earlier synthetic K4 closeout is superseded. On real RT-Graph paper
datasets, RAPIDS cuGraph is currently the strongest end-to-end baseline, RTDL is
correct on small/medium paper datasets where the current unsegmented lowering
fits memory, and RTDL fails on larger paper datasets because it globally
materializes two-hop relations before native OptiX traversal.

The project accepts the documented scalability limitation as the closeout
boundary for this benchmark app. The app is closed as a bounded benchmark app,
not as a full RT-Graph reproduction and not as a paper-dataset speedup claim.

## Review Inputs

- Codex report:
  `docs/reports/goal2593_rt_graph_paper_dataset_evaluation_2026-05-24.md`
- Claude review:
  `docs/reports/goal2593_claude_review_rt_graph_paper_dataset_2026-05-24.md`
- Gemini review:
  `docs/reports/goal2593_gemini_review_rt_graph_paper_dataset_2026-05-24.md`
- Raw evidence:
  `docs/reports/goal2593_paper_dataset_raw/`

## Agreements

- The dataset preparation evidence is consistent with the RT-Graph README
  dataset table.
- Every successful method returned the expected triangle count.
- cuGraph should be treated as the strongest current end-to-end paper-dataset
  baseline.
- The authors' pure count kernels remain fast, but authors' full pipelines are
  dominated by preprocessing and graph-to-RT/GPU construction on this pod.
- RTDL's failures are pre-traversal memory failures in the current CuPy
  lowering, not native OptiX correctness failures.
- Native RTDL engine app-agnostic boundaries remain intact; graph semantics
  stay in Python/CuPy benchmark lowering code.

## Follow-Up Work

1. Implement segmented or streamed RT-Graph triangle-counting lowering that
   avoids global two-hop materialization.
2. Preserve the generic engine contract: device columns for rays, triangles,
   weights, and scalar reductions. Do not add graph-specific native engine ABI.
3. Re-run the paper-dataset matrix after segmented lowering exists.
4. If final cuGraph performance numbers are used for a public claim, rerun large
   datasets with an explicit warmup pass.
5. Keep PostgreSQL out of the paper-dataset performance table until it completes
   cleanly with preserved JSON evidence.

## Closeout Status

Goal2593 is closed as an evaluation and consensus goal. The RT-Graph
triangle-counting benchmark app is also closed with the accepted limitation:
RTDL currently covers correctness and same-input evaluation on paper datasets
that fit the unsegmented lowering, while largest paper-dataset scalability is a
future segmented/streamed-lowering target.
