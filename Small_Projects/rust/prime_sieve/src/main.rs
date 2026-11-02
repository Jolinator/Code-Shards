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
    cache_thread_count::eratosthenes_cache_thread_count,
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

fn save_report(report: &str, differentiator: &str, use_cargo_path: bool) -> PathBuf {
    let timestamp = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .expect("system clock is before 1970")
        .as_nanos();
    let dir = if use_cargo_path {
        Path::new(env!("CARGO_MANIFEST_DIR")).join("results")
    } else {
        env::current_exe()
            .expect("could not determine executable path")
            .parent()
            .expect("executable path has no parent")
            .join("results")
    };
    fs::create_dir_all(&dir).expect("could not create results directory");
    let path = dir.join(format!("result_test_{differentiator}_{timestamp}.txt"));
    fs::write(&path, report).expect("could not write results file");
    path
}

fn run_increasing_values(
    cache_bytes: usize,
    thread_count: usize,
    cache_usage_factor: f64,
    store: bool
) -> String {
    let mut report = String::new();
    let values = [
        100,
        1_000,
        10_000,
        100_000,
        1_000_000,
        10_000_000,
        100_000_000,
        1_000_000_000,
        10_000_000_000
    ];
    for limit in values {
        let start = std::time::Instant::now();
        let count = if store {
            eratosthenes_cache_thread(limit, cache_bytes, thread_count, cache_usage_factor).len()
        } else {
            eratosthenes_cache_thread_count(limit, cache_bytes, thread_count, cache_usage_factor)
        };
        let elapsed = start.elapsed();

        writeln!(
            report,
            "Limit: {limit}, Prime count: {count}, Cache bytes: {cache_bytes}, \
             Cache usage factor: {cache_usage_factor}, Thread count: {thread_count}, \
             Time: {elapsed:?}"
        )
        .unwrap();
    }
    report
}

fn usage() -> ! {
    eprintln!("Usage: prime_sieve [compare | scaling (default)]     [--store] [--cargo]");
    eprintln!("  --store  (scaling only) keep the primes instead of only counting them");
        eprintln!("  --cargo  save results in the project's results folder instead of beside the executable");
    std::process::exit(1);
}

fn main() {
    let args: Vec<String> = env::args().skip(1).collect();
    let mode = match args.first() {
        Some(first) if !first.starts_with("--") => first.clone(),
        _ => "scaling".to_string(),
    };
    let store = args.iter().any(|a| a == "--store");
    let use_cargo_path = args.iter().any(|a| a == "--cargo");
    //In my computer the fastest version of this algo found 4118054813 (up to 10^11) primes in 15.24 seconds
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

    match mode.as_str() {
        "compare" => {
            let report = test_compare(cache_bytes, thread_count);
            let path = save_report(&report, "test_compare", use_cargo_path);
            println!("Results saved to {}", path.display());
        }
        "scaling" => {
            let report = run_increasing_values(cache_bytes, logical_threads, 0.5, store);
            let name = if store { "scaling_store" } else { "scaling_count" };
            let path = save_report(&report, name, use_cargo_path);
            println!("Results saved to {}", path.display());
        }
        _ => usage(),
    }
}
