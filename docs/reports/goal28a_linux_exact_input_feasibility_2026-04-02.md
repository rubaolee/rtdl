# Goal 28A: Linux Exact-Input Feasibility Audit

Date: 2026-04-02
Host: `192.168.1.20` (`lx1`)

## Purpose

Goal 28A answers the first serious question for Linux-host Embree reproduction:

- can `192.168.1.20` serve as the next RTDL Embree performance platform,
- can the RayJoin paper dataset families be staged there,
- and is it realistic to replace the previous Mac-only scaled-down policy with exact-input or near-exact-input runs on this host?

This goal is explicitly a feasibility and acquisition audit, not a full experiment execution round.

## Host Capacity

Observed on `192.168.1.20`:

- CPU: Intel Core i7-7700HQ
- Cores / threads: `4 / 8`
- RAM: `15 GiB`
- Free disk on `/`: about `186 GiB`

This host is materially better than the local Mac for unattended Linux Embree runs, but it is **not** a large-memory workstation. Therefore Goal 28A rejects the assumption that all RayJoin paper-scale inputs can be executed unchanged just because the machine is independent.

## Exact-Input Source Audit

The current paper-source picture from the Linux host is:

| Source | Host Result | Interpretation |
| --- | --- | --- |
| RayJoin Dryad preprocessed share | `404 Not Found` | Preferred exact-input source is currently unavailable from the Linux host using the documented URL. |
| RayJoin README | `200 OK` | Project-level source documentation is reachable. |
| USCounty ArcGIS item | `200 OK` | Public raw-source page is reachable. |
| Zipcode ArcGIS item | `200 OK` | Public raw-source page is reachable. |
| BlockGroup ArcGIS item | `200 OK` | Public raw-source page is reachable. |
| WaterBodies ArcGIS item | `200 OK` | Public raw-source page is reachable. |
| SpatialHadoop datasets page | `200 OK` | Public raw-source catalog is reachable. |

Exact-input URL probed for the Dryad share:

```text
https://datadryad.org/stash/share/aIs0nLs2TsLE_dcWO2qPHiohRKoOI3kx0WGT5BnATtA
```

### Main result

The exact-input plan has changed in one important way:

- the previously preferred Dryad exact-input URL cannot currently be treated as an available source
- so the project must proceed from the raw public source families unless a new exact-input location is obtained from the RayJoin authors

## Dataset Family Classification

| Dataset Family | Exact-Input Status | Derived-Input Status | Linux Host Execution Readiness | Notes |
| --- | --- | --- | --- | --- |
| `USCounty__Zipcode` | `blocked` | `possible` | `best first target` | Dryad exact-input unavailable; both raw public source pages are reachable; this is the strongest current bridge from existing RTDL work to a more faithful Linux-host run. |
| `USACensusBlockGroupBoundaries__USADetailedWaterBodies` | `blocked` | `possible-but-riskier` | `conditional` | Dryad exact-input unavailable; raw public source pages are reachable, but BlockGroup conversion is likely more fragile and the family is less mature in RTDL than County/Zipcode. |
| `lakes_parks_Africa` | `blocked` | `possible` | `not yet feasible to promise` | Public catalog page is reachable, but exact-input is unavailable and continent-scale extraction/conversion size is still unknown on a 15 GiB host. |
| `lakes_parks_Asia` | `blocked` | `possible` | `not yet feasible to promise` | Same reasoning as Africa. |
| `lakes_parks_Australia` | `blocked` | `possible` | `not yet feasible to promise` | Same reasoning as Africa. |
| `lakes_parks_Europe` | `blocked` | `possible` | `not yet feasible to promise` | Same reasoning as Africa. |
| `lakes_parks_North_America` | `blocked` | `possible` | `not yet feasible to promise` | Same reasoning as Africa, with especially high risk that the full pair may exceed practical memory/runtime limits on this host. |
| `lakes_parks_South_America` | `blocked` | `possible` | `not yet feasible to promise` | Same reasoning as Africa. |

Interpretation:

- `blocked`: the preferred exact-input path is currently unavailable
- `possible`: a raw-source or public-catalog path exists and can be pursued in Goal 28B
- `best first target`: this is the best candidate for the first serious Linux-host reproduction slice
- `conditional`: worth trying after the first family works, but not yet low-risk
- `not yet feasible to promise`: the current host and current dataset state do not justify a promise of paper-scale execution yet

## Linux Run Budget Policy

