import os
import PyPDF2
import torch  # Use if model is in PyTorch
import pickle  # Use for Scikit-learn
import tensorflow as tf  # Use for TensorFlow/Keras
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Load the trained model (Adjust based on framework)
MODEL_TYPE = "pkl"  # Change to "h5" for TensorFlow or "pth" for PyTorch
MODEL_PATH = "model.pkl"  # Update with actual file

if MODEL_TYPE == "pkl":  # Scikit-learn
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
elif MODEL_TYPE == "h5":  # TensorFlow/Keras
    model = tf.keras.models.load_model(MODEL_PATH)
elif MODEL_TYPE == "pth":  # PyTorch
    from model_architecture import MyModel  # Import your model class
    model = MyModel()
    model.load_state_dict(torch.load(MODEL_PATH))
    model.eval()

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, "rb") as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
    return text.strip()

# API endpoint for PDF upload and summarization
@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)

    # Extract text from PDF
    extracted_text = extract_text_from_pdf(file_path)

    # Generate summary using ML model
    if MODEL_TYPE == "pkl":
        summary = model.predict([extracted_text])[0]  # Example for Scikit-learn
    elif MODEL_TYPE == "h5":
        summary = model.predict([extracted_text])[0]  # Example for TensorFlow/Keras
    elif MODEL_TYPE == "pth":
        with torch.no_grad():
            summary = model(extracted_text)  # Example for PyTorch
        summary = summary.item() if isinstance(summary, torch.Tensor) else summary

    return jsonify({"summary": summary, "text": extracted_text})

if __name__ == "__main__":
    app.run(debug=True)
