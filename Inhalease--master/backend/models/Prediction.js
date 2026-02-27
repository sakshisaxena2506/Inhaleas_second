const mongoose = require('mongoose');

const PredictionSchema = new mongoose.Schema({
    location: {
        city: { type: String },
        latitude: { type: Number },
        longitude: { type: Number }
    },
    predictedAqi: { type: Number, required: true },
    forecastDate: { type: Date, required: true },
    createdAt: { type: Date, default: Date.now }
});

module.exports = mongoose.model('Prediction', PredictionSchema);
