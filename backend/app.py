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
        advice = (
        "Tanaman dalam kondisi sehat. "
        "Lakukan perawatan rutin dengan langkah-langkah berikut:\n"
        "Siram tanaman secara teratur sesuai kebutuhan tanah.\n"
        "Berikan pupuk organik atau NPK sesuai dosis anjuran.\n"
        "Pastikan tanaman mendapat cahaya matahari yang cukup.\n"
        "Bersihkan gulma di sekitar tanaman untuk mencegah kompetisi nutrisi.\n"
        "Lakukan pemantauan berkala agar penyakit bisa dideteksi sejak dini."
    )
    elif label == "Early Blight":
        advice = (
        "Terdeteksi gejala awal penyakit bercak daun (Early Blight). "
        "Segera lakukan langkah berikut:\n"
        "Gunakan fungisida berbahan aktif seperti mankozeb atau klorotalonil sesuai dosis.\n"
        "Pangkas daun yang terinfeksi untuk mencegah penyebaran.\n"
        "Hindari penyiraman langsung ke daun (gunakan sistem irigasi tetes bila memungkinkan).\n"
        "Tingkatkan sirkulasi udara antar tanaman dengan jarak tanam yang cukup.\n"
        "Tambahkan pupuk kalium untuk meningkatkan ketahanan tanaman."
    )
    else:
        advice = (
        "Terdeteksi penyakit hawar daun lanjut (Late Blight) yang berbahaya. "
        "Segera lakukan penanganan intensif:\n"
        "Semprot tanaman dengan fungisida sistemik seperti metalaksil atau fosetil-Al sesuai anjuran.\n"
        "Cabut dan musnahkan bagian tanaman yang parah terinfeksi agar tidak menular ke tanaman lain.\n"
        "Perbaiki drainase lahan untuk mencegah kelembaban berlebih.\n"
        "Lakukan rotasi tanaman (misalnya dengan jagung atau kacang-kacangan) pada musim berikutnya untuk memutus siklus penyakit.\n"
        "Jika serangan sangat luas, konsultasikan dengan penyuluh pertanian untuk strategi pengendalian terpadu."
    )

    return jsonify({
        "prediction": label,
        "confidence": confidence,
        "advice": advice
    })

if __name__ == "__main__":
    app.run(debug=True)

