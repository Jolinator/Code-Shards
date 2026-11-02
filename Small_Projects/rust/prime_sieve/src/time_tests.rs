use std::{
    env,
    fmt::Write as _,
    fs,
    path::{Path, PathBuf},
    time::{Duration, Instant, SystemTime, UNIX_EPOCH},
};

use crate::sieves::{
    cache_thread::eratosthenes_cache_thread, cache_thread_count::eratosthenes_cache_thread_count,
    naive::eratosthenes_naive, optimized::eratosthenes_algo_optimized,
};

pub struct TestResult {
    pub limit: usize,
    pub time: Duration,
    pub primes: Vec<usize>,
}

pub struct ThreadCacheTestResult {
    pub limit: usize,
    pub cache_usage_factor: f64,
    pub thread_count: usize,
    pub time: Duration,
    pub primes: Vec<usize>,
}

pub fn time_test(func: &impl Fn(usize) -> Vec<usize>, limit: usize) -> TestResult {
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
    thread_count: &[usize],
) -> Vec<Vec<ThreadCacheTestResult>> {
    let values = vec![
        100,
        1_000,
        10_000,
        1_000_000,
        10_000_000,
        100_000_000,
        1_000_000_000,
    ];
    let cache_usage_factors = [0.25, 0.5, 1.0, 1.5, 2.0, 5.0];
    let mut results = Vec::with_capacity(values.len());

    for limit in values {
        let mut per_value_results = Vec::with_capacity(cache_usage_factors.len());
        for cache_usage_factor in cache_usage_factors {
            for &thread_n in thread_count {
                let start = Instant::now();
                let primes = func(limit, cache_bytes, thread_n, cache_usage_factor);
                let duration = start.elapsed();
                per_value_results.push(ThreadCacheTestResult {
                    limit,
                    cache_usage_factor,
                    thread_count: thread_n,
                    time: duration,
                    primes,
                });
            }
        }
        results.push(per_value_results);
    }
    results
}

pub fn test_compare(
    cache_bytes: usize,
    logical_threads: usize,
    primes_dir: Option<&Path>,
) -> String {
    let thread_count = &[1, logical_threads / 2, logical_threads];
    let results_naive = time_function(eratosthenes_naive);
    let results_optimized = time_function(eratosthenes_algo_optimized);
    let results_cache_thread = time_thread_cache(
        |limit, cache_bytes, threads, factor| {
            eratosthenes_cache_thread(limit, cache_bytes, threads, factor, &PathBuf::new())
        },
        cache_bytes,
        thread_count,
    );

    let mut report = String::new();
    for (index, (naive, optimized)) in results_naive.iter().zip(&results_optimized).enumerate() {
        if let Some(dir) = primes_dir {
            dump_primes(naive.primes.clone(), dir);
        }
        let mut same_primes = naive.primes == optimized.primes;
        writeln!(
            report,
            "Limit: {}, Same primes: {}",
            naive.limit, same_primes
        )
        .unwrap();
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

pub fn create_results_dir(use_cargo_path: bool) -> PathBuf {
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
    dir
}

pub fn create_primes_dir(results_dir: &Path) -> PathBuf {
    let timestamp = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .expect("system clock is before 1970")
        .as_nanos();
    let dir = results_dir.join(format!("primes_{timestamp}"));
    fs::create_dir_all(&dir).expect("could not create primes directory");
    dir
}

pub fn save_report(report: &str, differentiator: &str, results_dir: &Path) -> PathBuf {
    let timestamp = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .expect("system clock is before 1970")
        .as_nanos();
    let path = results_dir.join(format!("result_test_{differentiator}_{timestamp}.txt"));
    fs::write(&path, report).expect("could not write results file");
    path
}

pub fn run_increasing_values(
    cache_bytes: usize,
    thread_count: usize,
    cache_usage_factor: f64,
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
        10_000_000_000,
        100_000_000_000,
    ];
    for limit in values {
        let start = std::time::Instant::now();
        let count = eratosthenes_cache_thread_count(
            limit,
            cache_bytes,
            thread_count,
            cache_usage_factor,
            &PathBuf::new(),
        );
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

const LINE_WIDTH: usize = 80;

// Writes the primes to `primes_{start}_{stop}.txt` in `primes_dir`.
pub fn save_primes(primes: &[usize], start: usize, stop: usize, primes_dir: &Path) -> PathBuf {
    let path = primes_dir.join(format!("primes_{start}_{stop}.txt"));
    let mut out = String::with_capacity(primes.len() * 12);
    let mut line_len = 0;
    for (i, prime) in primes.iter().enumerate() {
        // A line may run past the target width; the next prime then starts a new line.
        if line_len >= LINE_WIDTH {
            out.push('\n');
            line_len = 0;
        } else if line_len > 0 {
            out.push(' ');
            line_len += 1;
        }
        let before = out.len();
        write!(out, "{prime}").unwrap();
        if i + 1 < primes.len() {
            out.push(',');
        }
        line_len += out.len() - before;
    }
    out.push('\n');
    fs::write(&path, out).expect("could not write primes file");
    path
}

// Saves the primes using their first and last values as start and stop, then frees them.
// Does nothing if there are no primes.
pub fn dump_primes(primes: Vec<usize>, primes_dir: &Path) -> Option<PathBuf> {
    let (start, stop) = (*primes.first()?, *primes.last()?);
    Some(save_primes(&primes, start, stop, primes_dir))
}

pub fn run_find_all(
    limit: usize,
    cache_bytes: usize,
    thread_count: usize,
    cache_usage_factor: f64,
    primes_dir: Option<&Path>,
) -> (String, Option<PathBuf>) {
    let start = std::time::Instant::now();
    let segments_dir = primes_dir.map(Path::to_path_buf).unwrap_or_default();
    let primes = eratosthenes_cache_thread(
        limit,
        cache_bytes,
        thread_count,
        cache_usage_factor,
        &segments_dir,
    );
    let elapsed = start.elapsed();

    let report = format!(
        "Limit: {limit}, Prime count: {}, Cache bytes: {cache_bytes}, \
         Cache usage factor: {cache_usage_factor}, Thread count: {thread_count}, \
         Time: {elapsed:?}\n",
        primes.len()
    );

    let primes_path = primes_dir.and_then(|dir| dump_primes(primes, dir));
    (report, primes_path)
}

pub fn run_count(
    limit: usize,
    cache_bytes: usize,
    thread_count: usize,
    cache_usage_factor: f64,
    primes_dir: Option<&Path>,
) -> String {
    let prime_store = primes_dir.map(Path::to_path_buf).unwrap_or_default();
    let start = std::time::Instant::now();
    let count = eratosthenes_cache_thread_count(
        limit,
        cache_bytes,
        thread_count,
        cache_usage_factor,
        &prime_store,
    );
    let elapsed = start.elapsed();

    format!(
        "Limit: {limit}, Prime count: {count}, Cache bytes: {cache_bytes}, \
         Cache usage factor: {cache_usage_factor}, Thread count: {thread_count}, \
         Time: {elapsed:?}\n"
    )
}
