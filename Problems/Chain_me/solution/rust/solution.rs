fn chain<F: Fn(i32)->i32>(input: i32, functions: &[F]) -> i32 {
    let mut buffer: i32 = input;
    for func in functions {
        buffer = func(buffer)
    }
    buffer
}