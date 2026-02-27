import os
import sqlite3
import random
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from sklearn.ensemble import RandomForestRegressor

app = Flask(__name__)
app.secret_key = 'smart-breathe-super-secret'

DATABASE = 'smartbreathe.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                name TEXT NOT NULL
            )
        ''')
        db.commit()

# ========================================
# AI ARCHITECTURE CONCEPT (Code Comments Only)
# ========================================
#
# 1) Edge AI Processing on Wearable Device:
# Wearable devices process raw biomarker telemetry (e.g. acoustic cough patterns)
# locally using tinyML to preserve battery and privacy. Only aggregated anomaly
# scores (e.g., airway resistance delta) are transmitted to the main system.
#
# 2) Federated Learning Approach:
# We maintain a privacy-preserving global training model where local RF models
# are trained on user's private devices. Only model weights are parametrically
# shared back to the central server to improve global respiratory anomaly detection
# without exposing personal health data.
#
# 3) Explainable AI (XAI) Layer:
# The system utilizes SHAP (SHapley Additive exPlanations) values internally to
# determine top contributing factors for a high risk. This provides transparency
# to the user, e.g., "Your risk is Critical due to highly fluctuating SpO2."

# Train a dummy RF model for AQI prediction
X_dummy = pd.DataFrame([{
    'microsensor_aqi': random.randint(30, 150),
    'satellite_aod': random.uniform(0.1, 0.8),
    'humidity': random.randint(30, 90),
    'temperature': random.randint(10, 35),
    'traffic_density': random.uniform(0.1, 1.0),
    'urban_topology': random.uniform(0.8, 1.2)
} for _ in range(100)])
y_dummy = X_dummy['microsensor_aqi'] * X_dummy['satellite_aod'] * X_dummy['traffic_density']

rf_model = RandomForestRegressor(n_estimators=10, random_state=42)
rf_model.fit(X_dummy, y_dummy)

def generate_environmental_inputs():
    """Simulates Environmental Intelligence Module"""
    return {
        'microsensor_aqi': random.randint(40, 180),
        'satellite_aod': round(random.uniform(0.2, 0.9), 2),
        'humidity': random.randint(40, 85),
        'temperature': random.randint(15, 32),
        'traffic_density': round(random.uniform(0.2, 0.9), 2),
        'urban_topology': round(random.uniform(0.9, 1.3), 2)
    }

def generate_biometrics():
    """Simulates Wearable Respiratory Biomarker Module"""
    return {
        'breathing_rate_variability': round(random.uniform(12, 25), 1),
        'cough_frequency': random.randint(0, 15),
        'spo2_fluctuation': round(random.uniform(0.5, 4.0), 1),
        'airway_resistance': round(random.uniform(1.0, 3.5), 1)
    }

def personalized_risk_engine(predicted_aqi, biometrics, env_modifiers):
    """
    Combines Predicted AQI, biometric stress, and environmental modifiers.
    Outputs: Personalized AQI Exposure Score (0-100), Risk classification, Forecast trend.
    """
    # Base risk derived from Predicted AQI (normalize roughly max expected 200)
    base_aqi_risk = min(predicted_aqi / 200.0 * 50, 50)
    
    # Biometric stress component (max ~30 points)
    bio_risk = 0
    bio_risk += (biometrics['cough_frequency'] / 15.0) * 10
    bio_risk += (biometrics['spo2_fluctuation'] / 4.0) * 10
    bio_risk += (biometrics['airway_resistance'] / 3.5) * 10
    
    # Environmental modifier component (max ~20 points)
    env_risk = 0
    env_risk += (env_modifiers['traffic_density']) * 10
    env_risk += (env_modifiers['urban_topology'] - 0.9) * 25
    
    total_score = min(base_aqi_risk + bio_risk + env_risk, 100)
    
    classification = "Low"
    if total_score > 85:
        classification = "Critical"
    elif total_score > 65:
        classification = "High"
    elif total_score > 40:
        classification = "Moderate"
        
    trend_choices = ["Rising", "Stable", "Falling"]
    if classification in ["Critical", "High"]:
        trend = random.choice(["Rising", "Stable"])
    else:
        trend = random.choice(["Stable", "Falling"])
        
    return {
        "score": round(total_score, 1),
        "classification": classification,
        "trend": trend
    }


@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        action = request.form.get('action')
        db = get_db()
        
        if action == 'register':
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            
            if not name or not email or not password:
                flash('All fields are required.', 'error')
            else:
                hashed_password = generate_password_hash(password)
                try:
                    db.execute("INSERT INTO users (email, password, name) VALUES (?, ?, ?)", 
                               (email, hashed_password, name))
                    db.commit()
                    flash('Registration successful. Please log in.', 'success')
                except sqlite3.IntegrityError:
                    flash('Email already registered.', 'error')
                    
        elif action == 'login':
            email = request.form.get('email')
            password = request.form.get('password')
            user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
            
            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['user_name'] = user['name']
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid email or password.', 'error')
                
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('index'))
        
    env = generate_environmental_inputs()
    bio = generate_biometrics()
    
    input_df = pd.DataFrame([env])
    predicted_aqi = rf_model.predict(input_df)[0]
    predicted_aqi = round(predicted_aqi, 1)
    
    risk_assessment = personalized_risk_engine(predicted_aqi, bio, env)
    
    # Location base for Leaflet
    lat = 40.7128 + random.uniform(-0.05, 0.05)
    lng = -74.0060 + random.uniform(-0.05, 0.05)
    
    data = {
        'env': env,
        'bio': bio,
        'predicted_aqi': predicted_aqi,
        'risk': risk_assessment,
        'user_name': session.get('user_name', 'User'),
        'lat': lat,
        'lng': lng
    }
    
    return render_template('dashboard.html', data=data)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5005)
