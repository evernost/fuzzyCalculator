# Fuzzy Calculator

## What is it?
The Fuzzy Calculator is a command-line calculator.<br>
It's a calculator that's been enhanced to handle not only standard operations, but also operations on **intervals** instead of just scalars.

In other words: 
- with numbers: it does the usual computation (`2*3+1/7`, `cos(10)`, `2*exp(-1.0)`,  ...)
- with intervals: it runs a Monte-Carlo simulation based on the statistics of the operands.

Not only it gives the **output range** of an expression, but also a most **plausible** values it can take.

## What can I do with it?
Typical use cases:
- **worst case analysis**: what is the min/max range an expression can reach? or what are the most plausible values?
- **fine algorithm design**: determine numbers of bits required for a variable that endures various processings.

## Example
You are on a swing, and you'd like to estimate the length of the attaching ropes based on the oscillation period.
You measured 5T = 25s with a 0.5s uncertainty on the start/stop time.

Let's declare T = 5.0 +/- 0.1s:

`> var_T = variable.rand(name = "T", val = 5.0, abs = 0.1)`

Let's also assume that we don't know the local gravity _that_ well:

`> var_g = variable.rand(name = "g", val = 9.8, abs = 0.05)`

Create a Fuzzy Calculator object:

`> fcalc = fuzzyCalculator.Calc()`

Compile the expression to be calculated. Here we use T = 2π sqrt(L/g) and solve for `L`:

`> fcalc.compile("g*(T/(2*pi))^2")`

Run a Monte-Carlo simulation (10 000 runs):

`> fcalc.sim(runs = 10000)`

Plot the result:

`> fcalc.plot(bins = 100)`

![image](https://github.com/user-attachments/assets/7ffbf511-a095-4566-b2cd-6c1161af6eec)

This gives already a very good idea of the most plausible range for `L`: L = 5.9m ... 6.4m

Using the `percentileRange function`, you can directly get the range that contains 95% of the values:

`> fcalc.percentileRange(p = 0.95)`

Terminal output:<br>
[INFO] Creating a uniform random variable for 'T' (range = [4.9, 5.1])<br>
[INFO] Creating a uniform random variable for 'g' (range = [9.75, 9.850000000000001])<br>
[INFO] Compile OK.<br>
[INFO] Simulation done (runs: 10000)<br>

Percentile range (95.0%): [5.984 ... 6.431]

## How do I use it?
The calculator takes as input a string containing the mathematical expression.
All the parsing machinery is included.

The integrated parser supports "natural" inputs like good old TI calculators:
- implicit multiplications: `2x-3y`, `(a+b)(c-d)`, etc.
- lazy parenthesis (no need to close brackets): ```2(x+y```, ```"sin(x+cox(y"```

Then, declare the variables and their statistics (uniform in range, gaussian, etc.) configure the simulation settings and _voilà_.

> [!NOTE]
> Several rules apply for the parsing and the way it is going to be interpreted.</br>
> A detailed list of those rules can be found in ```src/qParser.py```

## What else do I need?
In order to keep it easily portable for any target and/or programming language, it is based on 'native' Python and does not require any specific library.

In particular:
- no need for regex
- no complex string manipulation
- no call to Python ```eval``` (that would be lame...)

Only ```numpy``` is used eventually at the end to evaluate the math functions.

## What operations can I do with it?
The calculator provides the most classical math operators (```'+'```, ```'-'```, ```'*'```, ```'/'```, ```'^'```) and more obscure ones (```'//'``` for parallel resistor association).
Usual math functions are included (```sin```, ```cos```, ```log```, ```log10```, ```exp```, ```abs```, ...) 

Structure is quite flexible so it is possible to **add custom functions and infix operators**. 
Refer to ```src/qParser.py``` for more information about the limitations.

## What features might come next?
The integrated parser tries to treat the inputs as 'placeholders' as much as possible which gives flexibility for the manipulated objects.
Future releases could handle fixed point numbers, integers, matrices, etc.

It is worth mentionning that the built-in parser preserves the order of the input, therefore it does not assume commutativity of infix like ```'+'```, ```'*'```, ... which makes it possible to extend it to matrices, quaternions, etc.

> [!NOTE]
> Pipe char "|" has been considered as a shortcut for ```abs()```, but it turns out it leads to ambiguity. </br>
> **Example:** ```|a + b|cos(x)|c + d|```</br>
> It would be great to find a solution for that.


## TODO / Ideas
Sorted by increasing effort:
- add a pretty print for the 'binary tree' to check/debug the parser's interpretation
- add support for units (consistency check, display output in the right units, etc.)
- add possibility to compose expressions
- add support for scientific notation
- add support for thousands delimitation using "_": ```"3_141_592"``` vs ```"3141592"```
- add support for special characters (```π```?)
- add support for 'dot-prefixed' operators like ```".+"```? Current parser does not accept it.
- add support for complex numbers
- add an interactive mode where: 
  - a command prompt appears
  - variables and their statistics can be typed in the CLI
  - the tree is built as the user types in the expression for immediate feedback
  - pipes ```"|"``` are immediately translated to ```"abs("```
  - implicit multiplications are automatically expanded
  - possible warnings (ambiguities, ...), errors are shown as the user types
  - ...
- add one-liners for intervals, to allow inputs like: ```"[1,2]*[-1,3] + [2,3]"```


## What is the development status?
So far, it has been tested **successfully** on various expressions with scalars (see unit tests in ```src/qParser.py```).

Remaining tasks: 
- [X] Wrap the complexity in a 'Calculator' object (high-level and user-friendly functions)
- [X] Add a proper variable detection (parser) and declaration (user)
- [X] Link the detected variable with the 'Variable' objects
- [X] Add the Monte-Carlo simulator
- [X] Plot the simulation results (histogram)
- [X] Add expression composition
- [ ] Add scripting: read variable definition and expressions from a file
- [ ] Add support for discrete random variables (finite set instead of a full range)
- [ ] Add the ability to account for the units in which the variables are expressed
- [ ] Binary object: add an "explanatory" mode (detailed operation stack) that breaks down the calculations done
- [ ] Add support for complex numbers
- [ ] Is there a simple way to determine the variable that accounts for most of the total variation?

