import os
import random
from flask import Flask, render_template_string, request, session, redirect, url_for, jsonify

app = Flask(__name__)
app.secret_key = 'super_secret_hackathon_key'

# =============================================================================
# 7) ARCHITECT CONCEPTUALLY (Edge AI, Federated Learning, Explainable AI)
# =============================================================================
#
# EDGE AI PROCESSING ON WEARABLE:
# - Wearable devices run lightweight, quantized ML models (e.g., TensorFlow Lite) 
#   locally on microcontrollers (like ARM Cortex-M).
# - This allows for real-time anomaly detection in respiratory metrics without 
#   latency or constant cloud connectivity, conserving battery.
#
# FEDERATED LEARNING FOR PRIVACY-PRESERVING TRAINING:
# - Sensitive health data (breathing patterns, cough audio features) remains on 
#   the user's edge device.
# - Only locally calculated model weight updates (gradients) are sent to the cloud.
# - The global model aggregates these updates to improve generalized predictions, 
#   ensuring no raw personal health data is exposed.
#
# EXPLAINABLE AI (XAI) RISK EXPLANATION LAYER:
# - Using SHAP (SHapley Additive exPlanations) or LIME on the backend.
# - Users receive a breakdown of *why* their exposure risk is high 
#   (e.g., "50% due to local NO2 spikes, 30% due to your dropped SpO2, 
#   20% due to traffic density in your geofence").
# =============================================================================

# --- Mock ML Model for AQI Prediction ---
class AQIModel:
    def predict(self, feature_list):
        # Feature list: [temp, humidity, traffic, topology_risk]
        # Random simple logic to simulate RandomForest output
        base = sum(f * 10 for f in feature_list) 
        return max(15, min(500, int(base + random.randint(-20, 20))))

ml_model = AQIModel()

# --- Logic Modules ---

def get_simulated_wearable_data():
    """ 2) Simulated wearable respiratory data module """
    return {
        "breathing_rate_variability": round(random.uniform(0.5, 2.5), 2), # seconds
        "cough_frequency": random.randint(0, 10), # coughs per hour
        "spo2": random.randint(92, 99), # blood oxygen %
        "airway_resistance": round(random.uniform(2.0, 5.5), 2) # cmH2O/L/s
    }

def get_environmental_inputs():
    """ 3) Environmental intelligence inputs (simulated) """
    return {
        "hyperlocal_aqi": random.randint(30, 180),
        "satellite_aod": round(random.uniform(0.1, 1.5), 2),
        "temperature": random.randint(15, 35), # Celsius
        "humidity": random.randint(30, 80), # %
        "traffic_density": round(random.uniform(0.5, 2.0), 2), # Multiplier
        "urban_topology_risk": round(random.uniform(0.8, 1.5), 2) # Modifier (canyon effect)
    }

def calculate_exposure_risk(wearable, env):
    """ 4) Personalized Exposure Risk Score """
    # Base AQI component (scaled to roughly 50 points)
    aqi_component = min(env["hyperlocal_aqi"] / 300.0 * 50, 50)
    
    # Health component (scaled to roughly 50 points)
    # Penalty for low SpO2, high cough, high resistance
    spo2_penalty = max(0, 98 - wearable["spo2"]) * 2
    cough_penalty = wearable["cough_frequency"] * 1.5
    resist_penalty = max(0, (wearable["airway_resistance"] - 2.0)) * 5
    
    health_component = min(spo2_penalty + cough_penalty + resist_penalty, 50)
    
    # Combined score
    score = min(100, max(0, int(aqi_component + health_component)))
    
    # Categorization
    if score < 30:
        category = "Low"
    elif score < 60:
        category = "Moderate"
    elif score < 85:
        category = "High"
    else:
        category = "Critical"
        
    return score, category

def get_forecast(current_score):
    """ 5) Short-Term Exposure Forecast (Next 1 hour) """
    trend = random.choice(["increasing", "stable", "decreasing"])
    if trend == "increasing":
        forecast = min(100, current_score + random.randint(5, 15))
    elif trend == "decreasing":
        forecast = max(0, current_score - random.randint(5, 15))
    else:
        forecast = current_score + random.randint(-2, 2)
    return forecast, trend

def get_recommendation(category):
    """ 6) Adaptive Health Recommendations """
    if category == "Low":
        return "Air quality is good and biometrics are stable. Safe for outdoor activities."
    elif category == "Moderate":
        return "Air quality is moderate. Limit intense outdoor physical activity if you are sensitive."
    elif category == "High":
        return "High exposure risk! Wear an N95 mask outdoors. Consider staying indoors."
    elif category == "Critical":
        return "EMERGENCY: Respiratory metrics and air quality are at dangerous levels. Stay indoors immediately with purifiers on."


# --- HTML Templates (Embedded for single-file requirement) ---

