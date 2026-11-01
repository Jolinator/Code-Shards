use super::optimized::{clear_bit, eratosthenes_algo_optimized, get_primes_from_bits};
use std::cmp::min;
use std::thread::{self, available_parallelism};

pub fn sieve_with_primes(
    start_odd: usize,
    stop_odd: usize,
    primes: &[usize],
    nums: &mut Vec<u64>,
) -> Vec<usize> {
    let mut counter: usize;
    for &p in primes {
        if p == 2 {
            continue;
        }
        counter = (start_odd / p) * p;
        if counter % 2 == 0 {
            counter += p;
        } else if counter < start_odd {
            counter += 2 * p;
        }
        while counter <= stop_odd {
            clear_bit(nums, (counter - start_odd) / 2);
            counter += p * 2;
        }
    }

    get_primes_from_bits(start_odd, stop_odd, nums.as_slice())
}

pub fn eratosthenes_cache_thread(
    limit: usize,
    cache_bytes: usize,
    logical_threads: usize,
    cache_usage_factor: f64,
) -> Vec<usize> {
    let byte_split = (cache_bytes as f64 * cache_usage_factor) as usize;
    let limit_sqrt = (limit as f64).sqrt() as usize;
    let limit_sqrt = if limit_sqrt%2==0{
        limit_sqrt+1
    }
    else {
        limit_sqrt
    };

    let primes = eratosthenes_algo_optimized(limit_sqrt + 1);
    let first_odd = limit_sqrt + 2;
    if first_odd > limit {
        return primes;
    }
    
    let odd_count = (limit - first_odd) / 2 + 1;
    let bit_split = byte_split*8;
    let workloads = odd_count.div_ceil(bit_split);
    if workloads == 0 {
        return primes;
    }

    let thread_count = min(logical_threads, workloads);

    let mut start_odds = vec![0; workloads];
    let mut stop_odds = vec![0; workloads];
    for i in 0..workloads {
        start_odds[i] = first_odd + i * bit_split * 2;
        // exclusive stop, so limit itself is included
        stop_odds[i] = min(start_odds[i] + bit_split * 2, limit + 1);
    }

    let nums_vecs: Vec<Vec<u64>> = (0..workloads)
        .map(|i| vec![!0u64; (stop_odds[i] - start_odds[i]).div_ceil(2).div_ceil(64)])
        .collect();
    

    

    primes
}