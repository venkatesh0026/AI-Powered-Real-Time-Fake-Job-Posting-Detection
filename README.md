# AI-Powered Fake Job Posting Detection System

## 📋 Overview

A complete end-to-end web application for detecting fraudulent job postings using Deep Learning (BiLSTM) and modern full-stack technologies.

### Key Features:
- **Fraudulency Detection**: Binary classification of job postings as Genuine or Fraudulent
- **Deep Learning Model**: BiLSTM-based architecture for NLP
- **Real-time API**: FastAPI backend with JWT authentication
- **Interactive Dashboard**: React frontend with responsive UI
- **Performance Metrics**: Comprehensive model evaluation metrics
- **User Authentication**: Secure login/registration system

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│              FRONTEND (React.js)                        │
│  ┌──────────────┬──────────────┬──────────────┐        │
│  │ Login/Auth   │ Dashboard    │ Metrics Page │        │
│  └──────────────┴──────────────┴──────────────┘        │
│              (Axios API Client)                         │
└────────────────┬───────────────────────────────────────┘
                 │ HTTP/REST
                 ▼
┌─────────────────────────────────────────────────────────┐
│         BACKEND (FastAPI + Uvicorn)                    │
│  ┌──────────────┬──────────────┬──────────────┐        │
│  │ Auth Routes  │ Prediction   │ Metrics      │        │
│  │ (JWT)        │ API          │ Routes       │        │
│  └──────────────┴──────────────┴──────────────┘        │
│              (SQLAlchemy + SQLite)                      │
└────────────────┬───────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│    ML INFERENCE ENGINE (PyTorch)                        │
│  ┌──────────────┬──────────────┬──────────────┐        │
│  │ Tokenizer    │ BiLSTM Model │ Predictions  │        │
│  └──────────────┴──────────────┴──────────────┘        │
│              Dataset: Preprocessed CSV                  │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Folder Structure

```
project/
│
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   └── database.py          # Database models
│   │
│   ├── ml/
│   │   ├── dataset/
│   │   │   └── fake_job_postings.csv
│   │   │
│   │   ├── models/              # Trained models & artifacts
│   │   │   ├── bilstm_model.pt
│   │   │   ├── tokenizer.pkl
│   │   │   ├── config.json
│   │   │   ├── training_history.json
│   │   │   └── evaluation_report.json
│   │   │
│   │   └── scripts/             # Training & utility scripts
│   │       ├── 01_data_loader.py
│   │       ├── 02_preprocessing.py
│   │       ├── 03_model_architecture.py
│   │       ├── 04_train_model.py
│   │       ├── 05_evaluate_model.py
│   │       ├── preprocessing_utils.py
│   │       └── main_pipeline.py
│   │
│   ├── requirements.txt
│   ├── .env.example
│   └── .env                     # (create from .env.example)
│
├── frontend/
│   ├── public/
│   │   └── index.html
│   │
│   ├── src/
│   │   ├── api/
│   │   │   └── apiClient.js
│   │   │
│   │   ├── pages/
│   │   │   ├── Login.js
│   │   │   ├── Register.js
│   │   │   ├── Dashboard.js
│   │   │   └── Metrics.js
│   │   │
│   │   ├── styles/
│   │   │   ├── Auth.css
│   │   │   ├── Dashboard.css
│   │   │   └── Metrics.css
│   │   │
│   │   ├── App.js
│   │   ├── App.css
│   │   ├── index.js
│   │   └── index.css
│   │
│   └── package.json
│
└── README.md

```

---

## 🚀 Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 16+
- pip & npm
- Git

### Step 1: Backend Setup

#### 1.1 Create Virtual Environment
```bash
cd project/backend
python -m venv venv

# Activate venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

#### 1.2 Install Dependencies
```bash
pip install -r requirements.txt
```

#### 1.3 Create .env File
```bash
cp .env.example .env
# Edit .env with your configuration
```

Content:
```
SECRET_KEY=your-secret-key-change-in-production
DATABASE_URL=sqlite:///./fake_jobs.db
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

#### 1.4 Train the Model (First Time Only)
```bash
cd ml/scripts
python main_pipeline.py
```

This will:
- Load the dataset
- Preprocess data (handle missing values, duplicates, class imbalance)
- Create train/val/test splits
- Train BiLSTM model
- Evaluate on test set
- Save model, tokenizer, and metrics

#### 1.5 Run Backend Server
```bash
cd project/backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`
API Docs: `http://localhost:8000/docs`

### Step 2: Frontend Setup

#### 2.1 Install Dependencies
```bash
cd project/frontend
npm install
```

