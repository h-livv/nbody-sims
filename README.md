# N-body Simulations

Physics simulations written in C++, with Python scripts for plotting and animation. This is built to learn the language by simulating physical systems, with the goal of a general optimized N-body solver.

## Current

### N bodies under the effect of one large body and mutual gravitational fields.

![Three-body simulation](n-body/n-body.png)

## Reproduce it

From the root:
```
cd n-body
g++ n-body.cpp -o n-body
./n-body
python animate_n_body.py
```

## Planned

- Symplectic integrators
- Optimization algorithms to make it scale to larger N
- Exploration of the Fast Multipole Method