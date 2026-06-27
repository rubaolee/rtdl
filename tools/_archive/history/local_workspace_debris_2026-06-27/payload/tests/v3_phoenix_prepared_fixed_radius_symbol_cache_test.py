from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest import mock

import rtdsl as rt
from rtdsl import embree_runtime
from rtdsl import optix_runtime


class _FakeRowView:
    def __init__(self, *args, **kwargs) -> None:
        self.closed = False

    def to_dict_rows(self):
        return (
            {"query_id": 1, "neighbor_count": 1, "threshold_reached": 1},
        )

    def close(self) -> None:
        self.closed = True


class V3PhoenixPreparedFixedRadiusSymbolCacheTest(unittest.TestCase):
    def test_embree_2d_count_threshold_handle_caches_hot_symbols(self) -> None:
        lookup_counts: dict[str, int] = {}
        calls: list[str] = []

        def create_symbol(_records, _count, handle_out, _error, _error_size):
            calls.append("create")
            handle_out._obj.value = 101
            return 0

        def run_symbol(*_args):
            calls.append("run")
            return 0

        def destroy_symbol(_handle):
            calls.append("destroy")
            return 0

        symbols = {
            "rtdl_embree_fixed_radius_count_threshold_2d_create": create_symbol,
            "rtdl_embree_fixed_radius_count_threshold_2d_run": run_symbol,
            "rtdl_embree_fixed_radius_count_threshold_2d_destroy": destroy_symbol,
        }
        library = SimpleNamespace(**symbols)

        def fake_symbol(_library, symbol_name: str):
            lookup_counts[symbol_name] = lookup_counts.get(symbol_name, 0) + 1
            return symbols.get(symbol_name)

        points = (rt.Point(id=1, x=0.0, y=0.0),)
        with (
            mock.patch.object(embree_runtime, "_load_configured_embree_library", return_value=library),
            mock.patch.object(embree_runtime, "_require_optional_embree_symbol", side_effect=fake_symbol),
            mock.patch.object(embree_runtime, "EmbreeRowView", side_effect=_FakeRowView),
        ):
            with rt.prepare_embree_fixed_radius_count_threshold_2d(points) as prepared:
                self.assertEqual(len(prepared.run(points, radius=0.5, threshold=1)), 1)
                self.assertEqual(len(prepared.run(points, radius=0.5, threshold=1)), 1)

        self.assertEqual(
            lookup_counts,
            {
                "rtdl_embree_fixed_radius_count_threshold_2d_create": 1,
                "rtdl_embree_fixed_radius_count_threshold_2d_run": 1,
                "rtdl_embree_fixed_radius_count_threshold_2d_destroy": 1,
            },
        )
        self.assertEqual(calls, ["create", "run", "run", "destroy"])

    def test_embree_3d_count_threshold_handle_caches_hot_symbols(self) -> None:
        lookup_counts: dict[str, int] = {}
        calls: list[str] = []

        def create_symbol(_records, _count, handle_out, _error, _error_size):
            calls.append("create")
            handle_out._obj.value = 202
            return 0

        def run_symbol(*args):
            calls.append("run")
            traversal_seconds = args[-3]
            traversal_seconds._obj.value = 0.001
            return 0

        def destroy_symbol(_handle):
            calls.append("destroy")
            return 0

        symbols = {
            "rtdl_embree_fixed_radius_count_threshold_3d_create": create_symbol,
            "rtdl_embree_fixed_radius_count_threshold_3d_run": run_symbol,
            "rtdl_embree_fixed_radius_count_threshold_3d_destroy": destroy_symbol,
        }
        library = SimpleNamespace(**symbols)

        def fake_symbol(_library, symbol_name: str):
            lookup_counts[symbol_name] = lookup_counts.get(symbol_name, 0) + 1
            return symbols.get(symbol_name)

        points = (rt.Point3D(id=1, x=0.0, y=0.0, z=0.0),)
        with (
            mock.patch.object(embree_runtime, "_load_configured_embree_library", return_value=library),
            mock.patch.object(embree_runtime, "_require_optional_embree_symbol", side_effect=fake_symbol),
            mock.patch.object(embree_runtime, "EmbreeRowView", side_effect=_FakeRowView),
        ):
            with rt.prepare_embree_fixed_radius_count_threshold_3d(points) as prepared:
                self.assertEqual(len(prepared.run(points, radius=0.5, threshold=1)), 1)
                self.assertEqual(len(prepared.run(points, radius=0.5, threshold=1)), 1)
                self.assertEqual(prepared.last_traversal_seconds, 0.001)

        self.assertEqual(
            lookup_counts,
            {
                "rtdl_embree_fixed_radius_count_threshold_3d_create": 1,
                "rtdl_embree_fixed_radius_count_threshold_3d_run": 1,
                "rtdl_embree_fixed_radius_count_threshold_3d_destroy": 1,
            },
        )
        self.assertEqual(calls, ["create", "run", "run", "destroy"])

    def test_optix_3d_count_threshold_handle_caches_hot_symbols(self) -> None:
        lookup_counts: dict[str, int] = {}
        calls: list[str] = []

        def prepare_symbol(_records, _count, _max_radius, handle_out, _error, _error_size):
            calls.append("prepare")
            handle_out._obj.value = 303
            return 0

        def write_symbol(*_args):
            calls.append("write")
            return 0

        def destroy_symbol(_handle):
            calls.append("destroy")
            return 0

        symbols = {
            "rtdl_optix_prepare_fixed_radius_count_threshold_3d": prepare_symbol,
            optix_runtime._OPTIX_PREPARED_FIXED_RADIUS_COUNT_THRESHOLD_3D_DEVICE_OUTPUT_SYMBOL: write_symbol,
            "rtdl_optix_destroy_prepared_fixed_radius_count_threshold_3d": destroy_symbol,
        }
        library = SimpleNamespace(**symbols)

        def fake_find(_library, symbol_name: str):
            lookup_counts[symbol_name] = lookup_counts.get(symbol_name, 0) + 1
            return symbols.get(symbol_name)

        def fake_handoff(_value, *, access):
            return SimpleNamespace(
                data_ptr=4096,
                device_type="cuda",
                device_id=0,
                dtype="uint32",
                shape=(1,),
                strides=(4,),
                source_protocol="fake",
            )

        points = (rt.Point3D(id=1, x=0.0, y=0.0, z=0.0),)
        with (
            mock.patch.object(optix_runtime, "_load_optix_library", return_value=library) as load_library,
            mock.patch.object(optix_runtime, "_find_optional_backend_symbol", side_effect=fake_find),
            mock.patch.object(optix_runtime._partner, "prepare_direct_device_pointer_handoff", side_effect=fake_handoff),
            mock.patch.object(optix_runtime, "_require_partner_device_any_hit_output_layout", return_value=None),
        ):
            with rt.prepare_optix_fixed_radius_count_threshold_3d(points, max_radius=1.0) as prepared:
                for _ in range(2):
                    prepared.write_device_count_threshold_columns(
                        points,
                        radius=0.5,
                        threshold=1,
                        query_ids_out=object(),
                        neighbor_counts_out=object(),
                        threshold_flags_out=object(),
                    )

        self.assertEqual(load_library.call_count, 1)
        self.assertEqual(
            lookup_counts,
            {
                "rtdl_optix_prepare_fixed_radius_count_threshold_3d": 1,
                optix_runtime._OPTIX_PREPARED_FIXED_RADIUS_COUNT_THRESHOLD_3D_DEVICE_OUTPUT_SYMBOL: 1,
                "rtdl_optix_destroy_prepared_fixed_radius_count_threshold_3d": 1,
            },
        )
        self.assertEqual(calls, ["prepare", "write", "write", "destroy"])

    def test_optix_2d_device_search_prepared_constructor_initializes_symbol_cache(self) -> None:
        lookup_counts: dict[str, int] = {}
        calls: list[str] = []

        def prepare_symbol(*args):
            calls.append("prepare")
            handle_out = args[-3]
            handle_out._obj.value = 404
            return 0

        def count_symbol(_handle, _records, count, _radius, _threshold, reached_out, _error, _error_size):
            calls.append("count")
            reached_out._obj.value = count
            return 0

        def destroy_symbol(_handle):
            calls.append("destroy")
            return 0

        symbols = {
            optix_runtime._OPTIX_PARTNER_PREPARED_FIXED_RADIUS_DEVICE_SEARCH_SYMBOL: prepare_symbol,
            "rtdl_optix_count_prepared_fixed_radius_threshold_reached_2d": count_symbol,
            "rtdl_optix_destroy_prepared_fixed_radius_count_threshold_2d": destroy_symbol,
        }
        library = SimpleNamespace(**symbols)

        def fake_find(_library, symbol_name: str):
            lookup_counts[symbol_name] = lookup_counts.get(symbol_name, 0) + 1
            return symbols.get(symbol_name)

        packet = {
            "metadata": {"point_count": 1},
            "points": {
                "ids": SimpleNamespace(data_ptr=1000),
                "x": SimpleNamespace(data_ptr=1008),
                "y": SimpleNamespace(data_ptr=1016),
            },
        }
        points = (rt.Point(id=1, x=0.0, y=0.0),)
        with (
            mock.patch.object(optix_runtime, "_load_optix_library", return_value=library) as load_library,
            mock.patch.object(optix_runtime, "_find_optional_backend_symbol", side_effect=fake_find),
            mock.patch.object(
                optix_runtime,
                "pack_optix_fixed_radius_count_threshold_2d_device_point_inputs",
                return_value=packet,
            ),
        ):
            with optix_runtime.prepare_optix_fixed_radius_count_threshold_2d_device_search_columns(
                {"x": object(), "y": object()},
                max_radius=1.0,
            ) as prepared:
                self.assertEqual(prepared.count_threshold_reached(points, radius=0.5, threshold=1), 1)
                self.assertEqual(prepared.count_threshold_reached(points, radius=0.5, threshold=1), 1)

        self.assertEqual(load_library.call_count, 1)
        self.assertEqual(
            lookup_counts,
            {
                optix_runtime._OPTIX_PARTNER_PREPARED_FIXED_RADIUS_DEVICE_SEARCH_SYMBOL: 1,
                "rtdl_optix_count_prepared_fixed_radius_threshold_reached_2d": 1,
                "rtdl_optix_destroy_prepared_fixed_radius_count_threshold_2d": 1,
            },
        )
        self.assertEqual(calls, ["prepare", "count", "count", "destroy"])


if __name__ == "__main__":
    unittest.main()
