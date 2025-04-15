# Fuzzy Calculator - Integrated Parser
The following note summarises the parsing rules implemented in the **Fuzzy Calculator**.

## Features
The integrated parser supports *natural* inputs (e.g. implicit multiplications) and lazy parenthesis.

So expressions like "(a+b)(c-d)" or "sin(x+cos(y" are **accepted**.

The calculator provides the most common math operators (`+`, `-`, `*`, `/`, `^`) 
and some obscure ones (`//` for parallel resistor association)

Usual math functions are included (`sin`, `cos`, `log`, `exp`, `abs`, ...) 

Order of operands is preserved while evaluating. In other words, no commutativity is assumed, even for infix like `+` and `*`. 
Therefore, future releases could potentially handle advanced types, like matrices or quaternions.

When called as a 'main', the library runs unit tests on the built-in
parsing functions.

## Requirements
The parser is based on native Python and does not require any specific library:
- no regex
- no complex string manipulation

However, if transcription to another programming language is needed, 
the following features would be nice to have:
- OOP 
- string to float conversion routines
- math functions (`sin`, `cos`, `exp`, etc.)
- random number generation for the Monte-Carlo analysis
- some plotting features


## Add custom infix operators and functions
Coming soon.


# Parsing rules

The following gives the parsing strategy and lists all rules that apply 
when an expression is evaluated.

## [R1] Case sensitivity

The parser is case sensitive.

- `pi` and `Pi` are not the same constant
- `cos()` and `Cos()` are not the same function
- `myVar` and `MyVAR` are not the same variable
- etc.

## [R2] Constant/variable/function name prefixing

The name of a function/variable/constant cannot start with a **number**.

Otherwise, the parser could not tell the difference between a name and an implicit
product.<br>
Expressions like `3var` are always seens as `3`*`var`.

## [R3] Function call syntax

No space is accepted between the name of the function and the parenthesis.

- `exp(-2t)` → ✅
- `exp (-2t)` → ❌


Allowing this space has no added value, and it makes the parsing more complicated.<br>


## [R4] Void arguments

A function cannot be called with empty arguments.
- `exp(0)` → ✅
- `exp()` → ❌

## [R5] Implicit multiplication rules

The following priorities have been defined based on what feels the most "natural" interpretation.<br>
In case of ambiguity, a warning is raised.

General rule for implicit products:
| Rule    | Example | Rationale |
| :-------- | ------- |------- |
| R5.1  | `pixel` → `var("pixel")`| The variable as a whole is more likely than a product of smaller variables.<br> Why not even `pi`* `x`*`el`?|





Rules for prefixing digit/number:
| Rule    | Example | Rationale |
| :-------- | ------- |------- |
| R5.2 | `1X` → `1*var("X")`| A variable cannot start with a digit (rule R2)|
| R5.3 | `1_X` → `1*var("_X")`| Same as R5.2<br> Also, prefixing with `_` is allowed.|
| R5.4 | `1.0X` → `1.0*var("X")`| Same as R5.2|
| R5.5 | `1.0_X` → `1.0*var("_X")`| Same as R5.2|
             


Rules for suffixing digit/number:
| Rule    | Example | Rationale |
| :-------- | ------- |------- |
| R5.6 | `X2` -> `var("X2")`| Typical variable suffixing. |
| R5.7 | `X_2` -> `var("X_2")`| Same as R5.6 |


[R5.8]  "X2.0       -> var("X")*2.0             | A decimal number interrupts the variable parsing.
                                                | A bit odd, but it is probably the most plausible meaning.
                                                | Raises a warning.
[R5.9]  "X_2.0      -> var("X_")*2.0            Same as R5.8