#### 2.2 Create .env File (Optional)
```bash
# Create .env file in frontend directory
echo "REACT_APP_API_URL=http://localhost:8000" > .env
```

#### 2.3 Run Frontend Server
```bash
npm start
```

Frontend will be available at: `http://localhost:3000`

---

## 🧠 ML Model Details

### BiLSTM Architecture

```
Input Text (max 512 tokens)
        ↓
    Embedding Layer (100-dim)
        ↓
    BiLSTM (256 units × 2 directions)
        ↓
    Dropout (30%)
        ↓
    Dense Layer (128 units, ReLU)
        ↓
    Dropout (30%)
        ↓
    Dense Layer (64 units, ReLU)
        ↓
    Output Layer (2 units, Softmax)
        ↓
    [Genuine Probability, Fraudulent Probability]
```

### Training Configuration

```python
Optimizer: AdamW (learning_rate=0.001, weight_decay=1e-5)
Loss Function: CrossEntropyLoss (with class weights for imbalance)
Batch Size: 32
Epochs: 20
Learning Rate Scheduler: ReduceLROnPlateau
Validation Split: 10%
Test Split: 20%
Max Text Length: 512 tokens
```

### Data Processing

1. **Text Combination**: Merges `title`, `description`, `company_profile`, `requirements`, `benefits`
2. **Cleaning**: Lowercasing, URL/email removal, special character removal, whitespace normalization
3. **Tokenization**: Simple word-based tokenization with vocabulary size of 10,000
4. **Padding/Truncation**: Sequences padded or truncated to 512 tokens
5. **Class Imbalance**: Handled via oversampling and class weights

### Model Metrics

Typical performance on test set:
- **Accuracy**: 80-85%
- **Precision**: 80-85%
- **Recall**: 80-85%
- **F1-Score**: 80-85%
- **ROC-AUC**: 85-90%

---

## 📡 API Endpoints

### Authentication

**POST /auth/register**
```json
{
  "username": "user123",
  "email": "user@example.com",
  "password": "secure_password"
}
```

**POST /auth/login**
```json
{
  "username": "user123",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Prediction

**POST /predict**
```json
{
  "title": "Senior Software Engineer",
  "description": "We are looking for...",
  "company_profile": "Our company is...",
  "requirements": "5+ years experience...",
  "benefits": "Health insurance, 401k...",
  "location": "San Francisco, CA",
  "salary_range": "$120k - $150k"
}
```

**Response:**
```json
{
  "prediction": "Genuine",
  "confidence": 0.92,
  "probability_genuine": 0.92,
  "probability_fraudulent": 0.08,
  "input_text_length": 1543,
  "timestamp": "2024-02-03T10:30:45.123456"
}
```

**POST /predict/batch**
- Batch predictions for multiple job postings

### Metrics

**GET /metrics**
- Returns comprehensive evaluation metrics

**GET /model/info**
- Returns model configuration and info

### Health Check

**GET /health**
- Returns API health status

---

## 🎯 Usage Guide

### 1. Register/Login
- Go to `http://localhost:3000`
- Create account or login
- Receive JWT token (stored in localStorage)

### 2. Submit Job Posting for Analysis
- Fill in job details (title, description, company profile, requirements, benefits)
- Click "Analyze Job Posting"
- View prediction: Genuine or Fraudulent
- See confidence score and probabilities

### 3. View Model Metrics
- Click "View Metrics" button
- See comprehensive performance statistics
- Understand model's strengths and weaknesses

### 4. Batch Analysis (Advanced)
- Use API directly: `POST /predict/batch` with list of jobs

---

## 🔐 Security Features

- **JWT Authentication**: Token-based API security
- **Password Hashing**: (Implement bcrypt in production)
- **CORS**: Configured for frontend access
- **Input Validation**: Pydantic models for type safety
- **Rate Limiting**: (Add in production)
- **HTTPS**: (Configure in production)

---

## 📊 Model Training Process

### Dataset Statistics
- **Total Samples**: ~17,880 job postings
- **Genuine**: ~87% (class 0)
- **Fraudulent**: ~13% (class 1)
- **Class Imbalance Ratio**: ~6.7:1

### Preprocessing Steps
1. Load raw CSV
2. Handle missing values (fill empty text fields)
3. Remove exact duplicates
4. Combine text features
5. Clean text (lowercase, remove URLs/emails, special chars)
6. Create labels (0=Genuine, 1=Fraudulent)
7. Handle class imbalance (oversampling)
8. Train/val/test split (70/10/20)

