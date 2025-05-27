import io
import joblib
expense_model=joblib.load('expense_categorizer_logistic.pkl')
print("Model loaded successfully")
import re
import pandas as pd
import pdfplumber
import ofxparse
from ofxparse import OfxParser
from werkzeug.utils import secure_filename
from collections import defaultdict
from datetime import datetime
from dateutil.parser import parse
from dateutil import parser
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import csv
from io import StringIO, BytesIO
import PyPDF2
from functools import wraps
import numpy as np

app = Flask(__name__,static_url_path='/static')

model_path = os.path.join(os.path.dirname(__file__), 'budget_prediction_rf_model.pkl')
model = joblib.load(model_path)

app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expense_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'


os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    expenses = db.relationship('Expense', backref='user', lazy=True)
    budgets = db.relationship('Budget', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    payment_method = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'amount': self.amount,
            'category': self.category,
            'description': self.description,
            'date': self.date.isoformat(),
            'payment_method': self.payment_method,
            'user_id': self.user_id
        }

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    period = db.Column(db.String(20))  
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'category': self.category,
            'amount': self.amount,
            'period': self.period,
            'user_id': self.user_id
        }


with app.app_context():
    db.create_all()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

def model_list_to_dict(model_list):
    return [item.to_dict() for item in model_list]


@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid email or password', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))
        
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    today = datetime.now()
    start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    
    recent_expenses = Expense.query.filter_by(user_id=user_id)\
        .order_by(Expense.date.desc()).limit(5).all()
    
    
    monthly_expenses = Expense.query.filter(
    Expense.user_id == user_id,
    Expense.date >= start_of_month,
    Expense.date <= today
    ).order_by(Expense.date.desc()).all()

    
    total_spent = sum(expense.amount for expense in monthly_expenses)
    
    
    budgets = Budget.query.filter_by(user_id=user_id).all()
    
    
    categories = {}
    for expense in monthly_expenses:
        if expense.category in categories:
            categories[expense.category] += expense.amount
        else:
            categories[expense.category] = expense.amount
    
    return render_template('dashboard.html',
                        recent_expenses=model_list_to_dict(recent_expenses),
                        total_spent=total_spent,
                        budgets=model_list_to_dict(budgets),
                        categories=categories)

