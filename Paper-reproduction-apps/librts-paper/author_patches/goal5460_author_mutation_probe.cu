#include <optix_function_table_definition.h>

#include <cstdlib>
#include <iostream>
#include <string>
#include <vector>

#include "rtspatial/spatial_index.cuh"
#include "rtspatial/utils/stream.h"

int main(int argc, char** argv) {
  if (argc != 2) {
    std::cerr << "usage: goal5460_author_mutation_probe <counting-ptx-root>\n";
    return 2;
  }

  using index_t = rtspatial::SpatialIndex<float, 2>;
  using point_t = index_t::point_t;
  using envelope_t = index_t::envelope_t;

  rtspatial::Config config;
  config.ptx_root = argv[1];
  config.max_geometries = 16;
  config.max_queries = 8;
  config.preallocate = true;

  rtspatial::Stream stream;
  index_t index;
  index.Init(config);

  thrust::device_vector<envelope_t> initial;
  initial.push_back(envelope_t(point_t(0.0f, 0.0f), point_t(1.0f, 1.0f)));
  initial.push_back(envelope_t(point_t(0.5f, 0.5f), point_t(1.5f, 1.5f)));

  thrust::device_vector<envelope_t> query;
  query.push_back(envelope_t(point_t(0.25f, 0.25f), point_t(0.75f, 0.75f)));

  rtspatial::SharedValue<unsigned long long> counter;
  std::vector<unsigned long long> counts;
  auto capture = [&]() {
    counter.set(stream.cuda_stream(), 0);
    index.Query(rtspatial::Predicate::kIntersects,
                rtspatial::ArrayView<envelope_t>(query), counter.data(),
                stream.cuda_stream());
    counts.push_back(counter.get(stream.cuda_stream()));
  };

  index.Insert(rtspatial::ArrayView<envelope_t>(initial), stream.cuda_stream());
  stream.Sync();
  capture();

  thrust::device_vector<thrust::pair<size_t, envelope_t>> updates;
  updates.push_back(thrust::make_pair(
      static_cast<size_t>(1),
      envelope_t(point_t(5.0f, 5.0f), point_t(6.0f, 6.0f))));
  index.Update(
      rtspatial::ArrayView<thrust::pair<size_t, envelope_t>>(updates),
      stream.cuda_stream());
  stream.Sync();
  capture();

  thrust::device_vector<size_t> deleted_ids;
  deleted_ids.push_back(0);
  index.Delete(rtspatial::ArrayView<size_t>(deleted_ids), stream.cuda_stream());
  stream.Sync();
  capture();

  thrust::device_vector<envelope_t> inserted;
  inserted.push_back(envelope_t(point_t(0.4f, 0.4f), point_t(0.6f, 0.6f)));
  index.Insert(rtspatial::ArrayView<envelope_t>(inserted), stream.cuda_stream());
  stream.Sync();
  capture();

  index.Clear();
  capture();

  const std::vector<unsigned long long> expected{2, 1, 0, 1, 0};
  const bool matched = counts == expected;
  std::cout << "{\"schema\":\"librts.author_mutation_probe.v1\","
            << "\"counts\":[";
  for (size_t i = 0; i < counts.size(); ++i) {
    if (i != 0) std::cout << ',';
    std::cout << counts[i];
  }
  std::cout << "],\"expected\":[2,1,0,1,0],"
            << "\"implicit_inserted_id\":2,"
            << "\"matched\":" << (matched ? "true" : "false") << "}\n";
  return matched ? 0 : 1;
}
