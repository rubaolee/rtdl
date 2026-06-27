# Goal 22 Dataset Sources

This artifact records the current public-source acquisition picture for the missing RayJoin paper dataset families.

| Asset | Source Type | Current Status | Preferred Use | Source URL | Notes |
| --- | --- | --- | --- | --- | --- |
| `rayjoin_preprocessed_share` | `dryad-share` | `source-identified` | Preferred exact-input source for all paper dataset families when accessible. | https://datadryad.org/stash/share/aIs0nLs2TsLE_dcWO2qPHiohRKoOI3kx0WGT5BnATtA | RayJoin README states this share contains preprocessed datasets without exposing author identification. |
| `uscounty_arcgis` | `arcgis-item` | `source-identified` | Exact-input source family for County ⊲⊳ Zipcode when using raw public data. | https://www.arcgis.com/home/item.html?id=14c5450526a8430298b2fa74da12c2f4 | ArcGIS item currently resolves to an Esri Feature Service and is updated annually. |
| `zipcode_arcgis` | `arcgis-item` | `source-identified` | Exact-input source family for County ⊲⊳ Zipcode when using raw public data. | https://www.arcgis.com/home/item.html?id=d6f7ee6129e241cc9b6f75978e47128b | ArcGIS item currently resolves to an Esri Feature Service and is updated annually. |
| `blockgroup_arcgis` | `arcgis-item` | `source-identified` | Exact-input source family for Block ⊲⊳ Water when using raw public data. | https://www.arcgis.com/home/item.html?id=1c924a53319a491ab43d5cb1d55d8561 | ArcGIS item is currently a retired Layer Package listing; manual export/conversion remains required. |
| `waterbodies_arcgis` | `arcgis-item` | `source-identified` | Exact-input source family for Block ⊲⊳ Water when using raw public data. | https://www.arcgis.com/home/item.html?id=48c77cbde9a0470fb371f8c8a8a7421a | ArcGIS item currently resolves to an Esri Feature Service and also links to a layer-package variant. |
| `lakes_parks_spatialhadoop` | `dataset-catalog` | `source-identified` | Derived-input source for continent-level Lakes/Parks pairs when exact-input share is unavailable. | https://spatialhadoop.cs.umn.edu/datasets.html | The catalog lists public Lakes and Parks families; some historical Google Drive download links may no longer be live. |
