import random
from math import sqrt
import matplotlib.pyplot as plt
import numpy as np
import math

NU = 0.1
MU = 0.1
LAMBDA = 1
DT = 1
spread = 3


def poisson(la, k):
    return (math.e ** (-la) * la ** k) / math.factorial(k)


def value_of_poisson(la, k):
    x = random.random()
    s = 0
    for i in range(k):
        s += poisson(la, i)
        if s >= x:
            return i
    return k


class Order:
    def __init__(self, volume, arrival_time):
        self.volume = volume
        self.arrival_time = arrival_time

    def __str__(self) -> str:
        return f"V:{self.volume};T:{self.arrival_time}"


class OrderQueue:
    def __init__(self, price_level):
        self.price_level = price_level
        self.orders = list()

    def add_order(self, order):
        self.orders.append(order)

    def cancel_order(self, n):
        del self.orders[n]

    def order_sum(self):
        return sum([i.volume for i in self.orders])


def create_order_queue(size):
    return [OrderQueue(i) for i in range(size)]


pl = plt.figure()


def simulate_model(lambda_, nu_, mu_, t_max, limit_order_book):
    t = 0
    a = 0
    b = 100
    size = len(limit_order_book)
    middle_prices = list()
    total_volume = list()
    while t < t_max:
        v = 0
        m = (a + b) / 2

        for i in range(max(int(m) - spread * 5, 0), min(int(m) + spread * 5, size)):
            la = value_of_poisson(lambda_, 10)
            for j in range(la):
                v = value_of_poisson(lambda_ / nu_, 10) + 1
                if i <= m:
                    limit_order_book[i].add_order(Order(v, t))
                    a = i if a <= i else a
                else:
                    limit_order_book[i].add_order((Order(-v, t)))
                    b = i if b >= i else b

        for i in range(size // 2 - spread * 5, size // 2 + spread * 5):
            for_delete = list()
            for j in range(len(limit_order_book[i].orders)):
                nu = value_of_poisson(nu_, 1)
                if nu:
                    for_delete.append(j)
            for j in for_delete[::-1]:
                limit_order_book[i].cancel_order(j)
        market_sell = value_of_poisson(mu_, 10)
        market_buy = value_of_poisson(mu_, 10)
        for i in range(b, size):
            for j in range(len(limit_order_book[i].orders)):
                if abs(limit_order_book[i].orders[j].volume) >= market_buy:
                    limit_order_book[i].orders[j].volume += market_buy
                else:
                    market_buy -= abs(limit_order_book[i].orders[j].volume)
                    limit_order_book[i].orders[j].volume = 0
        for i in range(a, 0, -1):
            for j in range(len(limit_order_book[i].orders)):
                if limit_order_book[i].orders[j].volume >= market_sell:
                    limit_order_book[i].orders[j].volume -= market_sell
                else:
                    market_sell -= limit_order_book[i].orders[j].volume
                    limit_order_book[i].orders[j].volume = 0
        for i in range(b, size):
            if i == b and limit_order_book[i].order_sum() == 0 and b != size:
                b += 1
        for i in range(a, 0, -1):
            if i == a and limit_order_book[i].order_sum() == 0 and a != 0:
                a -= 1
        for i in range(size):
            v += abs(limit_order_book[i].order_sum())
        t += DT
        middle_prices.append(m)
        total_volume.append(v)
    return middle_prices, total_volume


total_volume1 = simulate_model(1, 1, 1, 1000, create_order_queue(100))[1]

total_volume2 = simulate_model(1, 0.1, 1, 1000, create_order_queue(100))[1]

total_volume3 = simulate_model(0.1, 1, 1, 1000, create_order_queue(100))[1]

plt.plot(total_volume1, 'blue')

plt.plot(total_volume2, 'green')

plt.plot(total_volume3, 'red')


plt.savefig("file.png")
