# API Documentation

## Base URL
```
http://localhost:8000
```

## Interactive API Documentation
```
http://localhost:8000/docs
```

---

## Authentication Endpoints

### Register User
```http
POST /auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password_123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Login User
```http
POST /auth/login
Content-Type: application/json

{
  "username": "john_doe",
  "password": "secure_password_123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

---

## Prediction Endpoints

### Single Job Posting Prediction
```http
POST /predict
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "title": "Senior Software Engineer",
  "description": "We are looking for an experienced software engineer to join our growing team. You will work on scalable systems and cutting-edge technologies.",
  "company_profile": "TechCorp is a leading software development company with offices in San Francisco and New York.",
  "requirements": "5+ years of experience in Python, JavaScript, and AWS. Strong understanding of microservices architecture.",
  "benefits": "Competitive salary, health insurance, 401k matching, flexible work hours",
  "location": "San Francisco, CA",
  "salary_range": "$120,000 - $160,000"
}
```

**Response (200):**
```json
{
  "prediction": "Genuine",
  "confidence": 0.9234,
  "probability_genuine": 0.9234,
  "probability_fraudulent": 0.0766,
  "input_text_length": 1234,
  "timestamp": "2024-02-03T10:30:45.123456"
}
```

**Error Response (401):**
```json
{
  "error": "Invalid authentication credentials",
  "status_code": 401
}
```

### Batch Job Postings Prediction
```http
POST /predict/batch
Authorization: Bearer {access_token}
Content-Type: application/json

[
  {
    "title": "Software Engineer",
    "description": "Join our team...",
    "company_profile": "We are...",
    "requirements": "5+ years...",
    "benefits": "Health insurance...",
    "location": "NYC",
    "salary_range": "$100k - $120k"
  },
  {
    "title": "Marketing Manager",
    "description": "Manage campaigns...",
    "company_profile": "Marketing firm...",
    "requirements": "3+ years...",
    "benefits": "Bonus structure...",
    "location": "LA",
    "salary_range": "$70k - $90k"
  }
]
```

**Response (200):**
```json
{
  "predictions": [
    {
      "title": "Software Engineer",
      "prediction": "Genuine",
      "confidence": 0.92,
      "probability_genuine": 0.92,
      "probability_fraudulent": 0.08
    },
    {
      "title": "Marketing Manager",
      "prediction": "Fraudulent",
      "confidence": 0.78,
      "probability_genuine": 0.22,
      "probability_fraudulent": 0.78
    }
  ],
  "total": 2
}
```

---

## Metrics Endpoints

### Get Model Performance Metrics
```http
GET /metrics
Authorization: Bearer {access_token}
```

**Response (200):**
```json
{
  "test_metrics": {
    "accuracy": 0.8234,
    "precision": 0.8156,
    "recall": 0.8312,
    "f1": 0.8233,
    "roc_auc": 0.8892,
    "per_class": {
      "genuine": {
        "precision": 0.8412,
        "recall": 0.8234,
        "f1": 0.8322,
        "support": 2456.0
      },
      "fraudulent": {
        "precision": 0.7234,
        "recall": 0.7567,
        "f1": 0.7396,
        "support": 412.0
      }
    },
    "confusion_matrix": [
      [2023, 433],
      [98, 314]
    ]
  },
  "summary": {
    "total_samples": 2868,
    "genuine_samples": 2456,
    "fraudulent_samples": 412,
    "correct_predictions": 2337,
    "incorrect_predictions": 531
  }
}
```

### Get Model Information
```http
GET /model/info
Authorization: Bearer {access_token}
```

**Response (200):**
```json
{
  "model_type": "BiLSTM",
  "config": {
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
  },
  "device": "cuda",
  "model_loaded": true
}
```

---

## Health Check

### System Health Status
```http
GET /health
```

**Response (200):**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "device": "cpu"
}
```

---

## Error Responses

### Validation Error
```json
{
  "error": "Input validation error",
  "status_code": 422
}
```

### Model Not Found
```json
{
  "error": "Model not loaded. Please train the model first.",
  "status_code": 500
}
```

### Token Expired
```json
{
  "error": "Token has expired",
  "status_code": 401
}
```

### Invalid Token
```json
{
  "error": "Invalid token",
  "status_code": 401
}
```

---

## Request/Response Details

### Field Descriptions

**Job Posting Input:**
- `title` (string, required): Job title (5-200 characters)
- `description` (string, required): Detailed job description (20-5000 characters)
- `company_profile` (string, required): Company information (10-2000 characters)
- `requirements` (string, required): Job requirements (10-2000 characters)
- `benefits` (string, optional): Benefits offered (0-2000 characters)
- `location` (string, optional): Job location
- `salary_range` (string, optional): Salary information

**Prediction Response:**
- `prediction` (string): "Genuine" or "Fraudulent"
- `confidence` (float): Confidence score (0.0 to 1.0)
- `probability_genuine` (float): Probability of being genuine
- `probability_fraudulent` (float): Probability of being fraudulent
- `input_text_length` (integer): Total character count of input text
- `timestamp` (string): ISO format timestamp

---

## Usage Examples

### Python Requests
```python
import requests

# Login
response = requests.post(
    'http://localhost:8000/auth/login',
    json={'username': 'user123', 'password': 'pass123'}
)
token = response.json()['access_token']

# Make prediction
headers = {'Authorization': f'Bearer {token}'}
response = requests.post(
    'http://localhost:8000/predict',
    headers=headers,
    json={
        'title': 'Software Engineer',
        'description': 'Join our team...',
        'company_profile': 'Tech company...',
        'requirements': '5+ years experience...',
        'benefits': 'Health insurance...'
    }
)

prediction = response.json()
print(f"Prediction: {prediction['prediction']}")
print(f"Confidence: {prediction['confidence']:.2%}")
```

### JavaScript/Fetch
```javascript
// Login
const loginResponse = await fetch('http://localhost:8000/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'user123',
    password: 'pass123'
  })
});
const { access_token } = await loginResponse.json();

// Make prediction
const predictionResponse = await fetch('http://localhost:8000/predict', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${access_token}`
  },
  body: JSON.stringify({
    title: 'Software Engineer',
    description: 'Join our team...',
    company_profile: 'Tech company...',
    requirements: '5+ years experience...',
    benefits: 'Health insurance...'
  })
});

const prediction = await predictionResponse.json();
console.log(`Prediction: ${prediction.prediction}`);
console.log(`Confidence: ${(prediction.confidence * 100).toFixed(2)}%`);
```

### cURL
```bash
# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user123","password":"pass123"}'

# Prediction
curl -X POST http://localhost:8000/predict \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title":"Software Engineer",
    "description":"Join our team...",
    "company_profile":"Tech company...",
    "requirements":"5+ years...",
    "benefits":"Health insurance..."
  }'
```

---

## Rate Limiting (Future)
Currently not implemented. Will be added in production:
- 100 requests per minute per IP
- 1000 requests per hour per user

---

## Versioning
Current API Version: 1.0.0

---

## Support
For API issues, check:
1. Authentication token validity
2. Request payload format
3. API documentation at /docs
4. Server logs
