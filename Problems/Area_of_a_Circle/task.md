Complete the function which will return the area of a circle with the given `radius`. 

Returned value is expected to be accurate up to tolerance of 0.01.

~~~if:coffeescript,javascript,typescript
If the `radius` is not positive, throw `Error`.
~~~
~~~if:csharp
If the `radius` is not positive, throw `ArgumentException`.
~~~
~~~if:haskell
If the radius is positive, return `Just area`. Otherwise, return `Nothing`.
~~~
~~~if:java
If the `radius` is not positive, throw `IllegalArgumentException`.
~~~
~~~if:python
If the `radius` is not positive, raise `ValueError`.
~~~
~~~if:ruby
If the `radius` is not positive, raise `ArgumentError`.
~~~

Example:

```coffeescript
circleArea 43.2673     # returns 5881.248  (± 0.01)
circleArea 68          # returns 14526.724 (± 0.01)
circleArea 0           # throws Error
circleArea -1          # throws Error
```
```csharp
Kata.CalculateAreaOfCircle(43.2673); // returns 5881.248  (± 0.01)
Kata.CalculateAreaOfCircle(68);      // returns 14526.724 (± 0.01)
Kata.CalculateAreaOfCircle(0.0);     // throws ArgumentException
Kata.CalculateAreaOfCircle(-1.0);    // throws ArgumentException
```
```haskell
circleArea 43.2673 -- returns Just ( 5881.248 ± 0.01)
circleArea 68      -- returns Just (14526.724 ± 0.01)
circleArea 0       -- returns Nothing
circleArea (-1)    -- returns Nothing
```
```java
Circle.area(43.2673);     // returns 5881.248  (± 0.01)
Circle.area(68);          // returns 14526.724 (± 0.01)
Circle.area(0);           // throws IllegalArgumentException
Circle.area(-1);          // throws IllegalArgumentException
```
```javascript
circleArea(43.2673);     // returns 5881.248  (± 0.01)
circleArea(68);          // returns 14526.724 (± 0.01)
circleArea(0);           // throws Error
circleArea(-1);          // throws Error
```
```python
circle_area(43.2673)      # returns 5881.248  (± 0.01)
circle_area(68)           # returns 14526.724 (± 0.01)
circle_area(0)            # raises ValueError
circle_area(-1)           # raises ValueError
```
```ruby
circle_area(43.2673)      # returns 5881.248  (± 0.01)
circle_area(68)           # returns 14526.724 (± 0.01)
circle_area(0)            # raises ArgumentError
circle_area(-1)           # raises ArgumentError
```
```typescript
circleArea(43.2673);     // returns 5881.248  (± 0.01)
circleArea(68);          // returns 14526.724 (± 0.01)
circleArea(0);           // throws Error
circleArea(-1);          // throws Error
```