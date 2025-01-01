from tabulate import tabulate
import mysql.connector
import re

def get_db_connection():
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="student",
            port=3307,
            database="Institute"
        )
        return mydb
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def create_database():
    """Create the Institute database if it does not exist."""
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="student",
            port=3307
        )
        cursor = mydb.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS Institute")
        mydb.close()
    except mysql.connector.Error as err:
        print(f"Error creating database: {err}")

def initialize_connection():
    """Initialize the database and return a connection."""
    create_database()  
    return get_db_connection()  

mydb = initialize_connection()
if mydb:
    cursor = mydb.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS Course (
    Course_Id INT AUTO_INCREMENT PRIMARY KEY,
    Course_name VARCHAR(20) NOT NULL,
    Course_duration VARCHAR(25) NOT NULL,
    Course_fee INT NOT NULL)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS student (
    Student_Id INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(20) NOT NULL,
    Course_Id INT NOT NULL,
    Phone_No BIGINT NOT NULL,
    FOREIGN KEY (Course_Id) REFERENCES Course(Course_Id)
);
""")

cursor.execute("""
        CREATE TABLE IF NOT EXISTS Timetable (
        Id INT AUTO_INCREMENT PRIMARY KEY,
        Day VARCHAR(20),
        first_period INT,
        second_period INT,
        third_period INT,
        fourth_period INT,
        FOREIGN KEY (first_period) REFERENCES course(course_id),
        FOREIGN KEY (second_period) REFERENCES course(course_id),
        FOREIGN KEY (third_period) REFERENCES course(course_id),
        FOREIGN KEY (fourth_period) REFERENCES course(course_id)
    )
""")

cursor.execute("""CREATE TABLE IF NOT EXISTS trainer (
        Id INT AUTO_INCREMENT PRIMARY KEY,
        Name VARCHAR(20) NOT NULL,
        Course_Id INT NOT NULL,
        FOREIGN KEY (Course_Id) REFERENCES Course(Course_Id)
);
""")

cursor.execute("""CREATE TABLE IF NOT EXISTS visitor_register (
        Register_Id INT PRIMARY KEY AUTO_INCREMENT,
        Name VARCHAR(20) NOT NULL,
        Course_Id INT NOT NULL,
        Phone_No BIGINT,
        Email VARCHAR(30),
        FOREIGN KEY (Course_Id) REFERENCES course(Course_Id) ON DELETE CASCADE)
