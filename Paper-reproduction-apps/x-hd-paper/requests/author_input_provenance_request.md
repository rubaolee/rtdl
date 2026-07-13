# Draft: X-HD Author Input Provenance Request

Status: `prepared_not_sent`

Suggested recipients from the paper PDF first page:

```text
liang.geng@case.edu
yuan.1203@osu.edu
liru@cse.ohio-state.edu
fusheng.wang@stonybrook.edu
zhang.574@osu.edu
```

Subject:

```text
X-HD reproduction: request for paper input provenance / hashes
```

Body:

```text
Hello,

We are attempting an independent RTDL/Python reproduction of the X-HD paper.
We have reproduced several bounded and public/source-matched scalar cases, but
full paper reproduction is currently blocked on exact input provenance.

Could you share, or confirm the availability of, any of the following for the
paper-run /local/storage/shared/HDDatasets inputs?

1. A sha256 or other checksum manifest for the paper input files used in
   Figure 5 and related experiments.
2. The input files or an archived HDDatasets bundle, if redistributable.
3. If raw inputs cannot be shared, the exact source URLs, snapshot identifiers,
   export parameters, and preprocessing scripts needed to regenerate them
   byte-identically.
4. For graphics inputs: the exact Dragon, HappyBuddha, AsianDragon, and
   ThaiStatuette files, scaling / translation / preprocessing parameters, and
   postprocessed point counts or hashes.
5. For geo inputs: the exact WKT files or hashes for dtl_cnty, uszipcode,
   USADetailedWaterBodies, USACensusBlockGroupBoundaries, lakes, parks, and
   all_nodes; plus WKT conversion/export precision and source snapshot details.
6. For BraTS: the exact validation file list/hashes and the NIfTI-to-point
   conversion rule used before hd_exec.
7. Any command-line/config details not fully captured by the checked-in JSON
   logs, including grid/cell parameters.

If datasets cannot be shared, a checksum manifest plus conversion/provenance
notes would still let us classify the reproduction status accurately without
overclaiming exact paper reproduction.

Thank you.
```
