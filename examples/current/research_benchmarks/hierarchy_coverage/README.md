# V4 hierarchy coverage example

This non-paper example consumes the same app-neutral bounded hierarchy-
frontier composition used by RT-BarnesHut, but requests the closed
`aggregate_count` reducer. It is a real second consumer: the output reports
per-station exact-peer or accepted-cell coverage counts. The example supplies
neither an OptiX callback nor a hierarchy controller.

The compiler requires one threaded root, exact next/rope columns, a complete
output capacity, and the derived `2 * node_count + 1` visit bound. Execution
must produce a complete behavioral OptiX receipt and zero status for every
source.