""")

cursor.execute("""CREATE TABLE IF NOT EXISTS student_register (
    Student_Id INT NOT NULL,
    Name VARCHAR(20),
    Course_Id INT NOT NULL,
    Email VARCHAR(30),
    User_name VARCHAR(10),
    Password VARCHAR(25),
    PRIMARY KEY (Student_Id),
    FOREIGN KEY (Student_Id) REFERENCES student(Student_Id) ON DELETE CASCADE,
    FOREIGN KEY (Course_Id) REFERENCES course(Course_Id) ON DELETE CASCADE);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    Attendance_Id INT PRIMARY KEY AUTO_INCREMENT,
    Student_Id INT NOT NULL,
    Course_id INT NOT NULL,
    Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  
    Status VARCHAR(10) NOT NULL,  
    FOREIGN KEY (Student_Id) REFERENCES student_register(Student_Id),
    FOREIGN KEY (Course_id) REFERENCES course(Course_Id)
);
""")

cursor.execute("""CREATE TABLE IF NOT EXISTS trainer_register (
    Trainer_Id INT NOT NULL,
    Name VARCHAR(20),
    Course_Id INT NOT NULL,
    User_name VARCHAR(10),
    Password VARCHAR(25),
    PRIMARY KEY (Trainer_Id),
    FOREIGN KEY (Trainer_Id) REFERENCES trainer(Id) ON DELETE CASCADE,
    FOREIGN KEY (Course_Id) REFERENCES course(Course_Id) ON DELETE CASCADE
);
""")

cursor.execute("""CREATE TABLE IF NOT EXISTS payment (
    Payment_Id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    Student_Id INT NOT NULL,
    Course_Id INT NOT NULL,
    Amount DECIMAL(10, 2) NOT NULL,
    Payment_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (Student_Id) REFERENCES student_register(Student_Id) ON DELETE CASCADE,
    FOREIGN KEY (Course_Id) REFERENCES course(Course_Id) ON DELETE CASCADE
);
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS marks (
    Mark_Id INT PRIMARY KEY AUTO_INCREMENT,
    Student_Id INT NOT NULL,
    Course_id INT NOT NULL,
    Mark INT,
    Grade CHAR(2),
    FOREIGN KEY (Student_Id) REFERENCES student_register(Student_Id),
    FOREIGN KEY (Course_id) REFERENCES course(Course_id)
);
""")

def get_choice(options):
    """Helper function to handle user choice input."""
    while True:
        try:
            choice = int(input(f"Choose one {options}: "))
            if choice in range(1, len(options) + 1):
                return choice
            else:
                print("Invalid choice! Please select a valid option.")
        except ValueError:
            print("Invalid input! Please enter a number.")

def admin_login():
    """Handle admin login."""
    admin_name = input("Enter username: ")
    admin_password = input("Enter password: ")
    if admin_name == "admin" and admin_password == "admin@123":
        print("Successfully Logged In!")
        print("..............................")
        admin_menu()
    else:
        print("Incorrect name/password!")
        print(".............................")


class admin:
    def __init__(self, name, course):
        self.name = name
        self.course_duration = course
    def add_course_details(self):
            course_name = input("Enter course name: ").lower()
            course_duration = input("Enter course duration: ")
            try:
                course_fee = int(input("Enter course fee: "))
            except ValueError:
                print("Please enter a valid fee (numeric).")
            else:
                cursor.execute("""
                    INSERT INTO course (Course_name, Course_duration, Course_fee)
                    VALUES (%s, %s, %s)
                """, (course_name, course_duration, course_fee))
                mydb.commit()
                print("Course added successfully!")

    def view_courses(self):
        try:
            cursor.execute("SELECT * FROM course")
        except Exception as e:
            print("Error retrieving courses:", e)
        else:
            data = cursor.fetchall()
            if data:
                print(tabulate(data, headers=["Course_Id", "Course_name", "Course_duration", "Course_fee"], tablefmt="grid"))
            else:
                print("No courses available.")

    def register_visitor(self):
        name = input("Enter name: ")
        if name.isalpha():
            cursor.execute("SELECT course_id, course_name FROM course")
            courses = cursor.fetchall()

            print("Available courses:")
            for course in courses:
                print(f"{course[0]}. {course[1]}")

            course = input("Enter the name of the course you are interested: ").lower()
            try:
                cursor.execute("SELECT Course_Id FROM course WHERE Course_name = %s", (course,))
                course_data = cursor.fetchone()
                if course_data is None:
                    print("Course not found!")
                    return
                else:
                    try:
                        phone_no = int(input("Enter phone number: "))
                    except Exception:
                        print("Invalid phone number!")
                    else:
                        if len(str(phone_no)) == 10:
                            cursor.execute("SELECT Phone_No FROM visitor_register WHERE Phone_No=%s", (phone_no,))
                            if cursor.fetchone():
                                print("You already registered with this phone number!")
                            else:
                                email = input("Enter email: ")
                                if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                                    cursor.execute("INSERT INTO visitor_register(Name, Course_Id, Phone_No, Email) VALUES (%s, %s, %s, %s)", (name, course_data[0],phone_no, email))
                                    mydb.commit()
                                    print("Registered successfully!")
                                    print('---------------------------------------------')
                                else:
                                    print("Enter a valid email address!")
                        else:
                            print("Please enter a valid phone number!")

                            
            except Exception:
                print("Course not found!")

    def view_visitor(self):
        try:
        
            cursor.execute("SELECT * FROM visitor_register")
            visitors = cursor.fetchall()
            
            if visitors:
            
                headers = ["Visitor_ID", "Name", "Course_Id", "Phone_No", "Email"]
                print("--------------------------- Visitor Register ---------------------------")
                print(tabulate(visitors, headers=headers, tablefmt="grid"))
            else:
                print("No visitors found in the register.")
        except Exception as e:
            print(f"Error fetching visitor data: {e}")

                    
    def about(self):
        with open("about", "r") as f:
            print("=======================================================================TechVerse==============================================================================")
            print(f.read())
            print("For more information please register with us!\n")
            
        while True:
            print("1. REGISTER")
            print("2. EXIT")
            choice = input("Select: \n")
            if choice == '1':
                self.register_visitor()
            elif choice == '2':
                print(exit())
            else:
                print("Invalid choice!")

    def view_payments(self):
        cursor.execute("""
            SELECT p.Student_Id, s.Name, c.Course_Name, p.Amount
            FROM payment p
            JOIN student_register s ON p.Student_Id = s.Student_Id
            JOIN course c ON p.Course_Id = c.Course_Id
        """)
        
        data = cursor.fetchall()
        print(f"------------------PAYMENT DETAILS-------------------")
        print(tabulate(data, headers=["Student_Id", "Name", "Course_Name", "Amount"], tablefmt="grid"))

    def handle_timetable(self):
        day = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
        day1 = input("Enter day: ")
        lower = day1.lower()

        if lower not in day:
            print("Invalid day!")
            print("..............................")
            return

        cursor.execute("SELECT * FROM Timetable WHERE Day = %s", (lower,))
        existing_timetable = cursor.fetchall()

        if existing_timetable:
            print(f"Timetable already marked for {day1}!")
            return

        cursor.execute("SELECT course_id, course_name FROM course")
        courses = cursor.fetchall()

        print("Available courses:")
        for course in courses:
            print(f"{course[0]}. {course[1]}")

        course_ids = []
        for i in range(1, 5):  # 4 periods
            while True:
                try:
                    selected_course_id = int(input(f"Enter {i} period course ID: "))
                    if selected_course_id not in [course[0] for course in courses]:
                        print("Invalid course ID, try again.")
                    else:
                        course_ids.append(selected_course_id)
                        break
                except ValueError:
                    print("Invalid input! Please enter a number.")

        cursor.execute("""
            INSERT INTO Timetable (Day, first_period, second_period, third_period, fourth_period)
            VALUES (%s, %s, %s, %s, %s)
        """, (lower, *course_ids))
        mydb.commit()
        print("Timetable marked successfully!")


    def view_timetable(self):
        cursor.execute("SELECT * FROM timetable")
        data = cursor.fetchall()
        print(tabulate(data, headers=["Id", "Day", "9.30:11.00", "11.30:1.00", "1.30:3.00", "3.30:5.00"], tablefmt="grid"))

course1=admin('name','course_duration')

class AdminTrainer(admin):
    def __init__(self, name, course):
        super().__init__(name, course)

    def add_trainer(self):

        name = input("Enter trainer name: ")
        if name.isalpha():
                course_name = input("Enter course name for the trainer: ").lower()
                cursor.execute("SELECT Course_Id FROM course WHERE Course_name = %s", (course_name,))
                course_data = cursor.fetchone()
                if course_data:
                    cursor.execute("""
                        INSERT INTO trainer (Name, Course_id)
                        VALUES (%s, %s)
                    """, (name, course_data[0]))
                    mydb.commit()
                    print("Trainer added successfully!")
                else:
                    print("Course not found!")
        else:
                print("Invalid trainer name.")
    def view_trainers(self):
        try:
            cursor.execute("""
                SELECT trainer.Id, trainer.Name, course.Course_name
                FROM trainer
                JOIN course ON trainer.Course_id = course.Course_Id
            """)
        except Exception as e:
            print("Error retrieving trainers:", e)
        else:
            data = cursor.fetchall()
            if data:
                print(tabulate(data, headers=["Trainer_Id", "Name", "Course_name"], tablefmt="grid"))
            else:
                print("No trainers available.")

    def delete_trainer(self):
        self.view_trainers()
        trainer_id = input("Enter the Id of the trainer you want to delete: ")
        cursor.execute("DELETE FROM trainer WHERE Id = %s", (trainer_id,))
        mydb.commit()
        print(f"Trainer with Id {trainer_id} deleted successfully!")


    def update_trainer(self):
        self.view_trainers()
        trainer_id = input("Enter the Trainer_Id you want to update: ")
        try:
            trainer_id = int(trainer_id)
        except ValueError:
            print("Invalid Trainer_Id!")
            return

        cursor.execute("SELECT * FROM trainer WHERE Id = %s", (trainer_id,))
        trainer_data = cursor.fetchone()

        if trainer_data is None:
            print(f"Trainer with ID {trainer_id} not found!")
            return

        print(f"Updating record for {trainer_data[1]} (ID: {trainer_id})")

        new_name = input("Enter new trainer name: ")
        if new_name.isalpha():
            new_course = input("Enter new course name: ").lower()

            cursor.execute("SELECT Course_Id FROM course WHERE Course_name = %s", (new_course,))
            course_data = cursor.fetchone()

            if course_data is None:
                print("Course not found!")
                return

            cursor.execute("""
                UPDATE trainer 
                SET Name = %s, Course_id = %s
                WHERE Id = %s
            """, (new_name, course_data[0], trainer_id))
            mydb.commit()
            print(f"Trainer record with ID {trainer_id} updated successfully!")
        else:
            print("Invalid trainer name! Please use only alphabetic characters.")
trainer=AdminTrainer('name','course_name')

class AdminStudent(admin):
    def __init__(self, name, course, phno):
        super().__init__(name, course)
        self.phno = phno
    def add_student(self):
        name = input("Enter student name: ")
        if name.isalpha():
                course_name = input("Enter course name for the student: ").lower()
                cursor.execute("SELECT Course_Id FROM course WHERE Course_name = %s", (course_name,))
                course_data = cursor.fetchone()
                if course_data:
                    phone_number = input("Enter phone number: ")
                    if len(phone_number) == 10 and phone_number.isdigit():
                        cursor.execute("""
                            INSERT INTO student (Name, Course_id, Phone_No)
                            VALUES (%s, %s, %s)
                        """, (name, course_data[0], phone_number))
                        mydb.commit()
                        print("Student added successfully!")
                    else:
                        print("Invalid phone number. Please enter a 10-digit phone number.")
                else:
                    print("Course not found!")
        else:
                print("Invalid student name.")

    def view_students(self):
        try:
            cursor.execute("""
                SELECT student.Student_Id, student.Name, course.Course_name, student.Phone_No
                FROM student
                JOIN course ON student.Course_id = course.Course_Id
            """)
        except Exception as e:
            print("Error retrieving students:", e)
        else:
            data = cursor.fetchall()
            if data:
                print(tabulate(data, headers=["Student_Id", "Name", "Course_name", "Phone_No"], tablefmt="grid"))
            else:
                print("No students available.")

    def update_student(self):
        self.view_students()
        student_id = input("Enter the Student_Id you want to update: ")
        try:
            student_id = int(student_id)
        except ValueError:
            print("Invalid Student_Id!")
            return
        
        cursor.execute("SELECT * FROM student WHERE Student_Id = %s", (student_id,))
        student_data = cursor.fetchone()

        if student_data is None:
            print(f"Student with ID {student_id} not found!")
            return

        print(f"Updating record for {student_data[1]} (ID: {student_id})")

        new_name = input("Enter new student name: ")
        if new_name.isalpha():
            new_course = input("Enter new course name: ").lower()

            cursor.execute("SELECT Course_Id FROM course WHERE Course_name = %s", (new_course,))
            course_data = cursor.fetchone()

            if course_data is None:
                print("Course not found!")
                return
            
            new_phno = input("Enter new phone number: ")
            if len(new_phno) == 10 and new_phno.isdigit():
                cursor.execute("""
                    UPDATE student 
                    SET Name = %s, Course_id = %s, Phone_No = %s
                    WHERE Student_Id = %s
                """, (new_name, course_data[0], new_phno, student_id))
                mydb.commit()
                print(f"Student record with ID {student_id} updated successfully!")
            else:
                print("Invalid phone number! Please enter a 10-digit number.")
        else:
            print("Invalid student name! Please use only alphabetic characters.")

    def delete_student(self):
        self.view_students()
        student_id = input("Enter the Id of the student you want to delete: ")
        cursor.execute("DELETE FROM student WHERE Student_Id = %s", (student_id,))
        mydb.commit()
        print(f"Student with Id {student_id} deleted successfully!")

student=AdminStudent('name','course_name','phno')
    
class Trainer:
    def __init__(self, id, name, status):
        self.id = id
        self.name = name
        self.status = status

    def get_course_id(self, tid):
        cursor.execute("SELECT Course_id FROM trainer WHERE Id = %s", (tid,))
        course_id = cursor.fetchone()
        if course_id:
            return course_id[0]
        print("Invalid Trainer ID.")
        return None

    def add_attendance(self, tid):
        course_id = self.get_course_id(tid)
        if not course_id:
            return       
        try:
            student_id = int(input("Enter student ID: "))
        except ValueError:
            print("Invalid student ID!")
            return

        cursor.execute("SELECT Name FROM student WHERE Student_Id = %s AND Course_id = %s", (student_id, course_id))
        student = cursor.fetchone()
        
        if student:
            name = student[0]
            status = input("Enter attendance status (Present/Absent): ").strip().lower()
            if status in ["present", "absent"]:
                cursor.execute("""
                    INSERT INTO attendance (Student_Id, Course_id, Date, Status) 
                    VALUES (%s, %s, CURDATE(), %s)
                """, (student_id, course_id, status.capitalize()))
                mydb.commit()
                print("Attendance added.")
            else:
                print("Please enter 'Present' or 'Absent' for status.")
        else:
            print("Student not found in this course.")

    def view_attendance(self, tid):
        course_id = self.get_course_id(tid)
        if not course_id:
            return

        cursor.execute("SELECT * FROM attendance WHERE Course_id = %s", (course_id,))
        attendance_records = cursor.fetchall()
        print("-----------------Attendance Records---------------------")
        head=["Attendance_Id","Student_Id","Course_Id","Date","Status"]
        print(tabulate(attendance_records,headers=head,tablefmt="grid"))
        
    def add_mark(self, tid):
        course_id = self.get_course_id(tid)
        if not course_id:
            return

        try:
            student_id = int(input("Enter student ID: "))
        except ValueError:
            print("Invalid student ID!")
            return
        
        cursor.execute("SELECT Name FROM student WHERE Student_Id = %s AND Course_id = %s", (student_id, course_id))
        student = cursor.fetchone()

        if student:
            name = student[0]
            try:
                mark = int(input("Enter mark: "))
            except ValueError:
                print("Invalid mark input!")
                return
            
            grade = self.calculate_grade(mark)
            cursor.execute("""
                INSERT INTO marks (Student_Id, Course_id, Mark, Grade) 
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE Mark = %s, Grade = %s
            """, (student_id, course_id, mark, grade, mark, grade))
            mydb.commit()
            print("Mark added.")
        else:
            print("Student not found in this course.")

    def view_marks(self, tid):
        course_id = self.get_course_id(tid)
        if not course_id:
            return

        cursor.execute("SELECT * FROM marks WHERE Course_id = %s", (course_id,))
        mark_records = cursor.fetchall()

        print("---------------Marks Records------------------------:")
        head=["Mark_Id","Student_Id","Course_Id","Mark","Grade"]
        print(tabulate(mark_records,headers=head,tablefmt="grid"))
     
    def view_feedback(self, tid):  
        course_id = self.get_course_id(tid)
        if not course_id:
            print("Course ID not found for the given teacher ID.")
            return

        feedback_found = False
        try:
            with open("feedback.txt", "r") as file:
                entry = {}
                for line in file:
                    line = line.strip()                  
                    if line.startswith("Student Id:"):
                        entry['Student_Id'] = line.split(":")[1].strip()
                    elif line.startswith("Name:"):
                        entry['Name'] = line.split(":")[1].strip()
                    elif line.startswith("Course Id:"):
                        entry['Course_Id'] = line.split(":")[1].strip()
                    elif line.startswith("Feedback:"):
                        entry['Feedback_Text'] = line.split(":")[1].strip()
                    elif line.startswith("-" * 50):
                        if entry.get("Course_Id") == str(course_id):
                            print(f"Student ID: {entry['Student_Id']}")
                            print(f"Name: {entry['Name']}")
                            print(f"Course ID: {entry['Course_Id']}")
                            print(f"Feedback: {entry['Feedback_Text']}")
                            print("-" * 50)  
                            feedback_found = True
                        entry = {}
            if not feedback_found:
                print(f"No feedback found for Course ID: {course_id}")

        except FileNotFoundError:
            print("Feedback file not found.")
        except Exception as e:
            print(f"An error occurred while reading feedback: {e}")


    def view_students(self, tid):
        course_id = self.get_course_id(tid)
        if not course_id:
            return
        cursor.execute("SELECT * FROM student WHERE Course_id = %s", (course_id,))
        students = cursor.fetchall()
        print("-------------------------Students------------------------")
        head=["Student_Id","Name","Course_Id","Phone_No"]
        print(tabulate(students,headers=head,tablefmt="grid"))

    @staticmethod
    def calculate_grade(mark):
        if 90 <= mark <= 100:
            return 'A+'
        elif 80 <= mark < 90:
            return 'A'
        elif 70 <= mark < 80:
            return 'B+'
        elif 60 <= mark < 70:
            return 'B'
        elif 50 <= mark < 60:
            return 'C+'
        elif 40 <= mark < 50:
            return 'C'
        elif 30 <= mark < 40:
            return 'D+'
        elif 20 <= mark < 30:
            return 'D'
        else:
            return 'Failed'
trainer_funct = Trainer('id', 'name' ,'status')

class trainer_authentication:
    def __init__(self, tid, name, username, password, course_id):
        self.tid = tid
        self.tr_name = name
        self.tr_username = username
        self.tr_password = password
        self.tr_course_id = course_id

    def trainer_register(self):
        try:
            tr_id = int(input("Enter Trainer ID:"))
        except Exception:
            print("Invalid ID!")
        else:
            cursor.execute("SELECT Id, Name, Course_Id FROM trainer")
            trainer_data = cursor.fetchall()
            f = False
            for i in trainer_data:
                if tr_id == i[0]:
                    f = True
                    break
            if f:
                cursor.execute("SELECT trainer_Id, User_name, Password FROM trainer_register")
                tr_reg = cursor.fetchall()
                for i in tr_reg:
                    if tr_id == i[0]:
                        print("Trainer already registered!")
                        break
                else:
                    name = input("Enter name: ")
                    if name.isalpha():
                        course_id = int(input("Enter Course ID: "))
                        f = 0
                        for i in trainer_data:
                            if i[1] == name and i[2] == course_id:
                                f = 1
                                break
                        else:
                            print("Enter your correct name/course ID!")
                        if f == 1:
                            username = input("Enter username: ")
                            password = input("Enter password: ")
                            if len(password) >= 8 and len(password) <= 50:
                                for i in tr_reg:
                                    if username == i[1] or password == i[2]:
                                        print("Username/Password already used, try another one!")
                                        break
                                else:
                                    cursor.execute("INSERT INTO trainer_register (Trainer_Id, Name, Course_Id, User_name, Password) VALUES (%s, %s, %s, %s, %s)", (tr_id, name, course_id, username, password))
                                    mydb.commit()
                                    print(f"{name} Registered Successfully!")
                            else:
                                print("Please enter a password of minimum 8 characters!")
                    else:
                        print("Invalid name!")
            else:
                print("Can't register, something went wrong!")

    def trainer_login(self):
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        cursor.execute("SELECT User_name, Password, Name, Trainer_Id, Course_Id FROM trainer_register")
        trainer_log = cursor.fetchall()
        f = 0
        for i in trainer_log:
            if username == i[0] and password == i[1]:
                f = 1
                break
        else:
            print("Invalid username/password!")
        if f == 1:
            print(f"Login successful! Welcome, {i[2]}!")
            try:
                tid = int(input("Enter your ID: "))
            except Exception:
                print("Invalid ID!")
            else:
                f = 0
                for i in trainer_log:
                    if username == i[0] and password == i[1] and tid == i[3]:
                        f = 1
                        break
                else:
                    print("Incorrect ID!")
                if f == 1:
                    trainer_menu2(tid)

    def tr_reset_password(self):
        try:
            Id = int(input("Enter Trainer ID: "))
        except Exception:
            print("Invalid ID!")
        else:
            cursor.execute("SELECT Trainer_Id, User_name, Password FROM trainer_register")
            reset = cursor.fetchall()
            f = 0
            for i in reset:
                if Id == i[0]:
                    f = 1
                    new_user = input("Enter new username: ")
                    new_pass = input("Enter new password: ")
                    if len(new_pass) >= 8 and len(new_pass) <= 50:
                        for i in reset:
                            if new_user == i[1] or new_pass == i[2]:
                                print("Username/Password already used, try another one!")
                                break
                        else:
                            confm_pass = input("Confirm your password: ")
                            if new_pass == confm_pass:
                                cursor.execute("UPDATE trainer_register SET User_name = %s, Password = %s WHERE Trainer_Id = %s", (new_user, new_pass, Id))
                                mydb.commit()
                                print("Password changed!")
                                break
                            else:
                                print("Confirm Password does not match!")
                                break
                    else:
                        print("Please enter a password of minimum 8 characters!")
                        break
            if f == 0:
                print("You are not registered!")

auth=trainer_authentication('tid','name','username','password','course_id')

class StudentAuthentication:
    def __init__(self, sd_Id, name, course_id, email, username, password):
        self.sd_Id = sd_Id
        self.sd_name = name
        self.course_id = course_id  
        self.sd_email = email
        self.sd_username = username
        self.sd_password = password

    def student_register(self):
        try:
            sd_Id = int(input("Enter your Student ID: "))
        except ValueError:
            print("Invalid ID! Please enter a numeric value.")
            return

        cursor.execute("SELECT Student_Id, Name, Course_id FROM student")
        student_data = cursor.fetchall()

        if not any(sd_Id == i[0] for i in student_data):
            print("Student ID not found in the database!")
            return

        cursor.execute("SELECT Course_id FROM student where Student_Id=%s",(sd_Id,))
        courses = cursor.fetchall()
        course_list = [course[0] for course in courses]  
        if not course_list:
            print("No courses found for this student ID!")
            return

        cursor.execute("SELECT Student_Id, User_name, Password FROM student_register")
        sd_reg = cursor.fetchall()

        if any(sd_Id == i[0] for i in sd_reg):
            print("Student already registered!")
            return

        name = input("Enter your name: ")
        if not name.isalpha():
            print("Invalid name! Only alphabetic characters are allowed.")
            return

        email = input("Enter your email: ")
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            print("Invalid email format!")
            return

        username = input("Enter your username: ")
        password = input("Enter your password: ")

        if len(password) < 8 or len(password) > 50:
            print("Password must be between 8 and 50 characters!")
            return

        if any(username == i[1] or password == i[2] for i in sd_reg):
            print("Username or password already used. Try a different one.")
            return

        cursor.execute("""
            INSERT INTO student_register (Student_Id, Name, Course_id, Email, User_name, Password)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (sd_Id, name, course_list[0],email, username, password))
        mydb.commit()
        print(f"{name} registered successfully!")

    def student_login(self):
        username = input("Enter your username: ")
        password = input("Enter your password: ")

        cursor.execute("SELECT User_name, Password, Name, Student_Id FROM student_register")
        stud_log = cursor.fetchall()

        if not any(username == i[0] and password == i[1] for i in stud_log):
            print("Invalid username/password!")
            return

        student = next(i for i in stud_log if i[0] == username and i[1] == password)
        print(f"Login successful! Welcome, {student[2]}!")
        
        try:
            sid = int(input("Enter your ID: "))
        except ValueError:
            print("Invalid ID!")
            return

        if student[3] != sid:
            print("Incorrect ID!")
            return

        print("Access granted!")
        student_menu2(sid)

    def student_reset_password(self):
        try:
            sd_Id = int(input("Enter your Student ID: "))
        except ValueError:
            print("Invalid ID! Please enter a numeric value.")
            return

        cursor.execute("SELECT Student_Id FROM student WHERE Student_Id = %s", (sd_Id,))
        if cursor.fetchone() is None:
            print("Student ID not found!")
            return

        cursor.execute("SELECT Student_Id, User_name, Password FROM student_register")
        reset = cursor.fetchall()

        if sd_Id not in [i[0] for i in reset]:
            print("You are not registered!")
            return

        new_user = input("Enter your new username: ")
        new_pass = input("Enter your new password: ")

        if len(new_pass) < 8 or len(new_pass) > 50:
            print("Password must be between 8 and 50 characters!")
            return

        if any(new_user == i[1] or new_pass == i[2] for i in reset):
            print("Username or password already used. Try a different one.")
            return

        confirm_pass = input("Confirm your new password: ")
        if new_pass != confirm_pass:
            print("Passwords do not match!")
            return

        cursor.execute("UPDATE student_register SET User_name = %s, Password = %s WHERE Student_Id = %s", (new_user, new_pass, sd_Id))
        mydb.commit()
        print("Password updated successfully!")

