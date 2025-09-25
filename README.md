# Coqui TTS SageMaker Serverless Deployment

Panduan lengkap untuk mendeploy Coqui TTS ke AWS SageMaker Serverless Inference.

## Struktur Proyek

```
coqui-sagemaker/
├── model/                 # Kosongkan dulu, untuk file model nanti
├── code/
│   ├── inference.py      # Skrip Python untuk inference
│   └── requirements.txt  # Dependencies Python
├── Dockerfile            # Resep untuk membangun kontainer
├── test_endpoint.py      # Script untuk testing endpoint
└── README.md            # Dokumentasi ini
```

## Prasyarat

1. **Akun AWS** dengan izin ke ECR dan SageMaker
2. **AWS CLI** terinstal dan terkonfigurasi
3. **Docker** terinstal dan berjalan

## Langkah Deployment

### 1. Build dan Push Docker Image

```bash
# Login ke ECR (ganti YOUR_REGION dan YOUR_AWS_ACCOUNT_ID)
aws ecr get-login-password --region YOUR_REGION | docker login --username AWS --password-stdin YOUR_AWS_ACCOUNT_ID.dkr.ecr.YOUR_REGION.amazonaws.com

# Buat repository ECR
aws ecr create-repository --repository-name coqui-tts-serverless --image-scanning-configuration scanOnPush=true

# Build image
docker build -t coqui-tts-serverless .

# Tag dan push image
docker tag coqui-tts-serverless:latest YOUR_AWS_ACCOUNT_ID.dkr.ecr.YOUR_REGION.amazonaws.com/coqui-tts-serverless:latest
docker push YOUR_AWS_ACCOUNT_ID.dkr.ecr.YOUR_REGION.amazonaws.com/coqui-tts-serverless:latest
```

### 2. Deploy di AWS SageMaker

1. Buka **AWS Management Console** → **SageMaker**
2. **Inference > Models** → **Create model**
   - Model name: `coqui-tts-model`
   - Container image URI: `YOUR_AWS_ACCOUNT_ID.dkr.ecr.YOUR_REGION.amazonaws.com/coqui-tts-serverless:latest`

3. **Inference > Endpoints** → **Create endpoint**
   - Endpoint name: `coqui-tts-endpoint`
   - Pilih model yang sudah dibuat
   - **Edit model** → **Serverless**
   - Memory size: **6144 MB (6 GB)**
   - Max concurrency: **1**

### 3. Testing Endpoint

Jalankan `test_endpoint.py` untuk menguji endpoint:

```python
# Edit REGION_NAME dan ENDPOINT_NAME sesuai dengan deployment Anda
python test_endpoint.py
```

## Cara Kerja

1. **Serverless Scaling**: SageMaker hanya menjalankan infrastruktur saat ada permintaan
2. **GPU Support**: Kontainer menggunakan NVIDIA CUDA untuk performa optimal
3. **Auto Model Loading**: Model XTTS v2 di-download otomatis saat pertama kali digunakan
4. **Health Check**: Endpoint `/ping` untuk monitoring kesehatan

## Penggunaan Endpoint

```python
import boto3
import json

# Inisialisasi client
sagemaker_runtime = boto3.client("sagemaker-runtime", region_name="YOUR_REGION")

# Payload
payload = {"text": "Teks yang ingin diubah menjadi suara"}

# Panggil endpoint
response = sagemaker_runtime.invoke_endpoint(
    EndpointName="coqui-tts-endpoint",
    ContentType="application/json",
    Body=json.dumps(payload)
)

# Simpan audio
with open("output.wav", "wb") as f:
    f.write(response["Body"].read())
```

## Cost Optimization

- **Pay per millisecond**: Hanya bayar saat model aktif bekerja
- **Auto scale to zero**: Infrastruktur dimatikan saat idle
- **GPU on-demand**: GPU tersedia hanya saat diperlukan

## Troubleshooting

- **Model loading timeout**: Tingkatkan memory size di SageMaker
- **GPU not available**: Pastikan container menggunakan base image NVIDIA CUDA
- **Endpoint not responding**: Cek CloudWatch logs di SageMaker
