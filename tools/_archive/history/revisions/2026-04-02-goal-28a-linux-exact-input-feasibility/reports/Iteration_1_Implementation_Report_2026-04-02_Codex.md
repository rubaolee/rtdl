# Goal 28A Implementation Report

Date: 2026-04-02

## Work Performed

- measured Linux host CPU, memory, and disk capacity on `192.168.1.20`
- probed the RayJoin exact-input and raw public source URLs directly from the Linux host
- found that the documented Dryad exact-input URL returns `404 Not Found`
- confirmed that the public raw-source pages and RayJoin README are reachable from the Linux host
- created `/home/lestat/work/rayjoin_sources` on the Linux host
- staged the reachable public-source documentation files there
- wrote the Goal 28A feasibility report in the repo

## Main Result

The Linux host is a valid Embree testing platform, but the next bottleneck is dataset acquisition/conversion, not runtime installation. Exact-input execution cannot currently start from the previously preferred Dryad share because that URL is unavailable from the host.
