import sqlite3


class Database:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.executescript('''
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                phone TEXT,
                age INTEGER NOT NULL,
                balance REAL NOT NULL DEFAULT 0,
                patient_type TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS doctors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doctor_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                specialization TEXT NOT NULL,
                consultation_fee REAL NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT NOT NULL,
                doctor_id TEXT NOT NULL,
                appointment_date TEXT NOT NULL,
                appointment_time TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pending'
            );

            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT NOT NULL,
                doctor_id TEXT,
                amount REAL NOT NULL,
                payment_type TEXT NOT NULL,
                payment_date TEXT NOT NULL DEFAULT CURRENT_DATE,
                description TEXT
            );

            CREATE TABLE IF NOT EXISTS medical_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT NOT NULL,
                doctor_id TEXT,
                diagnosis TEXT,
                treatment TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_DATE
            );
        ''')
        self.conn.commit()

    def add_patient(self, patient_id, name, phone, age, balance, patient_type):
        self.cursor.execute('''
            INSERT INTO patients (patient_id, name, phone, age, balance, patient_type)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (str(patient_id), name, phone, int(age), float(balance), patient_type))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_all_patients(self):
        self.cursor.execute('SELECT * FROM patients ORDER BY id')
        return self.cursor.fetchall()

    def find_patient(self, patient_id):
        self.cursor.execute('SELECT * FROM patients WHERE patient_id = ?', (str(patient_id),))
        return self.cursor.fetchone()

    def update_patient_balance(self, patient_id, new_balance):
        self.cursor.execute('UPDATE patients SET balance = ? WHERE patient_id = ?', (float(new_balance), str(patient_id)))
        self.conn.commit()

    def add_doctor(self, doctor_id, name, specialization, consultation_fee):
        self.cursor.execute('''
            INSERT INTO doctors (doctor_id, name, specialization, consultation_fee)
            VALUES (?, ?, ?, ?)
        ''', (str(doctor_id), name, specialization, float(consultation_fee)))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_all_doctors(self):
        self.cursor.execute('SELECT * FROM doctors ORDER BY id')
        return self.cursor.fetchall()

    def find_doctor(self, doctor_id):
        self.cursor.execute('SELECT * FROM doctors WHERE doctor_id = ?', (str(doctor_id),))
        return self.cursor.fetchone()

    def add_appointment(self, patient_id, doctor_id, appointment_date, appointment_time, status='Pending'):
        self.cursor.execute('''
            INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (str(patient_id), str(doctor_id), appointment_date, appointment_time, status))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_all_appointments(self):
        self.cursor.execute('SELECT * FROM appointments ORDER BY id')
        return self.cursor.fetchall()

    def update_appointment_status(self, appointment_id, status):
        self.cursor.execute('UPDATE appointments SET status = ? WHERE id = ?', (status, appointment_id))
        self.conn.commit()

    def update_appointment(self, appointment_id, patient_id, doctor_id, appointment_date, appointment_time, status):
        self.cursor.execute('''
            UPDATE appointments
            SET patient_id = ?, doctor_id = ?, appointment_date = ?, appointment_time = ?, status = ?
            WHERE id = ?
        ''', (str(patient_id), str(doctor_id), appointment_date, appointment_time, status, appointment_id))
        self.conn.commit()

    def delete_appointment(self, appointment_id):
        self.cursor.execute('DELETE FROM appointments WHERE id = ?', (appointment_id,))
        self.conn.commit()

    def delete_patient(self, patient_id):
        patient_id = str(patient_id)
        self.cursor.execute('DELETE FROM appointments WHERE patient_id = ?', (patient_id,))
        self.cursor.execute('DELETE FROM payments WHERE patient_id = ?', (patient_id,))
        self.cursor.execute('DELETE FROM medical_records WHERE patient_id = ?', (patient_id,))
        self.cursor.execute('DELETE FROM patients WHERE patient_id = ?', (patient_id,))
        self.conn.commit()

    def delete_doctor(self, doctor_id):
        doctor_id = str(doctor_id)
        self.cursor.execute('DELETE FROM appointments WHERE doctor_id = ?', (doctor_id,))
        self.cursor.execute('DELETE FROM payments WHERE doctor_id = ?', (doctor_id,))
        self.cursor.execute('DELETE FROM medical_records WHERE doctor_id = ?', (doctor_id,))
        self.cursor.execute('DELETE FROM doctors WHERE doctor_id = ?', (doctor_id,))
        self.conn.commit()

    def update_patient(self, patient_id, name, phone, age, balance, patient_type):
        self.cursor.execute('''
            UPDATE patients
            SET name = ?, phone = ?, age = ?, balance = ?, patient_type = ?
            WHERE patient_id = ?
        ''', (name, phone, int(age), float(balance), patient_type, str(patient_id)))
        self.conn.commit()

    def update_doctor(self, doctor_id, name, specialization, consultation_fee):
        self.cursor.execute('''
            UPDATE doctors
            SET name = ?, specialization = ?, consultation_fee = ?
            WHERE doctor_id = ?
        ''', (name, specialization, float(consultation_fee), str(doctor_id)))
        self.conn.commit()

    def add_payment(self, patient_id, amount, payment_type, doctor_id=None, description=None):
        self.cursor.execute('''
            INSERT INTO payments (patient_id, doctor_id, amount, payment_type, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (str(patient_id), str(doctor_id) if doctor_id is not None else None, float(amount), payment_type, description))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_all_payments(self):
        self.cursor.execute('SELECT * FROM payments ORDER BY id')
        return self.cursor.fetchall()

    def get_patient_payments(self, patient_id):
        self.cursor.execute('''
            SELECT * FROM payments WHERE patient_id = ? ORDER BY id
        ''', (str(patient_id),))
        return self.cursor.fetchall()

    def get_doctor_payments(self, doctor_id):
        self.cursor.execute('''
            SELECT * FROM payments WHERE doctor_id = ? ORDER BY id
        ''', (str(doctor_id),))
        return self.cursor.fetchall()

    def add_medical_record(self, patient_id, diagnosis, treatment, doctor_id=None):
        self.cursor.execute('''
            INSERT INTO medical_records (patient_id, doctor_id, diagnosis, treatment)
            VALUES (?, ?, ?, ?)
        ''', (str(patient_id), str(doctor_id) if doctor_id is not None else None, diagnosis, treatment))
        self.conn.commit()
        return self.cursor.lastrowid

    def close(self):
        self.conn.close()