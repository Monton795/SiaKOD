import random
import time
import tracemalloc
import statistics
import csv
from typing import List

ELEMENT_SIZE = 8


# ---------- Задание 1: реализация трёх способов ----------
# Требование к данным для dup_cycle: все элементы в [1, n], где n = len(a) - 1,
# ровно одно значение повторяется. Иначе — бесконечный цикл.
def dup_set(a: List[int]) -> int:
    s = set()
    for x in a:
        if x in s:
            return x
        s.add(x)
    raise ValueError


def dup_sort(a: List[int]) -> int:
    b = sorted(a)
    for i in range(1, len(b)):
        if b[i] == b[i - 1]:
            return b[i]
    raise ValueError


def dup_cycle(a: List[int]) -> int:
    s = f = a[0]
    while True:
        s = a[s]
        f = a[a[f]]
        if s == f:
            break
    s = a[0]
    while s != f:
        s = a[s]
        f = a[f]
    return s


# ---------- Задание 2: бенчмаркинг времени ----------
def gen(n: int, seed: int = 42) -> List[int]:
    r = random.Random(seed)
    a = list(range(1, n + 1))
    a.append(r.randint(1, n))
    r.shuffle(a)
    return a


def bench(sizes, reps=7):
    res = {"set": [], "sort": [], "cycle": []}
    for n in sizes:
        a = gen(n)
        for name, fn in (("set", dup_set), ("sort", dup_sort), ("cycle", dup_cycle)):
            times = []
            for _ in range(reps):
                t = time.perf_counter()
                fn(a)
                times.append(time.perf_counter() - t)
            res[name].append(statistics.median(times) * 1000)
    return res


# ---------- Задание 3: замер памяти ----------
def mem(n):
    a = gen(n)
    out = {}
    for name, fn in (("set", dup_set), ("sort", dup_sort), ("cycle", dup_cycle)):
        tracemalloc.start()
        fn(a)
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        out[name] = {"current": current, "peak": peak}
    return out


# ---------- Тесты ----------
def test_all_agree():
    for n in (1, 2, 3, 5, 10, 100, 1000):
        a = gen(n, seed=n)
        assert dup_set(a) == dup_sort(a) == dup_cycle(a)


def test_known_cases():
    assert dup_set([1, 1]) == 1
    assert dup_sort([1, 1]) == 1
    assert dup_cycle([1, 1]) == 1
    assert dup_set([1, 2, 3, 3, 4]) == 3
    assert dup_sort([1, 2, 3, 3, 4]) == 3
    assert dup_cycle([1, 2, 3, 3, 4]) == 3
    assert dup_set([2, 2, 1, 3]) == 2
    assert dup_sort([2, 2, 1, 3]) == 2
    assert dup_cycle([2, 2, 1, 3]) == 2


def test_returns_int():
    a = gen(50, seed=7)
    for fn in (dup_set, dup_sort, dup_cycle):
        assert isinstance(fn(a), int)


def test_exact_duplicate():
    for n in (2, 10, 50, 200):
        a = gen(n, seed=n)
        dup = dup_set(a)
        assert a.count(dup) == 2
        assert len(a) == n + 1


def test_no_duplicate_raises():
    for fn in (dup_set, dup_sort):
        try:
            fn([1, 2, 3])
            assert False
        except ValueError:
            pass


def test_input_not_modified():
    a = gen(100, seed=3)
    b = a.copy()
    dup_set(a)
    dup_sort(a)
    dup_cycle(a)
    assert a == b


def test_random_many():
    for seed in range(50):
        n = random.Random(seed).randint(1, 200)
        a = gen(n, seed=seed)
        assert dup_set(a) == dup_sort(a) == dup_cycle(a)


def run_tests():
    tests = [
        test_all_agree,
        test_known_cases,
        test_returns_int,
        test_exact_duplicate,
        test_no_duplicate_raises,
        test_input_not_modified,
        test_random_many,
    ]
    for t in tests:
        t()
        print(f"PASS {t.__name__}")
    print(f"\nВсе {len(tests)} тестов пройдены\n")


if __name__ == "__main__":
    run_tests()

    sizes = [100, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000, 200000]
    r = bench(sizes)

    print(f"{'bytes':>12} {'set_ms':>10} {'sort_ms':>10} {'cycle_ms':>10}")
    for i, n in enumerate(sizes):
        b = (n + 1) * ELEMENT_SIZE
        print(f"{b:>12} {r['set'][i]:>10.4f} {r['sort'][i]:>10.4f} {r['cycle'][i]:>10.4f}")

    m = mem(100000)
    print("\nПамять (n=100000):")
    for k, v in m.items():
        print(f"  {k:>6}: current={v['current']:>10} B, peak={v['peak']:>10} B")

    with open("results.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["bytes", "set_ms", "sort_ms", "cycle_ms"])
        for i, n in enumerate(sizes):
            b = (n + 1) * ELEMENT_SIZE
            w.writerow([b, f"{r['set'][i]:.6f}", f"{r['sort'][i]:.6f}", f"{r['cycle'][i]:.6f}"])
    print("\nresults.csv сохранён.")