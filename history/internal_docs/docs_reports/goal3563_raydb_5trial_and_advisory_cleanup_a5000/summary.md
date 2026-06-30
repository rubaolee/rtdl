# Goal3563 RayDB 5-Trial and RT-DBSCAN Advisory Cleanup Artifact

GPU: `NVIDIA RTX A5000, 580.126.09, 24564 MiB`

## RayDB 5-Trial Medians

| Mode | v2.3 median sec | v2.8/v2.9 median sec | v2.8/v2.9 speedup |
| --- | ---: | ---: | ---: |
| count | 0.000585723 | 0.000584166 | 1.002664x |
| sum | 0.000753220 | 0.000787107 | 0.956948x |

## RT-DBSCAN Seed Repeat-4 Probe

| Lane | metric sec | repeat | warmup | measured run count |
| --- | ---: | ---: | ---: | ---: |
| v23 | 0.014903007 | 4 | 1 | 3 |
| v28 | 0.014715746 | 4 | 1 | 3 |

RT-DBSCAN seed speedup: `1.012725x`. Internal evidence only; no public claim authorized.
