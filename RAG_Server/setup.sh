# Create Virtual Environment
python -m venv venv

# Activate Virtual Environment
./.venv/Scripts/activate

# Install dependencies
pip install -r requirements.txt

# Install SPacy model
python -m spacy download en_core_web_sm

# Print message indicating readiness to run the application
echo "Setup complete. You can now run the application using: python app.py"