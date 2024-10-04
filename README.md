# Fuzzy Calculator


## What is it?
The Fuzzy Calculator looks like a regular calculator. It supports classical math operations, but it has been pimped to work on **intervals** instead of scalars.

In other words: 
- with numbers: it does the usual computation,
- with intervals: it runs a Monte-Carlo simulation based on the statistics of the operands.

Not only it gives the **output range** of an expression, but also a most **plausible** values it can take.

## What can I do with it?
Non-exhaustive list:
- worst case analysis: what is the min/max range an expression can reach?
- signal processing: determine numbers of bits required for a variable that endures various processings.

## How do I use it?
The calculator takes as input a string containing the mathematical expression.
All the parsing machinery is included.

The integrated parser supports "natural" inputs like good old TI calculators, which includes:
- implicit multiplications
- lazy parenthesis

So expressions like ```"(a+b)(c-d)"``` or ```"sin(x+cox(y"``` are valid.

Then, declare the variables and their statistic (uniform in range, gaussian, etc.) configure the simulation settings and _voilà_.

> [!NOTE]
> Several rules apply for the parsing and the way it is going to be interpreted.</br>
> A detailed list of those rules can be found in "qParser.py"

## What else do I need?
In order to keep it easily portable for any target and/or programming language, it is based on 'native' Python and does not require any specific library.

In particular:
- no need for regex
- no complex string manipulation
- no call to Python ```eval``` (that would be lame...)

Only ```numpy``` is used eventually at the end to calculate the functions.

## What operations can I do with it?
The calculator provides the most classical math operators (```'+'```, ```'-'```, ```'*'```, ```'/'```, ```'^'```) and more obscure ones (```'//'``` for parallel resistor association).
Usual math functions are included (```sin```, ```cos```, ```log```, ```log10```, ```exp```, ```abs```, ...) 

Structure is quite flexible so it is possible to add custom functions and infix operators. 
Refer to ```parser.py``` for more information about the limitations.

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
- add support for scientific notation
- add support for thousands delimitation using "_": ```"3_141_592"``` vs ```"3141592"```
- add support for special characters (```π```?)
- add support for 'dot-prefixed' operators like ```".+"```?
- add support for complex numbers
- add an interactive mode where: 
  - a command prompt appears
  - variables and their statistics can be typed in the CLI
  - the tree is built as the user types in the expression for immediate feedback
  - pipes ```"|"``` are immediately translated to ```"abs("```
  - implicit multiplications are automatically expanded
  - possible warnings (ambiguities, ...), errors are shown as the user types
  - ...


## What is the development status?
So far, it has been tested **successfully** on various expressions with scalars (see unit tests).

What is remaining:
- solve bugs with the constants
- add support for variables and attach them the appropriate random generator


