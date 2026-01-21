import os
import telebot
from flask import render_template, request, jsonify, redirect, url_for
from app import app, db
from models import User, Room, Transaction, GameSession
import random
import requests
from werkzeug.security import generate_password_hash, check_password_hash
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
        session = GameSession()
        session.room_id = room_id
        session.status = 'active'
        db.session.add(session)
        db.session.flush()
        room.active_session_id = session.id
        db.session.commit()
    return session

@app.route("/landing")
def landing():
    return render_template("landing.html")

from werkzeug.security import generate_password_hash, check_password_hash

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            # For now, we redirect to home which shows rooms
            return jsonify({"success": True, "redirect": url_for('index')})
        return jsonify({"success": False, "message": "Invalid username or password"}), 401
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        return redirect(url_for('index'))
    return render_template("signup.html")

@app.route("/send-otp", methods=["POST"])
def send_otp():
    data = request.json
    username = data.get('username')
    telegram_chat_id = data.get('telegram_chat_id')
    
    if not username or not telegram_chat_id:
        return jsonify({"success": False, "message": "Missing username or chat ID"}), 400
        
    otp = str(random.randint(100000, 999999))
    OTPS[telegram_chat_id] = otp
    
    if bot:
        try:
            bot.send_message(telegram_chat_id, f"Your verification code is: {otp}")
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "message": f"Could not send message to Telegram: {str(e)}"}), 500
    
    return jsonify({"success": False, "message": "Bot not initialized"}), 500

@app.route("/verify-otp", methods=["POST"])
def verify_otp():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    telegram_chat_id = data.get('telegram_chat_id')
    otp = data.get('otp')
    
    if OTPS.get(telegram_chat_id) == otp:
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            return jsonify({"success": False, "message": "Username already taken"}), 400
            
        new_user = User()
        new_user.username = username
        new_user.password_hash = generate_password_hash(password)
        new_user.telegram_chat_id = telegram_chat_id
        
        db.session.add(new_user)
        db.session.commit()
        
        # Clear OTP
        del OTPS[telegram_chat_id]
        return jsonify({"success": True})
    
    return jsonify({"success": False, "message": "Invalid verification code"}), 400

@app.route("/api/user/balance")
def get_balance():
    return jsonify({"balance": 0.0, "error": "Disabled"}), 403

@app.route("/")
def index():
    # If user is logged in (conceptually), we would show rooms
    # For now, let's see if we have rooms in the database
    rooms = Room.query.all()
    if rooms:
        return render_template("index.html", rooms=rooms)
    return render_template("landing.html")

@app.route("/buy-card/<int:room_id>", methods=["POST"])
def buy_card(room_id):
    return jsonify({"success": False, "message": "Disabled"}), 403

@app.route("/declare-winner/<int:room_id>", methods=["POST"])
def declare_winner(room_id):
    return jsonify({"success": False, "message": "Disabled"}), 403

@app.route("/admin", methods=["GET", "POST"])
def admin_panel():
    return "Unauthorized", 403

@app.route("/setup-rooms")
def setup_rooms():
    return "Disabled", 403
