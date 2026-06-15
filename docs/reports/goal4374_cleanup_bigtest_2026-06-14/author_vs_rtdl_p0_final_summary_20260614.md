# RayJoin Author vs RTDL Comparison

| Program | Implementation | Timing View | Seconds | Count | Notes |
|---|---|---|---:|---:|---|
| lsi | rayjoin_author_rt | end_to_end_process | 17.110517 | 180,506 | Author command wall time, includes its own read/init/build/query/cleanup phases. |
| lsi | rayjoin_author_rt | author_query | 0.004386 | 180,506 | Author-reported Query phase. |
| pip | rayjoin_author_rt | end_to_end_process | 16.256993 |  | Author command wall time, includes its own read/init/build/query/cleanup phases. |
| pip | rayjoin_author_rt | author_query | 0.007200 |  | Author-reported Query phase. |
| overlay | rayjoin_author_rt | end_to_end_process | 7.149181 |  | Author command wall time, includes its own read/init/build/query/cleanup phases. |
| overlay | rayjoin_author_rt | intersection_edges | 0.005974 |  | Author-reported Intersection edges phase. |
| overlay | rayjoin_author_rt | computer_output_polygons | 0.033563 |  | Author-reported Computer output polygons phase. |
| lsi | rtdl_embree | hot_median | 5.892485 | 181,629 | RTDL hot median after warmup=1 repeat=3. |
| lsi | rtdl_embree | native_median |  | 181,629 | Native traversal/RT phase where available. |
| lsi | rtdl_optix | hot_median | 2.520978 | 181,629 | RTDL hot median after warmup=1 repeat=3. |
| lsi | rtdl_optix | native_median | 0.002023 | 181,629 | Native traversal/RT phase where available. |
| pip | rtdl_embree | hot_median | 0.303879 | 3,823,783 | RTDL hot median after warmup=5 repeat=60. |
| pip | rtdl_embree | native_median | 0.303813 | 3,823,783 | Native traversal/RT phase where available. |
| pip | rtdl_optix | hot_median | 0.277429 | 3,823,783 | RTDL hot median after warmup=5 repeat=60. |
| pip | rtdl_optix | native_median | 0.118839 | 3,823,783 | Native traversal/RT phase where available. |
| pip | rtdl_optix_device_resident | hot_median | 0.118584 | 3,823,783 | RTDL hot median after warmup=5 repeat=60. |
| pip | rtdl_optix_device_resident | native_median | 0.118549 | 3,823,783 | Native traversal/RT phase where available. |
| pip | rtdl_optix_device_segment_ids | hot_median | 0.118565 | 5,288,684 | RTDL hot median after warmup=5 repeat=60. |
| pip | rtdl_optix_device_segment_ids | native_median | 0.118543 | 5,288,684 | Native traversal/RT phase where available. |
| overlay | rtdl_embree | end_to_end | 10.704975 | 181,629 | RTDL overlay median including CDB load/pack/cache and compute after warmup=1 repeat=3. |
| overlay | rtdl_embree | load_pack | 0.046806 |  | RTDL app ingestion plus packed-array load/pack. |
| overlay | rtdl_embree | compute_without_load_pack | 10.658170 | 181,629 | RTDL overlay total minus load/pack phase. |
| overlay | rtdl_optix | end_to_end | 5.780408 | 181,629 | RTDL overlay median including CDB load/pack/cache and compute after warmup=1 repeat=3. |
| overlay | rtdl_optix | load_pack | 0.047190 |  | RTDL app ingestion plus packed-array load/pack. |
| overlay | rtdl_optix | compute_without_load_pack | 5.733218 | 181,629 | RTDL overlay total minus load/pack phase. |
