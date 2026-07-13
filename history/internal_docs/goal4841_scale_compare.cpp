#include <cmath>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <limits>

using i64 = long long;

int main() {
  const double min_x = -179.148909, max_x = 179.778465;
  const double min_y = -14.548692, max_y = 71.390482;
  constexpr i64 internal_max = (i64(1) << 46) - i64(1);
  constexpr i64 internal_min = -(i64(1) << 46);
  const double margin = 1.0;
  const double box_max_x = max_x + margin, box_min_x = min_x - margin;
  const double box_max_y = max_y + margin, box_min_y = min_y - margin;
  const double internal_range = double(internal_max - internal_min);
  const double rx = internal_range / (box_max_x - box_min_x);
  const double ry = internal_range / (box_max_y - box_min_y);
  const double deltax = 0.5 * (double(internal_max + internal_min) - (box_max_x + box_min_x) * rx);
  const double deltay = 0.5 * (double(internal_max + internal_min) - (box_max_y + box_min_y) * ry);

  auto scale_x_mul = [&](double x) { return (i64)(x * rx + deltax); };
  auto scale_y_mul = [&](double y) { return (i64)(y * ry + deltay); };
  auto scale_x_fma = [&](double x) { return (i64)std::fma(x, rx, deltax); };
  auto scale_y_fma = [&](double y) { return (i64)std::fma(y, ry, deltay); };

  const double qx = -86.492726, qy = 32.360947;
  const double x0 = -86.492757, y0 = 32.361268;
  const double x1 = -86.492726, y1 = 32.360947;

  std::cout << std::setprecision(17);
  std::cout << "rx " << rx << " ry " << ry << " deltax " << deltax << " deltay " << deltay << "\n";
  std::cout << "q mul " << scale_x_mul(qx) << " " << scale_y_mul(qy)
            << " fma " << scale_x_fma(qx) << " " << scale_y_fma(qy) << "\n";
  std::cout << "seg mul " << scale_x_mul(x0) << " " << scale_y_mul(y0)
            << " -> " << scale_x_mul(x1) << " " << scale_y_mul(y1) << "\n";
  std::cout << "seg fma " << scale_x_fma(x0) << " " << scale_y_fma(y0)
            << " -> " << scale_x_fma(x1) << " " << scale_y_fma(y1) << "\n";

  auto diff = [&](const char* label, i64 qsx, i64 qsy, i64 sx0, i64 sy0, i64 sx1, i64 sy1) {
    __int128 a = (__int128)sy0 - sy1;
    __int128 b = (__int128)sx1 - sx0;
    __int128 c = -((__int128)sx0 * a) - ((__int128)sy0 * b);
    if (b < 0) {
      a = -a;
      b = -b;
      c = -c;
    }
    const __int128 numerator = -(a * (__int128)qsx) - c;
    const __int128 diffnum = (__int128)qsy * b - numerator;
    const long double hit_y = (long double)numerator / (long double)b;
    std::cout << label << " b " << (long long)b
              << " diffnum " << (long long)diffnum
              << " hit_y " << (double)hit_y
              << " point_sy " << qsy
              << " diff/b " << (double)((long double)diffnum / (long double)b)
              << "\n";
  };
  diff("diff mul", scale_x_mul(qx), scale_y_mul(qy),
       scale_x_mul(x0), scale_y_mul(y0), scale_x_mul(x1), scale_y_mul(y1));
  diff("diff fma", scale_x_fma(qx), scale_y_fma(qy),
       scale_x_fma(x0), scale_y_fma(y0), scale_x_fma(x1), scale_y_fma(y1));
  return 0;
}
