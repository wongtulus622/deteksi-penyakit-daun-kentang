from flask import Flask, request, jsonify
import joblib, cv2, numpy as np
from skimage.feature import graycomatrix, graycoprops
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# load model
model = joblib.load("decision_tree_glcm_best.pkl")
CLASS_NAMES = ["Early Blight", "Healthy", "Late Blight"]

def extract_glcm_features(img_gray):
    glcm = graycomatrix(img_gray, distances=[1], angles=[0],
                        symmetric=True, normed=True)
    feats = [
        graycoprops(glcm, 'contrast')[0,0],
        graycoprops(glcm, 'homogeneity')[0,0],
        graycoprops(glcm, 'energy')[0,0],
        graycoprops(glcm, 'correlation')[0,0],
    ]
    return np.array(feats)

@app.route("/predict", methods=["POST"])
def predict():
    file = request.files["file"]
    img = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    feats = extract_glcm_features(gray).reshape(1, -1)
    probs = model.predict_proba(feats)[0]
    class_idx = int(np.argmax(probs))
    confidence = f"{probs[class_idx]*100:.2f}%"
    label = CLASS_NAMES[class_idx]

    # rekomendasi sederhana
    advice = ""
    if label == "Healthy":
        advice = "Lakukan perawatan rutin agar tanaman tetap sehat."
    elif label == "Early Blight":
        advice = "Gunakan fungisida ringan dan pantau perkembangan daun."
    else:
        advice = "Lakukan tindakan intensif atau konsultasi dengan ahli pertanian."

    return jsonify({
        "prediction": label,
        "confidence": confidence,
        "advice": advice
    })

if __name__ == "__main__":
    app.run(debug=True)
