# Electric Vehicle Charging Analytics Platform

A comprehensive full-stack web application for analyzing electric vehicle charging patterns with machine learning capabilities and real-time data processing.

## Features

### 🔋 Data Analytics
- Interactive dashboards for EV charging patterns
- Real-time charging session monitoring
- Cost optimization analysis
- Peak demand forecasting

### 🤖 Machine Learning
- Charging duration prediction
- User behavior clustering
- Demand forecasting models
- Cost optimization algorithms

### 🌐 Full-Stack Architecture
- **Backend**: FastAPI with Python
- **Frontend**: Next.js with React
- **Database**: PostgreSQL
- **Cache**: Redis
- **ML Pipeline**: Scikit-learn, Pandas, NumPy
- **Visualization**: Plotly, Chart.js

### 📊 Real-time Processing
- Live data ingestion
- Background job processing
- WebSocket connections
- Automated model retraining

## Quick Start

### Prerequisites
- Python 3.11+ (for backend)
- Node.js 18+ (for frontend)
- Git

### Option 1: Using Startup Scripts (Recommended)

#### Quick Start (Simplest):
```bash
# Clone the repository
git clone <repository-url>
cd electric-vehicle-charging

# Run the simple startup script
./start-simple.sh

# To stop the servers later
./stop-simple.sh
```

#### For Docker deployment:
```bash
# Clone the repository
git clone <repository-url>
cd electric-vehicle-charging

# Run the startup script
./start.sh
```

#### For local development:
```bash
# Clone the repository
git clone <repository-url>
cd electric-vehicle-charging

# Run the local development script
./start-local.sh
```

### Option 2: Manual Setup

#### Backend Setup
```bash
cd backend

# Create and activate virtual environment
python3 -m venv venv-simple
source venv-simple/bin/activate  # On Windows: venv-simple\Scripts\activate

# Install dependencies
pip install fastapi uvicorn[standard] pydantic sqlalchemy aiosqlite pandas numpy scikit-learn python-multipart python-dotenv

# Start the backend server
python3 simple_server.py
```

#### Frontend Setup (in another terminal)
```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

### Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Project Structure

```
electric-vehicle-charging/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Core configuration
│   │   ├── db/             # Database models and connections
│   │   ├── ml/             # Machine learning models
│   │   ├── services/       # Business logic
│   │   ├── main.py         # Full FastAPI application
│   │   └── main_simple.py  # Simplified demo version
│   ├── simple_server.py    # Standalone demo server
│   ├── requirements.txt    # Full dependencies
│   ├── requirements-minimal.txt  # Minimal dependencies
│   └── venv-simple/        # Virtual environment
├── frontend/               # Next.js frontend
│   ├── components/         # React components
│   ├── pages/              # Next.js pages
│   ├── lib/                # API client and utilities
│   ├── styles/             # CSS styles
│   └── contexts/           # React contexts
├── data/                   # Raw and processed data
├── models/                 # Trained ML models
├── logs/                   # Application logs
├── docker-compose.yml      # Docker services configuration
├── start.sh               # Docker startup script
├── start-local.sh         # Local development script
├── .env.example           # Environment variables template
└── README.md
```

## Troubleshooting

### Common Issues

#### Backend won't start
1. **Python version**: Ensure you have Python 3.11+ installed
2. **Dependencies**: Try installing dependencies individually:
   ```bash
   pip install fastapi uvicorn pydantic
   ```
3. **Port conflict**: Check if port 8000 is already in use:
   ```bash
   lsof -i :8000
   ```

#### Frontend won't start
1. **Node.js version**: Ensure you have Node.js 18+ installed
2. **Clear cache**: Try clearing npm cache:
   ```bash
   npm cache clean --force
   rm -rf node_modules package-lock.json
   npm install
   ```
3. **Port conflict**: Check if port 3000 is already in use:
   ```bash
   lsof -i :3000
   ```

#### API connection issues
1. **CORS errors**: Make sure both frontend and backend are running
2. **Network issues**: Check if backend is accessible:
   ```bash
   curl http://localhost:8000/health
   ```
3. **Environment variables**: Verify API URL in frontend/.env.local

### Development Tips

1. **Backend Development**: Use the simplified server (`simple_server.py`) for quick testing
2. **Frontend Development**: The app uses SWR for data fetching with automatic refresh
3. **API Testing**: Use the interactive docs at http://localhost:8000/docs
4. **Data**: Sample data is included and automatically loaded

## Current Status

✅ **Application is currently running and ready to use!**

The platform includes:
- **Backend API** running on http://localhost:8000 with sample data
- **Frontend Dashboard** running on http://localhost:3000 with interactive charts
- **API Documentation** available at http://localhost:8000/docs
- **Sample Analytics Data** including charging patterns, cost analysis, and usage metrics

### What You Can Do Right Now

1. **View the Dashboard**: Open http://localhost:3000 to see the analytics dashboard
2. **Explore the API**: Visit http://localhost:8000/docs to test API endpoints
3. **Test ML Predictions**: Use the duration prediction endpoint with sample data
4. **Analyze Data**: View charging patterns, cost breakdowns, and usage heatmaps

### Sample API Calls

```bash
# Get analytics overview
curl http://localhost:8000/api/v1/analytics/overview

