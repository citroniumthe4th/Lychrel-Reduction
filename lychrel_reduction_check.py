"""Machine verification for "Carry Sequences and Palindromes in the
Reverse-and-Add Process".

Reproduces every computational claim in the paper:
  - Theorems 2.3 and 2.4 (the two gates), exhaustively for 1 <= n < 10^6,
    both directions;
  - Theorems 3.2 and 3.3 (precursor signature, chained congruence) for every
    starting value m < 10^6, including the 495 orbits of Example 3.4;
  - Table 1: depth statistics for the first 20,000 steps of the orbit of 196.

Pure Python, no dependencies. Full run takes a few minutes.
"""

def col_model(n):
    d = [int(c) for c in str(n)]
    L = len(d)
    s = [d[i] + d[L - 1 - i] for i in range(L)]     # column sums, left to right
    e = [0] * L                                     # e[i] = carry into column i
    c = 0
    for i in range(L - 1, -1, -1):
        e[i] = c
        c = (s[i] + c) // 10
    t = [(s[i] + e[i]) % 10 for i in range(L)]
    return d, s, e, t, c                            # c = overflow bit e_0


def overflow_gate(d, s, e):
    """Theorem 2.4: palindrome iff d_1+d_L = 11 and all shifted congruences hold."""
    L = len(d)
    if d[0] + d[-1] != 11:
        return False
    # condition at 1-indexed j in 1..L-1; j and L-j are equivalent, reps j <= L//2
    return all((s[j] - s[j - 1] - e[j - 1] + e[L - j - 1]) % 10 == 0
               for j in range(1, L // 2 + 1))


def delta_noflow(e):
    """min 1-indexed i with e_i != e_{L+1-i}; None if palindromic carry vector."""
    L = len(e)
    return next((i + 1 for i in range(L // 2) if e[i] != e[L - 1 - i]), None)


def delta_flow(d, s, e):
    """0 if d_1+d_L != 11, else min failing rep j of Theorem 2.4(ii); None if palindrome."""
    L = len(d)
    if d[0] + d[-1] != 11:
        return 0
    return next((j for j in range(1, L // 2 + 1)
                 if (s[j] - s[j - 1] - e[j - 1] + e[L - j - 1]) % 10 != 0), None)


def exhaustive_precursor(N):
    """Theorems 3.2+3.3: an overflow-step palindrome forces the precursor signature
    (previous step no-overflow, s_1 = 5, e_1 = 1, hence successor starts 6 ends 5)
    and the chained congruence 2*s_2 + e_2 + e_{L-1} in {0,1,2} mod 10."""
    hits = []
    for m in range(1, N):
        d, s, e, t, c = col_model(m)
        n2 = m + int(str(m)[::-1])
        d2, s2, e2, t2, c2 = col_model(n2)
        T2 = n2 + int(str(n2)[::-1])
        if c2 and str(T2) == str(T2)[::-1]:
            L = len(d)
            assert c == 0 and s[0] == 5 and e[0] == 1, m               # Theorem 3.2
            assert L >= 3, m
            assert str(n2)[0] == '6' and str(n2)[-1] == '5', m
            assert (2 * s[1] + e[1] + e[L - 2]) % 10 in (0, 1, 2), m   # Theorem 3.3
            hits.append((m, n2, T2))
    print(f"Theorems 3.2+3.3 verified for all predecessors m < {N}; "
          f"{len(hits)} overflow-step palindromes found, first: {hits[:5]}")


def orbit_chain(seed=196, steps=20000):
    """In-vivo check of Theorems 3.2+3.3 on the orbit + survivor structure stats."""
    n, prev = seed, None
    n_flow = kill0 = surv = relaxed = 0
    max_df = 0
    for k in range(steps):
        d, s, e, t, c = col_model(n)
        if c:
            n_flow += 1
            df = delta_flow(d, s, e)
            assert df is not None, f"palindrome at step {k}?!"
            max_df = max(max_df, df)
            if df == 0:
                kill0 += 1
            else:
                surv += 1
                if k:
                    pc, ps1, pe1 = prev
                    assert pc == 0 and ps1 == 5 and pe1 == 1, k        # Theorem 3.2
                if s[1] % 10 in (0, 1, 2):
                    relaxed += 1                                       # Theorem 3.3 relaxation
        prev = (c, s[0], e[0])
        n += int(str(n)[::-1])
    print(f"{seed} orbit, {steps} steps: {n_flow} overflow steps "
          f"({n_flow/steps:.1%}); depth-0 kills {kill0} ({kill0/n_flow:.1%}), "
          f"survivors {surv} (every one has the Theorem-3.2 precursor signature), "
          f"of which pass relaxed depth-1 gate (s_2 mod 10 in 0..2): {relaxed}; "
          f"max delta' = {max_df}")


def exhaustive(N):
    for n in range(1, N):
        d, s, e, t, c = col_model(n)
        assert s == s[::-1], n                                   # Observation 2.1
        assert all(x in (0, 1) for x in e), n                    # Lemma 2.2
        T = n + int(str(n)[::-1])
        assert int(('1' if c else '') + ''.join(map(str, t))) == T, n
        is_pal = str(T) == str(T)[::-1]
        if c == 0:
            assert is_pal == (e == e[::-1]), n                   # Theorem 2.3
            assert is_pal == (delta_noflow(e) is None), n
        else:
            assert is_pal == overflow_gate(d, s, e), n           # Theorem 2.4
            assert is_pal == (delta_flow(d, s, e) is None), n
    print(f"Theorems 2.3+2.4 verified exhaustively for 1 <= n < {N}")


def orbit_stats(seed=196, steps=5000):
    n, prev_overflow = seed, False
    n_flow = n_noflow = kill0 = consec = 0
    max_dn = max_df = 0
    for k in range(steps):
        d, s, e, t, c = col_model(n)
        if c:
            n_flow += 1
            df = delta_flow(d, s, e)
            assert df is not None, f"palindrome at step {k}?!"
            if df == 0:
                kill0 += 1
                if prev_overflow:
                    consec += 1                                  # Proposition 3.1 case
            max_df = max(max_df, df)
        else:
            n_noflow += 1
            dn = delta_noflow(e)
            assert dn is not None, f"palindrome at step {k}?!"
            max_dn = max(max_dn, dn)
        prev_overflow = bool(c)
        n += int(str(n)[::-1])
    print(f"{seed} orbit, {steps} steps: {n_noflow} no-overflow / {n_flow} overflow "
          f"({n_flow/steps:.1%})")
    print(f"  no-overflow: max delta = {max_dn}")
    print(f"  overflow:    max delta' = {max_df}; "
          f"depth-0 kills (d_1+d_L != 11): {kill0}/{n_flow} ({kill0/n_flow:.1%}), "
          f"of which consecutive-overflow (Prop 3.1): {consec}")


if __name__ == "__main__":
    exhaustive(10**6)
    exhaustive_precursor(10**6)
    orbit_stats(steps=20000)
    orbit_chain(steps=20000)
