import sqlite3


class Database:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                age INTEGER NOT NULL,
                balance REAL NOT NULL DEFAULT 0,
                patient_type TEXT NOT NULL
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS doctors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                specialization TEXT NOT NULL,
                consultation_fee REAL NOT NULL DEFAULT 0
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                doctor_id INTEGER NOT NULL,
                appointment_date TEXT NOT NULL,
                appointment_time TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pending',
                FOREIGN KEY (patient_id) REFERENCES patients(id),
                FOREIGN KEY (doctor_id) REFERENCES doctors(id)
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                doctor_id INTEGER,
                amount REAL NOT NULL,
                payment_type TEXT NOT NULL,
                payment_date TEXT NOT NULL DEFAULT CURRENT_DATE,
                description TEXT,
                FOREIGN KEY (patient_id) REFERENCES patients(id),
                FOREIGN KEY (doctor_id) REFERENCES doctors(id)
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS medical_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                doctor_id INTEGER,
                diagnosis TEXT,
                treatment TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_DATE,
                FOREIGN KEY (patient_id) REFERENCES patients(id),
                FOREIGN KEY (doctor_id) REFERENCES doctors(id)
            )
        ''')

        self.conn.commit()

    def add_patient(self, name, phone, age, balance, patient_type):
        self.cursor.execute('''
            INSERT INTO patients (name, phone, age, balance, patient_type)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, phone, age, balance, patient_type))
        self.conn.commit()

    def get_all_patients(self):
        self.cursor.execute('SELECT * FROM patients')
        return self.cursor.fetchall()

    def add_doctor(self, name, specialization, consultation_fee):
        self.cursor.execute('''
            INSERT INTO doctors (name, specialization, consultation_fee)
            VALUES (?, ?, ?)
        ''', (name, specialization, consultation_fee))
        self.conn.commit()

    def get_all_doctors(self):
        self.cursor.execute('SELECT * FROM doctors')
        return self.cursor.fetchall()

    def add_appointment(self, patient_id, doctor_id, appointment_date, appointment_time, status='Pending'):
        self.cursor.execute('''
            INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (patient_id, doctor_id, appointment_date, appointment_time, status))
        self.conn.commit()

    def get_all_appointments(self):
        self.cursor.execute('SELECT * FROM appointments')
        return self.cursor.fetchall()

    def add_payment(self, patient_id, amount, payment_type, doctor_id=None, description=None):
        self.cursor.execute('''
            INSERT INTO payments (patient_id, doctor_id, amount, payment_type, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (patient_id, doctor_id, amount, payment_type, description))
        self.conn.commit()

    def add_medical_record(self, patient_id, diagnosis, treatment, doctor_id=None):
        self.cursor.execute('''
            INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment)
            VALUES (?, ?, ?, ?)
        ''', (patient_id, doctor_id, diagnosis, treatment))
        self.conn.commit()

    def close(self):
        self.conn.close()