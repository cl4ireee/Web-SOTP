from flask import Flask, render_template, request, redirect, url_for, flash
import requests
import uuid
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Lokasi file penyimpanan key di komputer user
KEY_FILE = "user_key.txt"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/YoshCasaster/verifikasi-sotp/refs/heads/main/valid_keys.txt"
JSON_CONFIG_URL = "https://raw.githubusercontent.com/YoshCasaster/verifikasi-sotp/main/otp_config.json"

# Fungsi untuk membuat key baru
def create_key():
    new_key = str(uuid.uuid4())  # Membuat key unik
    with open(KEY_FILE, 'w') as key_file:
        key_file.write(new_key)  # Menyimpan key ke file
    return new_key

# Fungsi untuk membaca key dari file lokal
def read_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, 'r') as key_file:
            return key_file.read().strip()
    return None

# Fungsi untuk memvalidasi key ke GitHub Raw
def validate_key(key):
    try:
        response = requests.get(GITHUB_RAW_URL)
        if response.status_code == 200:
            valid_keys = response.text.splitlines()
            return key in valid_keys
        else:
            return False
    except Exception as e:
        return False

# Fungsi untuk mengirim OTP
def send_otp_requests(phone_number):
    responses = []
    try:
        response = requests.get(JSON_CONFIG_URL)
        config = response.json()

        for item in config:
            api_url = item.get("url")
            data = item.get("data").replace("target_number", phone_number)
            headers = item.get("headers")
            response = requests.post(api_url, headers=headers, data=data)
            responses.append(response.text)
        return responses
    except Exception as e:
        return [f"Gagal mengambil konfigurasi OTP: {e}"]

@app.route('/', methods=['GET', 'POST'])
def home():
    key = read_key()
    if not key:
        key = create_key()

    if request.method == 'POST':
        phone_number = request.form['phone']
        if validate_key(key):
            otp_responses = send_otp_requests(phone_number)
            return render_template('home.html', responses=otp_responses, key=key, key_valid=True)
        else:
            flash('Key tidak valid, silakan perbarui.')
            return redirect(url_for('home'))

    return render_template('home.html', key=key, key_valid=validate_key(key))

if __name__ == '__main__':
    app.run(debug=True)
