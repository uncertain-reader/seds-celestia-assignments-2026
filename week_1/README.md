# Week 1: Bouncing balls

| File | What it is |
|---|---|
| `bouncingball.py` | 1D: ball falls onto a flat floor. Plain Python floats. |
| `roundboundary.py` | 2D: ball bounces inside a circle. Same physics as numpy vectors. |

## The loop

Every frame does the same four things:

1. **measure `dt`**: seconds since the last frame
2. **move**: `pos += vel * dt`
3. **collide**: detect overlap, push out, reflect velocity
4. **accelerate**: `vel += g * dt`

then draw.

### Why `dt` is measured, not hardcoded

`clock.tick(FPS)` caps the loop at `FPS` and returns how many **milliseconds**
actually passed, so `/1000` gives seconds. Using the measured value instead of
a fixed `1/60` keeps the ball falling at the same real-world speed even when a
frame runs late. The sim slows down its steps, not its physics.

### Why gravity comes after the move

Moving first and *then* updating the velocity is semi-implicit (symplectic)
Euler. It is the same amount of code as plain Euler but does not bleed energy
over a long run, so the ball keeps bouncing to roughly the same height instead
of slowly dying or blowing up.

## Collisions

Two rules, both files:

**Detect on the edge, not the centre.** That is where every `r` comes from:
the floor is hit when `y + r > H`, the circular wall when `distance + r > R`.

**Fix the position before the velocity.** A frame moves the ball in one jump,
so it lands *inside* the wall. Flip the velocity and leave it buried and it is
still overlapping next frame, flips again, and sticks there vibrating. So
measure the overshoot (`offset`) and undo exactly that much first.

The rest is just direction. A flat floor always faces up, so the bounce is a
sign flip (`v *= -1`) and backing out is `y -= offset`. A circle faces a
different way at every point, so both steps need the normal `n` first. That
case is worked out below.

## The equations (`roundboundary.py`)

$\mathbf{p}$ = ball centre, $\mathbf{v}$ = velocity, $\mathbf{c}$ = arena centre,
$R$ = arena radius, $r$ = ball radius.

**1. Move.** Update position with the old velocity, then the velocity.

$$\mathbf{p} \mathrel{+}= \mathbf{v}\,\Delta t \qquad\qquad \mathbf{v} \mathrel{+}= \mathbf{g}\,\Delta t$$

**2. Are we hitting the wall?** Measure centre to centre, add the radius to
reach the ball's outer edge:

$$\mathbf{d} = \mathbf{p} - \mathbf{c}, \qquad D = \lVert \mathbf{d} \rVert, \qquad \text{hit if } D + r > R$$

**3. Which way is the wall facing?** Divide $\mathbf{d}$ by its own length and
you keep the direction but get length 1. That unit vector points straight out
of the circle at the touch point:

$$\mathbf{n} = \frac{\mathbf{d}}{D}, \qquad \lVert \mathbf{n} \rVert = 1$$

**4. Push it back out.** The frame moved the ball in one jump, so it landed
$s$ deep inside the wall. Step back inward by exactly that much:

$$s = D + r - R, \qquad \mathbf{p} \mathrel{-}= s\,\mathbf{n}$$

**5. Bounce.** Split the velocity into the part heading into the wall and the
part sliding along it:

$$\mathbf{v} = \underbrace{(\mathbf{v}\cdot\mathbf{n})\,\mathbf{n}}_{\text{into the wall}} + \underbrace{\mathbf{v} - (\mathbf{v}\cdot\mathbf{n})\,\mathbf{n}}_{\text{along the wall}}$$

Keep the sliding part, reverse the other one. Subtract it once to cancel it,
twice to flip it, which is where the 2 comes from:

$$\mathbf{v}' = \mathbf{v} - 2(\mathbf{v}\cdot\mathbf{n})\,\mathbf{n}$$

Nothing gets rescaled here, only flipped, so $\lVert \mathbf{v}' \rVert = \lVert \mathbf{v} \rVert$ and the ball bounces forever.
To lose energy, scale that flip by a restitution $e$:

$$\mathbf{v}' = \mathbf{v} - (1+e)(\mathbf{v}\cdot\mathbf{n})\,\mathbf{n}$$

$e = 1$ is the code above, $e = 0.9$ decays each bounce, $e = 0$ makes the
ball slide along the wall instead of bouncing.

## numpy in `roundboundary.py`

The 1D version needs no numpy, since the ball only moves along `y`. In 2D every
quantity is an `[x, y]` pair, and numpy lets one expression handle both axes.

**`np.array([a, b])`**
Makes a small fixed-size list of numbers, here `[x, y]`. The useful part is
that maths on it happens **elementwise**, slot by slot:

```
np.array([1, 2]) + np.array([10, 20])   ->  [11, 22]
np.array([1, 2]) * 3                    ->  [3, 6]
```

So `pos += vel * dt` scales both `vx` and `vy` by `dt` and adds them to `x`
and `y`, all in one line. Without numpy that is two lines, and four once you
add gravity.

**`.copy()`**
`pos = center` does **not** make a second array. Both names label the same
one, so moving the ball would also move the arena's centre. `.copy()` hands
back a separate array with the same values, safe to modify.

**`.astype(float)` and `.astype(int)`**
Converts the numbers to another type. An int array cannot hold fractions: a
step of 0.4 px becomes 0 and the ball never moves, so the physics array is
`float`. Only when drawing do we go back to `int`, since pygame needs whole
pixel coordinates.

