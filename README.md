# CLIChess 

### A simple python-based chess game played locally on the command-line.

#### Starting a Game

From the repository's base directory, enter

```sh
python CLIChess.py
```

Run as above, or use the options `-l` or `--letters` to use the standard letter-based pieces in the board display.
Use the options `-p` or `--pieces` to use unicode chess piece characters in the board display.
For example,

```sh
python CLIChess.py -p
```

#### Playing Moves

To make a regular move, choose the source square (where the piece is currently), for example `e2`, and a destination square (where the piece will go), for example, `e4`. 
Enter the move by typing `e2 e4` and press enter. 
Simple as that!
This works the same for taking your opponent's pieces, or simply moving your own.

To castle, choose a direction, `short` (kingside) or `long` (queenside). 
Enter the move by typing `castle short` or `castle long` and press enter.

When pushing a pawn to promotion, an additional input is required for the move. 
Choose the piece to promote the pawn into (usually a Queen), and add that information to the move. 
For example, to push a pawn on the seventh rank to the eighth and promote it to a Queen, type `e7 e8 queen`.

Capitalization for the moves does not matter.

#### The Pieces

##### Letter-based display (default)

Pieces are represented by the first letter of their name, with pawns being lowercase and the other pieces being capitalized.
The pieces have a prefix `w` or `b` depending on their color, white or black.

For example, a black pawn is `bp` and a white rook is `wR`.

##### Unicode character-based display (optional)

Pieces are represented with unicode characters, &#9812;, &#9818;, etc.
Note that the display assumes a dark theme console, and flips the piece colors to compensate. 
If the console is light themed, the board will seem flipped.

#### Screenshots

Below are screenshots of the board after 

```
1. e4 e5
2. Bc4
```

with letter-based pieces and unicode character-based pieces.

Letter-based pieces:

![image](screenshots/letter_pieces.PNG?raw=true)

Unicode character-based pieces:

![image](screenshots/unicode_character_pieces.PNG?raw=true)
