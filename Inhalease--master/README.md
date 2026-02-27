# InhaleEase (Smart Breathe)

A full-stack, AI-driven air quality monitoring and respiratory health prediction platform.

## Architecture Structure

This project follows a simple, robust full-stack architecture:

### `/frontend`
Contains the static web application frontend.
- **Technologies:** HTML, CSS, JavaScript
- **Features:** Real-time dashboard, interactive Leaflet AI location selection, User authentication interfaces, and responsive aesthetics.
- **Run:** Open `frontend/index.html` in your browser or serve via `frontend/start.bat` on `http://localhost:3001`

### `/backend`
Contains all server-side logic and database interactions.
#### Node.js Server (`/backend`)
Handles the primary REST API, user authentication, and data retrieval.
- **Technologies:** Node.js, Express, MongoDB
- **Features:** User sessions, JWT authentication, and routing.
- **Run:** `npm start` or `npm run dev` (running on port `5000`)

#### AI Prototype & Flask Service (`/backend/flask-app`)
Contains the algorithmic prototypes for predicting air quality risk using Machine Learning.
- **Technologies:** Python, Flask, Scikit-learn, Pandas
- **Run:** `gunicorn app:app` or `python app.py`

## Getting Started Locally

1. **Prerequisites:** Have `Node.js`, `Python`, and `MongoDB` installed and running.
2. In the `frontend` folder, you can run `start.bat` on Windows to automatically spawn and serve both the Node backend and static frontend sequentially.
3. Access the application simultaneously at `http://localhost:3001`.

## Deployment
This project is configured out-of-the-box for [Render](https://render.com) using the `render.yaml` Blueprint file, which sequentially spins up the Node Backend, Flask Service, and Static Web server directly from the GitHub repository.

---

*Designed for seamless deployment and AI-backed health analytics.*
