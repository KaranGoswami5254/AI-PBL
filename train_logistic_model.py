import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.metrics import classification_report
import joblib

def train_expense_model_logistic():
    
    data = pd.read_csv('expense_dataset2.csv')
    data.dropna(inplace=True)

    
    X = data['description']
    y = data['category']
    
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    
    model = make_pipeline(
        TfidfVectorizer(),
        LogisticRegression(max_iter=1000)  
    )

    
    model.fit(X_train, y_train)

    
    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred))

    
    joblib.dump(model, 'expense_categorizer_logistic.pkl')
    print("✅ Logistic Regression model saved as 'expense_categorizer_logistic.pkl'")

if __name__ == "__main__":
    train_expense_model_logistic()
