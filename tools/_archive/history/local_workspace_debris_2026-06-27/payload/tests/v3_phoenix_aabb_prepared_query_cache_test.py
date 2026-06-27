import unittest
from unittest.mock import patch

from examples.current.research_benchmarks.contact_manifold import (
    rtdl_contact_manifold_benchmark_app as contact,
)
import rtdsl.optix_runtime as optix_runtime
from rtdsl.aabb_index import EmbreeAabbIndex2D, OptixAabbIndex2D


class _FakeOptixPreparedAabb:
    def __init__(self) -> None:
        self.range_query_record_ids: list[int] = []
        self.point_query_record_ids: list[int] = []

    def collect_range_intersection_rows(self, query_records, *, row_capacity: int):
        self.range_query_record_ids.append(id(query_records))
        return {
            "candidate_id_rows": ((20, 10),),
            "row_schema": ("query_id", "indexed_id"),
            "complete_candidate_coverage": True,
            "native_generic_symbol": "fake_optix_range_rows",
        }

    def collect_point_contains_rows(self, point_records, *, row_capacity: int):
        self.point_query_record_ids.append(id(point_records))
        return {
            "candidate_id_rows": ((30, 10),),
            "row_schema": ("query_id", "indexed_id"),
            "complete_candidate_coverage": True,
            "native_generic_symbol": "fake_optix_point_rows",
        }


class _FakeOptixPreparedQueryHandle:
    def __init__(self, query_records) -> None:
        self.query_record_id = id(query_records)
        self.closed = False
        self._closed = False

    def close(self) -> None:
        self.closed = True
        self._closed = True


class _FakeOptixPreparedAabbPackedQueries:
    def __init__(self) -> None:
        self.native_query_handle_ids: list[int] = []
        self.raw_range_collect_calls = 0

    def collect_range_intersection_rows_prepared_queries(self, prepared_queries, *, row_capacity: int):
        self.native_query_handle_ids.append(id(prepared_queries))
        return {
            "candidate_id_rows": ((20, 10),),
            "row_schema": ("query_id", "indexed_id"),
            "complete_candidate_coverage": True,
            "native_generic_symbol": "fake_optix_range_rows_packed_queries",
        }

    def collect_range_intersection_rows(self, query_records, *, row_capacity: int):
        self.raw_range_collect_calls += 1
        raise AssertionError("packed query handle path should not use raw range collect")


class _FakeEmbreePreparedAabb:
    native_aabb_index = True

    def __init__(self) -> None:
        self.range_query_record_ids: list[int] = []

    def collect_range_intersection_rows(self, query_records):
        self.range_query_record_ids.append(id(query_records))
        return {
            "candidate_id_rows": ((20, 10),),
            "row_schema": ("query_id", "indexed_id"),
            "complete_candidate_coverage": True,
            "native_generic_symbol": "fake_embree_range_rows",
        }


class _FakeEmbreePreparedAabbCount:
    native_aabb_index = True
    supports_packed_aabb_queries = True

    def __init__(self) -> None:
        self.point_query_ids: list[int] = []
        self.box_query_ids: list[int] = []

    def count(self, *, point_queries=(), box_queries=(), operation: str):
        if operation == "point_contains":
            self.point_query_ids.append(id(point_queries))
            return 3
        self.box_query_ids.append(id(box_queries))
        return 5 if operation == "range_contains" else 7


class _FakeContactPreparedAabb:
    def __init__(self, candidate_rows: tuple[tuple[int, int], ...]) -> None:
        self.candidate_rows = candidate_rows
        self.call_count = 0
        self.closed = False

    def intersection_rows(self, query_boxes, query_ids, *, row_capacity: int):
        self.call_count += 1
        return self.candidate_rows

    def prepared_query_cache_stats(self) -> dict[str, int]:
        return {
            "range_intersection_hits": max(0, self.call_count - 1),
            "range_intersection_misses": 1 if self.call_count else 0,
            "range_intersection_entries": 1 if self.call_count else 0,
        }

    def close(self) -> None:
        self.closed = True


