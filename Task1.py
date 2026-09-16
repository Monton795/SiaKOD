# task1.py
import random, time, tracemalloc  # импорт модулей
from typing import List  # импорт типа List


def dup_set(a: List[int]) -> int:  # способ 1: множество
    s = set()  # пустое множество
    for x in a:  # идём по массиву
        if x in s:  # элемент уже был
            return x  # это повтор
        s.add(x)  # добавляем в множество
    raise ValueError  # повтора нет


def dup_sort(a: List[int]) -> int:  # способ 2: сортировка
    b = sorted(a)  # отсортированная копия
    for i in range(1, len(b)):  # идём по соседям
        if b[i] == b[i - 1]:  # соседи равны
            return b[i]  # это повтор
    raise ValueError  # повтора нет


def dup_cycle(a: List[int]) -> int:  # способ 3: алгоритм Флойда
    s = f = a[0]  # черепаха и заяц в начале
    while True:  # ищем встречу в цикле
        s = a[s]  # черепаха: 1 шаг
        f = a[a[f]]  # заяц: 2 шага
        if s == f:  # встретились
            break  # выходим
    s = a[0]  # черепаха в начало
    while s != f:  # ищем вход в цикл
        s = a[s]  # шаг на 1
        f = a[f]  # шаг на 1
    return s  # это повтор


def gen(n: int, seed: int = 42) -> List[int]:  # генерация данных
    r = random.Random(seed)  # генератор с seed
    a = list(range(1, n + 1))  # n уникальных значений
    a.append(r.randint(1, n))  # добавляем повтор
    r.shuffle(a)  # перемешиваем
    return a  # возврат массива


def bench(sizes, reps=3):  # замер времени
    res = {k: [] for k in ("set", "sort", "cycle")}  # результаты
    for n in sizes:  # по размерам
        a = gen(n)  # данные
        for name, fn in (("set", dup_set), ("sort", dup_sort), ("cycle", dup_cycle)):  # по способам
            t = time.perf_counter()  # старт таймера
            for _ in range(reps):  # повторы
                fn(a)  # запуск алгоритма
            res[name].append((time.perf_counter() - t) / reps * 1000)  # среднее в мс
    return res  # возврат результатов


def mem(n):  # замер пиковой памяти
    a = gen(n)  # данные
    out = {}  # результаты
    for name, fn in (("set", dup_set), ("sort", dup_sort), ("cycle", dup_cycle)):  # по способам
        tracemalloc.start()  # вкл трассировку
        fn(a)  # запуск
        out[name] = tracemalloc.get_traced_memory()[1]  # пик в байтах
        tracemalloc.stop()  # выкл трассировку
    return out  # возврат результатов


def test_all_agree():  # тест: способы согласованы
    for n in (1, 2, 3, 5, 10, 100, 1000):  # по размерам
        a = gen(n, seed=n)  # данные
        assert dup_set(a) == dup_sort(a) == dup_cycle(a)  # ответы совпадают


def test_known_cases():  # тест: известные массивы
    assert dup_set([1, 1]) == 1  # минимум set
    assert dup_sort([1, 1]) == 1  # минимум sort
    assert dup_cycle([1, 1]) == 1  # минимум cycle
    assert dup_set([1, 2, 3, 3, 4]) == 3  # середина set
    assert dup_sort([1, 2, 3, 3, 4]) == 3  # середина sort
    assert dup_cycle([1, 2, 3, 3, 4]) == 3  # середина cycle
    assert dup_set([2, 2, 1, 3]) == 2  # начало set
    assert dup_sort([2, 2, 1, 3]) == 2  # начало sort
    assert dup_cycle([2, 2, 1, 3]) == 2  # начало cycle


def test_returns_int():  # тест: тип ответа int
    a = gen(50, seed=7)  # данные
    for fn in (dup_set, dup_sort, dup_cycle):  # по способам
        assert isinstance(fn(a), int)  # результат int


def test_exact_duplicate():  # тест: ровно один повтор
    for n in (2, 10, 50, 200):  # по размерам
        a = gen(n, seed=n)  # данные
        dup = dup_set(a)  # находим повтор
        assert a.count(dup) == 2  # ровно два вхождения
        assert 1 <= dup <= n  # в диапазоне
        assert len(a) == n + 1  # длина n+1


def test_no_duplicate_raises():  # тест: без повтора — ошибка
    for fn in (dup_set, dup_sort):  # cycle не годится — зациклится
        try:  # пробуем
            fn([1, 2, 3])  # массив без повтора
            assert False  # не должно дойти
        except ValueError:  # ждём исключение
            pass  # ок


def test_input_not_modified():  # тест: вход не меняется
    a = gen(100, seed=3)  # данные
    b = a.copy()  # копия
    dup_set(a)  # прогон 1
    dup_sort(a)  # прогон 2
    dup_cycle(a)  # прогон 3
    assert a == b  # массив прежний


def test_random_many():  # тест: много случайных
    for seed in range(50):  # 50 seed
        n = random.Random(seed).randint(1, 200)  # случайный размер
        a = gen(n, seed=seed)  # данные
        assert dup_set(a) == dup_sort(a) == dup_cycle(a)  # ответы совпадают


def run_tests():  # запуск всех тестов
    tests = [  # список тестов
        test_all_agree,  # согласие
        test_known_cases,  # известные
        test_returns_int,  # тип
        test_exact_duplicate,  # один повтор
        test_no_duplicate_raises,  # исключение
        test_input_not_modified,  # вход цел
        test_random_many,  # случайные
    ]
    for t in tests:  # по тестам
        t()  # запуск
        print(f"PASS {t.__name__}")  # отметка
    print(f"\nВсе {len(tests)} тестов пройдены")  # итог


if __name__ == "__main__":  # точка входа
    run_tests()  # тесты
    sizes = [100, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000, 200000]  # размеры
    r = bench(sizes)  # бенчмарк
    print(f"\n{'bytes':>10} {'set':>9} {'sort':>9} {'cycle':>9}")  # шапка таблицы
    for i, n in enumerate(sizes):  # по размерам
        print(f"{(n + 1) * 8:>10} {r['set'][i]:>9.4f} {r['sort'][i]:>9.4f} {r['cycle'][i]:>9.4f}")  # строка
    print("\nmem:", mem(100000))  # память
    with open("results.csv", "w") as f:  # открываем CSV
        f.write("bytes,set_ms,sort_ms,cycle_ms\n")  # заголовок
        for i, n in enumerate(sizes):  # по размерам
            f.write(f"{(n + 1) * 8},{r['set'][i]:.6f},{r['sort'][i]:.6f},{r['cycle'][i]:.6f}\n")  # строка