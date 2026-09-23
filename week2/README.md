# Week 2: The Sandbox

| File | What it is |
|---|---|
| `temp.py` | Falling-sand cellular automaton. Grid, drawing and mouse from the template, physics in `SandSim.update()`. |
| `week2.pdf` | The spec. |

## The tick

There are no positions or velocities this week. The world is one numpy
array, `grid[y, x]`, and every cell is a small integer: `0` empty, `1` sand,
`2` water. Row 0 is the **top** of the screen, so "below me" is `y + 1`.

Every frame `update()` does the same thing:

1. **copy**: `Gp = G.copy()`, the swap grid starts as a copy of the world
2. **visit**: every non-empty cell, bottom row first, columns in a random order
3. **rule**: read what I am from `G`, check where I can go in `Gp`, move in `Gp`
4. **swap**: `self._types = Gp`

### Why bottom-up

When a grain looks at the cell under it, that cell has already had its turn
this tick. If it moved away, its space is free and the grain drops into it; if
it stayed, the grain is blocked. Either way a grain moves at most one row per
frame, and a column of sand falls as a column. Scanning top-down, the upper
grain of a column sees the lower one still in place, thinks it is blocked,
and takes a diagonal it should not. Falling columns splay apart and flicker.

### Why `Gp` in the checks and `G` in the read

`is_empty` looks in `Gp` because that is where this tick's moves have landed.
Look in `G` instead and a grain hangs one frame above the gap the grain below
it just left. I had that bug; sand stacked in mid air for a tick.

The material `m` is read from `G` so every original cell is processed once. A
grain that moved *into* `(y, x)` earlier this tick only exists in `Gp`;
`G[y, x]` still says empty, so it is skipped and not moved twice.

## Rules

Three helpers, then the loop.

**`is_empty(yy, xx)`** is false off the grid, otherwise `Gp[yy, xx] == 0`.
Off-grid returning false is what makes the floor and the two walls solid
without any special code. The bounds check has to be explicit because numpy
happily reads `Gp[y, -1]` as the far right column instead of crashing.

**`move_to(y, x, yy, xx)`** copies the material into the target and writes
`0` into the origin. Two writes, both into `Gp`. Miss the second and the
grain duplicates.

**`try_fall(y, x)`** is the sand rule, in priority order:

1. below free: fall
2. else a diagonal-below free: slide, coin flip if both are free
3. else rest

It returns `True` if it moved. Sand ignores the answer. Water calls the same
function and, only if it returns `False`, tries the two cells beside it on the
same row, again with a coin flip. That one extra branch is the whole
difference between a pile and a puddle.

Straight down has to be checked first and alone. If a grain could take a
diagonal while the straight drop was still open, it would spread like a
liquid. Checking down first means slopes only form where the column below is
already full, which is what gives the ~45° angle of repose.

## numpy in `temp.py`

**`G.copy()`**
Same as week 1: `Gp = G` would be two names for one array and every "write
into the swap grid" would also change the world mid-tick. `.copy()` gives a
separate array.

**`_rng.permutation(W)`**
The numbers `0 .. W-1` in a random order. Generated once per tick and used as
the column visiting order for every row. Question 2 is about what happens when
you take it away.

**`_rng.random() < 0.5`**
`random()` is a float in `[0, 1)`, uniform, so this is a fair coin. All the
randomness comes from the one `_rng` the template already defines.

## Running

```bash
uv run python week2/temp.py
```

`1` sand, `2` water, `0` erase, `[` `]` brush size, `C` clear. See the
[root README](../README.md) for first-time setup.

## Assignment brief

Sand did what the spec says. A stream from one spot builds a cone with sides
close to 45°: pouring with the brush for a couple of seconds and letting it
settle gave a pile 21 cells high on a base 45 wide, so height over half-base
is about 0.95, and the two sides held 232 grains each. The little spike on top
while pouring is just the grains still in flight, not part of the pile. A
single grain drops exactly one row per frame and nothing is ever lost: pour
600 grains, count 600.

Water goes flat. A block of 126 cells dropped on a 30-wide floor ends up as
four full rows of 30 with six cells wandering about on the fifth. What
surprised me is that you cannot make a bowl out of sand to pour water into.
The sand walls slide away, because sand obeys the same diagonal rule as
everything else. You need something that never moves for that, which is what
wood is for in the bonus.

## Answers

### Question 1

> Why does the swap grid start as a copy of the current state, rather than
> being filled with zeros? What would happen to a grain that does not move if
> G' started empty?

The rules only write when something moves: the target gets the material and
the origin gets `0`. A grain that rests writes nothing at all. So whatever
`Gp` already holds at that position is what survives the swap.

If `Gp` started as zeros, that position holds `0`, and the grain is gone the
frame it stops moving. Every pile would vanish one tick after forming and only
falling grains would exist. Starting from a copy makes "do nothing" mean
"stay put" for free. It is also what lets things like wood or walls exist
without any rule of their own: the copy carries them across every tick.

A smaller second reason: the rules check targets in `Gp`. With an empty `Gp`
every cell would look free and grains would drop into occupied cells.

### Question 2

> Remove the randomised column order and replace it with a fixed left-to-right
> scan. Run the simulation for a few hundred ticks. What happens to the shape of
> a sand pile? Why?

Swapped `_rng.permutation(W)` for `range(W)` and poured with the brush.

The pile leans right. The peak ends up a few columns right of where the sand
is poured, the left face is still a clean 45° slope, and the right face runs
out into a long shallow tail, about half as steep. Counting grains on each
side of the source after a settled pour: 175 left, 414 right. With the shuffle
it was 232 and 234.

Why: scanning a row left to right, the grain on my left has already had its
turn this tick and the grain on my right has not. Suppose I cannot fall and
have to slide. If my left neighbour just fell straight down, it is now sitting
in my down-left diagonal. My down-right diagonal can only be blocked by
something that was already there, because the grain above it has not moved.
So every time two grains want the same cell, the left one wins and the loser
slides right. Then it cascades: the grain that slid right is now directly
under its right-hand neighbour, which cannot fall either, and whose down-left
diagonal is the cell I was sitting on, so it goes right too. A row of grains
landing together gets pushed right one after another.

The random permutation makes "who goes first" a coin flip every tick, so the
cascade runs left as often as right and it averages out.
