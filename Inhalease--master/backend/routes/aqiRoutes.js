const express = require('express');
const { getLiveAqi, getAqiPrediction, getAqiHistory, getAdvancedMetrics } = require('../controllers/aqiController');
const { protect } = require('../middleware/auth');

const router = express.Router();

router.get('/live', protect, getLiveAqi);
router.get('/predict', protect, getAqiPrediction);
router.get('/history', protect, getAqiHistory);
router.get('/advanced', protect, getAdvancedMetrics);

module.exports = router;
