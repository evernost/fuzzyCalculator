# Fuzzy Calculator


## What is it?
The Fuzzy Calculator looks like a regular calculator supporting classical math operations, but enhanced to work on intervals instead of scalars.

In other words, instead of executing calculations on numbers, it runs a Monte-Carlo simulation based on the statistics of the operands.

Not only it gives a range of the output, but it also gives a "plausible" range (probability) of it.

## What can I do with it?
Non exhaustive list:
- worst case analysis: what are the min/max values an expression can reach?
- signal processing: determine the range of a variable after some processing to the number of bits required.

## How do I use it?
The calculator takes as input a string containing the mathematical expression.
All the parsing machinery is included.

The integrated parser supports "natural" inputs like good old TI calculators, which includes:
- implicit multiplications
- lazy parenthesis
So expressions like "(a+b)(c-d)" or "sin(x+cox(y" are perfectly legal.

Then, declare the variables and their statistic (uniform in range, gaussian, etc.) configure the simulation settings and _voilà_.

> [!NOTE]
> Several rules apply for the parsing and the way it is going to be interpreted.</br>
> A detailed list of those rules can be found in "qParser.py"

## What else do I need?
In order to keep it easily portable for any target and/or programming language, it is based on 'native' Python and does not require any specific library.
In particular:
- no regex
- no complex string manipulation

Only numpy will be used at the end to calculate the functions.

## What operations can I do with it?
The calculator grants the most classical math operators ('+', '-', '*', '/', '^') and more obscure ones ('//' for parallel resistor association)
Usual math functions are included (sin, cos, log, log10, exp, abs, ...) 

Structure is quite flexible so it is possible to add custom functionsand infix operators. 
Refer to <parser.py> for more information about the limitations.

## What features might come next?
The integrated parser tries to treat the inputs as 'placeholders' as much as possible which gives flexibility for the manipulated objects.
Future releases could handle fixed point numbers, integers, matrices, etc.

It is worth mentionning that the built-in parser preserves the order of the input, therefore it does not assume commutativity of infix like '+', '*', ... which makes it possible to extend it to matrices, quaternions, etc.

> [!NOTE]
> Pipe char "|" have been considered as a shortcut for abs(), but it leads to ambiguity. </br>
> **Example:** |a + b|cos(x)|c + d|</br>
> It would be great to find a solution for that.


## TODO / Ideas
Sorted by increasing effort: 
- add a pretty print for the 'binary tree' to check/debug the parser's interpretation
- add support for scientific notation
- add support for thousands delimitation using "_": "3_141_592" vs "3141592"
- add support for special characters (pi?)
- add support for 'dot-prefixed' operators like '.+'?
- add support for complex numbers
- add an interactive mode where: 
  - a command prompt appears
  - variables and their statistics can be typed in the CLI
  - the tree is built as the user types in the expression for immediate feedback
  - pipes "|" are immediately translated to "abs("
  - implicit multiplications are automatically expanded
  - possible warnings (ambiguities, ...), errors are shown as the user types
  - ...


## What is the development status?
Still on-going, some expression already evaluate succesfully!


