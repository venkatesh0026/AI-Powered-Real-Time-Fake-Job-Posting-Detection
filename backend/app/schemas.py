"""
Pydantic Schemas for Request/Response Validation

These models provide automatic validation and documentation
for the API endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional


class JobInput(BaseModel):
    """Input schema for job posting prediction"""
    
    title: str = Field(
        ...,
        description="Job title",
        examples=["Software Engineer"]
    )
    company: str = Field(
        ...,
        description="Company name",
        examples=["Microsoft"]
    )
    description: str = Field(
        ...,
        description="Full job description (can include requirements and benefits)",
        examples=["We are looking for a skilled software developer..."]
    )
    requirements: Optional[str] = Field(default="", description="Job requirements")
    benefits: Optional[str] = Field(default="", description="Job benefits")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Senior Software Engineer",
                    "company": "Microsoft",
                    "description": "We are looking for an experienced software engineer to join our team. You will be working on cutting-edge projects using Python and machine learning.\n\nRequirements: 5+ years of Python experience, experience with ML frameworks\n\nBenefits: Competitive salary, health insurance, stock options, remote work"
                }
            ]
        }
    }


class PredictionResponse(BaseModel):
    """Response schema for prediction results"""
    
    label: str = Field(
        ...,
        description="Classification label: 'Genuine' or 'Fake'",
        examples=["Genuine"]
    )
    confidence: float = Field(
        ...,
        description="Confidence score (0-1)",
        examples=[0.92]
    )
    probability_fraud: Optional[float] = Field(
        default=None,
        description="Raw probability of fraud (0-1)",
        examples=[0.08]
    )
    details: str = Field(
        ...,
        description="Additional details about the prediction",
        examples=["Analysis based on ML model (Threshold: 0.35)."]
    )
    is_mock: Optional[bool] = Field(
        default=None,
        description="True if model is not loaded and mock result returned"
    )


class ErrorResponse(BaseModel):
    """Error response schema"""
    
    error: str = Field(..., description="Error message")
