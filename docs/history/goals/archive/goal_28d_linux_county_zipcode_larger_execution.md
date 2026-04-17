# Goal 28D Linux County Zipcode Larger Exact-Source Execution

Goal 28D completes the next serious Linux Embree step after Goal 28C.

Scope:
- finish full `Zipcode` staging on `192.168.1.20`
- preserve the existing exact-source conversion path from ArcGIS pages to CDB/logical RTDL inputs
- run a larger exact-source `County ⊲⊳ Zipcode` execution slice on the Linux host
- report Linux-host CPU vs Embree timings for `lsi` and `pip`
- keep all claims bounded by what the host can actually execute

Required closure conditions:
- full `Zipcode` raw-source staging is complete on `192.168.1.20`
- converted full or checkpoint datasets are documented honestly
- larger execution slices are defined and run on Linux
- CPU/Embree parity is demonstrated for the executed slices
- Claude approves the revised round and Gemini monitors the full process

Honest boundary:
- Goal 28D is not paper-scale completion unless the host actually sustains those runs
- if the host requires bounded slices, the report must state that explicitly
