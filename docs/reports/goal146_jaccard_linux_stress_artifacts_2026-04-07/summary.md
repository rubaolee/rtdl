# Goal 146 Jaccard Linux Stress

- generated_at: `2026-04-07T07:17:33`
- host: `Linux-6.17.0-20-generic-x86_64-with-glibc2.39`
- source: `MoNuSeg 2018 Training Data`
- xml_name: `MoNuSeg 2018 Training Data/Annotations/TCGA-38-6178-01Z-00-DX1.xml`
- selected_polygon_count: `16`
- base_left_polygon_count: `8556`
- base_right_polygon_count: `8556`
- accepted_claim: `Embree, OptiX, and Vulkan participate through the public run surfaces with documented native CPU/oracle fallback for this workload.`
- not_claimed: `No native Embree/OptiX/Vulkan Jaccard implementation, prepared-path story, or RT-core maturity is claimed here.`

| copies | left_polygon_count | right_polygon_count | python_sec | cpu_sec | embree_sec | optix_sec | vulkan_sec | cpu_ok | embree_ok | optix_ok | vulkan_ok | jaccard_similarity |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `64` | `547584` | `547584` | `8.279358` | `3.978596` | `3.699990` | `3.670949` | `3.636281` | `True` | `True` | `True` | `True` | `0.917956` |
| `128` | `1095168` | `1095168` | `16.526160` | `7.673124` | `7.421700` | `7.435530` | `7.400839` | `True` | `True` | `True` | `True` | `0.917956` |
