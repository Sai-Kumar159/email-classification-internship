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


📧 Email Classification for Support Team
🚀 Overview
This project classifies support emails into predefined categories and masks Personally Identifiable Information (PII). It is deployed as a RESTful API and designed to assist customer support teams in organizing and securing incoming emails efficiently.

✨ Features
✅ Email Classification
Automatically classifies emails into one of the following categories:

Incident

Request

Change

Problem

🔒 PII Masking
Detects and masks sensitive information types:

Full Name

Email Address

Phone Number

Date of Birth

Aadhar Number

Credit/Debit Card Number

CVV

Card Expiry Date

🔓 PII Demasking
Ability to retrieve the original data when required (securely handled).

🌐 Deployed as a REST API

🛠️ Technology Stack
Python

FastAPI – for building the REST API

scikit-learn – for TF-IDF and RandomForestClassifier

imblearn (SMOTE) – to handle imbalanced datasets

joblib – to persist models

🖥️ Setup Instructions (Run Locally)
bash
Copy
Edit
# 1. Clone the repository
git clone https://github.com/Sai-Kumar159/email-classification-internship.git
cd email-classification-internship

# 2. Create and activate virtual environment
python -m venv venv
# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Train the model
python models.py

# 5. Run the FastAPI app
uvicorn app:app --reload
🔗 Deployed API
Endpoint:
https://chaitanyasaikumar-email-classifier-internship.hf.space/classify

📥 Expected Request (JSON)
json
Copy
Edit
{
  "input_email_body": "string containing the email"
}
📤 Expected Response (JSON)
json
Copy
Edit
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
📡 Test the API
🧪 Using curl:
bash
Copy
Edit
curl -X POST https://chaitanyasaikumar-email-classifier-internship.hf.space/classify \
  -H "Content-Type: application/json" \
  -d '{"input_email_body": "Please update my credit card number 1234-5678-9876-5432"}'
🧪 Using PowerShell:
powershell
Copy
Edit
Invoke-RestMethod -Uri "https://chaitanyasaikumar-email-classifier-internship.hf.space/classify" `
  -Method POST `
  -Body '{"input_email_body": "Please update my phone number to 9876543210"}' `
  -ContentType "application/json"
🧭 API Documentation
Access interactive Swagger UI:
📎 https://chaitanyasaikumar-email-classifier-internship.hf.space/docs

📁 Project Structure
plaintext
Copy
Edit
├── app.py                 # Main FastAPI application
├── models.py              # Email classification and model training
├── utils.py               # Helper functions (PII detection/masking)
├── requirements.txt       # Python dependencies
├── *.joblib               # Serialized ML models
├── combined_emails_with_natural_pii (1).csv  # Training dataset with PII examples
🔗 GitHub Repository
👉 Visit the GitHub Repo :
https://github.com/Sai-Kumar159/email-classification-internship