LOGIN_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Login - Smart Breathe</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; background: #0f172a; color: white; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
        .glass-panel { background: rgba(255, 255, 255, 0.05); padding: 40px; border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); text-align: center; max-width: 400px; width: 90%; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        h1 { color: #38bdf8; margin-bottom: 5px; }
        p { color: #94a3b8; margin-bottom: 30px; font-size: 0.9em; line-height: 1.5; }
        input { width: 100%; padding: 12px; margin-bottom: 20px; border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 8px; background: rgba(255, 255, 255, 0.1); color: white; box-sizing: border-box; }
        button { width: 100%; padding: 12px; border: none; border-radius: 8px; background: #38bdf8; color: #0f172a; font-weight: bold; font-size: 16px; cursor: pointer; transition: 0.3s; }
        button:hover { background: #0284c7; color: white; }
    </style>
</head>
<body>
    <div class="glass-panel">
        <h1>Smart Breathe</h1>
        <p>Hyperlocal Predictive Air Quality<br>& Breath Health Monitoring</p>
        <form method="POST">
            <input type="text" name="username" placeholder="Enter your username (simulated)" required autocomplete="off">
            <button type="submit">Access Dashboard</button>
        </form>
    </div>
</body>
</html>
'''

DASHBOARD_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard - Smart Breathe</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        body { font-family: 'Inter', sans-serif; background: #0f172a; color: white; margin: 0; padding: 20px; }
        .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 15px; margin-bottom: 20px; }
        .header-title h2 { margin: 0; color: #38bdf8; display: flex; align-items: baseline; gap: 10px; }
        .logout { color: #ef4444; text-decoration: none; font-weight: bold; border: 1px solid; padding: 5px 15px; border-radius: 6px; transition: 0.2s; }
        .logout:hover { background: #ef4444; color: white; }
        
        /* 8) Modified UI Dashboard */
        .grid-layout { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 20px; }
        .card { background: rgba(255,255,255,0.05); padding: 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); }
        .card h3 { margin-top: 0; font-size: 0.95rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; }
        
        .value-large { font-size: 3rem; font-weight: 700; margin: 10px 0; }
        .text-low { color: #4ade80; }
        .text-moderate { color: #facc15; }
        .text-high { color: #fb923c; }
        .text-critical { color: #ef4444; }
        
        .banner { padding: 15px 20px; border-radius: 8px; margin-bottom: 20px; font-weight: bold; border-left: 5px solid; display: flex; align-items: center; gap: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .banner-Low { background: rgba(74,222,128,0.1); border-color: #4ade80; color: #4ade80; }
        .banner-Moderate { background: rgba(250,204,21,0.1); border-color: #facc15; color: #facc15; }
        .banner-High { background: rgba(251,146,60,0.1); border-color: #fb923c; color: #fb923c; }
        .banner-Critical { background: rgba(239,68,68,0.1); border-color: #ef4444; color: #ef4444; }
        
        ul.data-list { list-style: none; padding: 0; margin: 0; }
        ul.data-list li { padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.05); display: flex; justify-content: space-between; align-items:center;}
        ul.data-list li:last-child { border-bottom: none; }
        ul.data-list li strong { font-size: 1.1em; }
        
        #map { height: 350px; border-radius: 12px; width: 100%; border: 1px solid rgba(255,255,255,0.1); }
        
        .refresh-btn { background: #38bdf8; color: #0f172a; padding: 10px 20px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; margin-bottom: 20px; transition: 0.2s; }
        .refresh-btn:hover { background: #0284c7; color: white; }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-title">
            <h2>Smart Breathe</h2>
            <span style="color:#94a3b8; font-size:0.8rem; border: 1px solid #94a3b8; padding: 2px 8px; border-radius: 12px;">Hackathon Prototype</span>
        </div>
        <div style="display: flex; align-items: center; gap: 20px;">
            <div style="font-size:0.9em;color:#94a3b8;">User: <span style="color:white; font-weight:bold;">{{ user }}</span></div>
            <a href="/logout" class="logout">Logout</a>
        </div>
    </div>
    
    <!-- 8) Modify UI dashboard to display Health Recommendation Banner -->
    <div class="banner banner-{{ category }}">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
        <div>
            <div style="font-size: 0.8em; text-transform: uppercase; letter-spacing: 1px; opacity: 0.8; margin-bottom: 2px;">Recommendation</div>
            {{ recommendation }}
        </div>
    </div>
    
    <form method="GET" style="display:inline;">
        <button type="submit" class="refresh-btn">Sync Edge Device Data (Simulate Polling)</button>
    </form>

    <div class="grid-layout">
        <!-- Personalized Exposure Score Card -->
        <div class="card">
            <h3>Personalized Exposure Risk Score</h3>
            <div class="value-large text-{{ category|lower }}">{{ score }}<span style="font-size: 1rem; color: #64748b;"> / 100</span></div>
            <div style="font-size: 1.1rem;">Category: <strong class="text-{{ category|lower }}">{{ category }}</strong></div>
            <p style="font-size: 0.85em; color: #64748b; margin-top: 15px;">Fuses real-time AQI with wearable respiratory biometrics.</p>
        </div>
        
        <!-- Short-Term Exposure Forecast Card -->
        <div class="card">
            <h3>1-Hour Short-Term Forecast</h3>
            <div class="value-large" style="color:#f8fafc;">{{ forecast_score }}<span style="font-size: 1rem; color: #64748b;"> / 100</span></div>
            <div style="font-size: 1.1rem; color:#94a3b8;">Predicted Trend: <strong style="color:white;">{{ forecast_trend|capitalize }}</strong></div>
            <p style="font-size: 0.85em; color: #64748b; margin-top: 15px;">Driven by simulated RandomForest predictive modeling.</p>
        </div>
    </div>

    <div class="grid-layout">
        <!-- Simulated Wearable Data -->
        <div class="card">
            <h3>Wearable Respiratory Data <span style="font-size:0.7em; background:#38bdf8; color:#0f172a; padding: 2px 6px; border-radius: 4px; margin-left: 5px;">Edge AI</span></h3>
            <ul class="data-list">
                <li><span>Blood Oxygen (SpO2)</span> <strong {% if wearable.spo2 < 95 %}class="text-critical"{% endif %}>{{ wearable.spo2 }} %</strong></li>
                <li><span>Breathing Rate Variability</span> <strong>{{ wearable.breathing_rate_variability }} sec</strong></li>
                <li><span>Cough Frequency</span> <strong>{{ wearable.cough_frequency }} /hr</strong></li>
                <li><span>Airway Resistance</span> <strong>{{ wearable.airway_resistance }} cmH₂O/L/s</strong></li>
            </ul>
        </div>
        
        <!-- Environmental Intelligence -->
        <div class="card">
            <h3>Environmental Intelligence Inputs</h3>
            <ul class="data-list">
                <li><span>Hyperlocal AQI Sensor</span> <strong class="text-{{ 'low' if env.hyperlocal_aqi < 50 else 'moderate' if env.hyperlocal_aqi < 100 else 'high' if env.hyperlocal_aqi < 150 else 'critical' }}">{{ env.hyperlocal_aqi }}</strong></li>
                <li><span>Satellite AOD Factor</span> <strong>{{ env.satellite_aod }}</strong></li>
                <li><span>Meteo (Temp / Hum)</span> <strong>{{ env.temperature }}&deg;C / {{ env.humidity }}%</strong></li>
                <li><span>Traffic Density Mod.</span> <strong>{{ env.traffic_density }}x</strong></li>
                <li><span>Urban Topology Risk</span> <strong>{{ env.urban_topology_risk }}x</strong></li>
            </ul>
        </div>
    </div>

    <div class="card" style="margin-bottom: 40px;">
        <h3>Live Heatmap & Geofencing Pollution Alert</h3>
        <p style="font-size:0.9em; color:#94a3b8; margin-top:5px; margin-bottom:15px;">Radius and intensity dynamically tied to Hyperlocal sensor reading.</p>
        <div id="map"></div>
    </div>

    <script>
        // Initialize Leaflet Map centered on a simulated user location
        var map = L.map('map').setView([37.7749, -122.4194], 13); // SF reference
        
        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; OpenStreetMap contributors & CARTO',
            subdomains: 'abcd',
            maxZoom: 20
        }).addTo(map);

        // Geofencing Pollution Alert marker (dynamic radius based on AQI)
        var aqi = {{ env.hyperlocal_aqi }};
        var alertColor = aqi > 150 ? '#ef4444' : (aqi > 100 ? '#fb923c' : (aqi > 50 ? '#facc15' : '#4ade80'));
        
        var circle = L.circle([37.7790, -122.4200], {
            color: alertColor,
            fillColor: alertColor,
            fillOpacity: 0.35,
            radius: aqi * 6 
        }).addTo(map);
        
        circle.bindPopup("<b>Geofenced Pollution Zone!</b><br>Detected AQI Impact Radius.");
        
        // User location marker
        var userMarker = L.marker([37.7749, -122.4194]).addTo(map);
        userMarker.bindPopup("<b>Your Active Location</b><br>Wearable computing device active.").openPopup();
    </script>
</body>
</html>
'''

# --- Flask Routes ---

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form.get('username', 'DemoUser')
        return redirect(url_for('dashboard'))
    return render_template_string(LOGIN_HTML)

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
        
    wearable = get_simulated_wearable_data()
    env = get_environmental_inputs()
    
    score, category = calculate_exposure_risk(wearable, env)
    forecast_score, forecast_trend = get_forecast(score)
    recommendation = get_recommendation(category)
    
    return render_template_string(DASHBOARD_HTML, 
                                  user=session['username'],
                                  wearable=wearable,
                                  env=env,
                                  score=score,
                                  category=category,
                                  forecast_score=forecast_score,
                                  forecast_trend=forecast_trend,
                                  recommendation=recommendation)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    print("="*60)
    print(" SMART BREATHE HACKATHON PROTOTYPE STARTING ")
    print(" running on http://localhost:5001 ")
    print("="*60)
    # Exposing on all interfaces, port 5001 to avoid clash with other projects
    app.run(host='0.0.0.0', port=5001, debug=True)

