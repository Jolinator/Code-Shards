use super::cache_thread::eratosthenes_cache_thread;
use super::cache_thread::{SieveJob, build_early_pattern, mark_composites};
use super::optimized::eratosthenes_algo_optimized;
use std::cmp::min;
use std::path::PathBuf;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::thread;

//counts set bits in [lo, hi)
fn count_bits(nums: &[u64], lo: usize, hi: usize) -> usize {
    if lo >= hi {
        return 0;
    }
    let (first, last) = (lo / 64, (hi - 1) / 64);
    let mut total = 0;
    for w in first..=last {
        let mut bits = nums[w];
        if w == first {
            bits &= !0u64 << (lo % 64);
        }
        if w == last {
            let used = hi - w * 64;
            if used < 64 {
                bits &= (1u64 << used) - 1;
            }
        }
        total += bits.count_ones() as usize;
    }
    total
}

fn count_segment(job: SieveJob, i: usize, nums: &mut [u64]) -> usize {
    let start = job.start_odds[i];
    let stop = job.stop_odds[i];
    mark_composites(start, stop, job.primes, job.pattern, nums);
    let lo = job.first_odd.saturating_sub(start) / 2;
    let hi = (stop - start).div_ceil(2);
    count_bits(nums, lo, hi)
}

fn run_worker(job: SieveJob, next_segment: &AtomicUsize, nums: &mut [u64]) -> usize {
    let mut total = 0;
    loop {
        let i = next_segment.fetch_add(1, Ordering::Relaxed);
        if i >= job.start_odds.len() {
            return total;
        }
        total += count_segment(job, i, nums);
    }
}

fn run_workers(job: SieveJob, buffers: &mut [Vec<u64>]) -> usize {
    let next_segment = AtomicUsize::new(0);

    thread::scope(|scope| {
        let mut handles = Vec::new();
        for nums in buffers.iter_mut() {
            let next_segment = &next_segment;
            handles.push(scope.spawn(move || run_worker(job, next_segment, nums)));
        }
        handles
            .into_iter()
            .map(|handle| handle.join().unwrap())
            .sum()
    })
}

//same as eratosthenes_cache_thread but only returns how many primes are <= limit
pub fn eratosthenes_cache_thread_count(
    limit: usize,
    cache_bytes: usize,
    logical_threads: usize,
    cache_usage_factor: f64,
    prime_store: &PathBuf,
) -> usize {
    if limit < 10000 {
        return eratosthenes_algo_optimized(limit + 1).len();
    }

    let limit_sqrt = (limit as f64).sqrt() as usize;
    let limit_sqrt = if limit_sqrt % 2 == 0 {
        limit_sqrt + 1
    } else {
        limit_sqrt
    };

    let primes = eratosthenes_cache_thread(
        limit_sqrt + 1,
        cache_bytes,
        logical_threads,
        cache_usage_factor,
        prime_store,
    );
    let first_odd = limit_sqrt + 2;
    if first_odd > limit {
        return primes.len();
    }
    let first_aligned = (first_odd - 1) / 128 * 128 + 1;

    let byte_split = (cache_bytes as f64 * cache_usage_factor) as usize;
    let byte_split = (byte_split / 8 * 8).max(8);
    let odd_count = (limit - first_aligned) / 2 + 1;
    let bit_split = byte_split * 8;
    let workloads = odd_count.div_ceil(bit_split);
    if workloads == 0 {
        return primes.len();
    }

    let thread_count = min(logical_threads, workloads);

    let mut start_odds = vec![0; workloads];
    let mut stop_odds = vec![0; workloads];
    for i in 0..workloads {
        start_odds[i] = first_aligned + i * bit_split * 2;
        stop_odds[i] = min(start_odds[i] + bit_split * 2, limit + 1);
    }

    let mut nums_vecs: Vec<Vec<u64>> = (0..thread_count)
        .map(|_| vec![!0u64; bit_split / 64])
        .collect();

    let pattern = build_early_pattern();

    let job = SieveJob {
        primes: &primes,
        start_odds: &start_odds,
        stop_odds: &stop_odds,
        pattern: &pattern,
        first_odd,
    };
    primes.len() + run_workers(job, &mut nums_vecs)
}
