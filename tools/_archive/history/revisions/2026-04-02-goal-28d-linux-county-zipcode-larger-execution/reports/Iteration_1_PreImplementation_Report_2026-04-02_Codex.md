# Goal 28D Pre-Implementation Report (Codex)

Current position after Goal 28C:
- Linux host `192.168.1.20` is ready for Embree work
- `USCounty` is fully staged and converted
- `Zipcode` is only partially staged
- Goal 28C proved the conversion/runtime path and feature-limited CPU/Embree parity on Linux

What Goal 28D must answer:
- can `Zipcode` staging be completed on the Linux host?
- what larger exact-source slice can this host execute honestly?
- how do Linux-host CPU and Embree timings behave on that larger slice?

Success means:
- one materially larger exact-source execution package than Goal 28C
- honest documentation of scale, timing, parity, and any remaining hard limits
