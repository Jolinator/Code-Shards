mod sieves;
mod time_tests;

use std::{collections::HashMap, env};

use time_tests::{
    create_primes_dir, create_results_dir, run_count, run_find_all, run_increasing_values,
    save_report, test_compare,
};

static ENV_VAR_NAMES: &[&str] = &["CPU_L1D_CACHE_SIZE_PER_INSTANCE_KB", "CPU_LOGICAL_CORES"];

fn usage() -> ! {
    eprintln!(
        "Usage: prime_sieve [compare | scaling (default) | count <n> | findall <n>] [--cargo]"
    );
    eprintln!(
        "  findall stores the primes; compare and scaling only compare and time, count only counts them"
    );
    eprintln!(
        "  --cargo  save results in the project's results folder instead of beside the executable"
    );
    std::process::exit(1);
}

fn main() {
    //In my computer the fastest version of this algo found 4118054813 (up to 10^11) primes in 13.24 seconds

    let args: Vec<String> = env::args().skip(1).collect();
    let mode = match args.first() {
        Some(first) if !first.starts_with("--") => first.clone(),
        _ => "scaling".to_string(),
    };

    let count_limit = if mode == "count" || mode == "findall" {
        Some(
            args.get(1)
                .and_then(|value| value.parse::<usize>().ok())
                .unwrap_or_else(|| {
                    eprintln!("{mode} requires a non-negative integer limit");
                    usage()
                }),
        )
    } else {
        None
    };

    let use_cargo_path = args.iter().any(|a| a == "--cargo");
    dotenvy::dotenv().ok();

    let env_var_values: HashMap<String, usize> = ENV_VAR_NAMES
        .iter()
        .map(|&var_name| {
            // Hybrid CPUs list one value per core type (e.g. "32,48"); use the smallest.
            let value = env::var(var_name)
                .expect(&format!("{} must be set", var_name))
                .split(',')
                .map(|part| {
                    part.trim().parse::<usize>().expect(&format!(
                        "{} must be a comma separated list of usize",
                        var_name
                    ))
                })
                .min()
                .expect(&format!("{} must not be empty", var_name));
            (var_name.to_string(), value)
        })
        .collect();

    let cache_bytes = env_var_values["CPU_L1D_CACHE_SIZE_PER_INSTANCE_KB"] * 1024;

    let logical_threads = env_var_values["CPU_LOGICAL_CORES"];

    let optimal_thread_count = logical_threads;
    let optimal_cache_factor = 0.5;

    let results_dir = create_results_dir(use_cargo_path);

    match mode.as_str() {
        "compare" => {
            let report = test_compare(cache_bytes, logical_threads);
            let path = save_report(&report, "test_compare", &results_dir);
            println!("Results saved to {}", path.display());
        }
        "scaling" => {
            let report =
                run_increasing_values(cache_bytes, optimal_thread_count, optimal_cache_factor);
            let path = save_report(&report, "scaling_count", &results_dir);
            println!("Results saved to {}", path.display());
        }
        "count" => {
            let limit = count_limit.expect("count limit was validated");
            let report = run_count(
                limit,
                cache_bytes,
                optimal_thread_count,
                optimal_cache_factor,
            );
            let path = save_report(&report, &format!("count_{limit}"), &results_dir);
            println!("Results saved to {}", path.display());
        }
        "findall" => {
            let limit = count_limit.expect("count limit was validated");
            let primes_dir = create_primes_dir(&results_dir);
            let (report, primes_path) = run_find_all(
                limit,
                cache_bytes,
                optimal_thread_count,
                optimal_cache_factor,
                &primes_dir,
            );
            let path = save_report(&report, &format!("findall_{limit}"), &results_dir);
            println!("Results saved to {}", path.display());
            if let Some(primes_path) = primes_path {
                println!("Primes saved to {}", primes_path.display());
            }
        }
        _ => usage(),
    }
}