### Training Process
- Load preprocessed data
- Initialize tokenizer and build vocabulary
- Create BiLSTM model (total params: ~1.2M)
- Train with AdamW optimizer
- Validate every epoch with F1-score
- Save best model based on F1-score
- Evaluate on held-out test set

### Output Artifacts
- `bilstm_model.pt`: Trained model weights
- `tokenizer.pkl`: Word-to-index mapping
- `config.json`: Model hyperparameters
- `training_history.json`: Loss/accuracy curves
- `evaluation_report.json`: Final metrics

---

## 🧪 Testing

### Test Backend API
```bash
# Health check
curl http://localhost:8000/health

# Register user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"pass123"}'

# Make prediction (with token)
curl -X POST http://localhost:8000/predict \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{...job data...}'
```

### Test Frontend
- Open browser dev tools (F12)
- Check Network tab for API calls
- Verify predictions are being made
- Check Console for errors

---

## ⚙️ Configuration

### Backend Config (.env)
```
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///./fake_jobs.db
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Frontend Config (.env)
```
REACT_APP_API_URL=http://localhost:8000
```

### Model Config (ml/models/config.json)
```json
{
  "test_size": 0.2,
  "val_size": 0.1,
  "batch_size": 32,
  "epochs": 20,
  "learning_rate": 0.001,
  "vocab_size": 10000,
  "embedding_dim": 100,
  "hidden_dim": 256,
  "n_layers": 2,
  "dropout": 0.3,
  "max_length": 512,
  "random_state": 42
}
```

---

## 🚢 Deployment

### Docker Setup (Optional)

**Backend Dockerfile**
```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Frontend Dockerfile**
```dockerfile
FROM node:16
WORKDIR /app
COPY package.json .
RUN npm install
COPY . .
RUN npm run build
CMD ["npx", "serve", "-s", "build", "-l", "3000"]
```

### Production Deployment

1. **Backend**
   - Use Gunicorn with Uvicorn workers
   - Enable HTTPS/SSL
   - Configure production database (PostgreSQL)
   - Add rate limiting and CORS properly
   - Use environment-based configuration

2. **Frontend**
   - Build: `npm run build`
   - Deploy static files to CDN or web server
   - Configure API URL for production

3. **ML Model**
   - Load model on startup
   - Cache tokenizer in memory
   - Monitor inference latency
   - Implement model versioning

---

## 📈 Performance Optimization

### Backend Optimization
- Add caching for model predictions
- Implement request batching
- Use async/await for I/O operations
- Connection pooling for database

### Frontend Optimization
- Code splitting with React.lazy()
- Minification (npm run build)
- Image optimization
- Service workers for offline support

### Model Optimization
- Quantization for smaller model size
- ONNX conversion for faster inference
- Model pruning to reduce parameters
- Batch inference for multiple predictions

---

## 🐛 Troubleshooting

### Model Not Found Error
```
Solution: Run training pipeline first
python ml/scripts/main_pipeline.py
```

### Port Already in Use
```bash
# Backend (change port)
uvicorn app.main:app --port 8001

# Frontend (change port)
PORT=3001 npm start
```

### CORS Errors
- Check CORS middleware in FastAPI (already configured)
- Verify frontend URL in allowed origins
- Check Authorization header format

### Token Expired
- Token expires after 30 minutes
- User must login again
- Frontend handles this automatically

---

## 📚 Additional Resources

- [PyTorch Documentation](https://pytorch.org/docs/)
- [FastAPI Guide](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Scikit-learn](https://scikit-learn.org/)

---

## 📝 License

This project is provided as-is for educational purposes.

---

## 👨‍💻 Developer Notes

### Key Technologies
- **NLP**: BiLSTM with Tokenization
- **Deep Learning**: PyTorch
- **Backend**: FastAPI with async support
- **Frontend**: React with Hooks
- **Database**: SQLAlchemy ORM with SQLite
- **Auth**: JWT tokens

### Code Quality
- Comprehensive error handling
- Type hints throughout
- Clear documentation
- Modular architecture
- Clean separation of concerns

### Future Improvements
1. Add BERT/Transformer embeddings
2. Implement model ensemble
3. Add data versioning (DVC)
4. Implement ML monitoring
5. Add explainability (LIME/SHAP)
6. Real-time performance dashboards
7. Automated retraining pipeline

---

## 🤝 Support

For issues or questions:
1. Check troubleshooting section
2. Review error messages carefully
3. Check console logs (browser & terminal)
4. Verify all dependencies installed correctly

---

**Last Updated**: February 3, 2024
**Version**: 1.0.0