stud = StudentAuthentication('sd_Id', 'name', 'course_id', 'email', 'username', 'password')

def trainer_menu():
    """Trainer menu options."""
    while True:
        print("1. REGISTER")
        print("2. LOGIN")
        print("3. RESET PASSWORD")
        print("4. EXIT")
        choice = get_choice(["REGISTER", "LOGIN", "RESET PASSWORD", "EXIT"])

        if choice == 1:
            auth.trainer_register()
        elif choice == 2:
            auth.trainer_login()
        elif choice == 3:
            auth.tr_reset_password()
        else:
            break

def student_menu2(sid):
    while True:
        print("1. MY PROFILE")
        print("2. VIEW MARK")
        print("3. VIEW ATTENDANCE")
        print("4. FEEDBACK")
        print("5. PAYMENT")
        print("6. BACK")
        print("7. EXIT")
        print("=============================")
        choice = get_choice([1,2,3,4,5,6,7])
        if choice == 1:
            # View student profile
            cursor.execute("SELECT * FROM student_register WHERE Student_Id=%s", (sid,))
            sd_data = cursor.fetchall()
            if not sd_data:
                print("Student not registered!")
                print("................................")
            else:
                for i in sd_data:
                    print(f"Student_Id   : {i[0]}")
                    print(f"Name         : {i[1]}")
                    print(f"Course       : {i[2]}")
                    print(f"Email        : {i[3]}")
                    print(f"User name    : {i[4]}")
                    print(f"Password     : {i[5]}")
                    print("..............................")

        elif choice == 2:
            cursor.execute("SELECT * FROM marks WHERE Student_Id=%s", (sid,))
            marks = cursor.fetchall()
            if marks:
                head = ["Mark_Id", "Student_Id", "Course_Id", "Mark", "Grade"]
                print(tabulate(marks, headers=head, tablefmt="grid"))
                print("\n")
            else:
                print("Your mark is not uploaded!")
                print("............................")

        elif choice == 3:
    
            cursor.execute("SELECT * FROM attendance WHERE Student_Id=%s", (sid,))
            attendance = cursor.fetchall()
            if attendance:
                head = ["Attendance_Id","Student_Id","Course_Id","Date","Status"]
                print(tabulate(attendance, headers=head, tablefmt="grid"))
            else:
                print("Attendance record not found!")
                print("............................")

        elif choice == 4:
            name = input("Enter your name: ")
            cursor.execute("SELECT Student_Id, Name, Course_Id FROM student WHERE Student_Id=%s", (sid,))
            student_data = cursor.fetchone()
            if student_data and student_data[1] == name:
                course_id = student_data[2]
                feedback = input("Type your feedback: ")
                if not feedback:
                    print("Feedback is mandatory!")
                    print("................................")
                else:
                    with open("feedback.txt", "a") as f:
                        f.write("\nStudent Id: " + str(sid))
                        f.write("\nName: " + name)
                        f.write("\nCourse Id: "+ str(course_id))
                        f.write("\nFeedback: " + feedback)
                        f.write("\n" + "-" * 50)
                    print("Thank you for your feedback!")
                    print("................................")
            else:
                print("Incorrect name or student ID.")
                print("................................")

        elif choice == 5:
            cursor.execute("SELECT * FROM payment WHERE Student_Id=%s", (sid,))
            payment_record = cursor.fetchall()
            if payment_record:
                print("You already paid!")
                print("..........................")
            else:
                try:
                    amount = int(input("Enter fee Amount: "))
                except ValueError:
                    print("Invalid amount!")
                    print("...........................")
                    continue
                else:
                    cursor.execute("SELECT Course_Id FROM student_register WHERE Student_Id=%s", (sid,))
                    course_id = cursor.fetchone()
                    if course_id:
                        cursor.execute("SELECT Course_fee FROM course WHERE Course_Id=%s", (course_id[0],))
                        course_fee = cursor.fetchone()

                        if course_fee:
                            if amount < course_fee[0]:
                                print("..............................")
                                print("You can only pay the full fee!")
                                print("..............................")
                            else:
                                cursor.execute("""
                                    INSERT INTO payment (Student_Id,Course_Id, Amount) 
                                    VALUES (%s, %s,%s)
                                """, (sid, course_id[0],amount))
                                mydb.commit()
                                print("Payment successful!")
                                print(".................................")
                        else:
                            print("Course fee not found!")
                    else:
                        print("Student not enrolled in any course!")

        elif choice == 6:
            break
        elif choice == 7:
            print("Exiting...")
            exit()

        else:
            print("Invalid choice, please try again.")

