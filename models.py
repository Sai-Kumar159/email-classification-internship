import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier # Changed: Using RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib 
import os 
from collections import Counter # For checking class distribution

# Import SMOTE for oversampling
from imblearn.over_sampling import SMOTE

# Import the mask_email function from utils.py
from utils import mask_email

# Define paths for saving the trained model and vectorizer
MODEL_SAVE_PATH = 'random_forest_model.joblib'
VECTORIZER_SAVE_PATH = 'tfidf_vectorizer.joblib'
LABEL_ENCODER_SAVE_PATH = 'label_encoder.joblib'

def train_model(dataset_path: str = 'combined_emails_with_natural_pii (1).csv'):
    """
    Loads data, preprocesses it, masks PII, applies SMOTE for oversampling,
    trains the classification model (RandomForest), and saves the trained model and TF-IDF vectorizer.
    """
    print("Starting model training with SMOTE oversampling and Random Forest...")

    # 1. Load the dataset
    try:
        df = pd.read_csv(dataset_path)
    except FileNotFoundError:
        print(f"Error: Dataset not found at {dataset_path}. Please ensure the CSV file is in the correct directory.")
        return

    emails = df['email'].tolist()
    categories = df['type'].tolist()

    # Initial class distribution
    print("\nInitial Class Distribution:")
    print(Counter(categories))

    # 2. Apply PII Masking to emails
    print("Applying PII masking to emails (this might take a few minutes)...")
    masked_emails = []
    for email_body in emails:
        masked_text, _ = mask_email(email_body)
        masked_emails.append(masked_text)
    print("PII masking complete.")

    # 3. Convert categories to numerical labels
    label_encoder = LabelEncoder()
    encoded_categories = label_encoder.fit_transform(categories)
    
    # Save the label encoder
    joblib.dump(label_encoder, LABEL_ENCODER_SAVE_PATH)
    print(f"Label Encoder saved to {LABEL_ENCODER_SAVE_PATH}")

    # 4. Split data into training and validation sets
    X_train_masked, X_test_masked, y_train_encoded, y_test_encoded = train_test_split(
        masked_emails, encoded_categories, test_size=0.2, random_state=42, stratify=encoded_categories
    )
    print(f"Dataset split: Train samples={len(X_train_masked)}, Test samples={len(X_test_masked)}")

    # 5. Feature Extraction: TF-IDF Vectorizer
    vectorizer = TfidfVectorizer(max_features=5000, stop_words='english', ngram_range=(1, 2))
    X_train_tfidf = vectorizer.fit_transform(X_train_masked)
    X_test_tfidf = vectorizer.transform(X_test_masked)
    print(f"TF-IDF Vectorization complete. Vocabulary size: {len(vectorizer.vocabulary_)}")

    # 6. Apply SMOTE for Oversampling on TRAINING DATA ONLY
    print("\nApplying SMOTE to training data (this might take a few minutes)...")
    smote = SMOTE(sampling_strategy='auto', random_state=42, k_neighbors=min(5, X_train_tfidf.shape[0]-1) if X_train_tfidf.shape[0] > 1 else 1)
    
    X_train_resampled, y_train_resampled = smote.fit_resample(X_train_tfidf, y_train_encoded)
    print("SMOTE oversampling complete.")
    print("Class Distribution After SMOTE (Training Data):")
    print(Counter(y_train_resampled))

    # 7. Model Training: RandomForestClassifier
    model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
    print("Training Random Forest model on resampled data...")
    model.fit(X_train_resampled, y_train_resampled)
    print("Model training complete.")

    # Evaluate the model
    accuracy = model.score(X_test_tfidf, y_test_encoded)
    print(f"Model accuracy on test set (with SMOTE and Random Forest): {accuracy:.4f}")

    # 8. Save the trained model and vectorizer
    joblib.dump(model, MODEL_SAVE_PATH)
    joblib.dump(vectorizer, VECTORIZER_SAVE_PATH)
    print(f"Model saved to {MODEL_SAVE_PATH}")
    print(f"Vectorizer saved to {VECTORIZER_SAVE_PATH}")
    print("Model training process finished.")

def predict_category(
    masked_email_text: str,
    vectorizer: TfidfVectorizer = None,
    model: RandomForestClassifier = None, # Updated type hint for RandomForestClassifier
    label_encoder: LabelEncoder = None
) -> str:
    """
    Predicts the category of a single masked email using provided or loaded models.

    Args:
        masked_email_text (str): The content of the email after PII masking.
        vectorizer (TfidfVectorizer, optional): Loaded TF-IDF Vectorizer. If None, tries to load from disk.
        model (RandomForestClassifier, optional): Loaded RandomForestClassifier model. If None, tries to load from disk.
        label_encoder (LabelEncoder, optional): Loaded LabelEncoder. If None, tries to load from disk.

    Returns:
        str: The predicted category of the email (e.g., 'Incident', 'Request').
    """
    # Load models if not provided (for standalone testing of predict_category)
    if vectorizer is None:
        try:
            vectorizer = joblib.load(VECTORIZER_SAVE_PATH)
        except FileNotFoundError:
            return "Error: TF-IDF Vectorizer not found. Please train the model first."
    
    if model is None:
        try:
            model = joblib.load(MODEL_SAVE_PATH)
        except FileNotFoundError:
            return "Error: Trained model not found. Please train the model first."

    if label_encoder is None:
        try:
            label_encoder = joblib.load(LABEL_ENCODER_SAVE_PATH)
        except FileNotFoundError:
            return "Error: Label Encoder not found. Please train the model first."

    # Transform the input email using the loaded vectorizer
    email_tfidf = vectorizer.transform([masked_email_text])

    # Predict the category
    predicted_encoded_label = model.predict(email_tfidf)[0]

    # Convert the numerical label back to the original category string
    predicted_category = label_encoder.inverse_transform([predicted_encoded_label])[0]

    return predicted_category

if __name__ == '__main__':
    train_model()
