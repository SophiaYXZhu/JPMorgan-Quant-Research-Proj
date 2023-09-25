import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from collections import OrderedDict

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
        (self.a, self.b, self.c, self.d, self.e), _ = curve_fit(func, self.df['Times'], self.df['Prices'], p0=[0.6, 2*np.pi/365, 0.0012742786560679608, 10.292177276615813, 0], maxfev = 2000)

    def fit(self, time):
        return self.a * np.sin(self.b * time + self.e)+ self.c * time + self.d

class ContractValue:
    def __init__(self, model: Extropolate):
        self.model = model
        self.model.extropolate()
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
    
    def get_value(self, inject_dates, withdraw_dates, set_amount, rate, volume, costs):
        profit = 0
        cost = 0
        curr_volume = 0
        times = OrderedDict()
        for date in inject_dates:
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
            if times.get(val):
                times[val].append(1)
            else:
                times[val] = [1]
        for date in withdraw_dates:
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
            if times.get(val):
                times[val].append(0)
            else:
                times[val] = [0]
        # 1 represented an injection and 0 represents a withdrawal
        # times = OrderedDict(sorted(times.items(), key=lambda x: x[0]))
        times = sorted(times.items(), key=lambda x: x[0])
        for i, (time, types) in enumerate(times):
            cost += (time-times[i-1][0])//30 * costs # costs = cost of storage / month
            if 1 in types: # injection
                if curr_volume + set_amount <= volume:
                    curr_volume += set_amount
                else:
                    curr_volume = volume
                cost += self.model.fit(time) * set_amount # purchase costs
                cost += set_amount * rate # injection costs (rate = cost / million units of natural gas)
            if 0 in types: # withdrawal
                if curr_volume - set_amount >= 0:
                    curr_volume -= set_amount
                else:
                    curr_volume = 0
                profit += self.model.fit(time) * set_amount # selling profits
        return profit - cost


if __name__ == '__main__':
    model = Extropolate()
    inject_dates = input('Enter injection dates (e.g., 10/31/2020, 08/10/2021, 05/11/2023): ').split(',')
    withdraw_dates = input('Enter withdrawal dates (e.g., 11/21/2021, 09/05/2022, 04/23/2023): ').split(',')
    set_amount = float(input('Enter the set amount injected/withdrawn each time: '))
    rate = float(input('Enter the rate of injection/withdrawal: '))
    volume = float(input('Enter the maximum volume of storage: '))
    costs = float(input('Enter the costs of storage: '))

    cv = ContractValue(model)
    print(cv.get_value(inject_dates, withdraw_dates, set_amount, rate, volume, costs)) # in millions of units of natural gas