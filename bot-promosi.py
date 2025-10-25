import os
import json
import time
import threading
import telebot
from flask import Flask, request

# =========================
# Environment Variables
# =========================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
TARGET_CHAT_ID = int(os.environ.get("-1002604922644", 0))
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # Contoh: https://bot-promosi.onrender.com/webhook

if not BOT_TOKEN or not TARGET_CHAT_ID or not WEBHOOK_URL:
    print("⚠️ BOT_TOKEN, TARGET_CHAT_ID, atau WEBHOOK_URL belum di-set!")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="MarkdownV2")
app = Flask(__name__)

# =========================
# Escape MarkdownV2 Aman
# =========================
def escape_md2(text):
    special_chars = r'\_*[]()~`>#+-=|{}.!'
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text

# =========================
# Escape MarkdownV2 Aman
# =========================
def escape_md2(text):
    special_chars = r'\_*[]()~`>#+-=|{}.!'
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text

# =========================
# PROMO LIST
# =========================
PROMO_LIST = [
    {
        "photo": "https://assetsmac777.com/uploads/gen777/GARANSI100_.jpg",
        "caption": """🔥 *GARANSI 100% KHUSUS MEMBER BARU* 🔥

Bonus *50%* untuk *deposit pertama hari ini!*

Bonus ini berlaku khusus *member baru* yang belum mengambil promosi lain.
Bonus ini berlaku untuk member yang *kalah dari permainan SLOT*.
Untuk claim bonus ini wajib melalui grup Telegram official *GEN777*.

📆 Maksimal claim bonus garansi kekalahan adalah *1x24 jam* setelah periode deposit pertama.
💰 *Syarat withdraw:* saldo garansi harus mencapai minimal *5x (Deposit + Bonus)*.
CONTOH SYARAT WITHDRAW :

Deposit Awal IDR 50.000

Bonus Garansi 100% IDR 50.000

(50.000 + 50.000) x 5 = *500.000 (MINIMAL & MAKSIMAL WITHDRAW)*.
💸Kemenangan dari saldo garansi harus di-withdraw *FULL* dan tidak boleh disisakan dalam akun.

🚫 Promosi tidak berlaku untuk deposit via *Pulsa*.
❗ Bonus & kemenangan dibatalkan jika ada indikasi kecurangan atau multi akun.
Keputusan *GEN777* bersifat mutlak dan tidak dapat diganggu gugat."""
    },
    {
        "photo": "https://assetsmac777.com/uploads/gen777/NEWMEMBER30_.jpg",
        "caption": """🎯 *BONUS NEW MEMBER 30%* 🎯

Bonus *30%* berlaku untuk semua *member baru*!
Bisa digunakan di permainan *Sportbook*, *Slot Game*, dan *Tembak Ikan*.

❌ Tidak berlaku untuk *Togel*, *Live Casino*, dan *Sabung Ayam*.
🎟️ *Kode Promo:* `NEW30`

💰 Minimal deposit Rp *50.000* untuk mendapatkan bonus *30%* (maksimal bonus *Rp 500.000*).
📊 *Syarat withdraw:* TurnOver harus mencapai *10x* dari nilai deposit + bonus.

Member yang mengambil bonus *tidak mendapat rollingan dan cashback mingguan* dalam periode tersebut.
Bonus ini hanya berlaku untuk *1 username, nama rekening, IP, device, dan browser*.

🚫 Jika terdeteksi kecurangan, saldo & bonus akan ditahan dan user bisa di-*lock permanen*."""
    },
    {
        "photo": "https://assetsmac777.com/uploads/gen777/BONUSPENASARAN.jpg",
        "caption": """💥 *GARANSI PENASARAN 50%* 💥

_Bonus ini berlaku untuk deposit kedua dan ketiga akun baru di GEN777._

Untuk claim bonus ini:
- Saldo deposit harus habis
- Saldo akun kurang dari _Rp 5.000_
- Maksimal garansi diberikan *Rp 100.000*

🕧 Maksimal claim bonus garansi penasaran adalah 1x24 jam setelah periode deposit pertama.
💰 Berlaku untuk member yang kalah dari permainan *SLOT*.
📨 Claim wajib melalui grup Telegram official *GEN777*.

*Syarat withdraw:* saldo garansi minimal *4x (Deposit + Bonus)*.
Kemenangan dari saldo garansi wajib di-withdraw *FULL*.

🚫 Tidak berlaku untuk deposit via Pulsa.
❗ Keputusan *GEN777* bersifat mutlak."""
    },
    {
        "photo": "https://assetsmac777.com/uploads/gen777/DEPOSITPULSA.jpg",
        "caption": """💥 *DEPOSIT PULSA TANPA POTONGAN* 💥

Promo ini berlaku untuk semua member *GEN777* 🎉
TurnOver dikenakan *x5* dari total deposit.

📱 Provider yang diterima: *Telkomsel*
💰 Minimal deposit: *Rp 10.000*

Deposit bisa melalui *transfer pulsa* atau *isi ulang (SN)*.
Claim wajib di menu *Deposit* saat mengisi form.

❗ Jika tidak melampirkan bukti, deposit tidak akan diproses.
💸 Penarikan hanya melalui *Bank* dan *E-wallet* terdaftar.

🔁 Syarat dan ketentuan dapat berubah sewaktu-waktu."""
    },
    {
        "photo": "https://assetsmac777.com/uploads/gen777/BONUSLUCKYWHEEL.jpg",
        "caption": """🎡 *PUTAR RODA HOKI GEN777!* 🎡

Event *Spin Gratis* berhadiah *iPhone 14 Pro Max!* 📱🔥

💰 Minimal deposit: *Rp 250.000* = 1 tiket
🎰 TurnOver x1 dari deposit (hanya permainan *SLOT*)

📲 Claim kode kupon via *WhatsApp Official GEN777*.
Hadiah utama:
- 🏍️ *Motor N-Max*
- 📱 *iPhone 14 Pro Max*

🎁 Bonus bisa diambil *setiap hari* (tidak digabung Mystery Box).
🕛 Tiket berlaku sampai *23:59 WIB* — lewat dari itu *hangus*.

📸 Upload screenshot kemenangan di *Facebook Group GEN777 Official* dengan tagar:
`#GEN777 #RODAGEN777`

⚖️ Keputusan *GEN777* bersifat mutlak dan tidak dapat diganggu gugat."""
    },
    {
        "photo": "https://assetsmac777.com/uploads/asiahoki/GEN777_PROMO_1.png",
        "caption": """♨️ *BONUS HARIAN DAN MINGGUAN!* ♨️

*BONUS ROLLINGAN HARIAN* 🎰🔥

💰 Bonus rollingan CASINO 1% TANPA BATAS.
🎰 Bonus rollingan SLOT 0.8% TANPA BATAS.

📲 Bonus akan dibagikan setiap hari pukul 14:00 WIB.

🎁 Bonus akan dihitung otomatis oleh sistem dan masuk secara otomatis ke masing-masing akun tanpa harus diclaim.
🕛 Bonus akan dibagikan setiap hari pukul 14:00 WIB.

🎰 Rollingan yang dibagikan di hari ini merupakan perhitungan rollingan dari hari kemarin.

*BONUS CASHBACK MINGGUAN*

🎁 Bonus cashback SLOT 5% TANPA BATAS.
🎁 Bonus cashback SPORTSBOOK 7% TANPA BATAS.
⏳ Bonus akan dibagikan setiap hari senin pukul 14:00 WIB.
💸 Bonus akan dihitung otomatis oleh sistem dan masuk secara otomatis ke masing-masing akun tanpa harus diclaim.
🎰 Cashback yang dibagikan di hari senin merupakan perhitungan cashback dari total kekalahan minggu kemarin."""
    },
    {
        "photo": "https://assetsmac777.com/uploads/asiahoki/GEN777_PROMO.png",
        "caption": """🕧 *BONUS PAKET MALAM* 🕧

*BEBAS IP!!!* 🎰🔥

💰 Minimal deposit untuk mengikuti event ini adalah sebesar *IDR 40,000*. (maksimal bonus *Rp 30.000*).
📊 Event berlaku untuk semua member yang belum claim bonus deposit apapun.

📲 Event berlaku setiap hari dan hanya di jam 00.00 - 05.00 wib.

🎁 Bonus Deposit berlaku di semua game SLOT.
🎰 Claim event di grup telegram official GEN777.
⏳ Syarat melakukan WD wajib mencapai target turnover x7 dari (Deposit + Bonus).
💸 Bonus akan dihitung otomatis oleh sistem dan masuk secara otomatis ke masing-masing akun tanpa harus diclaim.
🔥 Pihak GEN777 berhak membatalkan, mencabut, menarik bonus dan kemenangan jika terjadinya Bonus hunter dan kecurangan lainnya."""
    },
    {
        "photo": "https://assetsmac777.com/uploads/asiahoki/gen77_promo_2.png",
        "caption": """🎗️ *BONUS SCATTER MAHJONG* 🎗️

*CLAIM 5X PERHARI* 🎰🔥

🎰 Event ini berlaku untuk game Mahjong Ways 1 dan Mahjong Ways 2 pada provider PG Soft.
📊 1 hari maksimal claim 5x per user id.

⏳ Untuk claim bonus, saldo tidak boleh dimainkan terlebih dahulu setelah freespin selesai, dan harus menunggu sampai bonus selesai diclaim.

🎁 Cara Claim : Member harus mengirim bukti Screenshot Kemenangan Freespin dan riwayat taruhan di grup facebook kami dengan hashtag #CLAIMSCATTERMAHJONGWAYS #PROMOSLOT #GEN777 lalu screenshot semua bukti ke grup telegram kami.
🎰 Promo ini tidak dapat digabungkan dengan promo lainnya di hari yang sama.
🔥 Bonus & Kemenangan di batalkan apabila ditemukan adanya indikasi kecurangan, Memiliki banyak akun, keputusan GEN777 adalah mutlak dan tidak dapat diganggu gugat."""
    },
    {
        "photo": "https://assetsmac777.com/uploads/asiahoki/gen_promo_3.png",
        "caption": """✨ *BONUS NEXT DEPOSIT AMBYARRR 5%* ✨

*CLAIM 5X PERHARI* 🎰🔥

🚀 Berlaku untuk semua member lama GEN777
♨️ Bonus akan diberikan di Awal dan Wajib claim bonus saat melakukan pengisian form deposit
💸 Minimal deposit untuk mendapatkan bonus adalah *IDR 20.000* dan Maximal bonus yang di berikan *IDR 100.000*
🎰 Promo hanya berlaku untuk permainan SLOTS

🎁 Promo ini bisa diclaim tanpa batasan setiap harinya.

🕧 Apabila ada kesamaan IP / menggunakan IP luar negri & melanggar ketentuan yang berlaku. Maka semua bonus dan kemenangan akan ditarik, lalu deposit dikembalikan.
🔥 Member yang mengikuti promo ini tidak mendapatkan bonus lainnya seperti cashback, refferal, turnover / rollingan.
📱 Syarat dan ketentuan umum GEN777 berlaku."""
    },
    {
        "photo": "https://assetsmac777.com/uploads/asiahoki/birthday_gidt.png",
        "caption": """🔥 *BIRTHDAY GIFT FROM GEN777* 🔥

*SYARAT DAN KETENTUAN :* 🎰🔥

♨️ Bonus presentase di berikan sesuai Tanggal lahir Bulan Berjalan 
💸 Wajib Share Promo apapun yang tersedia di GEN777 minimal ke 5  Grup / Komunitas
🎰 Jika Tanggal lahir 25 febuari 1980 maka bonus yang di berikan adalah *25%* dari deposit terakhir, 

🎁 apabila Berulang tahun di 15 Januari 1980, dan member claim di tanggal 18 Januari maka tidak bisa diproseskan, karena Tidak sesuai Tanggal .

🕧 Nama yang terdaftar di Akun ID anda harus sesuai dengan nama di Identitas yang berlaku.
🔥 Promo ini berlaku untuk semua member GEN777 yang Berulang Tahun pada hari tersebut.
📱 Claim Promo Birthday bisa melalui Whatsapp Official GEN777 dengan Melampirkan Bukti Share dan Identitas Diri yang berlaku"""
    },
    {
        "photo": "https://assetsmac777.com/uploads/asiahoki/diskon_tanggal_tua.png",
        "caption": """🥵 *BONUS TANGGAL TUA* 🥵

*DISKON DEPOSIT TANGGAL TUA* 🎰🔥

🎰 Berlaku tanggal setiap tanggal 23 sampai tanggal 1 setiap bulannya
📊 Event berlaku untuk semua member yang belum claim bonus deposit apapun.

⏳ Bonus ini hanya berlaku untuk permainan SLOT.

🎁 Untuk melakukan withdraw, turnover harus mencapai x6 dari total saldo yang didapatkan.
🎰 Maksimal claim 2x sehari per user id.
🔥 Pihak GEN777 berhak membatalkan, mencabut, menarik bonus dan kemenangan jika user id gagal memenuhi syarat & ketentuan yang sudah ditetapkan."""
    },
]

