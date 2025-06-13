# Development Guide

This guide provides detailed information for developers working on the Electric Vehicle Charging Analytics Platform.

## Architecture Overview

### Backend (FastAPI + Python)
- **Framework**: FastAPI with async/await support
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Cache**: Redis for performance optimization
- **Background Tasks**: Celery with Redis broker
- **ML Framework**: Scikit-learn, XGBoost, LightGBM
- **API Documentation**: Automatic OpenAPI/Swagger docs

### Frontend (Next.js + React)
- **Framework**: Next.js 14 with TypeScript
- **Styling**: Tailwind CSS with custom components
- **State Management**: SWR for server state, React Context for client state
- **Charts**: Chart.js and Plotly.js for visualizations
- **Real-time**: WebSocket connections for live updates

### Infrastructure
- **Containerization**: Docker and Docker Compose
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **Reverse Proxy**: Nginx (production)
- **Monitoring**: Built-in health checks and metrics

## Development Setup

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)
- Git

### Quick Start
```bash
# Clone the repository
git clone <repository-url>
cd electric-vehicle-charging

# Start all services
./start.sh

# Or manually with Docker Compose
docker-compose up --build
```

### Local Development

#### Backend Development
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp ../.env.example .env
# Edit .env with your local settings

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --port 8000
```

#### Frontend Development
```bash
cd frontend

# Install dependencies
npm install

# Set environment variables
cp ../.env.example .env.local
# Edit .env.local with your local settings

# Start development server
npm run dev
```

## Project Structure

```
electric-vehicle-charging/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes and endpoints
│   │   │   └── v1/
│   │   │       └── endpoints/
│   │   ├── core/           # Core configuration and utilities
│   │   ├── db/             # Database models and migrations
│   │   ├── ml/             # Machine learning models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic services
│   │   ├── tasks/          # Celery background tasks
│   │   └── main.py         # FastAPI application entry point
│   ├── data/               # Data files and exports
│   ├── models/             # Trained ML model files
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile
├── frontend/               # Next.js frontend
│   ├── components/         # React components
│   │   ├── charts/         # Chart components
│   │   └── ...
│   ├── contexts/           # React contexts
│   ├── lib/                # Utility libraries
│   ├── pages/              # Next.js pages
│   ├── styles/             # CSS and styling
│   ├── package.json        # Node.js dependencies
│   └── Dockerfile
├── data/                   # Shared data directory
├── docker-compose.yml      # Docker services configuration
├── .env.example           # Environment variables template
├── start.sh               # Startup script
└── README.md
```

## API Development

### Adding New Endpoints

1. **Create Pydantic schemas** in `backend/app/schemas/`
2. **Add database models** in `backend/app/db/models.py`
3. **Implement business logic** in `backend/app/services/`
4. **Create API endpoints** in `backend/app/api/v1/endpoints/`
5. **Register routes** in `backend/app/api/v1/api.py`

Example:
```python
# schemas/example.py
from pydantic import BaseModel

class ExampleCreate(BaseModel):
    name: str
    value: float

class ExampleResponse(ExampleCreate):
    id: int
    created_at: datetime

# api/v1/endpoints/example.py
from fastapi import APIRouter, Depends
from app.schemas.example import ExampleCreate, ExampleResponse

router = APIRouter()

@router.post("/", response_model=ExampleResponse)
async def create_example(data: ExampleCreate):
    # Implementation here
    pass
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Frontend Development

### Adding New Pages

1. **Create page component** in `pages/`
2. **Add navigation** in `components/Layout.tsx`
3. **Create necessary components** in `components/`
4. **Add API calls** in `lib/api.ts`

### Component Structure
```typescript
// components/ExampleComponent.tsx
import { useState } from 'react';
import { motion } from 'framer-motion';

interface ExampleComponentProps {
  data: any[];
  onAction: (id: string) => void;
}

export default function ExampleComponent({ data, onAction }: ExampleComponentProps) {
  const [loading, setLoading] = useState(false);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="card"
    >
      {/* Component content */}
    </motion.div>
  );
}
```

