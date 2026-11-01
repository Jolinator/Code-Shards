mod sieves;
mod time_tests;

use std::{collections::HashMap, env};

use sieves::{
    cache_thread::eratosthenes_cache_thread,
    naive::eratosthenes_naive,
    optimized::eratosthenes_algo_optimized,
};
use time_tests::{time_function, time_thread_cache};

static ENV_VAR_NAMES: &[&str] = &[
    "CPU_L1D_CACHE_SIZE_PER_INSTANCE_KB",
    "CPU_LOGICAL_CORES",
];

fn main() {
    dotenvy::dotenv().ok();

    let env_var_values: HashMap<String, usize> = ENV_VAR_NAMES
        .iter()
        .map(|&var_name| {
            let value = env::var(var_name)
                .expect(&format!("{} must be set", var_name))
                .parse::<usize>()
                .expect(&format!("{} must be a valid usize", var_name));
            (var_name.to_string(), value)
        })
        .collect();
    let cache_bytes = *env_var_values
        .get("CPU_L1D_CACHE_SIZE_PER_INSTANCE_KB")
        .unwrap_or(&32)
        * 1024;
    let logical_threads = *env_var_values
        .get("CPU_LOGICAL_CORES")
        .unwrap_or(&1);

    let results_naive = time_function(eratosthenes_naive);
    let results_optimized = time_function(eratosthenes_algo_optimized);
    let results_cache_thread = time_thread_cache(eratosthenes_cache_thread, cache_bytes, logical_threads);

    for (index, (naive, optimized)) in results_naive
        .iter()
        .zip(&results_optimized)
        .enumerate()
    {
        let mut same_primes = naive.primes == optimized.primes;
        println!("Limit: {}, Same primes: {}", naive.limit, same_primes);
        println!("Naive Sieve time: {:?}", naive.time);
        println!("Optimized Sieve time: {:?}", optimized.time);

        for cache_result in &results_cache_thread[index] {
            println!(
                "Limit: {}, Cache Usage Factor: {}, Time: {:?}",
                cache_result.limit, cache_result.cache_usage_factor, cache_result.time
            );
            same_primes = same_primes && naive.primes == cache_result.primes;
        }
        println!("All implementations match: {}\n", same_primes);
    }
}
