# File: test_endpoint.py
import boto3
import json

ENDPOINT_NAME = "coqui-tts-endpoint" # Pastikan nama ini sama
REGION_NAME = "ap-southeast-1" # Ganti dengan region Anda

# Inisialisasi klien SageMaker
sagemaker_runtime = boto3.client("sagemaker-runtime", region_name=REGION_NAME)

# Siapkan payload
payload = {
    "text": "Halo, ini adalah pengujian suara dari Amazon SageMaker."
}

# Panggil endpoint
response = sagemaker_runtime.invoke_endpoint(
    EndpointName=ENDPOINT_NAME,
    ContentType="application/json",
    Body=json.dumps(payload)
)

# Respons berisi streaming audio, simpan ke file
with open("output_sagemaker.wav", "wb") as f:
    f.write(response["Body"].read())

print("✅ Sukses! Audio disimpan sebagai 'output_sagemaker.wav'")
