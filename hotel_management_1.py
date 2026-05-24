import mysql.connector
import datetime
from colorama import Fore, Style
print(Fore.CYAN + "="*40)
print("** Hotel Management System **")
print("="*40 + Style.RESET_ALL)

# DB CONNECTION
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Sachin@123"
)

mycursor = mydb.cursor(buffered=True)

# DATABASE SETUP
def setup_database():
    mycursor.execute("CREATE DATABASE IF NOT EXISTS hotel_management")
    mycursor.execute("USE hotel_management")

    mycursor.execute("CREATE TABLE IF NOT EXISTS login(username VARCHAR(25), password VARCHAR(25))")

    mycursor.execute("""CREATE TABLE IF NOT EXISTS rooms(
        room_no INT PRIMARY KEY,
        room_type VARCHAR(25),
        price INT,
        status VARCHAR(25))""")

    mycursor.execute("""CREATE TABLE IF NOT EXISTS customers(
        customer_id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(25),
        age INT,
        gender CHAR(1),
        phone VARCHAR(15))""")

    mycursor.execute("""CREATE TABLE IF NOT EXISTS booking(
        booking_id INT AUTO_INCREMENT PRIMARY KEY,
        customer_id INT,
        room_no INT,
        check_in DATE,
        check_out DATE,
        total_bill INT)""")

    mycursor.execute("CREATE TABLE IF NOT EXISTS room_prices(standard INT, deluxe INT, suite INT)")

    # DEFAULT LOGIN
    mycursor.execute("SELECT * FROM login")
    if not mycursor.fetchone():
        mycursor.execute("INSERT INTO login VALUES(%s,%s)", ("admin", "hotel"))

    # DEFAULT PRICES
    mycursor.execute("SELECT * FROM room_prices")
    if not mycursor.fetchone():
        mycursor.execute("INSERT INTO room_prices VALUES(2000,4000,6000)")

    # DEFAULT ROOMS
    mycursor.execute("SELECT * FROM rooms")
    if not mycursor.fetchone():
        mycursor.execute("INSERT INTO rooms VALUES(101,'standard',2000,'Available')")
        mycursor.execute("INSERT INTO rooms VALUES(102,'Deluxe',4000,'Available')")

    mydb.commit()
    

# CHECK-IN
def check_in():
    print("\n-- Available Rooms --")
    mycursor.execute("SELECT * FROM rooms WHERE status='Available'")
    rooms = mycursor.fetchall()

    if not rooms:
        print("No rooms available")
        return

    for r in rooms:
        print(f"Room: {r[0]}, Type: {r[1]}, Price: {r[2]}")

    try:
        room_no = int(input("Enter Room No: "))
    except:
        print("Invalid input")
        return

    mycursor.execute("SELECT * FROM rooms WHERE room_no=%s AND status='Available'", (room_no,))
    if not mycursor.fetchone():
        print("Room not available")
        return

    name = input("Name: ")
    try:
        age = int(input("Age: "))
    except:
        print("Invalid age")
        return
    gender = input("Gender(m/f): ")
    phone = input("Phone: ")

    mycursor.execute(
        "INSERT INTO customers(name,age,gender,phone) VALUES(%s,%s,%s,%s)",
        (name, age, gender, phone)
    )
    cust_id = mycursor.lastrowid

    today = datetime.date.today()
    mycursor.execute(
        "INSERT INTO booking(customer_id,room_no,check_in) VALUES(%s,%s,%s)",
        (cust_id, room_no, today)
    )

    mycursor.execute("UPDATE rooms SET status='Booked' WHERE room_no=%s", (room_no,))
    mydb.commit()

    print(f"Check-In Successful | Customer ID: {cust_id}")

# ADD ROOM
def add_room():
    try:
        room_no = int(input("Enter Room No: "))
    except:
        print("Invalid input")
        return

    room_type = input("Type(Standard/Deluxe/Suite): ").lower()

    mycursor.execute("SELECT * FROM room_prices")
    std, dlx, ste = mycursor.fetchone()

    if room_type == "standard":
        price = std
    elif room_type == "deluxe":
        price = dlx
    elif room_type == "suite":
        price = ste
    else:
        print("Invalid type")
        return

    try:
        mycursor.execute(
            "INSERT INTO rooms VALUES(%s,%s,%s,'Available')",
            (room_no, room_type, price)
        )
        mydb.commit()
        print("Room added successfully")
    except:
        print("Room already exists")

