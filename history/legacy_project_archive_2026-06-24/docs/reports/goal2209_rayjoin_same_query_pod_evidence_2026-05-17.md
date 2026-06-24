# Goal2204 RayJoin Same-Query Pod Artifact Import

Status: imported pod artifacts for review; public performance claims remain unauthorized.

## Import

- Source artifact directory: `C:\Users\Lestat\Desktop\work\rtdl_v0_4_release_prep_review\scratch\goal2198_r6_artifacts_20260517`
- Repo artifact directory: `C:\Users\Lestat\Desktop\work\rtdl_v0_4_release_prep_review\docs\reports\goal2209_rayjoin_same_query_pod_evidence`
- Full query streams copied into repo: `false`

## Stream Provenance

| Workload | Stream | Bytes | SHA-256 | Copied |
| --- | --- | ---: | --- | --- |
| `lsi` | `rayjoin_lsi_gen100000_stream.json` | 12629253 | `5755c364fa968e084c944830d78fb9450df4caf9d71d56be6a4d891fde599d15` | false |
| `pip` | `rayjoin_pip_gen100000_stream.json` | 7059386 | `71a2efed61b4642aff795bdff17cb9c944f5435606326c3df7578f6fd6df6e2d` | false |

## Imported Files

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `environment.txt` | 3243 | `b4a624786d2627f0cb694c0c9b7389c08e303eae24ecea6717cbd46f250f0266` |
| `progress.log` | 4175 | `e70735d4d815c2719770fe0324255ec7f51aad6a72648494d7b5bde833c61b34` |
| `summary.json` | 5160 | `f17d9943f6d15f5e8b592fd88124dc1e3e7e867ff05f6dfce8f0c5a8b5bbd92b` |
| `rayjoin_lsi_grid.log` | 1074 | `98dff30bfe2ca576c1047cbcd230fc32e7546d883cf00e07b8a4b38412540913` |
| `rayjoin_lsi_lbvh.log` | 1074 | `5ab7272c870294904b1b65ce1b35aa3fa02c1792cbab4e1179de41f8908bd435` |
| `rayjoin_lsi_rt.log` | 1832 | `aa7d34676a89e3279bab1813d9a383a538b4a8c3132012d504033ea8f020206a` |
| `rtdl_lsi_same_rayjoin_stream.json` | 2305 | `ca89ac866330b184cb06a63fa2e540ce630bc0cbf0eb1a066b6c7656a3376aeb` |
| `rayjoin_pip_grid.log` | 673 | `ab4f8f7a94ec49165f1bbe6d5fd3c520c7a36177bd5c0fff435cf13f437f7b46` |
| `rayjoin_pip_lbvh.log` | 841 | `86110c3f0c9c39e290d1d3caa13205f038947791a7cf9271460b3360d367385f` |
| `rayjoin_pip_rt.log` | 1355 | `8aee5f74d06b71c1eac0e7e87deef009e5df91b06e5ac6236ce4d9a8d35e2cb9` |
| `rtdl_pip_same_rayjoin_stream.json` | 2300 | `562c8dc2a4080b0e63b07bd5c04c8f8da933774f28b9b15a19c3a85ab411ed43` |
| `evidence_summary.regenerated.json` | 10840 | `cc0d77a7cff64a2effc87e8d9ebf37b582be02ff72677281e608d3badda84b37` |
| `evidence_report.regenerated.md` | 1601 | `c4e7d74fecc048455ecd70ec5216e24baa7ea38246cb8420686d2ac0e818e201` |

## Evidence Summary

# Goal2201 RayJoin Same-Query Evidence Summary

Status: generated from pod artifacts; claim boundaries remain locked unless a later reviewed report changes them.

## Scope

This report summarizes RayJoin-generated PIP/LSI query streams and RTDL replay over the same streams.
It is not by itself a RayJoin paper reproduction or a v2.0 release authorization.

## RayJoin Query Phase

| Workload | Mode | Query ms | Build index ms | Adaptive grouping ms | OptiX launches | Intersections | Built-in check |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `lsi` | `grid` | 4.6893 | 2.72202 | n/a | 0 | 8921 | n/a |
| `lsi` | `lbvh` | 1.52763 | 4.31705 | n/a | 0 | 8921 | n/a |
| `lsi` | `rt` | 0.611623 | 0.721931 | 0.431061 | 4 | 8921 | n/a |
| `pip` | `grid` | 16.8404 | 1.86205 | n/a | 0 | n/a | n/a |
| `pip` | `lbvh` | 10.2307 | 21.0481 | n/a | 0 | n/a | pass |
| `pip` | `rt` | 0.575066 | 0.818968 | 0.550985 | 4 | n/a | pass |

## RTDL Same-Stream Replay

| Workload | Query count | Reference rows | CPU sec | Embree sec | OptiX sec | OptiX/CPU | OptiX/Embree |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `lsi` | 100000 | 8921 | 1.153435 | 106.047649 | 0.083064 | 0.072x | 0.001x |
| `pip` | 100000 | 8686 | 2.758106 | 0.106248 | 4.107544 | 1.489x | 38.660x |

## Boundary

The summary keeps these claims unauthorized:

- paper-scale RayJoin reproduction
- RTDL beats RayJoin
- broad RT-core speedup
- v2.0 release readiness

A stronger public performance claim needs the raw artifacts, external review, and a separate consensus report.


## Boundary

This import does not authorize RayJoin paper reproduction, RTDL beating RayJoin, broad RT-core speedup, or v2.0 release readiness.
Those claims require external review and a separate consensus report over the imported artifacts.
