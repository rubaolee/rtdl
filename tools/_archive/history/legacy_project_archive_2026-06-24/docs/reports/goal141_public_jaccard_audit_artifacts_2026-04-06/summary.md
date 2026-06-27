# Goal 141 Public Jaccard Audit

- generated_at: `2026-04-07T00:04:18`
- host: `Linux-6.17.0-20-generic-x86_64-with-glibc2.39`
- source: `MoNuSeg 2018 Training Data`
- xml_name: `MoNuSeg 2018 Training Data/Annotations/TCGA-38-6178-01Z-00-DX1.xml`
- raw_polygon_count: `424`
- selected_polygon_count: `16`
- base_left_polygon_count: `8556`
- base_right_polygon_count: `8556`
- pair_derivation: `right set is the same real-data-derived unit-cell polygon set shifted by +1 cell in x`

| copies | left_polygon_count | right_polygon_count | python_sec | cpu_sec | postgis_sec | python_parity_vs_postgis | cpu_parity_vs_postgis | jaccard_similarity |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `1` | `8556` | `8556` | `0.135213` | `0.061195` | `4.362636` | `True` | `True` | `0.917956` |
| `4` | `34224` | `34224` | `0.497132` | `0.211040` | `54.827503` | `True` | `True` | `0.917956` |
