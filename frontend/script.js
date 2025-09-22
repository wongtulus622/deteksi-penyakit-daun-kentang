// ==================== PREVIEW GAMBAR (INDEX) ====================
function previewImage(event) {
  const file = event.target.files && event.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = e => {
    const preview = document.getElementById("preview");
    const uploadText = document.getElementById("uploadText");
    const previewContainer = document.getElementById("preview-container");

    preview.src = e.target.result;
    previewContainer.style.display = "flex";
    uploadText.style.display = "none";
  };
  reader.readAsDataURL(file);
}

// ==================== CANCEL PREVIEW ====================
function cancelPreview() {
  const fileInput = document.getElementById("fileInput");
  const previewContainer = document.getElementById("preview-container");
  const uploadText = document.getElementById("uploadText");
  const preview = document.getElementById("preview");

  fileInput.value = "";
  preview.src = "";
  previewContainer.style.display = "none";
  uploadText.style.display = "block";
}

// ==================== ANALISIS FOTO (INDEX) ====================
async function analyzePhoto() {
  const fileInput = document.getElementById("fileInput");
  if (!fileInput || !fileInput.files[0]) {
    alert("Silakan pilih foto terlebih dahulu!");
    return;
  }

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  const reader = new FileReader();
  reader.onload = async function(e) {
    try {
      const response = await fetch("http://127.0.0.1:5000/predict", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("Gagal menganalisis gambar");

      const data = await response.json();
      console.log("Hasil prediksi:", data);

      // ✅ simpan hasil + base64 string
      localStorage.setItem(
        "hasilPrediksi",
        JSON.stringify({
          ...data,
          imageUrl: e.target.result, // base64 string
        })
      );

      // pindah ke halaman hasil
      window.location.href = "hasil.html";
    } catch (err) {
      console.error("Error:", err);
      alert("Terjadi kesalahan saat analisis.");
    }
  };

  reader.readAsDataURL(fileInput.files[0]);
}

// ==================== TAMPILKAN HASIL (HASIL.HTML) ====================
document.addEventListener("DOMContentLoaded", () => {
  if (!window.location.pathname.endsWith("hasil.html")) return;

  const hasil = JSON.parse(localStorage.getItem("hasilPrediksi"));

  // ❌ Jika belum ada hasil, kembalikan ke index.html
  if (!hasil) {
    alert("Silakan upload foto dan lakukan analisis terlebih dahulu!");
    window.location.href = "index.html";
    return;
  }

  const hasilLabel = document.getElementById("hasil-label");
  const progressBar = document.getElementById("progress-bar");
  const rekomendasi = document.getElementById("rekomendasi");
  const img = document.getElementById("hasil-preview");

  // isi data label
  hasilLabel.textContent = `${hasil.prediction} (${hasil.confidence})`;

  // reset class
  hasilLabel.className = "";
  progressBar.className = "progress-bar";

  // tentukan warna berdasarkan label
  if (hasil.prediction.toLowerCase().includes("healthy")) {
    hasilLabel.classList.add("healthy");
    progressBar.classList.add("healthy");
  } else if (hasil.prediction.toLowerCase().includes("early")) {
    hasilLabel.classList.add("early");
    progressBar.classList.add("early");
  } else if (hasil.prediction.toLowerCase().includes("late")) {
    hasilLabel.classList.add("late");
    progressBar.classList.add("late");
  }

  // progress bar
  progressBar.style.width = hasil.confidence;
  progressBar.textContent = `${hasil.prediction} (${hasil.confidence})`;

  // rekomendasi
  rekomendasi.textContent = hasil.advice;

  // preview gambar
  if (img && hasil.imageUrl) {
    img.src = hasil.imageUrl;
    img.style.display = "block";
  }
});
