mod sieves;
mod time_tests;

use std::{
    collections::HashMap,
    env,
    fmt::Write as _,
    fs,
    path::{Path, PathBuf},
    time::{SystemTime, UNIX_EPOCH},
};

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


fn test_compare(cache_bytes: usize, thread_count: &[usize]) -> String {
    let results_naive = time_function(eratosthenes_naive);
    let results_optimized = time_function(eratosthenes_algo_optimized);
    let results_cache_thread = time_thread_cache(eratosthenes_cache_thread, cache_bytes, thread_count);

    let mut report = String::new();
    for (index, (naive, optimized)) in results_naive
        .iter()
        .zip(&results_optimized)
        .enumerate()
    {
        let mut same_primes = naive.primes == optimized.primes;
        writeln!(report, "Limit: {}, Same primes: {}", naive.limit, same_primes).unwrap();
        writeln!(report, "Naive Sieve time: {:?}", naive.time).unwrap();
        writeln!(report, "Optimized Sieve time: {:?}", optimized.time).unwrap();

        for cache_result in &results_cache_thread[index] {
            writeln!(
                report,
                "Limit: {}, Cache Usage Factor: {}, Thread Count: {}, Time: {:?}",
                cache_result.limit,
                cache_result.cache_usage_factor,
                cache_result.thread_count,
                cache_result.time
            )
            .unwrap();
            same_primes = same_primes && naive.primes == cache_result.primes;
        }
        writeln!(report, "All implementations match: {}\n", same_primes).unwrap();
    }
    report
}

fn save_report(report: &str) -> PathBuf {
    let timestamp = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .expect("system clock is before 1970")
        .as_secs();
    let dir = Path::new(env!("CARGO_MANIFEST_DIR")).join("results");
    fs::create_dir_all(&dir).expect("could not create results directory");
    let path = dir.join(format!("result_test_{timestamp}.txt"));
    fs::write(&path, report).expect("could not write results file");
    path
}
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

    let thread_count = &[1, 2, logical_threads/2, logical_threads];


    let report = test_compare(cache_bytes, thread_count);
    print!("{report}");
    let path = save_report(&report);
    println!("Results saved to {}", path.display());
}