# CHECK-OUT
def check_out():
    try:
        booking_id = int(input("Enter Booking ID: "))
    except:
        print("Invalid input")
        return

    mycursor.execute("SELECT * FROM booking WHERE booking_id=%s AND check_out IS NULL", (booking_id,))
    data = mycursor.fetchone()

    if not data:
        print("Invalid booking")
        return

    room_no = data[2]
    check_in = data[3]
    today = datetime.date.today()

    days = (today - check_in).days
    if days == 0:
        days = 1

    mycursor.execute("SELECT price FROM rooms WHERE room_no=%s", (room_no,))
    price = mycursor.fetchone()[0]

    bill = days * price

    print(f"\nTotal Bill: {bill}")

    mycursor.execute(
        "UPDATE booking SET check_out=%s, total_bill=%s WHERE booking_id=%s",
        (today, bill, booking_id)
    )
    mycursor.execute("UPDATE rooms SET status='Available' WHERE room_no=%s", (room_no,))
    mydb.commit()

    print("Checked Out Successfully")

# VIEW DATA
def view_data():
    print("""
1. Customers
2. Rooms
3. Active Bookings
4. All Bookings
""")
    try:
        ch = int(input("Choice: "))
    except:
        print("Invalid input")
        return

    if ch == 1:
        mycursor.execute("SELECT * FROM customers")
    elif ch == 2:
        mycursor.execute("SELECT * FROM rooms")
    elif ch == 3:
        mycursor.execute("SELECT * FROM booking WHERE check_out IS NULL")
    elif ch == 4:
        mycursor.execute("SELECT * FROM booking")
    else:
        print("Invalid choice")
        return

    for row in mycursor.fetchall():
        print(row)

# MODIFY
def modify():
    print("""
1. Change Prices
2. Modify Room
""")
    try:
        ch = int(input("Choice: "))
    except:
        print("Invalid input")
        return

    if ch == 1:
        std = int(input("Standard price: "))
        dlx = int(input("Deluxe price: "))
        ste = int(input("Suite price: "))

        mycursor.execute("UPDATE room_prices SET standard=%s, deluxe=%s, suite=%s", (std, dlx, ste))
        mycursor.execute("UPDATE rooms SET price=%s WHERE room_type='standard'", (std,))
        mycursor.execute("UPDATE rooms SET price=%s WHERE room_type='deluxe'", (dlx,))
        mycursor.execute("UPDATE rooms SET price=%s WHERE room_type='suite'", (ste,))
        mydb.commit()
        print("Prices updated")

    elif ch == 2:
        room_no = int(input("Room no: "))

        print("1. Price\n2. Status")
        opt = int(input("Choice: "))

        if opt == 1:
            price = int(input("New price: "))
            mycursor.execute("UPDATE rooms SET price=%s WHERE room_no=%s", (price, room_no))
        elif opt == 2:
            status = input("New status: ")
            mycursor.execute("UPDATE rooms SET status=%s WHERE room_no=%s", (status, room_no))
        else:
            print("Invalid choice")
            return

        mydb.commit()
        print("Room updated")

# CHANGE PASSWORD
def change_password():
    old = input("Enter current password: ")
    mycursor.execute("SELECT * FROM login")
    user, pas = mycursor.fetchone()

    if old == pas:
        new = input("Enter new password: ")
        mycursor.execute("UPDATE login SET password=%s", (new,))
        mydb.commit()
        print("Password changed")
    else:
        print("Wrong password")

# MAIN
setup_database()

while True:
    print("\n1. Login\n2. Exit")
    try:
        ch = int(input("Choice: "))
    except:
        print("Invalid input")
        continue

    if ch == 1:
        pas = input("Enter Password: ")
        mycursor.execute("SELECT * FROM login")
        user, db_pass = mycursor.fetchone()

        if pas == db_pass:
            print("Login Success")

            while True:
                print("""
1. Check-In
2. Add Room
3. Check-Out
4. View Data
5. Modify
6. Change Password
7. Logout
""")
                try:
                    admin = int(input("Choice: "))
                except:
                    print("Invalid input")
                    continue

                if admin == 1:
                    check_in()
                elif admin == 2:
                    add_room()
                elif admin == 3:
                    check_out()
                elif admin == 4:
                    view_data()
                elif admin == 5:
                    modify()
                elif admin == 6:
                    change_password()
                elif admin == 7:
                    break
                else:
                    print("Invalid choice")

        else:
            print("Wrong Password")

    elif ch == 2:
        print("Exiting system...")
        break
    else:
        print("Invalid choice")