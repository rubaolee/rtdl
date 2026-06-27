# Goal 28D Spec (Codex)

Date: 2026-04-02
Round: Goal 28D Linux County Zipcode Larger Exact-Source Execution

Intent:
- continue from Goal 28C using the same exact-source family on the Linux Embree host
- move from feature-limited proof to a larger, more serious execution slice
- close the remaining raw-source staging blocker for `Zipcode`

Initial execution plan:
1. inspect the Linux host and the current `Zipcode` staging checkpoint
2. finish `Zipcode` raw-source acquisition if the service still responds
3. extend the Goal 28C driver as needed for larger bounded execution slices
4. run the larger Linux exact-source slice and capture timing/parity results
5. write the report, then send the frozen snapshot to Claude and Gemini
