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

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # Handle registration logic here
        return redirect(url_for('index'))
    return render_template("signup.html")

@app.route("/send-otp", methods=["POST"])
def send_otp():
    return jsonify({"success": False, "message": "Disabled"}), 403

@app.route("/verify-otp", methods=["POST"])
def verify_otp():
    return jsonify({"success": False, "message": "Disabled"}), 403

@app.route("/api/user/balance")
def get_balance():
    return jsonify({"balance": 0.0, "error": "Disabled"}), 403

@app.route("/")
def index():
    # Force direct rendering of landing to avoid any redirect issues on Render
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
