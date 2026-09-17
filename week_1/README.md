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