@app.route('/add_expense', methods=['GET', 'POST'])
@login_required
def add_expense():
    if request.method == 'POST':
        try:
            amount = float(request.form['amount'])
            description = request.form.get('description', '')
            payment_method = request.form.get('payment_method', 'cash')
            date_str = request.form.get('date')
            
            
            category = request.form.get('category', '').strip()
            if not category:
               
                predicted_category = expense_model.predict([description])  
                category = predicted_category[0]  # 

            
            date = datetime.strptime(date_str, '%Y-%m-%d') if date_str else datetime.utcnow()

            
            new_expense = Expense(
                amount=amount,
                category=category,
                description=description,
                payment_method=payment_method,
                date=date,
                user_id=session['user_id']
            )
            
            db.session.add(new_expense)
            db.session.commit()
            
            flash('Expense added successfully!', 'success')
            return redirect(url_for('dashboard'))
        
        except ValueError:
            flash('Invalid amount entered', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding expense: {str(e)}', 'danger')
    
    return render_template('add_expense.html', today=datetime.utcnow().strftime('%Y-%m-%d'))

ALLOWED_EXTENSIONS = {'csv', 'pdf', 'ofx', 'qif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/import-transactions', methods=['GET', 'POST'])
@login_required
def import_transactions():
    if request.method == 'POST':
        if 'transaction_file' not in request.files:
            flash('No file selected', 'danger')
            return redirect(request.url)

        file = request.files['transaction_file']
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash('Allowed formats: CSV, PDF, OFX, QIF', 'danger')
            return redirect(request.url)

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            user_id = session['user_id']
            transactions = []

            if filename.endswith('.csv'):
                transactions = process_csv(filepath)
            elif filename.endswith('.pdf'):
                transactions = process_pdf(filepath)
            elif filename.endswith(('.ofx', '.qif')):
                transactions = process_bank_statement(filepath)
            
            print(f"\nExtracted {len(transactions)} transactions from {filename}:\n")
            for txn in transactions:
                print(txn)
 
            for txn in transactions:
                if 'date' in txn and 'amount' in txn and 'description' in txn:
                    expense = Expense(
                        amount=txn['amount'],
                        description=txn['description'],
                        date=txn['date'],
                        category=txn.get('category', 'Uncategorized'),
                        payment_method=txn.get('payment_method', 'Other'),
                        user_id=user_id
                    )
                    db.session.add(expense)

            db.session.commit()
            flash(f'Successfully imported {len(transactions)} transactions', 'success')
            return redirect(url_for('view_expenses'))

        except Exception as e:
            db.session.rollback()
            flash(f'Import failed: {str(e)}', 'danger')
            return redirect(request.url)

    return render_template('import_transactions.html')

def process_csv(filepath):
    transactions = []
    try:
        with open(filepath, newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row_num, row in enumerate(reader, 1):
                try:
                    row = {k.strip().lower(): v for k, v in row.items()}
                    if not all(key in row for key in ['date', 'description', 'amount']):
                        raise ValueError("Missing required columns (Date, Description, Amount)")

                    try:
                        parsed_date = parser.parse(row['date'].strip()).date()
                    except Exception:
                        raise ValueError(f"Unrecognized date format in row {row_num}")


                    amount_str = str(row['amount']).replace('$', '').replace(',', '').strip()
                    amount = abs(float(amount_str))

                    description = row['description'].strip()

                    
                    raw_category = row.get('category', '').strip()
                    if raw_category:
                        category = raw_category
                    else:
                        category = expense_model.predict([description])[0]

                    transactions.append({
                        'date': parsed_date,
                        'description': description,
                        'amount': amount,
                        'category': category,
                        'payment_method': row.get('payment_method', 'Other').strip()
                    })

                except Exception as e:
                    flash(f"Row {row_num} skipped: {str(e)}", "warning")
                    continue

    except Exception as e:
        raise ValueError(f"CSV processing error: {str(e)}")

    if not transactions:
        raise ValueError("No valid transactions found in file")

    return transactions


def process_pdf(filepath):
    transactions = []
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            for line in text.split('\n'):
                pattern = r'(\d{2}/\d{2}/\d{4})\s+(.*?)\s+(-?\$?\d*\.\d{2})'
                match = re.search(pattern, line)
                if match:
                    date_str, desc, amount_str = match.groups()
                    try:
                        parsed_date = None
                        for fmt in ['%d/%m/%Y', '%m/%d/%Y']:
                            try:
                                parsed_date = datetime.strptime(date_str, fmt).date()
                                break
                            except ValueError:
                                continue
                        if not parsed_date:
                            continue

                        amount = abs(float(amount_str.replace('$', '').replace(',', '').strip()))
                        category=expense_model.predict([desc.strip()])[0]
                        transactions.append({
                            'date': parsed_date,
                            'description': desc.strip(),
                            'amount': amount,
                            'category':category
                        })
                    except:
                        continue
    return transactions

def process_bank_statement(filepath):
    transactions = []
    if filepath.endswith('.ofx'):
        with open(filepath) as f:
            ofx = OfxParser.parse(f)
            for txn in ofx.account.statement.transactions:
                transactions.append({
                    'date': txn.date.date(),
                    'description': txn.payee,
                    'amount': abs(float(txn.amount)),
                    'type': txn.type
                })
    elif filepath.endswith('.qif'):
        with open(filepath) as f:
            current_txn = {}
            for line in f:
                if line.startswith('D'):  
                    for fmt in ['%Y-%m-%d', '%m/%d/%y', '%d/%m/%y']:
                        try:
                            current_txn['date'] = datetime.strptime(line[1:].strip(), fmt).date()
                            break
                        except ValueError:
                            continue
                elif line.startswith('T'):  
                    try:
                        amount_str = line[1:].replace('$', '').replace(',', '').strip()
                        current_txn['amount'] = abs(float(amount_str))
                    except:
                        continue
                elif line.startswith('P'):  
                    current_txn['description'] = line[1:].strip()
                elif line.startswith('^'):  
                    if 'date' in current_txn and 'amount' in current_txn and 'description' in current_txn:
                        transactions.append(current_txn)
                    current_txn = {}
    return transactions

@app.route('/expenses')
@login_required
def view_expenses():
    expenses = Expense.query.filter_by(user_id=session['user_id'])\
        .order_by(Expense.date.desc()).all()
    return render_template('view_expenses.html', expenses=model_list_to_dict(expenses))

@app.route('/edit_expense/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_expense(id):
    expense = Expense.query.get_or_404(id)
    if expense.user_id != session['user_id']:
        flash('Unauthorized action', 'danger')
        return redirect(url_for('view_expenses'))

    if request.method == 'POST':
        try:
            expense.amount = float(request.form['amount'])
            expense.category = request.form['category']
            expense.description = request.form.get('description', '')
            expense.payment_method = request.form.get('payment_method', 'cash')
            date_str = request.form.get('date')
            
            if date_str:
                expense.date = datetime.strptime(date_str, '%Y-%m-%d')
            
            db.session.commit()
            flash('Expense updated successfully!', 'success')
            return redirect(url_for('view_expenses'))
        
        except ValueError:
            flash('Invalid amount entered', 'danger')
        except Exception as e:
            db.session.rollback()
            flash('Error updating expense: ' + str(e), 'danger')

    return render_template('edit_expense.html', 
                         expense=expense.to_dict(),
                         today=datetime.utcnow().strftime('%Y-%m-%d'))

@app.route('/delete_expense/<int:id>')
@login_required
def delete_expense(id):
    expense = Expense.query.get_or_404(id)
    if expense.user_id != session['user_id']:
        flash('Unauthorized action', 'danger')
        return redirect(url_for('view_expenses'))
    
    db.session.delete(expense)
    db.session.commit()
    flash('Expense deleted successfully', 'success')
    return redirect(url_for('view_expenses'))



@app.route('/budgets', methods=['GET', 'POST'])
@login_required
def manage_budgets():
    user_id = session['user_id']
    
    if request.method == 'POST':
        try:
            category = request.form['category']
            amount = float(request.form['amount'])
            period = request.form['period']
            
            existing_budget = Budget.query.filter_by(
                user_id=user_id,
                category=category
            ).first()
            
            if existing_budget:
                existing_budget.amount = amount
                existing_budget.period = period
            else:
                new_budget = Budget(
                    category=category,
                    amount=amount,
                    period=period,
                    user_id=user_id
                )
                db.session.add(new_budget)
            
            db.session.commit()
            flash('Budget updated successfully!', 'success')
        
        except ValueError:
            flash('Invalid amount entered', 'danger')
        except Exception as e:
            db.session.rollback()
            flash('Error updating budget: ' + str(e), 'danger')
    
    budgets = Budget.query.filter_by(user_id=user_id).all()
    return render_template('budgets.html', budgets=model_list_to_dict(budgets))

@app.route('/delete_budget/<int:id>')
@login_required
def delete_budget(id):
    budget = Budget.query.get_or_404(id)
    if budget.user_id != session['user_id']:
        flash('Unauthorized action', 'danger')
        return redirect(url_for('manage_budgets'))
    
    db.session.delete(budget)
    db.session.commit()
    flash('Budget deleted successfully', 'success')
    return redirect(url_for('manage_budgets'))

@app.route('/reports')
def reports():
    user_id = session.get("user_id")
    expenses = Expense.query.filter_by(user_id=user_id).all()
    budgets = Budget.query.filter_by(user_id=user_id).all()

    
    categories = defaultdict(float)
    monthly_spending = defaultdict(float)

    for expense in expenses:
        categories[expense.category] += expense.amount
        
        month_label = expense.date.strftime("%b")  
        monthly_spending[month_label] += expense.amount

    
    month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul',
                   'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    sorted_labels = [m for m in month_order if m in monthly_spending]
    sorted_data = [monthly_spending[m] for m in sorted_labels]

    total_spent = sum(categories.values())

    budget_dicts = [
        {
            "category": budget.category,
            "amount": budget.amount,
            "period": budget.period
        } for budget in budgets
    ]

    return render_template(
        "reports.html",
        categories=categories,
        total_spent=total_spent,
        budgets=budget_dicts,
        monthly_labels=sorted_labels,
        monthly_data=sorted_data
    )

@app.route('/budget-prediction')
def budget_prediction():
    """Render the budget prediction page"""
    return render_template('budget_prediction.html')

@app.route('/api/predict-budget', methods=['POST'])
def predict_budget():
    """API endpoint for making predictions"""
    try:
        data = request.get_json()
        
        
        if not data or 'last_month_expense' not in data or 'current_income' not in data:
            return jsonify({'error': 'Missing required fields'}), 400
            
        last_month_expense = float(data['last_month_expense'])
        current_income = float(data['current_income'])
        
        if last_month_expense < 0 or current_income < 0:
            return jsonify({'error': 'Values must be positive'}), 400
        
        
        features = np.array([[last_month_expense, current_income]])
        
        
        prediction = model.predict(features)[0]
        
        
        prediction = max(100, min(prediction, current_income * 1.1))
        
        
        confidence = min(95, 70 + abs(current_income - last_month_expense) / current_income * 25)
        
        return jsonify({
            'prediction': round(float(prediction), 2),
            'confidence': round(confidence, 1),
            'status': 'success'
        })
        
    except ValueError:
        return jsonify({'error': 'Invalid input values'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/export_csv')
@login_required
def export_csv():
    user_id = session['user_id']
    expenses = Expense.query.filter_by(user_id=user_id).order_by(Expense.date.desc()).all()
    
    
    si = StringIO()
    cw = csv.writer(si)
    
    
    cw.writerow(['Date', 'Category', 'Description', 'Payment Method', 'Amount'])
    
    
    for expense in expenses:
        cw.writerow([
            expense.date.strftime('%Y-%m-%d'),
            expense.category,
            expense.description,
            expense.payment_method,
            expense.amount
        ])
    
    
    mem = BytesIO()
    mem.write(si.getvalue().encode('utf-8'))
    mem.seek(0)
    si.close()

    
    return send_file(
        mem,
        mimetype='text/csv',
        as_attachment=True,
        download_name='expenses.csv'
    )

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = get_current_user()
    
    if request.method == 'POST':
        try:
            user.username = request.form['username']
            user.email = request.form['email']
            
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            
            if current_password and new_password:
                if user.check_password(current_password):
                    user.set_password(new_password)
                    flash('Password changed successfully', 'success')
                else:
                    flash('Current password is incorrect', 'danger')
                    return redirect(url_for('profile'))
            
            db.session.commit()
            flash('Profile updated successfully', 'success')
            return redirect(url_for('profile'))
        
        except Exception as e:
            db.session.rollback()
            flash('Error updating profile: ' + str(e), 'danger')
    
    return render_template('profile.html', user=user.to_dict())


@app.route('/api/expenses')
@login_required
def api_expenses():
    expenses = Expense.query.filter_by(user_id=session['user_id'])\
        .order_by(Expense.date.desc()).all()
    return jsonify(model_list_to_dict(expenses))

@app.route('/api/expenses_by_category')
@login_required
def api_expenses_by_category():
    expenses = Expense.query.filter_by(user_id=session['user_id']).all()
    
    categories = {}
    for expense in expenses:
        if expense.category in categories:
            categories[expense.category] += expense.amount
        else:
            categories[expense.category] = expense.amount
    
    return jsonify(categories)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv', 'pdf'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == '__main__':
    app.run(debug=True)