# =========================
# Auto Kirim Promo
# =========================
INTERVAL = 600  # detik (10 menit)
INDEX_FILE = "last_index.json"

def load_index():
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, "r") as f:
            return json.load(f).get("index", 0)
    return 0

def save_index(index):
    with open(INDEX_FILE, "w") as f:
        json.dump({"index": index}, f)

def auto_kirim_bergilir():
    index = load_index()
    while True:
        try:
            promo = PROMO_LIST[index]
            bot.send_photo(TARGET_CHAT_ID, promo["photo"], caption=escape_md2(promo["caption"]))
            print(f"[✅] Terkirim promo ke-{index+1}")
            index = (index + 1) % len(PROMO_LIST)
            save_index(index)
        except Exception as e:
            print(f"[⚠️] Gagal kirim promo ke-{index+1}: {e}")
        time.sleep(INTERVAL)

threading.Thread(target=auto_kirim_bergilir, daemon=True).start()

# =========================
# Webhook endpoint
# =========================
@app.route("/webhook", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

# =========================
# Command /set_webhook
# =========================
@app.route("/set_webhook", methods=["GET"])
def set_webhook():
    bot.remove_webhook()
    status = bot.set_webhook(url=WEBHOOK_URL)
    return f"Webhook status: {status}", 200

# =========================
# Jalankan Flask
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