The Linux-host experiment policy for `192.168.1.20` is:

- keep at least `4 GiB` of free memory headroom before starting a serious dataset run
- treat `USCounty__Zipcode` as the first high-priority exact-input or near-exact-input family
- allow Linux-host Embree jobs to exceed the previous Mac `5-10 minute` budget only when they are:
  - single-purpose
  - isolated on the Linux host
  - backed by saved input/output manifests
- require a pilot run on a reduced or partially converted slice before any full-family launch
- do not promise continent-scale Lakes/Parks full execution until real converted dataset sizes are measured on the host

This is a serious-host policy, but not an unlimited-host policy.

## Per-Artifact Feasibility Notes

| Paper Artifact | Linux Host Feasibility Note |
| --- | --- |
| Table 3: `County ⊲⊳ Zipcode` | Feasible first serious target, pending raw-source acquisition and conversion. |
| Table 3: `Block ⊲⊳ Water` | Possible, but should follow after County/Zipcode because acquisition and conversion risk is higher. |
| Table 3: continent-level `LK* ⊲⊳ PK*` pairs | Not yet feasible to promise at full size on a 15 GiB host until converted dataset sizes are measured. |
| Figure 13 (`lsi` synthetic/full-scale style) | More plausible than Figure 14 on this host, but still requires a staged pilot before any `1M..5M` promise is made. |
| Figure 14 (`pip` synthetic/full-scale style) | Higher risk than Figure 13 because the PIP path has historically been the more expensive RTDL/Embree path; should not be promised at full scale yet. |
| Table 4 / Figure 15 overlay slice | Remains an analogue path until the upstream dataset families are actually acquired and converted. |

## Host Staging Performed

Created a staging workspace on the Linux host:

```sh
/home/lestat/work/rayjoin_sources
```

Staged source materials:

- `rayjoin_readme.md`
- `uscounty_item.html`
- `zipcode_item.html`
- `blockgroup_item.html`
- `waterbodies_item.html`
- `spatialhadoop_datasets.html`

Observed host staging output:

```text
rayjoin_readme.md OK 8327
uscounty_item.html OK 1146
zipcode_item.html OK 1146
blockgroup_item.html OK 1146
waterbodies_item.html OK 1146
spatialhadoop_datasets.html OK 25284
```

This means the host now has a local acquisition workspace for the currently reachable public-source documentation layer, even though it does not yet have the final paper datasets themselves.

Important note:

- the ArcGIS item snapshots returned `HTTP 200`, but the saved files are small HTML responses and should be treated as **unverified item-page snapshots**, not yet as validated raw-data exports
- the Dryad URL was probed as a current live availability check; Goal 28A does not establish whether the `404` is permanent or temporary

## What Goal 28A Resolves

Goal 28A resolves the feasibility gate:

1. the Linux host is suitable for serious Embree testing
2. the host is not large enough to blindly promise all paper-scale exact-input runs
3. the preferred Dryad exact-input URL is currently unavailable
4. the raw public source families are reachable and now staged on the host
5. future exact-input reproduction must proceed from:
   - raw public sources, or
   - a newly obtained exact-input archive from the RayJoin authors
6. `County ⊲⊳ Zipcode` is the best first Linux-host execution target
7. continent-scale and heavy PIP-style runs are still not honest to promise without a further conversion-and-pilot phase

## What Goal 28A Does Not Yet Resolve

Goal 28A does **not** yet provide:

- converted County / Zipcode / BlockGroup / WaterBodies CDB datasets on the Linux host
- continent-level Lakes / Parks extracted datasets on the Linux host
- full paper-scale Table 3 / Table 4 execution
- Linux-host Figure 13 / Figure 14 / Figure 15 experiment outputs

## Practical Conclusion

The next correct execution step is **Goal 28B**:

- acquire and convert at least one serious raw-source family into RTDL/RayJoin-compatible local inputs on `192.168.1.20`
- then run the first Linux-host exact-input or near-exact-input Embree experiment slice

The most promising first target remains:

- `County ⊲⊳ Zipcode`

because it already has the strongest existing RTDL-side path and is the easiest bridge from current fixture/derived work toward a more faithful Linux-host dataset run.

## Final Result

Goal 28A is complete.

It establishes that `192.168.1.20` is a valid Linux Embree experiment host, but that exact-input RayJoin reproduction is now primarily a **dataset acquisition and conversion problem**, not just a CPU runtime problem.
