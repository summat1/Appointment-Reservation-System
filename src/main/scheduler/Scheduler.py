from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime


'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
current_patient = None

current_caregiver = None


def create_patient(tokens):
    # create_patient <username> <password>
    # check 1: make sure we have all 3 pieces of information
    if len(tokens) != 3:
        print("Failed to create patient. Make sure you put in a username and password.")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username is unique
    if username_exists_patient(username):
        print("Username taken, try again!")
        return
    
    # check 3: check for a strong password
    lower = 0
    upper = 0
    digits = 0
    letters = 0
    special = 0
    # first check, for password length
    if (len(password) >= 8):
        for i in password:
            if (i.islower()):
                lower += 1         
            if (i.isupper()):
                upper += 1           
            if (i.isdigit()):
                digits += 1    
            if (i == '!'or i == '@' or i == '#' or i == '?'):
                special += 1                
    if (lower >= 1 and upper >= 1 and digits >= 1 and special >= 1 and ((lower + upper + digits + special) == len(password))):
        salt = Util.generate_salt()
        hash = Util.generate_hash(password, salt)

        # create the patient
        patient = Patient(username, salt=salt, hash=hash)

        # save to caregiver information to our database
        try:
            patient.save_to_db()
        except pymssql.Error as e:
            print("Failed to create user.")
            quit()
        except Exception as e:
            print("Failed to create user.")
            return
        print("Created user ", username)
    else:
        print("Please create a strong password, at least 8 characters long. A password should contain a mix of lowercase, uppercase, numbers, and special chars.")
        return
    
def create_caregiver(tokens):
    # create_caregiver <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_caregiver(username):
        print("Username taken, try again!")
        return

    # check 3: check if password is strong    
    lower = 0
    upper = 0
    digits = 0
    letters = 0
    special = 0
    # first check, for password length
    if (len(password) >= 8):
        for i in password:
            if (i.islower()):
                lower += 1         
            if (i.isupper()):
                upper += 1           
            if (i.isdigit()):
                digits += 1    
            if (i == '!'or i == '@' or i == '#' or i == '?'):
                special += 1                
    if (lower >= 1 and upper >= 1 and digits >= 1 and special >=1 and lower + upper + digits + special == len(password)):
        salt = Util.generate_salt()
        hash = Util.generate_hash(password, salt)

        # create the caregiver
        caregiver = Caregiver(username, salt=salt, hash=hash)

        # save to caregiver information to our database
        try:
            caregiver.save_to_db()
        except pymssql.Error as e:
            print("Failed to create user.")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Failed to create user.")
            print(e)
            return
        print("Created user ", username)
    else:
        print("Please create a strong password, at least 8 characters long. A password should contain a mix of lowercase, uppercase, numbers, and special chars.")
        return