**`np.random.uniform(low, high, size)`**
Random numbers, every value in the range equally likely. Called here as
`np.random.uniform(-200, 200, 2)`:
- range `low = -200` to `high = 200` (200 itself excluded)
- `size = 2`, so you get 2 of them, not 1

That is the random launch velocity `[vx, vy]`, each component somewhere
between -200 and 200 px/second. Change `size` to `3` and you would get three
numbers back.

**`np.linalg.norm(d)`**
Length of the vector `d`, i.e. `sqrt(dx² + dy²)`, straight-line Pythagoras.
Since `d = pos - center`, this is how far the ball's centre is from the
arena's centre, which is what the collision test compares against `R`.

**`np.dot(vel, n)`**
Dot product: multiply the vectors slot by slot and add the results,
`vel[0]*n[0] + vel[1]*n[1]`. It answers "how much of `vel` points in the
direction of `n`?". Because `n` here has length 1, the answer comes out
directly as a speed: how fast the ball moves straight at the wall. Positive
means moving outward (into the wall), negative means moving back inward,
zero means sliding along it.

## Running

```bash
uv run "week 1/bouncingball.py"
uv run "week 1/roundboundary.py"
```

Run from the repo root. See the [root README](../README.md) for first-time
setup (clone, install `uv`, `uv sync`).

## Assignment brief

The single ball behaves the way Part B describes: the path curves, it never
escapes at normal speeds, and with `e_w < 1` each bounce is lower until it
settles at the bottom. The two-ball collision only changes velocity along the
line joining the centres, so a glancing hit barely deflects while a head-on hit
swaps the speeds, which matches the equations.

For many balls I used the double loop over every pair. It works, but the number
of pairs grows like `N^2`, so the frame rate drops quickly as N goes up. The
pair check is the bottleneck, not the drawing. Broadcasting with numpy would
remove the Python loop and is the obvious next step.

## Answers

### Question 1

> A fast enough ball can end up outside the arena without the wall bounce ever
> being detected. Why does the detection fail, and which of dt, |v|, rho, R and
> g decide whether it happens?

The wall is only checked once per frame. In between, the ball does not really
move, it teleports from where it was to where it is next, a distance of
`|v| * dt`. Nothing looks at it during that jump.

So the ball can only be caught if one of those frames happens to land while it
is touching the wall. That zone is not very wide. The centre counts as "at the
wall" while it sits between `R - rho` and `R + rho`, so the zone is about one
ball across, `2 * rho`. If a single jump is longer than that, the ball can go
from clearly inside to clearly outside without ever being seen in between, and
the `distance + rho > R` test is never true on any frame it is actually checked.

Which of the five matter:

- `dt` and `|v|` matter directly, because their product is the jump. Halving
  the timestep does the same thing as halving the speed.
- `rho` matters directly too, because it is the size of the zone you are trying
  to hit. A bigger ball is harder to miss.
- `g` and `R` do not show up in the condition at all, but they decide how fast
  the ball gets. Falling from the top of the arena gives about
  `|v| = sqrt(2 g R)`, so stronger gravity or a bigger arena means a faster ball
  at the bottom, which is exactly where it is most likely to slip through.

So it comes down to whether `|v| * dt` is bigger than the ball. `g` and `R`
only matter through how big `|v|` ends up.

### Question 2

> Set e_w = 1, so that no energy is lost at a bounce, and let the ball run for
> a few thousand steps. Does the peak height stay put, creep upward, or decay?
> Gravity and the bounce rule are the only things acting, so if it changes at
> all, where is that energy coming from?

Yes, it decays, but it depends on how the ball hits the wall.

When I drop the ball straight down from the centre it looks fine. It keeps
coming back up to the same height and I could not see it change even after
leaving it for a long time. But if I give it some sideways speed so it hits
the wall at an angle, the bounces slowly get lower and lower. Eventually it
stops bouncing at all and just rolls around the bottom of the arena, even
though with `e_w = 1` it is not supposed to lose anything.

Here is why I think this happens.

The bounce rule on its own cannot be the reason. Flipping the velocity only
changes its direction, not how fast the ball is going, so it leaves the wall
at the same speed it arrived. Gravity cannot be the reason either, since
whatever it takes on the way up it gives back on the way down. So the loss
must be coming from the way the program handles the collision, not from the
physics we wrote down.

What I think is going on is that the collision is always caught a little too
late. The ball is only checked once per frame, so by the time we notice it has
hit the wall it has already gone partly inside. We then do two things to fix
it: push it back out, and flip its velocity. But neither of those is quite
what would have happened in real life. The real bounce should have happened a
moment earlier, at a slightly different spot, with a slightly different
velocity. Every bounce is therefore a bit wrong, and the errors do not have to
cancel out.

In the straight drop the ball hits the floor head on every time, so the error
is the same every bounce, and it seems to average out to nothing, which is why
it looks stable. When the ball hits at an angle it mostly skims along the
curved wall instead. Then it is being caught and corrected on nearly every
frame, and the small errors pile up in one direction, so it keeps losing
height until it is just rolling.

So the energy is not coming from gravity or from the bounce rule. It is being
lost by the program catching collisions late and correcting them by hand. I
would expect that checking more often, so the ball is caught closer to the
wall, would make the decay slower.
