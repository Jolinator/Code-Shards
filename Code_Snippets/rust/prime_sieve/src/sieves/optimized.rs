use std::vec;

fn is_set(bits: &[u64], n: usize) -> bool {
    let mask = 1u64 << (n % 64);
    bits[n / 64] & mask != 0
}

pub(super) fn clear_bit(bits: &mut [u64], n: usize) {
    let mask = 1u64 << (n % 64);
    bits[n / 64] &= !mask;
}

pub(super) fn get_primes_from_bits(
    start_odd: usize,
    limit: usize,
    nums: &[u64],
) -> Vec<usize> {
    let mut primes = Vec::new();
    // limit is exclusive; start_odd is odd, so this is the number of odds in [start_odd, limit)
    let bit_limit = limit.saturating_sub(start_odd).div_ceil(2);
    let u64_limit = bit_limit.div_ceil(64);

    for (i, &bits) in nums.iter().enumerate().take(u64_limit) {
        for j in 0..64 {
            if i * 64 + j >= bit_limit {
                break;
            }
            if bits & (1u64 << j) != 0 {
                let n = start_odd + 2 * (i * 64 + j);
                primes.push(n);
            }
        }
    }
    primes
}

pub fn eratosthenes_algo_optimized(limit: usize) -> Vec<usize> {
    let odd_count = limit.saturating_sub(2) / 2;
    let mut nums = vec![u64::MAX; odd_count.div_ceil(64)];
    let mut invalidating = 3;
    let mut counter = invalidating * invalidating;

    while invalidating <= (limit as f64).sqrt() as usize {
        while counter < limit {
            clear_bit(&mut nums, (counter - 3) / 2);
            counter += invalidating * 2;
        }
        invalidating += 2;
        while !is_set(&nums, (invalidating - 3) / 2) {
            invalidating += 2;
        }
        counter = invalidating * invalidating;
    }
    let mut primes = vec![2];
    primes.extend(get_primes_from_bits(3, limit, &nums));
    primes
}
