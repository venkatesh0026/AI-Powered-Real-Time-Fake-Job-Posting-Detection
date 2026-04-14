"""
Prediction Router - FastAPI

This router provides the /predict endpoint for fake job detection.
"""

from fastapi import APIRouter, Depends, HTTPException
from app.schemas import JobInput, PredictionResponse, ErrorResponse
from app.deps import get_current_user
from app.services.model_service import ModelService

router = APIRouter()

# Initialize model service and load model immediately
model_service = ModelService()
print(">>> Preloading BERT model at startup...")
model_service.load_model()
print(f">>> Model loaded: {model_service.model is not None}")


@router.post(
    "/predict",
    response_model=PredictionResponse,
    responses={
        200: {"description": "Successful prediction"},
        400: {"model": ErrorResponse, "description": "Invalid input"},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
    summary="Predict if a job posting is fake",
    description="""
    Analyze a job posting to determine if it's genuine or fraudulent.
    
    The model uses BERT to analyze the text content and returns:
    - **label**: 'Genuine' or 'Fake'
    - **confidence**: How confident the model is in its prediction
    - **probability_fraud**: Raw fraud probability score
    """
)
async def predict_job(
    body: JobInput,
    token: str = Depends(get_current_user)
):
    """
    Predict if a job posting is fake or genuine.
    
    Accepts JSON body (e.g. from frontend) or form data. Uses BERT model to classify
    the posting as fraudulent or legitimate.
    """
    print(f"\n=== PREDICT ENDPOINT HIT ===")
    print(f"Token: {token}")
    print(f"Received job: {body.title}")
    print(f"Body: {body}")
    
    try:
        print("Creating data dict...")
        data = {
            "title": body.title,
            "description": body.description,
            "company_profile": body.company,
            "requirements": body.requirements or "",
            "benefits": body.benefits or ""
        }
        
        print(f"Model loaded: {model_service.model is not None}")
        print(f"Tokenizer loaded: {model_service.tokenizer is not None}")
        
        print("Calling predict...")
        result = model_service.predict(data)
        print(f"Prediction result: {result}")
        print(f"Result type: {type(result)}")
        
        response = PredictionResponse(**result)
        print(f"Response created: {response}")
        print(f"Response dict: {response.model_dump()}")
        
        return response
        
    except Exception as e:
        print(f"ERROR in predict: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