Rules for suffixing digit/number (continued):
[R5.10] "X3Y"       -> var("X3")*var("Y")       | If a variable contains a number, its name can only end with a digit.
        "R10C2"     -> var("R10")*var("C2")     |
        "C1cos("    -> var("C1")*cos(...        |
        "X2cos+3"   -> syntax error!            "cos" is not called according to the rules for functions (R3)
[R5.11] "X_3Y"      -> var("X_3")*var("Y")      | Same principle as [R5.10]
        "v_21cos("  -> var("v_21")*cos(...      |
        "X_2cos("   -> var("X_2")*cos(...       |
[R5.12] "X2.0cos("  -> var("X")*2.0*cos(...     Consistent with R5.8
[R5.13] "X_2.0cos(" -> var("X_")*2.0*cos(...    Consistent with R5.9
[R5.14] "R1_Y*pi"   -> var("R1_Y")*pi           | An underscore allows more complex variable names, even after a digit.
        "x_1_2_Y*4" -> var("x_1_2_Y")*4         | 
[R5.15] "X_3.0_Y"    -> var("X_")*3.0*var("_Y") Raises a warning


Consequences:
"X_3.1Y" -> var("X_")*3.1"*var("Y")           Consequence of rule R5.9

Behaviour not decided yet:
[R5.__] "pi4X"   -> const("pi")*4*var("X")     ??
[R5.__] "pi4.0X" -> const("pi")*4.0*var("X")   ??
[R5.__] "pi_5"   -> var("pi_5")                Underscore serves as disembiguation/indexing and overrides the constant

[R5.__] "pipi"   -> var("pipi")                If "pi*pi" was meant, maybe the user should make an effort here.
[R5.__] "inf"    -> const("inf")               Parser tries to see as a whole in priority (so not "i*nf", "i" being a constant too)
                                               See also [R5.10]
[R5.__] "ipi"    -> var("ipi")                 Same as [R5.13]

## [R6] Infix operator name
The super common ones (`+`, `-`, `/`, `*`, ...) along with exotic ones (`//`) are already included.

Users are free to customise with their favorite infix if they really want to, 
but some restrictions apply:
- infix ops cannot be made of letters, digits, commas, dots: this would mess with the rest of the parsing.<br>
  Special characters are recommended: `@`, `!`, `\`, `$`, `#`, ...<br>
  Feel free to combine them: `@*`, `+!`, ...
- the special character(s) for your custom infix need to be added to the 'white list' in function `TODO`.
- the expected behaviour for this new infix operator needs to be defined.

Infix operators that are not based on special characters will not be supported.
There are no plans to accept inputs like 'x DONG y' or 'a SUPER+ b'.
Reasons for that:
- ruins the readability
- special characters already give enough flexibility
- exotic infix operators are not that common. It is not worth the engineering.
- infix operators are 2 variables functions in disguise.
  Multiargs functions are already supported and should be the reasonable choice here.

Also, be careful when defining the priority of your new operator (see rules [R7.X] and [R11])

# [R7] Rules for omitted tokens
The infix operator "-" (minus sign) is the only operator that allows an implicit left operand.
In other words, expressions like "(-3x+..." are accepted.

There are not many cases where the implicit left operand is common and/or makes sense.
It is mostly used:
- to negate a number/constant/variable (rule [R7.1]) 
- for negative exponents               (rule [R7.2])

Based on that, the parser's strategy is the following:
- "(-3*..."  -> add a leading 0: "(0-3*..."
- "10^-4..." -> create a macroleaf with the 'opp' function: "10^M..."
  with M : {f = opp, M = [Num:'4']}.
  This should not have side effect with the rest of the expression
  since '^' has the highest priority.
  Keep that in mind when you define custom infix.

When the '-' appears at the beginning of an expression or subexpression
(like in a macroleaf) then rule [R7.1] applies.

Otherwise, rule [R7.2] is applied.

[R7.2] is derived as rule [R7.3] when the infix is not '^' anymore. 
Behaviour is the same but a warning is raised because the priority between 
operations becomes ambiguous and the expression does not look 'natural'.
Use of parenthesis is strongly recommended for both clarity and correctness.

Examples: 
- "(-5..." is valid                     (rule [7.1])
- "...^-5" is valid (e.g. for '10^-4')  (rule [7.2])
- "a^-3u" is be treated as "(a^(-3))*u" (rule [7.2])

The following will raise a warning:
- "...--4..." becomes "...-M..." with M = {f = opp, M = [Num:'4']}   (rule [7.3])
- "...*-pi..." becomes "...*M..." with M = {f = opp, M = [Cst:'pi']} (rule [7.3])

[R7.4] "(+4" is not accepted (implicit left operand is for minus sign only)
[R7.5] "-*4" is not accepted

Note: rule [7.1] only adds a zero and does not add parenthesis.
This prevents "-x^2" to be turned into "(-x)^2", which is probably
never what is really meant.

[R8] VARIABLE NAMING
Variable cannot start with a number.

[R9] WHITE SPACES
White spaces are not part of the syntax and are simply ignored.

[R10] OPERATORS ASSOCIATIVITY
Consecutive operators with identical priority are all treated 
with increasing nesting level (i.e. the 'rightest the deepest'):
- a+b+c+d -> a+(b+(c+d))
- a/b/c   -> a/(b/c)
- a//b//c -> a//(b//c)      (note: '//' is associative, parenthesis do not matter)
- a^b^c^d -> a^(b^(c^d))    (people will complain anyway, no matter what convention is chosen)
In doubt: check the output interpretation, add parenthesis.

[R11] OPERATORS PRECEDENCE
It is not recommended to change the relative priorities of the basic infix
operators: '+', '-', '*' , '/', '^'.
- as far as I know, there is no real need for that
- side effect will emerge due to the parsing strategy 
  (e.g. rule [R7.2]: '^' is assumed to have the highest precedence for proper operation)

Also, be careful when defining priority of custom infix: think twice about 
how it interacts with other infix.
Again, in doubt: use parenthesis and don't blindly rely on precedence. Parenthesis are free!

Priority level is limited to 100 (arbitrary limit)

