import random
from app import db
from models import Room

def get_bingo_card(user_id, room_id):
    """Generates a random 5x5 Bingo card and links it to a specific room"""
    ranges = {
        'B': range(1, 16),
        'I': range(16, 31),
        'N': range(31, 46),
        'G': range(46, 61),
        'O': range(61, 76)
    }
    
    cols = []
    for char in ['B', 'I', 'N', 'G', 'O']:
        nums = random.sample(ranges[char], 5)
        cols.append(nums)
        
    card_data = []
    for r in range(5):
        row = []
        for c in range(5):
            if r == 2 and c == 2:
                row.append(0)  # Center FREE space
            else:
                row.append(cols[c][r])
        card_data.append(row)
    
    # እዚህ ጋር ነው ካርዱን ከሩሙ ጋር የምናቆራኘው
    return card_data

def initialize_rooms():
    """strictly ensures only 5, 10, and 20 ETB rooms exist"""
    room_data = [
        {"name": "Bronze Room", "card_price": 5.0},
        {"name": "Silver Room", "card_price": 10.0},
        {"name": "Gold Room", "card_price": 20.0}
    ]
    
    # ሁሉንም አጥፍቶ በአዲስ መጀመር (Clean Slate)
    try:
        Room.query.delete() 
        db.session.commit()
        
        for data in room_data:
            new_room = Room(name=data["name"], card_price=data["card_price"])
            db.session.add(new_room)
        db.session.commit()
        print("Rooms initialized: 5, 10, 20 only.")
    except Exception as e:
        db.session.rollback()
        print(f"Error initializing rooms: {e}")

def get_room_by_id(room_id):
    return Room.query.get(room_id)

def get_room_by_price(price):
    # ዋጋውን ወደ float ቀይሮ በትክክል ፊልተር ማድረግ
    return Room.query.filter_by(card_price=float(price)).first()
