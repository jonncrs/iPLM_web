from sqlite3 import connect
import mysql.connector
import json

try:
    print('\n  ---------------------------------------')
    print(' |   U P D A T I N G   D A T A B A S E   |')
    print('  ---------------------------------------\n')
    print('     ESTABLISHING CONNECTIONS\n')
    # to connect to xampp/local server
    _db = mysql.connector.connect(host="localhost", user="root", password="")
    print('             CONNECTED TO SERVER\n')

    Q = _db.cursor()

    db_exists = False # db exist boolean
    print("     LOCATING DATABASE\n")
    Q.execute('SHOW DATABASES')
    # to check if db exists
    for exist_db in Q:
        if str(exist_db) == "('iplmdatabase',)":
            # if exist
            print("             DATABASE LOCATED\n")
            db_exists = True

    # to update database using config.json
    try:
        Q.execute('USE iplmdatabase') # to set db 
        to_file = os.getcwd() + "\\update\\" # to get current directory and set path to app folder
        print("     LOCATING DATABASE CONFIGURATIONS\n")
        with open(to_file + "config.json", "r") as get_config: # to open json file
            _config = json.load(get_config)
            print("             CONFIGURATIONS LOCATED\n")
            print("     APPLYING DATABASE UPDATES\n")
            print("              What's new ?\n")
            for x in _config:
                _events = x['events']
                try:
                    Q_events = f"CREATE TABLE IF NOT EXISTS crs_event (id INT AUTO_INCREMENT PRIMARY KEY, {_events['eventTitle']} TEXT, {_events['eventDescription']} TEXT, {_events['eventCategory']} TEXT, {_events['eventStartDate']} DATETIME, {_events['eventEndDate']} DATETIME)"
                    Q.execute(Q_events) # to run query
                    print("                 ADDED EVENTS TABLE\n")
                except:
                    # to display query if error
                    print("\n QUERY NOT RECOGNIZED")
                    print(" " + Q_events)
        print("     DATABASE UPDATES APPLIED\n")

        print('  ---------------------------------------------------------------------')
        print(' |   F I N I S H E D   R E Q U I R E D   S Y S T E M   U P D A T E S   |')
        print(' |        Y O U   C A N   R U N   T H E   S Y S T E M   N O W          |')
        print('  ---------------------------------------------------------------------')
    except:
        print("")
        for x in range (0, 5):
            print(" UNEXPECTED ERROR OCCURED. PLEASE CHECK IF update/config.json EXIST.")
except:
    print("")
    for x in range (0, 5):
        print(' ERROR: SERVER CONNECTION FAILED. PLEASE CHECK IF XAMPP IS RUNNING PROPERLY.')