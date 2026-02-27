// API Configuration 
const config = {
    // Determine context (local vs prod)
    API_BASE_URL: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' || window.location.protocol === 'file:' || window.location.hostname === ''
        ? 'http://localhost:5000/api'
        : 'https://inhaleease-api.com/api',
};

// Expose configuration globally
window.AppConfig = config;
