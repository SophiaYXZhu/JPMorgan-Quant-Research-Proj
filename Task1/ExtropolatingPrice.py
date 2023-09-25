import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

class Extropolate:
    def __init__(self, file_name = './Nat_Gas.csv'):
        self.months_normal = {
            1: 31,
            2: 28,
            3: 31,
            4: 30,
            5: 31,
            6: 30,
            7: 31,
            8: 31,
            9: 30,
            10: 31,
            11: 30,
            12: 31
        }
        self.months_leap = {
            1: 31,
            2: 29,
            3: 31,
            4: 30,
            5: 31,
            6: 30,
            7: 31,
            8: 31,
            9: 30,
            10: 31,
            11: 30,
            12: 31
        }
        df =  pd.read_csv('./Nat_Gas.csv')
        self.dates = df["Dates"].tolist()
        times = []
        # 10/31/2020
        for date in self.dates:
            [mm, dd, yy] = [int(i) for i in date.split('/')]
            val = 0
            if yy > 20:
                year = yy-1
                while year > 20:
                    month = 12
                    while month > 0:
                        if year%4 == 0:
                            val += self.months_leap[month]
                        else:
                            val += self.months_normal[month]
                        month -= 1
                    year -= 1
                if year % 4 == 0:
                    for month in range(1,mm):
                        val += self.months_leap[month]
                else:
                    for month in range(1,mm):
                        val += self.months_normal[month]
                val += dd
                val += 61
            if yy == 20:
                month = mm -1
                if mm > 10:
                    while month > 10:
                        val += self.months_leap[month]
                        month -= 1
                    val += dd
                else:
                    val = 0
            times.append(val)
        self.df = pd.DataFrame({
            "Times": times,
            "Prices": df['Prices']
        })

    def extropolate(self):
        def func(x, a, b, c, d, e):
            return a * np.sin(b * x + e) + c * x + d
        plt.plot(self.df['Times'], self.df['Prices'])
        (self.a, self.b, self.c, self.d, self.e), _ = curve_fit(func, self.df['Times'], self.df['Prices'], p0=[0.6, 2*np.pi/365, 0.0012742786560679608, 10.292177276615813, 0], maxfev = 2000)
        plt.plot(self.df['Times'], self.a * np.sin(self.b * self.df['Times'] + self.e)+ self.c * self.df['Times'] + self.d)
        plt.show()
        
    def fit(self, date):
        [mm, dd, yy] = [int(i) for i in date.split('/')]
        time = 0
        if yy > 20:
            year = yy-1
            while year > 20:
                month = 12
                while month > 0:
                    if year%4 == 0:
                        time += self.months_leap[month]
                    else:
                        time += self.months_normal[month]
                    month -= 1
                year -= 1
            if year % 4 == 0:
                for month in range(1,mm):
                    time += self.months_leap[month]
            else:
                for month in range(1,mm):
                    time += self.months_normal[month]
            time += dd
            time += 61
        if yy == 20:
            month = mm -1
            if mm > 10:
                while month > 10:
                    time += self.months_leap[month]
                    month -= 1
                time += dd
            else:
                time = 0
        return  self.a * np.sin(self.b * time + self.e)+ self.c * time + self.d

date = input()
model = Extropolate()
model.extropolate()
print(model.fit(date))