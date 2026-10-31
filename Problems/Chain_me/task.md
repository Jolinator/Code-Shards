~~~if-not:prolog
## Write a generic function chainer

Write a generic function chainer that takes a starting value, and an array of functions to execute on it (array of symbols for Ruby).

The input for each function is the output of the previous function (except the first function, which takes the starting value as its input). Return the final value after execution is complete.
~~~
~~~if:prolog
## Write a generic predicate chainer

Write a generic predicate chainer that takes a starting value, and an array of atoms to execute on it.

The first input for each predicate is the output of the previous predicate (except the first predicate, which takes the starting value as its input). Return the final value after execution is complete.
~~~

```javascript
function add(num) {
  return num + 1;
}

function mult(num) {
  return num * 30;
}

chain(2, [add, mult]);
// returns 90;
```
```haskell
add = (+ 1)
mul = (* 30)

chain 2 [add, mult] -> 90
```
```ruby
def add num
  num + 1
end

def mult num
  num * 30 
end

chain(2, [:add, :mult])
#=> returns 90
```
```csharp
double input = 2;

public static double add(double x) {
  return x + 1;
}

public static double mul(double x) {
   return x * 30;
}
Kata.Chain( input , new[] { (Func<double, double>)add, mul });
//=> returns 90
```

```c
int add10 (int x) { return x + 10; }
int mul30 (int x) { return x * 30; }

typedef int (*funcptr) (int);

chain(50, 2, (funcptr[2]) {add10, mul30});
// returns 1800
```

```python
def add10(x): return x + 10
def mul30(x): return x * 30

chain(50, [add10, mul30])
# returns 1800
```
```factor
: add10 ( x -- r ) 10 + ;
: mul30 ( x -- r ) 30 * ;

50 { [ add10 ] [ mul30 ] } chain
! returns 1800
```
```ocaml
let add n = n + 1 in
let mult n = n * 30 in

chain 2 [add; mult] (* -> 90 *)
```
```prolog
add(X,R):-R is X+1.
mul(X,R):-R is X*30.

?- chain(2,[add,mul],Result). % Result = 90.
```
```rust
fn add10(x) { x + 10 }
fn mul30(x) { x * 30 }

chain(50, &[&add10, &mul30]) //=> returns 1800
```