class V3PhoenixAabbPreparedQueryCacheTest(unittest.TestCase):
    def test_optix_reuses_range_query_records_without_caching_results(self) -> None:
        fake = _FakeOptixPreparedAabb()
        index = OptixAabbIndex2D(
            boxes=((0.0, 0.0, 1.0, 1.0),),
            prepared=fake,
            row_ids=(10,),
        )

        first = index.intersection_rows([(0.25, 0.25, 0.75, 0.75)], (20,), row_capacity=4)
        second = index.intersection_rows([(0.25, 0.25, 0.75, 0.75)], (20,), row_capacity=4)

        self.assertEqual(first, second)
        self.assertEqual(len(fake.range_query_record_ids), 2)
        self.assertEqual(fake.range_query_record_ids[0], fake.range_query_record_ids[1])
        self.assertEqual(
            index.prepared_query_cache_stats(),
            {
                "range_intersection_hits": 1,
                "range_intersection_misses": 1,
                "point_membership_hits": 0,
                "point_membership_misses": 0,
                "native_range_intersection_hits": 0,
                "native_range_intersection_misses": 0,
                "range_intersection_entries": 1,
                "point_membership_entries": 0,
                "native_range_intersection_entries": 0,
            },
        )

    def test_optix_reuses_native_range_query_handle_without_caching_results(self) -> None:
        fake = _FakeOptixPreparedAabbPackedQueries()
        index = OptixAabbIndex2D(
            boxes=((0.0, 0.0, 1.0, 1.0),),
            prepared=fake,
            row_ids=(10,),
        )
        prepared_handles: list[_FakeOptixPreparedQueryHandle] = []
        original_prepare = optix_runtime.prepare_optix_aabb_box_queries_2d

        def fake_prepare(query_records):
            handle = _FakeOptixPreparedQueryHandle(query_records)
            prepared_handles.append(handle)
            return handle

        optix_runtime.prepare_optix_aabb_box_queries_2d = fake_prepare
        try:
            first = index.intersection_rows([(0.25, 0.25, 0.75, 0.75)], (20,), row_capacity=4)
            second = index.intersection_rows([(0.25, 0.25, 0.75, 0.75)], (20,), row_capacity=4)
        finally:
            optix_runtime.prepare_optix_aabb_box_queries_2d = original_prepare

        self.assertEqual(first, second)
        self.assertEqual(len(prepared_handles), 1)
        self.assertEqual(len(fake.native_query_handle_ids), 2)
        self.assertEqual(fake.native_query_handle_ids[0], fake.native_query_handle_ids[1])
        self.assertEqual(fake.raw_range_collect_calls, 0)
        self.assertEqual(
            index.prepared_query_cache_stats(),
            {
                "range_intersection_hits": 1,
                "range_intersection_misses": 1,
                "point_membership_hits": 0,
                "point_membership_misses": 0,
                "native_range_intersection_hits": 1,
                "native_range_intersection_misses": 1,
                "range_intersection_entries": 1,
                "point_membership_entries": 0,
                "native_range_intersection_entries": 1,
            },
        )
        self.assertFalse(prepared_handles[0].closed)
        index.close()
        self.assertTrue(prepared_handles[0].closed)

    def test_optix_reuses_point_query_records_without_caching_results(self) -> None:
        fake = _FakeOptixPreparedAabb()
        index = OptixAabbIndex2D(
            boxes=((0.0, 0.0, 1.0, 1.0),),
            prepared=fake,
            row_ids=(10,),
        )

        first = index.point_membership_rows([(0.5, 0.5)], (30,), row_capacity=4)
        second = index.point_membership_rows([(0.5, 0.5)], (30,), row_capacity=4)

        self.assertEqual(first, second)
        self.assertEqual(len(fake.point_query_record_ids), 2)
        self.assertEqual(fake.point_query_record_ids[0], fake.point_query_record_ids[1])
        self.assertEqual(index.prepared_query_cache_stats()["point_membership_hits"], 1)
        self.assertEqual(index.prepared_query_cache_stats()["point_membership_misses"], 1)
        self.assertEqual(index.prepared_query_cache_stats()["point_membership_entries"], 1)

    def test_embree_native_reuses_range_query_records_without_caching_results(self) -> None:
        fake = _FakeEmbreePreparedAabb()
        index = EmbreeAabbIndex2D(
            boxes=((0.0, 0.0, 1.0, 1.0),),
            prepared=fake,
            row_ids=(10,),
        )

        first = index.intersection_rows([(0.25, 0.25, 0.75, 0.75)], (20,))
        second = index.intersection_rows([(0.25, 0.25, 0.75, 0.75)], (20,))

        self.assertEqual(first, second)
        self.assertEqual(len(fake.range_query_record_ids), 2)
        self.assertEqual(fake.range_query_record_ids[0], fake.range_query_record_ids[1])
        self.assertEqual(
            index.prepared_query_cache_stats(),
            {
                "range_intersection_hits": 1,
                "range_intersection_misses": 1,
                "count_point_query_hits": 0,
                "count_point_query_misses": 0,
                "count_box_query_hits": 0,
                "count_box_query_misses": 0,
                "range_intersection_entries": 1,
                "count_point_query_entries": 0,
                "count_box_query_entries": 0,
            },
        )

    def test_embree_native_count_reuses_packed_query_records(self) -> None:
        fake = _FakeEmbreePreparedAabbCount()
        index = EmbreeAabbIndex2D(
            boxes=((0.0, 0.0, 1.0, 1.0),),
            prepared=fake,
            row_ids=(10,),
        )

        first = index.count(
            point_queries=[(0.5, 0.5)],
            box_queries=[(0.25, 0.25, 0.75, 0.75)],
            operation="all",
        )
        second = index.count(
            point_queries=[(0.5, 0.5)],
            box_queries=[(0.25, 0.25, 0.75, 0.75)],
            operation="all",
        )

        self.assertEqual(first["counts"], second["counts"])
        self.assertEqual(first["counts"], {"point_contains": 3, "range_contains": 5, "range_intersects": 7})
        self.assertEqual(len(fake.point_query_ids), 2)
        self.assertEqual(len(fake.box_query_ids), 4)
        self.assertEqual(len(set(fake.point_query_ids)), 1)
        self.assertEqual(len(set(fake.box_query_ids)), 1)
        self.assertEqual(
            index.prepared_query_cache_stats(),
            {
                "range_intersection_hits": 0,
                "range_intersection_misses": 0,
                "count_point_query_hits": 1,
                "count_point_query_misses": 1,
                "count_box_query_hits": 1,
                "count_box_query_misses": 1,
                "range_intersection_entries": 0,
                "count_point_query_entries": 1,
                "count_box_query_entries": 1,
            },
        )

    def test_contact_aabb_evidence_surfaces_prepared_query_cache_stats(self) -> None:
        fixture = contact.build_fixture("grid", grid_count=4)
        candidate_rows = tuple(
            (query_id, scene_id)
            for _, query_id, scene_id in fixture.expected_witness_rows
        )
        fake = _FakeContactPreparedAabb(candidate_rows)

        def fake_prepare(*args, **kwargs):
            self.assertEqual(kwargs["backend"], "optix")
            return fake

        with patch("rtdsl.aabb_index.prepare_aabb_index_2d", side_effect=fake_prepare):
            payload = contact.aabb_broadphase_witness_rows(
                fixture,
                discovery_backend="optix",
                row_capacity=64,
                warmup_count=1,
                repeat_count=3,
            )

        self.assertTrue(fake.closed)
        self.assertEqual(payload["prepared_query_cache_stats"]["range_intersection_misses"], 1)
        self.assertEqual(payload["prepared_query_cache_stats"]["range_intersection_hits"], 3)
        self.assertEqual(payload["discovery_repeat_count"], 3)
        self.assertTrue(payload["prepared_execution_session_runner_used"])
        self.assertEqual(payload["productized_execution_path"], "prepared_execution_session_runner")
        self.assertEqual(
            payload["prepared_execution_session_runner_metadata"]["runtime_executed_count"],
            3,
        )


if __name__ == "__main__":
    unittest.main()
