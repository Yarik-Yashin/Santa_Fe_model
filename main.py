import random
import math
import matplotlib.pyplot as plt
from celluloid import Camera

NU = 0.012
MU = 7
LAMBDA = 0.222
t = 0
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


pl = plt.figure()
camera = Camera(pl)
limit_order_book = [OrderQueue(i) for i in range(100)]
a = 0
b = 100
while t < 100:
    m = (a + b) / 2

    for i in range(max(int(m) - spread * 5, 0), min(int(m) + spread * 5, 100)):
        la = value_of_poisson(LAMBDA, 10)
        for j in range(la):
            v = value_of_poisson(LAMBDA / NU, 10) + 1
            if i <= m:
                limit_order_book[i].add_order(Order(v, t))
                a = i if a <= i else a
            else:
                limit_order_book[i].add_order((Order(-v, t)))
                b = i if b >= i else b

    for i in range(50 - spread * 5, 50 + spread * 5):
        for_delete = list()
        for j in range(len(limit_order_book[i].orders)):
            nu = value_of_poisson(NU, 1)
            if nu:
                for_delete.append(j)
        for j in for_delete[::-1]:
            limit_order_book[i].cancel_order(j)
    market_sell = value_of_poisson(MU, 10)
    market_buy = value_of_poisson(MU, 10)
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
    pl = [i.order_sum() for i in limit_order_book]
    plt.bar([k for k in range(100)], pl, color='b')
    plt.text(0, 0, f"Mid price = {m}")
    camera.snap()
animation = camera.animate()
animation.save('celluloid_minimal.gif', writer='Pillow')
