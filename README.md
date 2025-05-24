SMART EXPENSE TRACKER

💸 Smart Expense Tracker
A smart, AI-powered expense tracking web application built with Flask, HTML/CSS/JS, and SQLAlchemy. It helps users manage their personal finances effortlessly with intelligent categorization, budget prediction, and insightful visual reports.

🚀 Features
🔐 User Authentication

Secure login system with session management

Random secret key for each session

📥 Expense Import

Upload transactions from CSV, PDF, OFX, and QIF files

Automatic parsing and data extraction into structured format

🧠 AI-Powered Categorization

Automatically categorize expenses using machine learning models

📊 Smart Analytics & Insights

View category-wise spending

Track monthly trends and spending patterns

📈 Budget Prediction

Predict monthly budget based on historical expenses and income

Real-time alerts when approaching budget limits

➕ Manage Expenses

Add, view, and delete transactions manually

Set and update budget goals

📄 Report Generation

Generate and export expense reports in readable formats

🛠️ Tech Stack
Frontend: HTML, CSS, JavaScript, Bootstrap

Backend: Python, Flask, SQLAlchemy

Database: SQLite

AI/ML: scikit-learn (for categorization & prediction)

📦 Installation
bash
Copy
Edit
git clone https://github.com/your-username/smart-expense-tracker.git
cd smart-expense-tracker
pip install -r requirements.txt
python app.py
Visit http://127.0.0.1:5000 in your browser.

📌 Project Structure
smart-expense-tracker/
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   └── import.html
├── static/
│   └── styles.css
├── models.py
├── app.py
├── utils/
│   ├── categorizer.py
│   └── extractor.py
├── requirements.txt
└── README.md

