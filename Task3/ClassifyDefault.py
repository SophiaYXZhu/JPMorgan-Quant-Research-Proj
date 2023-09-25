import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

class DecisionTreeClassifierWrapper:
    def __init__(self, df, target_col):
        self.df = df
        self.target_col = target_col
        self.X = df.drop(target_col, axis=1)
        self.y = df[target_col]
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(self.X, self.y, test_size=0.2, random_state=42)
        self.tree_model = None

    def fit_model(self, max_depth=None, min_samples_split=2, min_samples_leaf=1):
        self.tree_model = DecisionTreeClassifier(max_depth=max_depth, min_samples_split=min_samples_split, min_samples_leaf=min_samples_leaf)
        self.tree_model.fit(self.X_train, self.y_train)

    def evaluate_model(self):
        y_train_pred = self.tree_model.predict(self.X_train)
        y_test_pred = self.tree_model.predict(self.X_test)
        train_accuracy = accuracy_score(self.y_train, y_train_pred)
        test_accuracy = accuracy_score(self.y_test, y_test_pred)

        print("Train Accuracy:", train_accuracy)
        print("Test Accuracy:", test_accuracy)
        print("\nClassification Report on Test Data:\n")
        print(classification_report(self.y_test, y_test_pred))
    
    def fit_single_data(self, data):
        return self.tree_model.predict(data)

if __name__ == "__main__":
    df = pd.read_csv('./Task 3 and 4_Loan_Data.csv')
    df = df.drop('customer_id', axis=1)
    decision_tree_classifier = DecisionTreeClassifierWrapper(df, 'default')
    decision_tree_classifier.fit_model(max_depth=None, min_samples_split=2, min_samples_leaf=1)
    decision_tree_classifier.evaluate_model()

    data_point = np.array([
                    int(input('credit_lines_outstanding: ')),
                    float(input('loan_amt_outstanding: ')),
                    float(input('total_debt_outstanding: ')),
                    float(input('income: ')),
                    int(input('years_employed: ')),
                    int(input('fico_score: '))
                    ]).reshape(1, -1)
    print(decision_tree_classifier.fit_single_data(data_point))