### Styling Guidelines

- Use Tailwind CSS utility classes
- Follow the design system defined in `tailwind.config.js`
- Use custom components defined in `styles/globals.css`
- Prefer semantic class names for complex components

## Machine Learning Development

### Adding New Models

1. **Create model class** in `backend/app/ml/models.py`
2. **Implement training logic** in the model class
3. **Add prediction endpoints** in `backend/app/api/v1/endpoints/ml.py`
4. **Create Celery tasks** for training in `backend/app/tasks/ml_training.py`

Example:
```python
# ml/models.py
class NewPredictionModel(BaseMLModel):
    def __init__(self):
        super().__init__("new_prediction")
        self.model = RandomForestRegressor()
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        # Feature engineering logic
        return df
    
    def train(self, df: pd.DataFrame) -> Dict[str, float]:
        # Training logic
        return metrics
    
    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        # Prediction logic
        return result
```

### Model Training Pipeline

1. **Data Loading**: Load training data from database
2. **Feature Engineering**: Transform raw data into ML features
3. **Model Training**: Train the ML model with cross-validation
4. **Model Evaluation**: Calculate performance metrics
5. **Model Saving**: Save trained model to disk
6. **Model Registration**: Register model metadata in database

## Testing

### Backend Testing
```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_api.py
```

### Frontend Testing
```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test:watch
```

## Deployment

### Production Environment

1. **Environment Variables**: Set production values in `.env`
2. **Database**: Use managed PostgreSQL service
3. **Cache**: Use managed Redis service
4. **File Storage**: Use cloud storage for data and models
5. **Monitoring**: Set up logging and monitoring
6. **SSL**: Configure HTTPS with proper certificates

### Docker Production Build
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

## Performance Optimization

### Backend Optimization
- Use database indexes for frequently queried fields
- Implement caching for expensive operations
- Use async/await for I/O operations
- Optimize database queries with proper joins
- Use connection pooling

### Frontend Optimization
- Implement code splitting with Next.js
- Use SWR for efficient data fetching
- Optimize images with Next.js Image component
- Implement virtual scrolling for large datasets
- Use React.memo for expensive components

## Security Considerations

### Backend Security
- Input validation with Pydantic
- SQL injection prevention with SQLAlchemy
- Rate limiting for API endpoints
- Authentication and authorization
- CORS configuration

### Frontend Security
- XSS prevention with proper escaping
- CSRF protection
- Secure API communication
- Environment variable protection
- Content Security Policy

## Monitoring and Logging

### Application Monitoring
- Health check endpoints
- Performance metrics
- Error tracking
- User analytics
- System resource monitoring

### Logging
- Structured logging with JSON format
- Log levels: DEBUG, INFO, WARNING, ERROR
- Request/response logging
- ML model performance logging
- Background task logging

## Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make changes** following the coding standards
4. **Add tests** for new functionality
5. **Run tests** to ensure everything works
6. **Commit changes**: `git commit -m 'Add amazing feature'`
7. **Push to branch**: `git push origin feature/amazing-feature`
8. **Create Pull Request**

### Code Style

- **Python**: Follow PEP 8, use Black for formatting
- **TypeScript**: Follow ESLint rules, use Prettier for formatting
- **Commits**: Use conventional commit messages
- **Documentation**: Update docs for new features

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   - Check PostgreSQL is running
   - Verify connection string in .env
   - Check firewall settings

2. **Redis Connection Issues**
   - Verify Redis is running
   - Check Redis URL in .env
   - Test connection with redis-cli

3. **Frontend Build Issues**
   - Clear node_modules and reinstall
   - Check Node.js version compatibility
   - Verify environment variables

4. **ML Model Issues**
   - Check model file permissions
   - Verify training data format
   - Check model dependencies

### Getting Help

- Check the GitHub Issues for known problems
- Review the API documentation at `/docs`
- Check application logs with `docker-compose logs`
- Contact the development team