# Get charging sessions
curl http://localhost:8000/api/v1/data/sessions

# Test ML prediction
curl -X POST http://localhost:8000/api/v1/ml/predict/duration \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_model": "Tesla Model 3",
    "battery_capacity_kwh": 75,
    "state_of_charge_start_percent": 20,
    "state_of_charge_target_percent": 80,
    "charger_type": "Level 2",
    "temperature_celsius": 20,
    "vehicle_age_years": 2
  }'
```

## API Endpoints

### Data Analytics
- `GET /api/v1/analytics/overview` - Dashboard overview
- `GET /api/v1/analytics/patterns` - Charging patterns analysis
- `GET /api/v1/analytics/costs` - Cost analysis

### Machine Learning
- `POST /api/v1/ml/predict/duration` - Predict charging duration
- `POST /api/v1/ml/predict/cost` - Predict charging cost
- `GET /api/v1/ml/models/status` - Model status and metrics

### Data Management
- `GET /api/v1/data/sessions` - Charging sessions data
- `POST /api/v1/data/upload` - Upload new data
- `GET /api/v1/data/export` - Export processed data

## Machine Learning Models

### 1. Charging Duration Prediction
Predicts how long a charging session will take based on:
- Vehicle model and battery capacity
- Current state of charge
- Charger type and power rating
- Environmental factors (temperature)

### 2. Cost Optimization
Recommends optimal charging strategies considering:
- Time-of-use pricing
- Charging speed preferences
- Location availability
- User patterns

### 3. Demand Forecasting
Predicts charging demand for:
- Peak load management
- Infrastructure planning
- Grid optimization
- Resource allocation

### 4. User Behavior Clustering
Segments users based on:
- Charging frequency and patterns
- Location preferences
- Time-of-day usage
- Vehicle characteristics

## Data Pipeline

1. **Data Ingestion**: Real-time and batch data loading
2. **Data Validation**: Quality checks and anomaly detection
3. **Feature Engineering**: Extract meaningful features
4. **Model Training**: Automated retraining pipeline
5. **Model Deployment**: Seamless model updates
6. **Monitoring**: Performance tracking and alerts

## Summary

This Electric Vehicle Charging Analytics Platform is now **fully operational** with:

### ✅ Working Components
- **FastAPI Backend** with RESTful API endpoints
- **Next.js Frontend** with interactive dashboard
- **Machine Learning** prediction capabilities
- **Data Analytics** with real-time visualizations
- **Sample Data** for immediate testing

### 🚀 Quick Start Commands
```bash
# Start everything (recommended)
./start-simple.sh

# Stop everything
./stop-simple.sh

# Access the application
open http://localhost:3000
```

### 📊 Features Demonstrated
- Real-time charging session analytics
- Cost optimization analysis
- Usage pattern visualization
- ML-powered duration predictions
- Data quality monitoring
- Interactive API documentation

The platform showcases modern full-stack development with data engineering and ML capabilities, perfect for analyzing electric vehicle charging patterns and optimizing charging infrastructure.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.