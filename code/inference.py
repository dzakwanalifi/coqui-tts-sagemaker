import os
import torch
from flask import Flask, request, jsonify, send_file

# Set environment variable to automatically accept Coqui TTS terms
os.environ["COQUI_TOS_AGREED"] = "1"

# Handle PyTorch 2.6 weights_only issue for TTS models
import torch.serialization
try:
    # Try to import and add safe globals for TTS configs and models
    from TTS.tts.configs.xtts_config import XttsConfig
    from TTS.tts.models.xtts import XttsAudioConfig
    torch.serialization.add_safe_globals([XttsConfig, XttsAudioConfig])
except ImportError:
    # Fallback if the import fails
    pass

from TTS.api import TTS

app = Flask(__name__)

MODEL_PATH = "/opt/ml/model"

tts_model = None
def load_model():
    """Memuat model Coqui TTS ke memori."""
    global tts_model
    if tts_model is None:
        print("Model belum di-load, memulai proses loading...")
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Menggunakan device: {device}")
        
        
        tts_model = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
        print("Model Coqui TTS berhasil di-load.")
    return tts_model

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
        
        output_path = "/tmp/output.wav"
        
        
        tts_model.tts_to_file(
            text=text_to_speak,
            file_path=output_path,
            speaker="Ana Florence", 
            language="id" 
        )
        print(f"Audio berhasil dibuat di {output_path}")
        
        return send_file(output_path, mimetype="audio/wav")
    except Exception as e:
        print(f"Error saat inference: {e}")
        return jsonify(error=str(e)), 500
