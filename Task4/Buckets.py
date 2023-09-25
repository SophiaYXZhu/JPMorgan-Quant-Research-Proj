import pandas as pd
import numpy as np

class Quantization:
    def __init__(self, n):
        self.n = n
        self.buckets = None
        self.labels = None

    def fit(self, data, labels):
        self.data = data
        self.labels = labels
        self.num_samples = len(data)
        self.bucket_sizes = [self.num_samples // self.n] * self.n
        self.buckets = self.initialize_buckets()
        self.dynamic_programming()

    def initialize_buckets(self):
        bucket_boundaries = []
        start = 0
        for size in self.bucket_sizes:
            end = start + size
            bucket_boundaries.append((start, end))
            start = end
        return bucket_boundaries

    def log_likelihood(self):
        likelihood = 0
        for bucket in self.buckets:
            start, end = bucket
            num_ones = np.sum(self.labels[start:end])
            num_zeros = end - start - num_ones
            p_i = num_ones / (end - start)
            likelihood += num_ones * np.log(p_i) + num_zeros * np.log(1 - p_i)
        return likelihood

    def dynamic_programming(self):
        for _ in range(100):  # Maximum iterations
            new_buckets = self.buckets.copy()
            for i in range(1, self.n):
                new_boundary = (self.buckets[i - 1][1] + self.buckets[i][0]) / 2
                new_buckets[i] = (new_buckets[i][0], new_boundary)
                new_buckets[i - 1] = (new_boundary, new_buckets[i - 1][1])
            if new_buckets == self.buckets:
                break  # Converged
            self.buckets = new_buckets

    def quantize(self):
        quantized_data = np.zeros(self.num_samples)
        for i, bucket in enumerate(self.buckets):
            end, start = bucket
            quantized_data[round(start):round(end)] = self.n - i
        return quantized_data


if __name__ == "__main__":
    df = pd.read_csv('./Task 3 and 4_Loan_Data.csv')
    FICO = df['fico_score'].tolist()
    defaults = df['default'].tolist()

    n_buckets = int(input())

    quantizer = Quantization(n_buckets)
    quantizer.fit(np.array(FICO), np.array(defaults))
    quantized_data = quantizer.quantize()
    print("Quantized Data:",quantized_data)