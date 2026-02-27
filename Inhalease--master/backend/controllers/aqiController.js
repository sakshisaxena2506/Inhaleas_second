const AqiData = require('../models/AqiData');
const Prediction = require('../models/Prediction');

// @desc    Get live AQI (Dummy implementation)
// @route   GET /api/aqi/live
// @access  Private
exports.getLiveAqi = async (req, res) => {
    try {
        const { city, latitude, longitude } = req.query;

        const targetCity = city || 'New York';

        let hash = 0;
        for (let i = 0; i < targetCity.length; i++) {
            hash = targetCity.charCodeAt(i) + ((hash << 5) - hash);
        }
        hash = Math.abs(hash);

        // Deterministic dummy values based on real city hash 
        const dummyAqi = (hash % 180) + 20; // values between 20-199
        const dummyPm25 = Math.floor(dummyAqi * 0.3);

        // Save history for user
        const locationDetails = {
            city: targetCity,
            latitude: latitude || 40.7128,
            longitude: longitude || -74.0060
        };

        const aqiRecord = await AqiData.create({
            user: req.user._id,
            location: locationDetails,
            aqi: dummyAqi,
            pm25: dummyPm25,
            pm10: dummyPm25 + 10
        });

        res.json({
            success: true,
            data: aqiRecord
        });
    } catch (error) {
        res.status(400).json({ success: false, error: error.message });
    }
};

// @desc    Get AQI Prediction
// @route   GET /api/aqi/predict
// @access  Private
exports.getAqiPrediction = async (req, res) => {
    try {
        const { city } = req.query;

        const targetCity = city || 'New York';

        let hash = 0;
        for (let i = 0; i < targetCity.length; i++) {
            hash = targetCity.charCodeAt(i) + ((hash << 5) - hash);
        }
        hash = Math.abs(hash);

        const currentAqi = (hash % 180) + 20;

        // Predict AQI perfectly: slightly worse or better based on city name rules
        const offset = (targetCity.length % 2 === 0) ? -10 : 15;
        const predictedAqi = Math.max(10, currentAqi + offset);

        const prediction = await Prediction.create({
            location: { city: targetCity },
            predictedAqi,
            forecastDate: new Date(Date.now() + 24 * 60 * 60 * 1000) // Next 24 hours
        });

        res.json({
            success: true,
            data: prediction
        });
    } catch (error) {
        res.status(400).json({ success: false, error: error.message });
    }
};

// @desc    Get AQI History
// @route   GET /api/aqi/history
// @access  Private
exports.getAqiHistory = async (req, res) => {
    try {
        const history = await AqiData.find({ user: req.user._id }).sort({ recordedAt: -1 }).limit(10);

        // If DB is empty or fails gracefully, provide fake dummy data
        if (!history || history.length === 0) {
            return res.json({
                success: true,
                data: [
                    { aqi: 45, pm25: 12, recordedAt: new Date(Date.now() - 1000 * 60 * 60 * 24) },
                    { aqi: 52, pm25: 18, recordedAt: new Date(Date.now() - 1000 * 60 * 60 * 48) }
                ]
            });
        }

        res.json({
            success: true,
            data: history
        });
    } catch (error) {
        res.status(400).json({ success: false, error: error.message });
    }
};

// @desc    Get Advanced AQI & Wearable Data (Hackathon Features)
// @route   GET /api/aqi/advanced
// @access  Private
exports.getAdvancedMetrics = async (req, res) => {
    try {
        const { city } = req.query;
        const targetCity = city || 'New York';

        let hash = 0;
        for (let i = 0; i < targetCity.length; i++) {
            hash = targetCity.charCodeAt(i) + ((hash << 5) - hash);
        }
        hash = Math.abs(hash);

        // Dummy AQI from existing logic to match frontend
        const dummyAqi = (hash % 180) + 20;

        // 1) Simulated wearable respiratory data
        const wearable = {
            breathing_rate_variability: parseFloat((Math.random() * 2.0 + 0.5).toFixed(2)),
            cough_frequency: Math.floor(Math.random() * 11),
            spo2: Math.floor(Math.random() * 8) + 92,
            airway_resistance: parseFloat((Math.random() * 3.5 + 2.0).toFixed(2))
        };

        // 2) Environmental intelligence inputs
        const env = {
            hyperlocal_aqi: dummyAqi,
            satellite_aod: parseFloat((Math.random() * 1.4 + 0.1).toFixed(2)),
            temperature: Math.floor(Math.random() * 21) + 15,
            humidity: Math.floor(Math.random() * 51) + 30,
            traffic_density: parseFloat((Math.random() * 1.5 + 0.5).toFixed(2)),
            urban_topology_risk: parseFloat((Math.random() * 0.7 + 0.8).toFixed(2))
        };

        // 3) Personalized Exposure Risk Score
        const aqi_component = Math.min((env.hyperlocal_aqi / 300) * 50, 50);
        const spo2_penalty = Math.max(0, 98 - wearable.spo2) * 2;
        const cough_penalty = wearable.cough_frequency * 1.5;
        const resist_penalty = Math.max(0, wearable.airway_resistance - 2.0) * 5;
        const health_component = Math.min(spo2_penalty + cough_penalty + resist_penalty, 50);

        const score = Math.max(0, Math.min(100, Math.round(aqi_component + health_component)));

        let category;
        if (score < 30) category = 'Low';
        else if (score < 60) category = 'Moderate';
        else if (score < 85) category = 'High';
        else category = 'Critical';

        let recommendation;
        if (category === 'Low') recommendation = "Air quality is good and biometrics are stable. Safe for outdoor activities.";
        else if (category === 'Moderate') recommendation = "Air quality is moderate. Limit intense outdoor physical activity if you are sensitive.";
        else if (category === 'High') recommendation = "High exposure risk! Wear an N95 mask outdoors. Consider staying indoors.";
        else recommendation = "EMERGENCY: Respiratory metrics and air quality are at dangerous levels. Stay indoors immediately with purifiers on.";

        // 4) Short-Term Exposure Forecast
        const trends = ['increasing', 'stable', 'decreasing'];
        const trend = trends[Math.floor(Math.random() * trends.length)];
        let forecast_score;
        if (trend === 'increasing') forecast_score = Math.min(100, score + Math.floor(Math.random() * 11) + 5);
        else if (trend === 'decreasing') forecast_score = Math.max(0, score - Math.floor(Math.random() * 11) - 5);
        else forecast_score = score + Math.floor(Math.random() * 5) - 2;

        res.json({
            success: true,
            data: {
                wearable,
                env,
                score,
                category,
                forecast_score,
                forecast_trend: trend,
                recommendation
            }
        });
    } catch (error) {
        res.status(400).json({ success: false, error: error.message });
    }
};
