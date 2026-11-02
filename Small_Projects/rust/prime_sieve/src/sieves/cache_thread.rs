use super::optimized::{clear_bit, eratosthenes_algo_optimized, get_primes_from_bits};
use std::cmp::min;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::thread;

pub(super) const EARLY_PERIOD: usize = 105; // words: 3 * 5 * 7

//creates a mask that sieves primes 3 5 7 instantly
pub(super) fn build_early_pattern() -> [u64; EARLY_PERIOD] {
    let mut pattern = [!0u64; EARLY_PERIOD];
    for k in 0..EARLY_PERIOD * 64 {
        let n = 2 * k + 1;
        if n % 3 == 0 || n % 5 == 0 || n % 7 == 0 {
            pattern[k / 64] &= !(1u64 << (k % 64));
        }
    }
    pattern
}

fn init_with_early_pattern(nums: &mut [u64], pattern: &[u64; EARLY_PERIOD], word_offset: usize) {
    let mut idx = word_offset % EARLY_PERIOD;
    let mut rest = nums;
    while !rest.is_empty() {
        let n = rest.len().min(EARLY_PERIOD - idx);
        let (head, tail) = rest.split_at_mut(n);
        head.copy_from_slice(&pattern[idx..idx + n]);
        rest = tail;
        idx = 0;
    }
}

//Sieve with set primes in a range
fn sieve_with_primes(
    start_odd: usize,
    stop_odd: usize,
    primes: &[usize],
    pattern: &[u64; EARLY_PERIOD],
    nums: &mut [u64],
) -> Vec<usize> {
    mark_composites(start_odd, stop_odd, primes, pattern, nums);
    get_primes_from_bits(start_odd, stop_odd, nums)
}

pub(super) fn mark_composites(
    start_odd: usize,
    stop_odd: usize,
    primes: &[usize],
    pattern: &[u64; EARLY_PERIOD],
    nums: &mut [u64],
) {
    let mut counter: usize;
    // 128 because each word is 64 bits and each bit is an odd number so 1 bit for every 2 integers
    let word_offset = (start_odd-1) / 128; 
    init_with_early_pattern(nums, pattern, word_offset);
    for &p in &primes[4..] {
        counter = (start_odd / p) * p;
        if counter % 2 == 0 {
            counter += p;
        } else if counter < start_odd {
            counter += 2 * p;
        }
        while counter < stop_odd {
            clear_bit(nums, (counter - start_odd) / 2);
            counter += p * 2;
        }
    }
}

#[derive(Clone, Copy)]
pub(super) struct SieveJob<'a> {
    pub(super) primes: &'a [usize],
    pub(super) start_odds: &'a [usize],
    pub(super) stop_odds: &'a [usize],
    pub(super) pattern: &'a [u64; EARLY_PERIOD],
    pub(super) first_odd: usize,
}

type SegmentResult = (usize, Vec<usize>);

fn sieve_segment(job: SieveJob, i: usize, nums: &mut [u64]) -> Vec<usize> {
    let start = job.start_odds[i];
    let mut found = sieve_with_primes(start, job.stop_odds[i], job.primes, job.pattern, nums);
    if start < job.first_odd {
        found.retain(|&n| n >= job.first_odd);
    }
    found
}

fn run_worker(job: SieveJob, next_segment: &AtomicUsize, nums: &mut [u64]) -> Vec<SegmentResult> {
    let mut results = Vec::new();
    loop {
        let i = next_segment.fetch_add(1, Ordering::Relaxed);
        if i >= job.start_odds.len() {
            return results;
        }
        results.push((i, sieve_segment(job, i, nums)));
    }
}

fn run_workers(job: SieveJob, buffers: &mut [Vec<u64>]) -> Vec<SegmentResult> {
    let next_segment = AtomicUsize::new(0);
    
    thread::scope(|scope| {
        let mut handles = Vec::new();
        for nums in buffers.iter_mut() {
            let next_segment = &next_segment;
            handles.push(scope.spawn(move || run_worker(job, next_segment, nums)));
        }
        handles
            .into_iter()
            .flat_map(|handle| handle.join().unwrap())
            .collect()
    })
}

fn dispatch_threads(job: SieveJob, buffers: &mut [Vec<u64>]) -> Vec<usize> {
    let mut segments = run_workers(job, buffers);
    segments.sort_unstable_by_key(|&(i, _)| i);

    let mut all = job.primes.to_vec();
    all.extend(segments.into_iter().flat_map(|(_, found)| found));
    all
}

pub fn eratosthenes_cache_thread(
    limit: usize,
    cache_bytes: usize,
    logical_threads: usize,
    cache_usage_factor: f64,
) -> Vec<usize> {
    if limit < 62 { //sqroot of this number must have at least 4 primes (49). 62 is for safety.
        return eratosthenes_algo_optimized(limit + 1);
    }

    let limit_sqrt = (limit as f64).sqrt() as usize;
    let limit_sqrt = if limit_sqrt%2==0{
        limit_sqrt+1
    }
    else {
        limit_sqrt
    };

    //compute primes until sqroot
    let primes = eratosthenes_algo_optimized(limit_sqrt + 1);
    let first_odd = limit_sqrt + 2;
    if first_odd > limit {
        return primes;
    }
    let first_aligned = (first_odd - 1) / 128 * 128 + 1;
    
    //compute splits between workloads
    let byte_split = (cache_bytes as f64 * cache_usage_factor) as usize;
    let byte_split = (byte_split / 8 * 8).max(8); //round down to lower mult of 8 to fit in word
    let odd_count = (limit - first_aligned) / 2 + 1;
    let bit_split = byte_split*8;
    let workloads = odd_count.div_ceil(bit_split);
    if workloads == 0 {
        return primes;
    }

    let thread_count = min(logical_threads, workloads);

    //compute limits of workload
    let mut start_odds = vec![0; workloads];
    let mut stop_odds = vec![0; workloads];
    for i in 0..workloads {
        start_odds[i] = first_aligned + i * bit_split * 2;
        stop_odds[i] = min(start_odds[i] + bit_split * 2, limit + 1);
    }

    //allocate bit vectors
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
    dispatch_threads(job, &mut nums_vecs)
}