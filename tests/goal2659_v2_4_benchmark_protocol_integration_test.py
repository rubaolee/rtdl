import unittest

import rtdsl as rt
from examples.v2_0.research_benchmarks.contact_manifold import (
    rtdl_contact_manifold_benchmark_app as contact,
)
from examples.v2_0.research_benchmarks.triangle_counting import (
    rtdl_triangle_counting_benchmark_app as triangle,
)


class Goal2659V24BenchmarkProtocolIntegrationTest(unittest.TestCase):
    def test_contact_collect_k_payload_exposes_generic_protocol_descriptor(self):
        payload = contact.collect_k_reference_payload(dataset="tiny", witness_capacity=3)
        session = payload["v2_4_prepared_session"]

        self.assertEqual(session["v2_4_protocol_version"], rt.V2_4_PARTNER_PROTOCOL_VERSION)
        self.assertEqual(session["primitive"], "aabb_index_2d_bounded_i64_rows")
        self.assertEqual(session["backend"], "cpu")
        self.assertEqual(session["row_schema"], contact.ROW_SCHEMA)
        self.assertEqual(session["overflow_policy"], "fail_closed_no_partial_rows")
        self.assertEqual(session["input_buffers"][0]["name"], "candidate_id_rows")
        self.assertEqual(session["output_buffers"][0]["name"], "bounded_witness_rows")
        self.assertEqual(session["output_buffers"][1]["name"], "valid_count")
        self.assertFalse(session["app_specific_native_vocab_allowed"])
        self.assertEqual(session["native_symbols"], ())

    def test_contact_native_descriptor_names_stay_app_agnostic(self):
        session = contact.describe_v2_4_bounded_witness_session(
            backend="optix",
            candidate_row_count=64,
            witness_capacity=64,
        )

        self.assertEqual(session["backend"], "optix")
        self.assertEqual(session["native_symbols"], ("rtdl_optix_collect_k_bounded_i64",))
        native_vocab = " ".join((session["primitive"], *session["native_symbols"])).lower()
        self.assertNotIn("contact", native_vocab)
        self.assertNotIn("collision", native_vocab)

    def test_triangle_2a1_payload_exposes_weighted_any_hit_descriptor(self):
        payload = triangle.rt_graph_2a1_generic_rt_payload(
            fixture="degree_oriented_two_triangles",
            edge_file=None,
            edge_format="text",
            backend="cpu",
            detail="summary",
            partner="none",
            warmup=0,
            repeat=1,
        )
        session = payload["v2_4_prepared_session"]

        self.assertEqual(session["v2_4_protocol_version"], rt.V2_4_PARTNER_PROTOCOL_VERSION)
        self.assertEqual(session["primitive"], "ray_triangle_weighted_any_hit_sum_3d")
        self.assertEqual(session["backend"], "cpu")
        self.assertEqual(session["paper_method"], "RT-2A1")
        self.assertIn("ray_weights", [item["name"] for item in session["input_buffers"]])
        self.assertEqual(session["output_buffers"][0]["name"], "weighted_hit_sum")
        self.assertFalse(session["app_specific_native_vocab_allowed"])
        self.assertTrue(payload["triangle_count_matches_oracle"])

    def test_triangle_1a2_optix_descriptor_uses_generic_native_symbol(self):
        session = triangle.describe_rt_graph_v2_4_prepared_session(
            backend="optix",
            paper_method="RT-1A2",
            primitive_count=128,
            ray_count=256,
            device_column_summary=True,
            partner="cupy",
        )

        self.assertEqual(session["primitive"], "ray_triangle_hit_count_sum_3d")
        self.assertEqual(
            session["native_symbols"],
            ("rtdl_optix_static_triangle_scene_3d_ray_hit_count_sum_device_rays",),
        )
        native_vocab = " ".join((session["primitive"], *session["native_symbols"])).lower()
        self.assertNotIn("triangle_counting", native_vocab)
        self.assertNotIn("rt_graph", native_vocab)
        self.assertEqual(session["input_buffers"][0]["device"], "cuda:0")


if __name__ == "__main__":
    unittest.main()
