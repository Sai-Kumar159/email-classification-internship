from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Tuple, Any
import joblib
import os

# Import your utility functions for PII handling
from utils import mask_email, demask_email

# Import your model prediction function
from models import predict_category, MODEL_SAVE_PATH, VECTORIZER_SAVE_PATH, LABEL_ENCODER_SAVE_PATH

app = FastAPI(
    title="Email Classification API",
    description="API for classifying support emails and handling PII.",
    version="1.0.0"
)

# --- Pydantic Models for Request and Response ---
class MaskedEntity(BaseModel):
    position: Tuple[int, int]
    classification: str
    entity: str

class ClassifyRequest(BaseModel):
    input_email_body: str

class ClassifyResponse(BaseModel):
    input_email_body: str # The original, unmasked email body
    list_of_masked_entities: List[MaskedEntity]
    masked_email: str
    category_of_the_email: str


loaded_model = None
loaded_vectorizer = None
loaded_label_encoder = None

@app.on_event("startup")
async def load_ml_models():
    """
    Load the trained machine learning model, TF-IDF vectorizer, and LabelEncoder
    when the FastAPI application starts up.
    """
    global loaded_model, loaded_vectorizer, loaded_label_encoder
    try:
        if not os.path.exists(MODEL_SAVE_PATH):
            raise FileNotFoundError(f"Model file not found: {MODEL_SAVE_PATH}. Please run models.py to train the model first.")
        if not os.path.exists(VECTORIZER_SAVE_PATH):
            raise FileNotFoundError(f"Vectorizer file not found: {VECTORIZER_SAVE_PATH}. Please run models.py to train the model first.")
        if not os.path.exists(LABEL_ENCODER_SAVE_PATH):
            raise FileNotFoundError(f"Label Encoder file not found: {LABEL_ENCODER_SAVE_PATH}. Please run models.py to train the model first.")

        loaded_model = joblib.load(MODEL_SAVE_PATH)
        loaded_vectorizer = joblib.load(VECTORIZER_SAVE_PATH)
        loaded_label_encoder = joblib.load(LABEL_ENCODER_SAVE_PATH)
        print("ML Models and Vectorizer loaded successfully!")
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        raise HTTPException(status_code=500, detail=f"Server startup failed: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during model loading: {e}")
        raise HTTPException(status_code=500, detail=f"Server startup failed: {e}")


# --- API Endpoint ---
@app.post("/classify", response_model=ClassifyResponse)
async def classify_email_endpoint(request: ClassifyRequest):
    """
    Receives an email body, masks PII, classifies the masked email,
    and returns the original email, masked entities, masked email,
    and the predicted category.
    """
    original_email_body = request.input_email_body

    if loaded_model is None or loaded_vectorizer is None or loaded_label_encoder is None:
        raise HTTPException(status_code=503, detail="ML Models are not loaded yet. Server is starting up or failed to load models.")

    # 1. Mask PII
    masked_email, list_of_masked_entities = mask_email(original_email_body)

   
    category_of_the_email = predict_category(
        masked_email_text=masked_email,
        vectorizer=loaded_vectorizer,
        model=loaded_model,
        label_encoder=loaded_label_encoder
    )
    

    reconstructed_original_email = demask_email(masked_email, list_of_masked_entities)


    return ClassifyResponse(
        input_email_body=reconstructed_original_email, # Reconstructed using demask_email as required
        list_of_masked_entities=list_of_masked_entities,
        masked_email=masked_email,
        category_of_the_email=category_of_the_email
    )

# Health check endpoint
@app.get("/")
async def root():
    return {"message": "Email Classification API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# For running the app directly (optional, HF Spaces will handle this)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
