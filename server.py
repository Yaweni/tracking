from flask import Flask, render_template, request, jsonify
from flask_mysqldb import MySQL
from datetime import datetime

app = Flask(__name__)

# Configure MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = 'Passw0rd'
app.config['MYSQL_DB'] = 'software_tracking'

mysql = MySQL(app)

# Routes
@app.route('/update_status', methods=['POST'])
def update_status():
    data = request.get_json()
    computer_name = data['computer_name']
    username = data['username']
    software_statuses = data['software_status']

    # Get user and computer IDs from the database
    user_id = get_user_id(username)
    computer_id = get_computer_id(computer_name)
    for track in software_statuses:
        software_id = get_software_id(track[0])
        software_status = track[1]
        # Update runtime_logs table
        update_runtime_logs(user_id, computer_id,software_id, software_status)

    return jsonify({'message': 'Status updated successfully'}), 200

# Helper functions
def get_user_id(username):
    cur = mysql.connection.cursor()
    cur.execute("SELECT user_id FROM users WHERE username = %s", (username,))
    user_id = cur.fetchone()[0]
    cur.close()
    return user_id

def get_computer_id(computer_name):
    cur = mysql.connection.cursor()
    cur.execute("SELECT computer_id FROM computers WHERE computer_name = %s", (computer_name,))
    computer_id = cur.fetchone()[0]
    cur.close()
    return computer_id

def get_software_id(software_name):
    cur = mysql.connection.cursor()
    cur.execute("SELECT software_id FROM tracked_software WHERE software_name = %s", (software_name,))
    software_id = cur.fetchone()[0]
    cur.close()
    return software_id

def update_runtime_logs(user_id, computer_id, software_id,software_status):
    cur = mysql.connection.cursor()
    software_status = 'online' if software_status else 'offline'

    # Check if there's an entry for the current user, computer, and software on the current date
    cur.execute("SELECT log_id FROM runtime_logs WHERE user_id = %s AND computer_id = %s AND software_id = %s AND DATE(log_date) = CURDATE()",
                (user_id, computer_id,software_id))
    log_id = cur.fetchone()
    if software_status == 'online':

        if log_id:
            # Update existing entry
            cur.execute("UPDATE runtime_logs SET runtime_minutes = runtime_minutes + 5, status = %s WHERE log_id = %s",
                        (software_status, log_id))
        else:
            # Insert new entry
            cur.execute("INSERT INTO runtime_logs (user_id, computer_id,software_id, status, runtime_minutes) VALUES (%s, %s, %s, %s, 5)",
                        (user_id, computer_id, software_status))
    else:
        if log_id:
            cur.execute("UPDATE runtime_logs SET status = %s WHERE log_id = %s",
                        (software_status, log_id))

    mysql.connection.commit()
    cur.close()

if __name__ == '__main__':
    app.run(debug=True)
