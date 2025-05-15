import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import joblib
import numpy as np


data = pd.read_csv('large_expenses_data.csv')


X = data[['Previous_Month_Expense', 'Income']]
y = data['Next_Month_Budget']


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Step 4: Initialize the Random Forest Regressor
model = RandomForestRegressor(
    n_estimators=100,       # number of trees
    max_depth=10,           # control overfitting
    random_state=42
)


model.fit(X_train, y_train)


y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)

print(f"Mean Squared Error: {mse:.2f}")
print(f"Root Mean Squared Error: {rmse:.2f}")


joblib.dump(model, 'budget_prediction_rf_model.pkl')

print("Random Forest model trained and saved successfully.")
