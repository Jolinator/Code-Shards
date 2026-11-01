use std::time::{Duration, Instant};
use std::vec;

pub struct TestResult {
    pub limit: usize,
    pub time: Duration,
    pub primes: Vec<usize>,
}

pub struct ThreadCacheTestResult {
    pub limit: usize,
    pub cache_usage_factor: f64,
    pub time: Duration,
    pub primes: Vec<usize>,
}

fn time_test(func: &impl Fn(usize) -> Vec<usize>, limit: usize) -> TestResult {
    let start = Instant::now();
    let primes = func(limit);
    let duration = start.elapsed();
    TestResult {
        limit,
        time: duration,
        primes,
    }
}

pub fn time_function(func: impl Fn(usize) -> Vec<usize>) -> Vec<TestResult> {
    let values = vec![100, 1_000, 10_000, 1_000_000, 10_000_000, 100_000_000];
    let mut results = Vec::new();

    for limit in values {
        results.push(time_test(&func, limit));
    }
    results
}

pub fn time_thread_cache(
    func: impl Fn(usize, usize, usize, f64) -> Vec<usize>,
    cache_bytes: usize,
    thread_count: usize,
) -> Vec<Vec<ThreadCacheTestResult>> {
    let values = vec![100, 1_000, 10_000, 1_000_000, 10_000_000, 100_000_000];
    let cache_usage_factors = [0.25, 0.33, 0.5, 0.8];
    let mut results = Vec::with_capacity(values.len());

    for limit in values {
        let mut per_value_results = Vec::with_capacity(cache_usage_factors.len());
        for cache_usage_factor in cache_usage_factors {
            let start = Instant::now();
            let primes = func(limit, cache_bytes, thread_count, cache_usage_factor);
            let duration = start.elapsed();
            per_value_results.push(ThreadCacheTestResult {
                limit,
                cache_usage_factor,
                time: duration,
                primes,
            });
        }
        results.push(per_value_results);
    }
    results
}
