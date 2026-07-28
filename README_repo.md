# Carry Sequences and Palindromes in the Reverse-and-Add Process

Machine verification for the paper *Carry Sequences and Palindromes in the
Reverse-and-Add Process*. One file, pure Python 3, no dependencies.

```
python3 lychrel_reduction_check.py
```

Reproduces every computational claim in the paper (a few minutes total):

- **Theorems 2.3 and 2.4** (the two palindromicity gates): verified
  exhaustively, in both directions, for all `1 <= n < 10^6`.
- **Theorems 3.2 and 3.3** (precursor signature and chained congruence):
  verified for every starting value `m < 10^6`, finding the 495 orbits of
  Example 3.4 (smallest: `154 -> 605 -> 1111`).
- **Table 1**: depth statistics for the first 20,000 steps of the orbit
  of 196 (max delta = 29 on no-overflow steps; max delta' = 2 on overflow
  steps; 97.4% of overflow steps resolved at depth 0).

Expected output:

```
Theorems 2.3+2.4 verified exhaustively for 1 <= n < 1000000
Theorems 3.2+3.3 verified for all predecessors m < 1000000; 495 overflow-step palindromes found, first: [(154, 605, 1111), (253, 605, 1111), (352, 605, 1111), (451, 605, 1111), (550, 605, 1111)]
196 orbit, 20000 steps: 11707 no-overflow / 8293 overflow (41.5%)
  no-overflow: max delta = 29
  overflow:    max delta' = 2; depth-0 kills (d_1+d_L != 11): 8077/8293 (97.4%), of which consecutive-overflow (Prop 3.1): 1029
196 orbit, 20000 steps: 8293 overflow steps (41.5%); depth-0 kills 8077 (97.4%), survivors 216 (every one has the Theorem-3.2 precursor signature), of which pass relaxed depth-1 gate (s_2 mod 10 in 0..2): 68; max delta' = 2
```
