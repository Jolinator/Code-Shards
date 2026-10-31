use std::{println, time::{Duration, Instant}, vec};


fn eratosthenes_naive(limit: usize) -> Vec<usize> {
    let mut primes = Vec::new();
    let mut nums = vec![true; limit];
    nums[0] = false;
    nums[1] = false;
    let mut counter = 4;
    let mut invalidating = 2;
    while invalidating <= (limit as f64).sqrt() as usize {
        while counter < nums.len(){
            nums[counter] = false;
            counter+=invalidating;
        }
        invalidating+=1;
        while !nums[invalidating]{
            invalidating+=1;
        }
        counter=invalidating*2
    }
    for n in 0..nums.len()-1{
        if nums[n]{
            primes.push(n);
        }
    }
    primes
}

fn is_set(bits: &[u64], n: usize) -> bool {
    let mask = 1u64 << (n % 64);
    bits[n / 64] & mask != 0
}

fn clear_bit(bits: &mut [u64], n: usize) {
    let mask = 1u64 << (n % 64);
    bits[n / 64] &= !mask;
}

fn eratosthenes_algo_optimized(limit: usize) -> Vec<usize> {
    let mut primes = vec![2];
    let odd_count = limit.saturating_sub(2) / 2;
    let mut nums = vec![u64::MAX; odd_count.div_ceil(64)];
    let mut counter = 9;
    let mut invalidating = 3;
    while invalidating <= (limit as f64).sqrt() as usize {
        while counter < limit {
            clear_bit(&mut nums, (counter-3)/2);
            counter+=invalidating*2;
        }
        invalidating+=2;
        while !is_set(&nums, (invalidating-3)/2){
            invalidating+=2;
        }
        counter=invalidating*invalidating;
    }
    for n in 0..odd_count{
        if is_set(&nums, n){
            primes.push(2 * n + 3);
        }
    }
    primes
}

struct TestResult{
    limit:usize,
    time:Duration,
    primes:Vec<usize>
}

fn time_test(func: fn(usize) -> Vec<usize>, limit:usize) -> TestResult{
    let start = Instant::now();
    let primes = func(limit);
    let duration = start.elapsed();
    TestResult { limit, time: duration, primes }
}

fn time_function(func: fn(usize) -> Vec<usize>) -> Vec<TestResult>{
    let values = vec![100,1000,10000,1000000,10000000,100000000];
    let mut results = Vec::new();
    for limit in values {
        results.push(time_test(func, limit));
    }
    results
}

fn main() {
    let results_naive = time_function(eratosthenes_naive);
    let results_optimized = time_function(eratosthenes_algo_optimized);


    for (r1, r2) in results_naive.iter().zip(&results_optimized) {
        let same_primes = r1.primes == r2.primes;
        println!("Limit: {}, Same primes: {}", r1.limit, same_primes);
        println!("Naive Sieve time: {:?}", r1.time);
        println!("Optimized Sieve time: {:?}", r2.time);
        println!("");
    }
    
}
