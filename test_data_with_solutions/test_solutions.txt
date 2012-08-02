*------- Basic Tests -------*
*--- Solveable ---*
> Test 1 - Mutual Exclusion
	Very simple problem due
   to difficulty of representing a
   large system using only mutual
   exclusion.
	----------
	One: C D
	Two: A B
	----------
> Test 2 - Unary Exclusion
	-------------
	one: C G P
	two: J L
	three: B F
	four: E N O Q
	five: A K
	six: D H I M
	-------------
> Test 3 - Unary Inculsion
	-------------
	(same as 2)
	-------------
> Test 4 - Binary Equals
	-------------
	(same as 2)
	-------------
> Test 5 - Binary Not Equals
	-------------
	(same as 2)
	-------------
*--- No Solution ---*
> Test 6 - Mutual Exclusion
> Test 7 - Unary Exclusion
> Test 8 - Unary Inclusion
> Test 9 - Binary Equals
> Test 10 - Binary Not Equals


*------- Stress Tests -------*
> Test 11 - Basic Test
	The provided set from the
   assignment page. This had better
   work, or something is very wrong.
   ----------
   x: E D
   y: A B C
   z: H F
   ----------
> Test 12 - Combination
	A relatively quick test, with lots
   of constraints and few variables.
> Test 13 - "Snug"
	Solution possible. See "Too Snug"
> Test 14 - Sudoku Square (1/9)
	Solve this 3x3 square for sudoku.
	---------
	a: 3
	b: 6
	c: 7
	d: 5
	e: 4
	f: 2
	g: 1
	h: 9
	i: 8
	---------
> Test 15 - Combination 2
	Lots of varied constraints, average
   difficulty.
> Test 16 - Combination 3
	Similar to the last test, less
   items and bags and constraints,
   slightly more difficult to solve.
> Test 17 - Impossible
> Test 18 - Open Ended
	No fixed solution, just four bags
   and several items.
> Test 19 - "Too Snug"
	No solution: too many constraints.
   Same variable set as previous.
> Test 20 - Insufficient Total Weight
	Unsolvable: It may take some time
   to discover this without checking at
   the beginning.