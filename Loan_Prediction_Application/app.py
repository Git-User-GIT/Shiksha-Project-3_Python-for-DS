from flask import Flask, render_template, request, redirect, session
import mysql.connector
import pickle
import numpy as np

app = Flask(__name__)
app.secret_key = "secret_key"

# Load the ML model
with open('loan_model.pkl', 'rb') as file:
    model = pickle.load(file)

# Connect to MySQL database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="12345678",
    database="loginCredentials"
)
cursor = db.cursor()

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        db.commit()
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        if user:
            session['user'] = username
            return redirect('/predict')
        return "Invalid credentials"
    return render_template('login.html')

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if 'user' not in session:
        return redirect('/login')
    if request.method == 'POST':
        # Map string inputs to numeric values
        gender = 1 if request.form['gender'].lower() == 'male' else 0
        married = 1 if request.form['married'].lower() == 'yes' else 0
        education = 1 if request.form['education'].lower() == 'graduate' else 0
        self_employed = 1 if request.form['self_employed'].lower() == 'yes' else 0
        property_area_map = {'urban': 2, 'semiurban': 1, 'rural': 0}
        property_area = property_area_map[request.form['property_area'].lower()]

        # Collect remaining numeric inputs
        dependents = int(request.form['dependents'])
        applicant_income = float(request.form['applicant_income'])
        coapplicant_income = float(request.form['coapplicant_income'])
        loan_amount = float(request.form['loan_amount'])
        loan_term = float(request.form['loan_amount_term'])
        credit_history = int(request.form['credit_history'])

        # Create the feature array
        data = [
            gender, married, dependents, education, self_employed,
            applicant_income, coapplicant_income, loan_amount,
            loan_term, credit_history, property_area
        ]

        # Predict loan eligibility
        prediction = model.predict([data])[0]
        result = "Congrats!! you are Eligible for the loan" if prediction == 1 else "Sorry Not Eligible"

        # Render the result page
        return render_template('predict.html', result=result, data=request.form)
    return render_template('predict.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