def username_exists_caregiver(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Caregivers WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False

def username_exists_patient(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Patients WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        quit()
    except Exception as e:
        print("Error occurred when checking username")
    finally:
        cm.close_connection()
    return False

def login_patient(tokens):
    # login_patient <username> <password>
    # check 1: if another person is already logged-in, they need to log out first
    global current_patient
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in.")
        return

    # check 2: make sure all information is included
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    patient = None
    try:
        patient = Patient(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        quit()
    except Exception as e:
        print("Login failed.")
        return

    # check if the login was successful
    if patient is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_patient = patient


def login_caregiver(tokens):
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_caregiver
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    caregiver = None
    try:
        caregiver = Caregiver(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        quit()
    except Exception as e:
        print("Login failed.")
        return

    # check if the login was successful
    if caregiver is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_caregiver = caregiver


def search_caregiver_schedule(tokens):

    cm = ConnectionManager()
    conn = cm.create_connection()

    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return
    
    select_schedule = "SELECT caregiver_id FROM Availabilities WHERE Time = %s ORDER BY caregiver_id"
    select_vaccines = "SELECT * FROM Vaccines"

    try:
        date = tokens[1]
        # assume input in form mm-dd-yyyy
        date_tokens = date.split("-")
        
        if (len(date_tokens) > 3):
            print("Make sure to format the date mm-dd-yyyy.")
            return
        
        month = int(date_tokens[0])
        day = int(date_tokens[1])
        year = int(date_tokens[2])
        
        date = datetime.datetime(year, month, day)
        cursor = conn.cursor()
        cursor.execute(select_schedule, date)
        num_rows = cursor.rowcount

        for row in cursor:
            print("available caregiver: {}".format(row[0]))

        if num_rows != 0:
            cursor.execute(select_vaccines)
            for row in cursor:
                print("vaccine: {}, number of doses: {}".format(row[0], row[1]))
        else:
            print("Please try again!")
            return

    except pymssql.Error as e:
        print("Please try again!")
        quit()
    except Exception as e:
        print("Please try again!")
        return
    finally:
        cm.close_connection()


def reserve(tokens):
    if current_patient is None and current_caregiver is None:
        print("Please login first!")
        return
    elif current_patient is None:
        print("Please login as a patient!")
        return

    cm = ConnectionManager()
    conn = cm.create_connection()

    find_caregiver = "SELECT TOP 1 caregiver_id, Time FROM Availabilities WHERE Time = %s ORDER BY caregiver_id"
    create_appt = "INSERT INTO Appointments VALUES (%s, %s, %s, %s, %s)"
    vaccine_check = "SELECT Doses FROM Vaccines WHERE Name = %s"
    delete_avail = "DELETE FROM Availabilities WHERE caregiver_id = %s AND Time = CAST(%s AS date)"
    update_vaccine = "UPDATE Vaccines SET Doses = %s WHERE Name = %s"

    try: 
        date = tokens[1]
        # assume input in form mm-dd-yyyy
        date_tokens = date.split("-")
        month = int(date_tokens[0])
        day = int(date_tokens[1])
        year = int(date_tokens[2])
        
        vaccine = tokens[2]
        date = datetime.datetime(year, month, day)
        cursor = conn.cursor()
        cursor.execute(find_caregiver, date)
        if cursor.rowcount == 0:
            print("No Caregiver is Available!")
            return
        for row in cursor:
            caregiver = row[0]
            appointment_id = ("{}{}".format(row[0], str(row[1])))
       
        cursor.execute(vaccine_check, vaccine)

        row = cursor.fetchone()
        if row:
            vaccine_count = row[0]
        else: 
            print("Not enough available doses!")
            return
        if vaccine_count == 0:
            print("Not enough available doses!")
            return

        print("Appointment ID: {}, Caregiver username: {}".format(appointment_id, caregiver))

        # patient_name, vaccine_used, caregiver_id, time
        appointment_details = (appointment_id, current_patient.get_username(), vaccine, caregiver, str(date))

        cursor.execute(create_appt, appointment_details)

        delete_text = (caregiver, str(date))
        cursor.execute(delete_avail, delete_text)
        

        print("Your appointment is confirmed with {}. Your appointment ID is {}".format(caregiver, appointment_id))

        # update vaccine doses
        vaccine_update = (vaccine_count - 1, vaccine)
        cursor.execute(update_vaccine, vaccine_update)

    except pymssql.Error as e:
        print("Please try again!")
        print(e)
        quit()
    except Exception as e:
        print("Please try again!")
        return
    finally:
        conn.commit()
        cm.close_connection()    
    
def upload_availability(tokens):
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    try:
        d = datetime.datetime(year, month, day)
        current_caregiver.upload_availability(d)
    except pymssql.Error as e:
        print("Upload Availability Failed")
        print("Db-Error:", e)
        quit()
    except ValueError:
        print("Please enter a valid date!")
        return
    except Exception as e:
        print("Error occurred when uploading availability")
        print("Error:", e)
        return
    print("Availability uploaded!")


def add_doses(tokens):
    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    #  check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    vaccine_name = tokens[1]
    doses = int(tokens[2])
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, doses).get()
    except pymssql.Error as e:
        print("Error occurred when adding doses")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when adding doses")
        print("Error:", e)
        return

    # if the vaccine is not found in the database, add a new (vaccine, doses) entry.
    # else, update the existing entry by adding the new doses
    if vaccine is None:
        vaccine = Vaccine(vaccine_name, doses)
        try:
            vaccine.save_to_db()
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            return
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            vaccine.increase_available_doses(doses)
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    print("Doses updated!")


def show_appointments(tokens):
    if (current_patient is None) and (current_caregiver is None):
        print("Please login first.")
        return
    
    cm = ConnectionManager()
    conn = cm.create_connection()
    
    find_appts_patient = "SELECT appointment_id, vaccine_used, Time, caregiver_id FROM Appointments WHERE patient_id = %s"
    find_appts_caregiver = "SELECT appointment_id, vaccine_used, Time, patient_id FROM Appointments WHERE caregiver_id = %s"
    
    try:
        cursor = conn.cursor()
        # patient
        if current_caregiver is None:
            cursor.execute(find_appts_patient, current_patient.get_username())
            for row in cursor:
                print("{} {} {} {}".format(row[0], row[1], str(row[2]), row[3]))
        # caregiver
        else:
            cursor.execute(find_appts_caregiver, current_caregiver.get_username())
            for row in cursor:
                print("{} {} {} {}".format(row[0], row[1], str(row[2]), row[3]))
    except pymssql.Error as e:
        print("Please try again!")
        quit()
    except Exception as e:
        print("Please try again!")
        return
    finally:
        cm.close_connection() 


def logout(tokens):
    global current_caregiver
    global current_patient

    if len(tokens) != 1:
        print("Please try again!")
        return

    if (current_patient is None) and (current_caregiver is None):
        print("Please login first.")
        return
    
    else:
        current_patient = None
        current_caregiver = None
        print("Successfully logged out.")
        return


def start():
    stop = False
    print()
    print(" *** Please enter one of the following commands *** ")
    print("> create_patient <username> <password>")
    print("> create_caregiver <username> <password>")
    print("> login_patient <username> <password>")
    print("> login_caregiver <username> <password>")
    print("> search_caregiver_schedule <date>")  # // TODO: implement search_caregiver_schedule (Part 2)
    print("> reserve <date> <vaccine>")  # // TODO: implement reserve (Part 2)
    print("> upload_availability <date>")
    print("> cancel <appointment_id>")  # // TODO: implement cancel (extra credit)
    print("> add_doses <vaccine> <number>")
    print("> show_appointments")  # // TODO: implement show_appointments (Part 2)
    print("> logout")  # // TODO: implement logout (Part 2)
    print("> Quit")
    print()
    while not stop:
        response = ""
        print("> ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Please try again!")
            break
       
        tokens = response.split(" ")
        if len(tokens) == 0:
            ValueError("Please try again!")
            continue
        operation = tokens[0]
        if operation != "create_patient" and operation != "create_caregiver":
            for i in tokens:
                i = i.lower()

        if operation == "create_patient":
            create_patient(tokens)
        elif operation == "create_caregiver":
            create_caregiver(tokens)
        elif operation == "login_patient":
            login_patient(tokens)
        elif operation == "login_caregiver":
            login_caregiver(tokens)
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
        elif operation == "reserve":
            reserve(tokens)
        elif operation == "upload_availability":
            upload_availability(tokens)
        elif operation == "add_doses":
            add_doses(tokens)
        elif operation == "show_appointments":
            show_appointments(tokens)
        elif operation == "logout":
            logout(tokens)
        elif operation == "quit":
            print("Bye!")
            stop = True
        else:
            print("Invalid operation name!")


if __name__ == "__main__":
    '''
    // pre-define the three types of authorized vaccines
    // note: it's a poor practice to hard-code these values, but we will do this ]
    // for the simplicity of this assignment
    // and then construct a map of vaccineName -> vaccineObject
    '''

    # start command line
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")

    start()
