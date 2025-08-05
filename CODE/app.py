from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import pickle
import joblib

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Load the Model and Scaler
model = pickle.load(open('model.pkl', 'rb'))
scaler = joblib.load('scaler.pkl')

# User Database Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    mobile = db.Column(db.String(15), nullable=False)

# Home Page (Register Page)
@app.route('/')
def home():
    return render_template('register.html')

# Register Route
@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    age = request.form['age']
    email = request.form['email']
    password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
    gender = request.form['gender']
    mobile = request.form['mobile']

    new_user = User(name=name, age=age, email=email, password=password, gender=gender, mobile=mobile)
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('login'))

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('index'))
        else:
            return 'Invalid Credentials'
    return render_template('login.html')

# Dashboard (Index Page)
@app.route('/index')
def index():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return render_template('index.html', user_name=user.name)
    return redirect(url_for('login'))

# Prediction Route
@app.route('/predict', methods=['POST'])
def predict():
    if 'user_id' in session:
        input_data = [float(request.form[key]) for key in request.form.keys()]

        # Scaling Input Data
        scaled_data = scaler.transform([input_data])

        # Prediction
        prediction = model.predict(scaled_data)
        result = "Parkinson's Detected" if prediction[0] == 1 else "No Parkinson's Detected"

        return render_template('result.html', prediction=result, user_input=request.form)

    return redirect(url_for('login'))

# Logout Route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
