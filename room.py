import random
from app import db
from models import Room

def get_bingo_card(room_id):
    """Generates a random 5x5 Bingo card (with center FREE space)"""
    # Define ranges for each column (B, I, N, G, O)
    ranges = {
        'B': range(1, 16),
        'I': range(16, 31),
        'N': range(31, 46),
        'G': range(46, 61),
        'O': range(61, 76)
    }
    
    card = []
    # Generate 5 numbers for each column range
    cols = []
    for char in ['B', 'I', 'N', 'G', 'O']:
        nums = random.sample(ranges[char], 5)
        cols.append(nums)
        
    # Transpose to get rows
    for r in range(5):
        row = []
        for c in range(5):
            if r == 2 and c == 2:
                row.append(0)  # Center FREE space
            else:
                row.append(cols[c][r])
        card.append(row)
    
    return card

def initialize_rooms():
    """Ensures exactly three rooms exist: 5, 10, and 20 ETB"""
    existing_rooms = Room.query.all()
    room_data = [
        {"name": "Bronze Room", "card_price": 5.0},
        {"name": "Silver Room", "card_price": 10.0},
        {"name": "Gold Room", "card_price": 20.0}
    ]
    
    # If room count isn't 3, reset them
    if len(existing_rooms) != 3:
        # Clear existing
        for r in existing_rooms:
            db.session.delete(r)
        db.session.commit()
        
        # Create new ones
        for data in room_data:
            new_room = Room(name=data["name"], card_price=data["card_price"])
            db.session.add(new_room)
        db.session.commit()

def get_room_by_id(room_id):
    """Isolates room data using ID"""
    return Room.query.get(room_id)

def get_room_by_price(price):
    """Isolates room data using price/amount"""
    return Room.query.filter_by(card_price=float(price)).first()
