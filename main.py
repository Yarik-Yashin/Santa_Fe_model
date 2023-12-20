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


def count_middle_prices(lambda_, nu_, mu_, t_max, limit_order_book):
    t = 0
    a = 0
    b = 100
    middle_prices = list()
    while t < t_max:
        m = (a + b) / 2

        for i in range(max(int(m) - spread * 5, 0), min(int(m) + spread * 5, 100)):
            la = value_of_poisson(lambda_, 10)
            for j in range(la):
                v = value_of_poisson(lambda_ / nu_, 10) + 1
                if i <= m:
                    limit_order_book[i].add_order(Order(v, t))
                    a = i if a <= i else a
                else:
                    limit_order_book[i].add_order((Order(-v, t)))
                    b = i if b >= i else b

        for i in range(50 - spread * 5, 50 + spread * 5):
            for_delete = list()
            for j in range(len(limit_order_book[i].orders)):
                nu = value_of_poisson(nu_, 1)
                if nu:
                    for_delete.append(j)
            for j in for_delete[::-1]:
                limit_order_book[i].cancel_order(j)
        market_sell = value_of_poisson(mu_, 10)
        market_buy = value_of_poisson(mu_, 10)
        for i in range(b, 100):
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
        for i in range(b, 100):
            if i == b and limit_order_book[i].order_sum() == 0 and b != 100:
                b += 1
        for i in range(a, 0, -1):
            if i == a and limit_order_book[i].order_sum() == 0 and a != 0:
                a -= 1
        t += DT
        middle_prices.append(m)
    return middle_prices


middle_prices_1 = count_middle_prices(1, 1, 1, 10000, create_order_queue(100))
sigma_tau_1 = []
for tau in range(1, 1000):
    middle_prices_tau = [middle_prices_1[i] for i in range(len(middle_prices_1)) if i % tau == 0]
    returns_tau = [(middle_prices_tau[i] - middle_prices_tau[i - 1]) / middle_prices_tau[i - 1] for i in
                   range(1, len(middle_prices_tau))]
    sigma_tau_1.append(np.std(np.array(returns_tau)) / sqrt(tau))

plt.plot(sigma_tau_1, 'red')

middle_prices_2 = count_middle_prices(1, 0.01, 1, 10000, create_order_queue(100))
sigma_tau_2 = []
for tau in range(1, 1000):
    middle_prices_tau = [middle_prices_2[i] for i in range(len(middle_prices_2)) if i % tau == 0]
    returns_tau = [(middle_prices_tau[i] - middle_prices_tau[i - 1]) / middle_prices_tau[i - 1] for i in
                   range(1, len(middle_prices_tau))]
    sigma_tau_2.append(np.std(np.array(returns_tau)) / sqrt(tau))
plt.plot(sigma_tau_2, 'green')

middle_prices_3 = count_middle_prices(1, 0.1, 0.1, 10000, create_order_queue(100))
sigma_tau_3 = []
for tau in range(1, 1000):
    middle_prices_tau = [middle_prices_3[i] for i in range(len(middle_prices_3)) if i % tau == 0]
    returns_tau = [(middle_prices_tau[i] - middle_prices_tau[i - 1]) / middle_prices_tau[i - 1] for i in
                   range(1, len(middle_prices_tau))]
    sigma_tau_3.append(np.std(np.array(returns_tau)) / sqrt(tau))

plt.plot(sigma_tau_3, 'blue')

plt.loglog()
plt.savefig("file.png")
