from flask import Flask, request, jsonify
from flask_cors import CORS
import yagmail
import mysql.connector
import secrets
from urllib.parse import urlencode

app = Flask(__name__)
CORS(app)

app.secret_key = 'inderkiran@24'

def connect_to_database():
    try:
        # MySQL database configuration
        DB_HOST = '217.21.94.103'
        DB_NAME = 'u813060526_gameathonregis'
        DB_USER = 'u813060526_gameathonregis'
        DB_PASSWORD = '135@Hack'

        # Connect to the MySQL database
        conn = mysql.connector.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
        cursor = conn.cursor()

        cursor.execute("CREATE TABLE IF NOT EXISTS UniqueIGN (ign VARCHAR(255) UNIQUE)")
        conn.commit()

        cursor.execute('''CREATE TABLE IF NOT EXISTS BGMIregistrations (
            team_name VARCHAR(255) PRIMARY KEY,
            college_name VARCHAR(255),
            leader_name VARCHAR(255),
            leader_ign VARCHAR(255) UNIQUE,
            leader_game_id VARCHAR(255) UNIQUE,
            leader_id_no VARCHAR(255) UNIQUE,
            leader_contact VARCHAR(255) UNIQUE,
            leader_email VARCHAR(255) UNIQUE,
            p2_name VARCHAR(255),
            p2_ign VARCHAR(255) UNIQUE,
            p2_game_id VARCHAR(255) UNIQUE,
            p2_id_no VARCHAR(255) UNIQUE,
            p2_contact VARCHAR(255) UNIQUE,
            p3_name VARCHAR(255),
            p3_ign VARCHAR(255) UNIQUE,
            p3_game_id VARCHAR(255) UNIQUE,
            p3_id_no VARCHAR(255) UNIQUE,
            p3_contact VARCHAR(255) UNIQUE,
            p4_name VARCHAR(255),
            p4_ign VARCHAR(255) UNIQUE,
            p4_game_id VARCHAR(255) UNIQUE,
            p4_id_no VARCHAR(255) UNIQUE,
            p4_contact VARCHAR(255) UNIQUE
        );''')
        conn.commit()

        return conn, cursor
    except mysql.connector.Error as e:
        print("Error connecting to the database:", e)
        return None, None

def close_database_connection(conn, cursor):
    try:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        print("Database connection closed.")
    except mysql.connector.Error as e:
        print("Error closing database connection:", e)

conn, cursor = connect_to_database()

# Email configuration
sender_email = 'hackoverflow@cumail.in'
app_password = 'lgde lflp hmgu krrd'

email_tokens = {}

def generate_token():
    return secrets.token_hex(16)

def generate_auth_link(token, data):
    auth_link = f'https://bgmiregistration-render.onrender.com/verify/{token}?'
    auth_link += urlencode(data)
    return auth_link

def check_duplicate_ign(data):
    ign_set = set()
    igns = [data['team_name'], data['leader_ign'], data['leader_game_id'], data['leader_id_no'], data['leader_contact'], data['leader_email'], data['p2_ign'], data['p2_game_id'], data['p2_id_no'], data['p2_contact'], data['p3_ign'], data['p3_game_id'], data['p3_id_no'], data['p3_contact'], data['p4_ign'], data['p4_game_id'], data['p4_id_no'], data['p4_contact']]
    field_names = ['Team Name', 'Leader IGN', 'Leader Game ID', 'Leader ID Number', 'Leader Contact', 'Leader Email', 'P2 IGN', 'P2 Game ID', 'P2 ID Number', 'P2 Contact', 'P3 IGN', 'P3 Game ID', 'P3 ID Number', 'P3 Contact', 'P4 IGN', 'P4 Game ID', 'P4 ID Number', 'P4 Contact']
    duplicate_fields = []

    for i, ign in enumerate(igns):
        if ign in ign_set:
            print("Duplicate IGN detected at field", field_names[i], ":", ign)
            duplicate_fields.append(field_names[i])
            ign_set.add(ign)

    for ign in igns:
        cursor.execute("SELECT * FROM UniqueIGN WHERE ign = %s", (ign,))
        result = cursor.fetchone()
        if result:
            print("Duplicate IGN detected:", ign)
            return True, duplicate_fields, ign

    return False, [], ''

@app.route('/')
def index():
    return 'API is working'

@app.route('/submit', methods=['POST'])
def send_email():
    data = request.get_json()
    token = generate_token()

    result, duplicate_fields, duplicate_ign = check_duplicate_ign(data)
    if result:
        if duplicate_fields:
            return jsonify({'message': f'Duplicate data found at {duplicate_fields}: {duplicate_ign}.'}), 400
        else:
            return jsonify({'message': 'Duplicate data detected.'}), 400

    email = data['leader_email']
    email_tokens[email] = token

    auth_link = generate_auth_link(token, data)
    subject = 'Authentication Email for BGMI Registration'
    body = f'''
            <html>
            <head>
                <title>{subject}</title>
            </head>
            <body>
                <h2>Click on the link below to complete your registration:</h2>
                <h2><a href="{auth_link}" >Click Here</a><h2>
            </body>
            </html>
            '''

    try:
        yag = yagmail.SMTP(sender_email, app_password)
        yag.send(to=email, subject=subject, contents=body)
        return jsonify({'message': 'Email sent successfully.'})
    except Exception as e:
        print("Error sending email:", e)
        return jsonify({'message': 'An error occurred while sending the email.'}), 500

@app.route('/verify/<token>', methods=['GET'])
def verify(token):
    try:
        if token in email_tokens.values():
            emails = [key for key, value in email_tokens.items() if value == token][0]
            data = request.args.to_dict()
            uniqueigns = [data['team_name'], data['leader_ign'], data['leader_game_id'], data['leader_id_no'], data['leader_contact'], data['leader_email'], data['p2_ign'], data['p2_game_id'], data['p2_id_no'], data['p2_contact'], data['p3_ign'], data['p3_game_id'], data['p3_id_no'], data['p3_contact'], data['p4_ign'], data['p4_game_id'], data['p4_id_no'], data['p4_contact']]

            for y in uniqueigns:
                cursor.execute("INSERT INTO UniqueIGN (ign) VALUES (%s)", (y,))
            conn.commit()

            cursor.execute("INSERT INTO BGMIregistrations (team_name, college_name, leader_name, leader_ign, leader_game_id, leader_id_no, leader_contact, leader_email, p2_name, p2_ign, p2_game_id, p2_id_no, p2_contact, p3_name, p3_ign, p3_game_id, p3_id_no, p3_contact, p4_name, p4_ign, p4_game_id, p4_id_no, p4_contact) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                           (data['team_name'], data['college_name'], data['leader_name'], data['leader_ign'], data['leader_game_id'], data['leader_id_no'], data['leader_contact'], data['leader_email'], data['p2_name'], data['p2_ign'], data['p2_game_id'], data['p2_id_no'], data['p2_contact'], data['p3_name'], data['p3_ign'], data['p3_game_id'], data['p3_id_no'], data['p3_contact'], data['p4_name'], data['p4_ign'], data['p4_game_id'], data['p4_id_no'], data['p4_contact']))
            conn.commit()

            del email_tokens[emails]
            return 'Authentication successful. You are now registered for BGMI in gameathon.'
        else:
            return jsonify({'message': 'Invalid or expired verification link.'}), 400
    except mysql.connector.Error as e:
        print("Error executing MySQL query:", e)
        return jsonify({'message': 'An error occurred while verifying the token.'}), 500
