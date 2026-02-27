const mongoose = require('mongoose');

const AqiDataSchema = new mongoose.Schema({
    user: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
    location: {
        city: { type: String },
        latitude: { type: Number },
        longitude: { type: Number }
    },
    aqi: { type: Number, required: true },
    pm25: { type: Number },
    pm10: { type: Number },
    recordedAt: { type: Date, default: Date.now }
});

module.exports = mongoose.model('AqiData', AqiDataSchema);
