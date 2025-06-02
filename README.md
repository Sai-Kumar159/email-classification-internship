---
title: Email Classifier Internship
sdk: docker
emoji: 📚
colorFrom: blue
colorTo: green
pinned: false
short_description: ' gradio sdk_version: "4.44.0"'
sdk_version: 5.32.0
---
# email-classification-internship


Content:
Project Title: Email Classification for Support Team
Overview: Briefly explain what the project does (classifies support emails, handles PII).
Features:
Email classification into categories (Incident, Request, Change, Problem).
PII masking (listing all PII types you mask: full name, email, phone, DOB, Aadhar, Credit/Debit Card, CVV, Card Expiry).
PII demasking for original output.
Deployed as a REST API.
Technology Stack: Python, FastAPI, scikit-learn (TfidfVectorizer, RandomForestClassifier), imblearn (SMOTE), joblib.
Setup Instructions (How to run locally):
Clone the repository.
Create and activate a virtual environment (python -m venv venv, .\venv\Scripts\activate).
Install dependencies (pip install -r requirements.txt).
Train the model (python models.py).
Run the API (uvicorn app:app --reload).
API Usage:
Clearly state the Deployed API Endpoint: https://chaitanyasaikumar-email-classifier-internship.hf.space/classify
Show the Expected Request Body (JSON):
JSON

{
  "input_email_body": "string containing the email"
}
Show the Expected Response Body (JSON):
JSON

{
  "input_email_body": "string containing the email",
  "list_of_masked_entities": [
    {
      "position": [start_index, end_index],
      "classification": "entity_type",
      "entity": "original_entity_value"
    }
  ],
  "masked_email": "string containing the masked email",
  "category_of_the_email": "string containing the class"
}
Provide a curl example (or PowerShell Invoke-RestMethod) for testing the deployed API.
Mention the interactive docs at /docs (e.g., https://chaitanyasaikumar-email-classifier-internship.hf.space/docs).
Project Structure: Briefly list the files and their purpose (app.py, models.py, utils.py, requirements.txt, .joblib files, combined_emails_with_natural_pii (1).csv).
Link to GitHub Repository: https://github.com/Sai-Kumar159/email-classification-internship