def trainer_menu2(tid):
    while True:
        print("1. ADD ATTENDANCE")
        print("2. ADD MARK")
        print("3. VIEW")
        print("4. EXIT")
        print("=============================")
        try:
            choice = int(input("Enter your choice:"))
        except Exception:
            print("Wrong choice!")
            print("...........................")
        else:
            if choice == 1:
                trainer_funct.add_attendance(tid)
            elif choice == 2:
                trainer_funct.add_mark(tid)
            elif choice == 3:
                while True:
                    print("1. STUDENTS")
                    print("2. ATTENDANCE")
                    print("3. MARKS")
                    print("4. FEEDBACK")
                    print("5. BACK")
                    print("6. EXIT")
                    print("===============================")
                    try:
                        cho = int(input("Enter your choice:"))
                    except Exception:
                        print("Wrong choice!")
                        print("........................")
                    else:
                        if cho == 1:
                            trainer_funct.view_students(tid)
                        elif cho == 2:
                            trainer_funct.view_attendance(tid)
                        elif cho == 3:
                            trainer_funct.view_marks(tid)
                        elif cho == 4:
                            trainer_funct.view_feedback(tid)
                        elif cho == 5:
                            break
                        elif cho == 6:
                            print("Exiting...")
                            exit()
                        else:
                            print("Wrong choice!")
                            print("......................")
            elif choice == 4:
                print("Exiting...")
                exit()
            else:
                print("Wrong choice!")
                print("..........................")

