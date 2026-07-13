from __future__ import annotations

import time


def stamp(label: str, start: float) -> None:
    print(f"{label}: {time.perf_counter() - start:.3f}s", flush=True)


def main() -> None:
    start = time.perf_counter()
    stamp("start", start)
    from rtdsl.datasets import chains_to_planar_map_points
    from rtdsl.datasets import chains_to_planar_map_segments
    from rtdsl.datasets import load_cdb

    stamp("datasets", start)
    from rtdsl.optix_runtime import prepare_planar_map_lsi_2d_optix
    from rtdsl.optix_runtime import prepare_planar_map_point_location_2d_optix

    stamp("optix_runtime", start)
    print(load_cdb.__name__, chains_to_planar_map_segments.__name__, chains_to_planar_map_points.__name__)
    print(prepare_planar_map_lsi_2d_optix.__name__, prepare_planar_map_point_location_2d_optix.__name__)


if __name__ == "__main__":
    main()
