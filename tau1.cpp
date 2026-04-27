#include "tau1.hpp"

#include <chrono>
#include <random>
#include <string>
#include <vector>
#include <stdexcept>

namespace py = pybind11;

namespace {
    std::mt19937 rng(std::random_device{}());

    std::string generate_big_number(int num_digits) {
        if (num_digits <= 0) {
            throw std::invalid_argument("num_digits must be > 0");
        }

        std::uniform_int_distribution<int> first_dist(1, 9);
        std::uniform_int_distribution<int> other_dist(0, 9);

        std::string s;
        s.reserve(static_cast<size_t>(num_digits));
        s.push_back(static_cast<char>('0' + first_dist(rng)));

        for (int i = 1; i < num_digits; ++i) {
            s.push_back(static_cast<char>('0' + other_dist(rng)));
        }
        return s;
    }

    std::vector<int> multiply_strings(const std::string& a, const std::string& b) {
        int n = static_cast<int>(a.size());
        int m = static_cast<int>(b.size());
        std::vector<int> result(static_cast<size_t>(n + m), 0);

        for (int i = n - 1; i >= 0; --i) {
            for (int j = m - 1; j >= 0; --j) {
                int mul = (a[i] - '0') * (b[j] - '0');
                int sum = mul + result[static_cast<size_t>(i + j + 1)];
                result[static_cast<size_t>(i + j + 1)] = sum % 10;
                result[static_cast<size_t>(i + j)] += sum / 10;
            }
        }

        return result;
    }
}

void seed_rng(unsigned int seed) {
    rng.seed(seed);
}

double tau1_execution_time_ms(int num_digits) {
    using clock = std::chrono::high_resolution_clock;

    const std::string a = generate_big_number(num_digits);
    const std::string b = generate_big_number(num_digits);

    const auto start = clock::now();
    volatile auto product = multiply_strings(a, b);
    (void)product;
    const auto end = clock::now();

    std::chrono::duration<double, std::milli> elapsed = end - start;
    return elapsed.count();
}