def student_menu():
    """Student menu options."""
    while True:
        print("1. REGISTER")
        print("2. LOGIN")
        print("3. RESET PASSWORD")
        print("4. EXIT")
        choice = get_choice([1,2,3,4])

        if choice == 1:
            stud.student_register()
        elif choice == 2:
            stud.student_login()
        elif choice == 3:
            stud.student_reset_password()
        else:
            break

def view_entities():
    while True:
        print("1. VIEW TRAINER")
        print("2. VIEW STUDENT")
        print("3. VIEW COURSE")
        print("4. VIEW VISITOR REGISTER")
        print("5. VIEW STUDENT PAYMENTS")
        print("6. VIEW TIMETABLE")
        print("7. BACK")
        print("===============================")
        try:
            choice = int(input("Select one: "))
        except Exception:
            print("Wrong choice!")
            print("......................")
        else:
            if choice == 1:
                trainer.view_trainers()
            elif choice == 2:
                student.view_students()
            elif choice == 3:
                course1.view_courses()
            elif choice == 4:
                course1.view_visitor()
            elif choice == 5:
                course1.view_payments()
            elif choice == 6:
                course1.view_timetable()
            elif choice == 7:
                break
            else:
                print("Wrong choice!")
                print("......................")

def admin_menu():
    while True:
        print("1.TRAINER")
        print("2.STUDENT")
        print("3.COURSE DETAILS")
        print("4.TIME TABLE")
        print("5.VIEW")
        print("6.BACK")
        print("7.EXIT")
        print("==============================")
        try:
            choice = int(input("Select one: "))
        except Exception:
            print("Wrong choice!")
            print("......................")
        else:
            if choice == 1:
                while(True):
                    print("1.ADD")
                    print("2.DELETE")
                    print("3.UPDATE")
                    print("4.BACK")
                    print("============================")
                    try:
                        choice=int(input("enter your choice:"))
                    except Exception:
                        print("Wrong choice!")
                        print("...........................")
                    else:
                        if choice==1:
                            trainer.add_trainer()
                        elif choice==2:
                            trainer.delete_trainer()
                        elif choice==3:
                            trainer.update_trainer()
                        elif choice==4:
                            break
                        else:
                            print("Wrong choice!")
                            print(".......................")
						
            elif choice==2:
                while True:
                    print("1.ADD")
                    print("2.DELETE")
                    print("3.UPDATE")
                    print("4.BACK")
                    print("============================")
                    try:
                        choice=int(input("enter your choice:"))
                    except Exception:
                        print("Wrong choice!")
                        print("...........................")
                    else:
                        if choice==1:
                            student.add_student()
                        elif choice==2:
                            student.delete_student()
                        elif choice==3:
                            student.update_student()
                        elif choice==4:
                            break
                        else:
                            print("Wrong choice!")
                            print(".......................")
            elif choice == 3:
                course1.add_course_details()  
            elif choice == 4:
                course1.handle_timetable()
            elif choice == 5:
                view_entities()
            elif choice == 6:
                break
            elif choice == 7:
                print("Exiting...")
                break
            else:
                print("Wrong choice!")
                print("......................")


def main():

    print("=============TechVerse============")
    while True:
        print("1. ADMIN")
        print("2. TRAINER")
        print("3. STUDENT")
        print("4. HOME")
        print("5. EXIT")
        print("...............................")

        choice = get_choice([1, 2, 3, 4, 5])

        if choice == 1:
            admin_login()
        elif choice == 2:
            trainer_menu()
        elif choice == 3:
            student_menu()
        elif choice == 4:
            print("\n")
            course1.about()
        elif choice == 5:
            print("Exiting...")
            break

if __name__ == "__main__":
    main()
