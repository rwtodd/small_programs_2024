Makes a recursive (fractal-like) series of magic squares via the Lo-Shu pattern.  

It starts with just the trivial 1x1 square (1).

Then, it expands the (1) into the 3x3 Lo-Shu square.

Then, it expands every entry in the 3x3 square into a new 3x3 magic square, and puts them together into a 9x9 super-square.  Importantly,
every member of the 3x3 square is still in the same relative place in the new 9x9 square.

Then, it expands the 9x9 into a 27x27... then into 81x81... and could continue forever making increasingly larger magic squares of magic squares.

The program double-checks the sums, and checks that each square has no repeating numbers.

