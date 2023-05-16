from flask import Flask, jsonify, request
from settings import connection, handle_exceptions,logger
from datetime import date

app = Flask(__name__)


# add room
@app.route("/room", methods=["POST"])
@handle_exceptions
def room_booking():
    cur, conn = connection()
    logger(__name__).warning("starting the database connection")
    if "room_type" and "availability" not in request.json:
        raise Exception("data missing")
    room_type = request.json['room_type']
    availability = request.json['availability']
    cur = conn.cursor()
    cur.execute("INSERT INTO room (room_type, availability) VALUES (%s, %s)", (room_type, availability))
    conn.commit()
    logger(__name__).warning("stoping the database connection")
    return "room is added"


# check room availability
@app.route("/room_availability", methods=["GET"], endpoint="room_availability")
def room_availability():
    cur, conn = connection()
    logger(__name__).warning("starting the database connection")
    cur.execute("SELECT room_type,availability FROM room WHERE availability = TRUE")
    rows = cur.fetchall()
    if not rows:
        return jsonify({"message": f"No rows found "})
    data_list = []
    for row in rows:
        room_type, availability = row
        data = {
            "room_type": room_type,
            "availability": availability
        }
        data_list.append(data)
    logger(__name__).warning("stoping the database connection")
    return jsonify({"message": "available rooms", "details": data_list})


# all rooms details
@app.route("/all_rooms", methods=["GET"], endpoint="all_rooms")
def room_availability():
    cur, conn = connection()
    logger(__name__).warning("starting the database connection")
    cur.execute("SELECT * FROM room ")
    rows = cur.fetchall()
    if not rows:
        return jsonify({"message": f"No rows found "})
    data_list = []
    for row in rows:
        room_id,room_type, availability = row
        data = {
            "room_id": room_id,
            "room_type": room_type,
            "availability": availability
        }
        data_list.append(data)
    logger(__name__).warning("stoping the database connection")
    return jsonify({"message": "all rooms", "details": data_list})


# bookings
@app.route("/room/bookings",methods=["POST"],endpoint="create_bookings")
@handle_exceptions
def create_bookings():
    cur, conn = connection()
    if "room_type" and "guest_name" and "checkin_date" and "checkout_date" not in request.json:
        raise Exception("data missing")
    logger(__name__).warning("starting the database connection")
    data = request.get_json()
    room_type = data['room_type']
    guest_name = data['guest_name']
    checkin_date = data['checkin_date']
    checkout_date = data['checkout_date']
    cur.execute("INSERT INTO bookings (room_type, guest_name, checkin_date, checkout_date) VALUES (%s, %s, %s, %s)",
                (room_type, guest_name, checkin_date, checkout_date))
    conn.commit()
    logger(__name__).warning("stoping the database connection")
    return jsonify({"message": "Booking created successfully"})


# update availability
@app.route("/rooms/update/<int:room_id>", methods=["PUT"], endpoint="update_availability")
def update_availability(room_id):
    cur, conn = connection()
    logger(__name__).warning("starting the database connection")
    data = request.get_json()
    availability = data['availability']
    cur.execute('SELECT availability FROM room WHERE room_id= %s', (room_id,))
    row = cur.fetchone()
    if not row:
        return jsonify({'message': 'room_id is not available'}), 400

    # Update the book's availability
    cur.execute('UPDATE room SET availability=%s  WHERE room_id= %s', (availability,room_id,))
    conn.commit()

    return jsonify({'message': 'updated successfully'}), 200

@app.route("/delete/<int:room_id>",methods=["DELETE"],endpoint="delete_room")
def delete_room(room_id):
    cur, conn = connection()
    logger(__name__).warning("starting the database connection")
    cur.execute('DELETE FROM room WHERE room_id=%s', (room_id,))
    logger(__name__).warning("close the database connection")
    conn.commit()
    if cur.rowcount > 0:
        return jsonify({"message": "room deleted successfully"})
    else:
        return jsonify({"message": "room_id  not found"})




# cancel bookings
@app.route("/room/<int:booking_id>",methods=["DELETE"],endpoint="delete_booking")
@handle_exceptions
def delete_booking(booking_id):
    cur, conn = connection()
    logger(__name__).warning("starting the database connection")
    cur.execute("SELECT * FROM bookings WHERE booking_id = %s", (booking_id,))
    booking = cur.fetchone()
    if booking:
        cur.execute("DELETE FROM bookings WHERE booking_id = %s", (booking_id,))
        conn.commit()
        logger(__name__).warning("stoping the database connection")
        return jsonify({"message": "Booking canceled successfully"})
    else:
        raise jsonify({"message": "Booking not found"})
