import os
import torch
from flask import Flask, request, jsonify, send_file
from TTS.api import TTS

# Inisialisasi aplikasi Flask
app = Flask(__name__)

# Path tempat model akan disimpan di dalam kontainer
MODEL_PATH = "/opt/ml/model"

# Variabel global untuk menyimpan model yang sudah di-load
tts_model = None

def load_model():
    """Memuat model Coqui TTS ke memori."""
    global tts_model
    if tts_model is None:
        print("Model belum di-load, memulai proses loading...")

        # Cek apakah GPU tersedia
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Menggunakan device: {device}")

        # Inisialisasi model TTS. Gunakan model XTTS v2 yang bagus untuk cloning.
        # Model akan di-download otomatis saat pertama kali dijalankan.
        tts_model = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
        print("Model Coqui TTS berhasil di-load.")
    return tts_model

# Load model saat aplikasi pertama kali dimulai
load_model()

@app.route("/ping", methods=["GET"])
def ping():
    """Endpoint untuk health check SageMaker."""
    return jsonify(status="ok"), 200

@app.route("/invocations", methods=["POST"])
def invocations():
    """Endpoint utama untuk inference."""
    try:
        if not request.is_json:
            return jsonify(error="Request must be JSON"), 400

        data = request.get_json()
        text_to_speak = data.get("text")

        if not text_to_speak:
            return jsonify(error="JSON payload must contain 'text' field"), 400

        print(f"Menerima permintaan untuk teks: '{text_to_speak}'")

        # Path untuk menyimpan output audio sementara
        output_path = "/tmp/output.wav"

        # Gunakan model untuk sintesis suara
        # Untuk voice cloning, Anda akan menambahkan parameter speaker_wav
        tts_model.tts_to_file(
            text=text_to_speak,
            file_path=output_path,
            speaker="Ana Florence", # Contoh speaker bawaan
            language="id" # Bahasa Indonesia
        )

        print(f"Audio berhasil dibuat di {output_path}")

        # Mengirim file audio kembali sebagai response
        return send_file(output_path, mimetype="audio/wav")

    except Exception as e:
        print(f"Error saat inference: {e}")
        return jsonify(error=str(e)), 500
