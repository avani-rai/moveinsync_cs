import mysql.connector
import json
import math
from flask import Flask, request, jsonify, render_template
from flask_login import login_user, logout_user, login_required, UserMixin

app = Flask(__name__)

# Database connection
db = mysql.connector.connect(
  host='localhost',
  user='root',
  password='password',
  database='floor_plan_db'
)

cursor = db.cursor()

# User model
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

# FloorPlan class
class FloorPlan:
    def __init__(self, id, version, timestamp, data, user_id):
        self.id = id
        self.version = version
        self.timestamp = timestamp
        self.data = data
        self.user_id = user_id

# MeetingRoom class
class MeetingRoom:
    def __init__(self, id, capacity, location, availability):
        self.id = id
        self.capacity = capacity
        self.location = location
        self.availability = availability

# Conflict resolution mechanism
def resolve_conflict(floor_plan1, floor_plan2):
    if floor_plan1['version'] == floor_plan2['version']:
        if floor_plan1['timestamp'] == floor_plan2['timestamp']:
            if floor_plan1['user_id'] == admin_id:
                return floor_plan1
            elif floor_plan2['user_id'] == admin_id:
                return floor_plan2
        elif floor_plan1['timestamp'] > floor_plan2['timestamp']:
            return floor_plan1
        else:
            return floor_plan2
    else:
        
        print('Merge logic not implemented')

# Offline mechanism for admins
def store_changes_locally(changes):
    with open('floor_plan_changes.json', 'w') as f:
        json.dump(changes, f)

def sync_changes():
    with open('floor_plan_changes.json', 'r') as f:
        changes = json.load(f)
    cursor.execute('UPDATE floor_plans SET data = %s WHERE id = %s', (changes, floor_plan_id))
    db.commit()
    print('Changes synchronized successfully')

# Meeting room optimization
def recommend_meeting_room(participants, location):
    cursor.execute('SELECT * FROM meeting_rooms WHERE availability = 1 AND capacity >= %s', (participants,))
    meeting_rooms = cursor.fetchall()
    proximity_scores = []
    for meeting_room in meeting_rooms:
        distance = calculate_distance(location, meeting_room[2])
        proximity_score = 1 / (1 + math.exp(-distance))
        proximity_scores.append((meeting_room, proximity_score))
    recommended_meeting_room = max(proximity_scores, key=lambda x: x[1])[0]
    print(f'Recommended meeting room: {recommended_meeting_room[0]}')

def calculate_distance(location1, location2):
    # when we are given the data, we can use math to calculate distance
    print('Distance calculation logic not implemented')

# API endpoints
@app.route('/upload-floor-plan', methods=['POST'])
def upload_floor_plan():
    floor_plan = request.get_json()
    cursor.execute('INSERT INTO floor_plans SET ?', floor_plan)
    db.commit()
    return jsonify({'message': 'Floor plan uploaded successfully'})

@app.route('/update-floor-plan', methods=['POST'])
def update_floor_plan():
    floor_plan = request.get_json()
    cursor.execute('UPDATE floor_plans SET data = %s WHERE id = %s', (floor_plan['data'], floor_plan['id']))
    db.commit()
    return jsonify({'message': 'Floor plan updated successfully'})

@app.route('/book-meeting-room', methods=['POST'])
def book_meeting_room():
    booking = request.get_json()
    cursor.execute('INSERT INTO bookings SET ?', booking)
    db.commit()
    return jsonify({'message': 'Meeting room booked successfully'})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('index'))
        else:
            return 'Invalid username or password', 401
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
