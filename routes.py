import os
import telebot
from flask import render_template, request, jsonify, redirect, url_for
from app import app, db
from models import User, Room, Transaction, GameSession
import random
import requests
from werkzeug.security import generate_password_hash
from bot import bot, BOT_TOKEN

@app.route('/webhook/' + (BOT_TOKEN if BOT_TOKEN else 'token'), methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        if bot:
            bot.process_new_updates([update])
        return ''
    else:
        return jsonify({"error": "Forbidden"}), 403

# Temp storage for OTPs
OTPS = {}

def get_or_create_session(room_id):
    room = Room.query.get(room_id)
    if not room:
        return None
    
    session = None
    if room.active_session_id:
        session = GameSession.query.get(room.active_session_id)
        if session and session.status != 'active':
            session = None
            
    if not session:
        session = GameSession(room_id=room_id, status='active')
        db.session.add(session)
        db.session.flush()
        room.active_session_id = session.id
        db.session.commit()
    return session

@app.route("/landing")
def landing():
    return render_template("landing.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/send-otp", methods=["POST"])
def send_otp():
    data = request.json
    telegram_chat_id = data.get("telegram_chat_id")
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")

    if not bot_token:
        return jsonify({"success": False, "message": "Bot token not configured"}), 500

    # 3. MEMBERSHIP CHECK
    check_url = f"https://api.telegram.org/bot{bot_token}/getChatMember?chat_id={telegram_chat_id}&user_id={telegram_chat_id}"
    try:
        res = requests.get(check_url).json()
        if not res.get("ok"):
            return jsonify({"success": False, "message": "እባክዎ መጀመሪያ ቦቱን ይቀላቀሉ (Please start the bot first)"}), 400
    except Exception as e:
        return jsonify({"success": False, "message": f"Connection error: {str(e)}"}), 500

    # 4. OTP PROCESS
    otp = str(random.randint(100000, 999999))
    OTPS[telegram_chat_id] = otp
    
    send_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    requests.post(send_url, json={
        "chat_id": telegram_chat_id,
        "text": f"🎮 ወደ ROYAL BINGO ዌብሳይት ለመግባት የመለያ ማረጋገጫ ኮድዎ: {otp}"
    })
    
    return jsonify({"success": True})

@app.route("/verify-otp", methods=["POST"])
def verify_otp():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    telegram_chat_id = data.get("telegram_chat_id")
    user_otp = data.get("otp")

    if OTPS.get(telegram_chat_id) == user_otp:
        # Prevent duplicates
        existing = User.query.filter_by(telegram_chat_id=telegram_chat_id).first()
        if existing:
            return jsonify({"success": False, "message": "ይህ አካውንት ቀድሞ ተመዝግቧል"}), 400

        try:
            # 5. FINAL SAVE
            new_user = User()
            new_user.username = username
            new_user.telegram_chat_id = telegram_chat_id
            new_user.password_hash = generate_password_hash(password)
            db.session.add(new_user)
            db.session.commit()
            return jsonify({"success": True})
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "message": "Registration failed. Try different username."}), 400
            
    return jsonify({"success": False, "message": "ትክክለኛ ያልሆነ ኮድ"}), 400

@app.route("/api/user/balance")
def get_balance():
    # Hardcoded for the default user as specified in the current index route logic
    user = User.query.filter_by(telegram_chat_id='0980682889').first()
    if user:
        return jsonify({"balance": user.balance})
    return jsonify({"balance": 0.0, "error": "User not found"}), 404

@app.route("/")
def index():
    # Force direct rendering of landing to avoid any redirect issues on Render
    return render_template("landing.html")

@app.route("/buy-card/<int:room_id>", methods=["POST"])
def buy_card(room_id):
    user = User.query.filter_by(telegram_chat_id='0980682889').first()
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404
    
    room = Room.query.get_or_404(room_id)
    session = get_or_create_session(room_id)
    
    if not session:
        return jsonify({"success": False, "message": "Room session error"}), 500
        
    if user.balance >= room.card_price:
        user.balance -= room.card_price
        transaction = Transaction()
        transaction.user_id = user.id
        transaction.room_id = room.id
        transaction.session_id = session.id
        transaction.amount = room.card_price
        db.session.add(transaction)
        db.session.commit()
        
        player_count = db.session.query(db.func.count(db.distinct(Transaction.user_id)))
        player_count = player_count.filter(Transaction.room_id == room.id, Transaction.session_id == session.id).scalar()
        
        house_cut = 0.2
        total_bets = player_count * room.card_price
        prize_amount = total_bets * (1 - house_cut)
        
        return jsonify({
            "success": True, 
            "new_balance": user.balance, 
            "message": f"Purchased card for {room.name}",
            "players": player_count,
            "prize": round(prize_amount, 2),
            "bet": room.card_price
        })
    
    return jsonify({"success": False, "message": "Insufficient balance"}), 400

@app.route("/declare-winner/<int:room_id>", methods=["POST"])
def declare_winner(room_id):
    room = Room.query.get_or_404(room_id)
    if not room.active_session_id:
        return jsonify({"success": False, "message": "No active session"})
        
    session = GameSession.query.get(room.active_session_id)
    if session and session.status == 'active':
        session.status = 'completed'
        room.active_session_id = None
        db.session.commit()
        return jsonify({"success": True, "message": "Game cleared, new session ready."})
    
    return jsonify({"success": False, "message": "No active session"})

@app.route("/admin", methods=["GET", "POST"])
def admin_panel():
    user = User.query.filter_by(telegram_chat_id='0980682889').first()
    if not user or not user.is_admin:
        return "Unauthorized", 403

    if request.method == "POST":
        target_chat_id = request.form.get("chat_id")
        new_balance = request.form.get("balance")
        target_user = User.query.filter_by(telegram_chat_id=target_chat_id).first()
        if target_user:
            target_user.balance = float(new_balance)
            db.session.commit()
            return redirect(url_for('admin_panel'))

    rooms = Room.query.all()
    users = User.query.all()
    return render_template("admin.html", rooms=rooms, users=users)

@app.route("/setup-rooms")
def setup_rooms():
    # Force delete all existing rooms to ensure we only have what we want
    db.session.query(Transaction).delete()
    db.session.query(GameSession).delete()
    db.session.query(Room).delete()
    db.session.commit()
    
    prices = [5.0, 10.0, 20.0]
    for p in prices:
        r = Room()
        r.name = f"{int(p)} ETB Room"
        r.card_price = p
        db.session.add(r)
    db.session.commit()
    return "Rooms setup completed! Only 5, 10, 20 ETB rooms exist now."
