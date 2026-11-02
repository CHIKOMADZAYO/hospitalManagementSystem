import os
import sys
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

if __package__ in (None, ""):
    parent_dir = str(Path(__file__).resolve().parent.parent)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

try:
    from OopImproved.database import Database
except ModuleNotFoundError:
    from database import Database


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "hospital_db.sqlite")
db = Database(DB_PATH)


class HospitalService(ABC):
    @abstractmethod
    def process_payment(self, amount):
        pass


class Patient(HospitalService):
    def __init__(self, name, patient_id, phone, age, balance):
        self.name = name
        self.patient_id = patient_id
        self.phone = phone
        self.age = age
        self.__balance = float(balance)

    def display_details(self):
        print(f"Name: {self.name}")
        print(f"Patient ID: {self.patient_id}")
        print(f"Phone: {self.phone}")
        print(f"Age: {self.age}")
        print(f"Balance: Ksh {self.__balance:.2f}")

    def check_balance(self):
        return self.__balance

    def deposit_money(self, amount):
        try:
            amount = float(amount)
        except ValueError:
            print("Invalid amount entered. Please enter a number.")
            return False

        if amount <= 0:
            print("Deposit amount must be greater than zero.")
            return False

        self.__balance += amount
        print(f"Deposit successful. New balance: Ksh {self.__balance:.2f}")
        return True

    def withdraw_money(self, amount):
        try:
            amount = float(amount)
        except ValueError:
            print("Invalid amount entered. Please enter a number.")
            return False

        if amount <= 0:
            print("Withdrawal amount must be greater than zero.")
            return False

        if amount > self.__balance:
            print("Insufficient balance. Withdrawal not allowed.")
            return False

        self.__balance -= amount
        print(f"Withdrawal successful. Remaining balance: Ksh {self.__balance:.2f}")
        return True

    def _get_balance(self):
        return self.__balance

    def _set_balance(self, new_balance):
        self.__balance = float(new_balance)

    def process_payment(self, amount):
        raise NotImplementedError("Payment logic must be implemented by the patient type.")


class Outpatient(Patient):
    def patient_type(self):
        print("Outpatient Patient")

    def process_payment(self, consultation_fee):
        total = consultation_fee + 100
        if self._get_balance() >= total:
            self._set_balance(self._get_balance() - total)
            print(f"Outpatient payment processed successfully. Ksh {total:.2f} deducted.")
            return True
        print(f"Insufficient balance. Outpatient payment of Ksh {total:.2f} cannot be processed.")
        return False


class Inpatient(Patient):
    def patient_type(self):
        print("Inpatient Patient")

    def process_payment(self, consultation_fee):
        total = consultation_fee + 200
        if self._get_balance() >= total:
            self._set_balance(self._get_balance() - total)
            print(f"Inpatient payment processed successfully. Ksh {total:.2f} deducted.")
            return True
        print(f"Insufficient balance. Inpatient payment of Ksh {total:.2f} cannot be processed.")
        return False


class Doctor:
    def __init__(self, name, doctor_id, specialization, consultation_fee):
        self.name = name
        self.doctor_id = doctor_id
        self.specialization = specialization
        self.consultation_fee = float(consultation_fee)

    def display_details(self):
        print(f"Doctor Name: {self.name}")
        print(f"Doctor ID: {self.doctor_id}")
        print(f"Specialization: {self.specialization}")
        print(f"Consultation Fee: Ksh {self.consultation_fee:.2f}")


class Appointment:
    def __init__(self, patient, doctor, appointment_date, appointment_time):
        self.patient = patient
        self.doctor = doctor
        self.appointment_date = appointment_date
        self.appointment_time = appointment_time
        self.status = "Pending"
        self.appointment_id = None

    def display_details(self):
        print("Appointment Details")
        print(f"Patient: {self.patient.name} (ID: {self.patient.patient_id})")
        print(f"Doctor: {self.doctor.name} (ID: {self.doctor.doctor_id})")
        print(f"Date: {self.appointment_date}")
        print(f"Time: {self.appointment_time}")
        print(f"Status: {self.status}")

    def confirm_appointment(self):
        self.status = "Confirmed"
        print(f"Appointment confirmed for {self.patient.name} with Dr. {self.doctor.name}.")

    def cancel_appointment(self):
        self.status = "Cancelled"
        print(f"Appointment cancelled for {self.patient.name}.")


class PatientService:
    def __init__(self, database):
        self.db = database
        self.patients = []
        self.load_all()

    def load_all(self):
        self.patients = []
        for row in self.db.get_all_patients():
            patient_type = row["patient_type"]
            patient = (
                Outpatient(row["name"], row["patient_id"], row["phone"], row["age"], row["balance"])
                if patient_type == "Outpatient"
                else Inpatient(row["name"], row["patient_id"], row["phone"], row["age"], row["balance"])
            )
            self.patients.append(patient)

    def find_by_id(self, patient_id):
        for patient in self.patients:
            if str(patient.patient_id) == str(patient_id):
                return patient
        return None

    def register(self, name, patient_id, phone, age, balance, patient_type_choice):
        if any(str(existing.patient_id) == str(patient_id) for existing in self.patients):
            print(f"Patient ID {patient_id} already exists. Please use a unique ID.")
            return None

        if patient_type_choice == "1":
            patient = Outpatient(name, patient_id, phone, age, balance)
            patient_type = "Outpatient"
        elif patient_type_choice == "2":
            patient = Inpatient(name, patient_id, phone, age, balance)
            patient_type = "Inpatient"
        else:
            print("Invalid patient type selected.")
            return None

        self.db.add_patient(patient_id, name, phone, age, balance, patient_type)
        self.patients.append(patient)
        return patient

    def update(self, patient_id, name, phone, age, balance, patient_type):
        self.db.update_patient(patient_id, name, phone, age, balance, patient_type)
        patient = self.find_by_id(patient_id)
        if patient is not None:
            patient.name = name
            patient.phone = phone
            patient.age = int(age)
            patient._set_balance(balance)

    def delete(self, patient_id):
        self.db.delete_patient(patient_id)
        self.patients = [p for p in self.patients if str(p.patient_id) != str(patient_id)]

    def payment_history(self, patient_id):
        return self.db.get_patient_payments(patient_id)


class DoctorService:
    def __init__(self, database):
        self.db = database
        self.doctors = []
        self.load_all()

    def load_all(self):
        self.doctors = []
        for row in self.db.get_all_doctors():
            doctor = Doctor(row["name"], row["doctor_id"], row["specialization"], row["consultation_fee"])
            self.doctors.append(doctor)

    def find_by_id(self, doctor_id):
        for doctor in self.doctors:
            if str(doctor.doctor_id) == str(doctor_id):
                return doctor
        return None

    def register(self, name, doctor_id, specialization, consultation_fee):
        if any(str(existing.doctor_id) == str(doctor_id) for existing in self.doctors):
            print(f"Doctor ID {doctor_id} already exists. Please use a unique ID.")
            return None

        doctor = Doctor(name, doctor_id, specialization, consultation_fee)
        self.db.add_doctor(doctor_id, name, specialization, consultation_fee)
        self.doctors.append(doctor)
        return doctor

    def update(self, doctor_id, name, specialization, consultation_fee):
        self.db.update_doctor(doctor_id, name, specialization, consultation_fee)
        doctor = self.find_by_id(doctor_id)
        if doctor is not None:
            doctor.name = name
            doctor.specialization = specialization
            doctor.consultation_fee = float(consultation_fee)

    def delete(self, doctor_id):
        self.db.delete_doctor(doctor_id)
        self.doctors = [d for d in self.doctors if str(d.doctor_id) != str(doctor_id)]


class AppointmentService:
    def __init__(self, database, patient_service, doctor_service):
        self.db = database
        self.patient_service = patient_service
        self.doctor_service = doctor_service
        self.appointments = []
        self.load_all()

    def load_all(self):
        self.appointments = []
        for row in self.db.get_all_appointments():
            patient = self.patient_service.find_by_id(row["patient_id"])
            doctor = self.doctor_service.find_by_id(row["doctor_id"])
            if patient is None or doctor is None:
                continue
            appointment = Appointment(patient, doctor, row["appointment_date"], row["appointment_time"])
            appointment.appointment_id = row["id"]
            appointment.status = row["status"]
            self.appointments.append(appointment)

    def add(self, patient_id, doctor_id, appointment_date, appointment_time):
        patient = self.patient_service.find_by_id(patient_id)
        doctor = self.doctor_service.find_by_id(doctor_id)
        if patient is None or doctor is None:
            return None

        appointment = Appointment(patient, doctor, appointment_date, appointment_time)
        appointment.appointment_id = self.db.add_appointment(patient_id, doctor_id, appointment_date, appointment_time, "Confirmed")
        appointment.confirm_appointment()
        self.appointments.append(appointment)
        return appointment

    def update(self, index, patient_id, doctor_id, appointment_date, appointment_time, status):
        if not (0 <= index < len(self.appointments)):
            return False

        appointment = self.appointments[index]
        patient = self.patient_service.find_by_id(patient_id)
        doctor = self.doctor_service.find_by_id(doctor_id)
        if patient is None or doctor is None:
            return False

        if appointment.appointment_id is not None:
            self.db.update_appointment(appointment.appointment_id, patient_id, doctor_id, appointment_date, appointment_time, status)

        appointment.patient = patient
        appointment.doctor = doctor
        appointment.appointment_date = appointment_date
        appointment.appointment_time = appointment_time
        appointment.status = status
        return True

    def delete(self, index):
        if not (0 <= index < len(self.appointments)):
            return False

        appointment = self.appointments[index]
        if appointment.appointment_id is not None:
            self.db.delete_appointment(appointment.appointment_id)
        self.appointments.pop(index)
        return True

    def cancel(self, index):
        if not (0 <= index < len(self.appointments)):
            return False
        self.appointments[index].cancel_appointment()
        if self.appointments[index].appointment_id is not None:
            self.db.update_appointment_status(self.appointments[index].appointment_id, "Cancelled")
        return True


patient_service = None
doctor_service = None
appointment_service = None


def load_patients_from_db():
    patient_service.load_all()


def load_doctors_from_db():
    doctor_service.load_all()


def load_appointments_from_db():
    appointment_service.load_all()


def find_patient(patient_id):
    return patient_service.find_by_id(patient_id)


def find_doctor(doctor_id):
    return doctor_service.find_by_id(doctor_id)


def register_patient():
    try:
        name = input("Enter patient full name: ").strip()
        patient_id = input("Enter patient ID: ").strip()
        phone = input("Enter phone number: ").strip()
        age = int(input("Enter age: ").strip())
        balance = float(input("Enter account balance: ").strip())
        patient_type_choice = input("Select patient type: 1=Outpatient, 2=Inpatient: ").strip()

        if not name:
            print("Patient name cannot be empty.")
            return
        if age <= 0:
            print("Age must be greater than zero.")
            return
        if balance < 0:
            print("Balance cannot be negative.")
            return

        patient = patient_service.register(name, patient_id, phone, age, balance, patient_type_choice)
        if patient is not None:
            print("Patient registered successfully.")
            return patient
    except ValueError:
        print("Invalid input. Please enter valid values.")


def register_doctor():
    try:
        name = input("Enter doctor name: ").strip()
        doctor_id = input("Enter doctor ID: ").strip()
        specialization = input("Enter doctor specialization: ").strip()
        consultation_fee = float(input("Enter consultation fee: ").strip())

        if not name or not specialization:
            print("Doctor name and specialization cannot be empty.")
            return
        if consultation_fee < 0:
            print("Consultation fee cannot be negative.")
            return

        doctor = doctor_service.register(name, doctor_id, specialization, consultation_fee)
        if doctor is not None:
            print("Doctor registered successfully.")
            return doctor
    except ValueError:
        print("Invalid input. Please enter valid numeric values.")


def book_appointment():
    try:
        patient_id = input("Enter patient ID: ").strip()
        doctor_id = input("Enter doctor ID: ").strip()
        appointment_date = input("Enter appointment date (YYYY-MM-DD): ").strip()
        appointment_time = input("Enter appointment time (HH:MM): ").strip()

        patient = find_patient(patient_id)
        doctor = find_doctor(doctor_id)
        if patient is None:
            print("Appointment failed. Patient does not exist.")
            return
        if doctor is None:
            print("Appointment failed. Doctor does not exist.")
            return

        datetime.strptime(appointment_date, "%Y-%m-%d")
        appointment = appointment_service.add(patient_id, doctor_id, appointment_date, appointment_time)
        if appointment is not None:
            print("Appointment booked successfully.")
            return appointment
    except ValueError:
        print("Invalid date format. Please use YYYY-MM-DD.")


def display_patients():
    if not patient_service.patients:
        print("No patients registered yet.")
        return

    print("\nRegistered Patients")
    for patient in patient_service.patients:
        patient.display_details()
        print("-" * 20)


def display_doctors():
    if not doctor_service.doctors:
        print("No doctors registered yet.")
        return

    print("\nRegistered Doctors")
    for doctor in doctor_service.doctors:
        doctor.display_details()
        print("-" * 20)


def display_appointments():
    if not appointment_service.appointments:
        print("No appointments booked yet.")
        return

    print("\nAppointments")
    for appointment in appointment_service.appointments:
        appointment.display_details()
        print("-" * 20)


def search_patient():
    patient_id = input("Enter patient ID to search: ").strip()
    patient = find_patient(patient_id)
    if patient is None:
        print(f"No patient found with ID {patient_id}.")
        return None
    print(f"Patient found: {patient.name}")
    patient.display_details()
    return patient


def search_doctor():
    doctor_id = input("Enter doctor ID to search: ").strip()
    doctor = find_doctor(doctor_id)
    if doctor is None:
        print(f"No doctor found with ID {doctor_id}.")
        return None
    print(f"Doctor found: {doctor.name}")
    doctor.display_details()
    return doctor


def view_patient_payment_history():
    patient_id = input("Enter patient ID: ").strip()
    patient = find_patient(patient_id)
    if patient is None:
        print("Patient not found.")
        return

    payments = patient_service.payment_history(patient_id)
    if not payments:
        print(f"No payment history found for patient {patient.name}.")
        return

    print(f"\nPayment history for {patient.name} ({patient.patient_id}):")
    for payment in payments:
        doctor_name = "-"
        if payment["doctor_id"]:
            doctor = find_doctor(payment["doctor_id"])
            if doctor is not None:
                doctor_name = doctor.name
        print(f"Type: {payment['payment_type']} | Amount: Ksh {float(payment['amount']):.2f} | Doctor: {doctor_name} | Date: {payment['payment_date']} | Note: {payment['description']}")


def update_patient_record():
    patient_id = input("Enter patient ID to update: ").strip()
    patient = find_patient(patient_id)
    if patient is None:
        print(f"Patient with ID {patient_id} not found.")
        return False

    try:
        new_name = input(f"New name ({patient.name}): ").strip() or patient.name
        new_phone = input(f"New phone ({patient.phone}): ").strip() or patient.phone
        new_age_input = input(f"New age ({patient.age}): ").strip()
        new_age = patient.age if new_age_input == "" else int(new_age_input)
        new_balance_input = input(f"New balance ({patient.check_balance()}): ").strip()
        new_balance = patient.check_balance() if new_balance_input == "" else float(new_balance_input)
        current_type = "Outpatient" if isinstance(patient, Outpatient) else "Inpatient"
        new_type = input(f"Patient type ({current_type}) [1=Outpatient, 2=Inpatient]: ").strip()
        patient_type = current_type
        if new_type == "1":
            patient_type = "Outpatient"
        elif new_type == "2":
            patient_type = "Inpatient"

        patient_service.update(patient_id, new_name, new_phone, new_age, new_balance, patient_type)
        patient.name = new_name
        patient.phone = new_phone
        patient.age = new_age
        patient._set_balance(new_balance)
        print(f"Patient {patient_id} updated successfully.")
        return True
    except ValueError:
        print("Invalid input. Please enter valid values.")
        return False


def update_doctor_record():
    doctor_id = input("Enter doctor ID to update: ").strip()
    doctor = find_doctor(doctor_id)
    if doctor is None:
        print(f"Doctor with ID {doctor_id} not found.")
        return False

    try:
        new_name = input(f"New doctor name ({doctor.name}): ").strip() or doctor.name
        new_specialization = input(f"New specialization ({doctor.specialization}): ").strip() or doctor.specialization
        new_fee_input = input(f"New consultation fee ({doctor.consultation_fee}): ").strip()
        new_fee = doctor.consultation_fee if new_fee_input == "" else float(new_fee_input)

        doctor_service.update(doctor_id, new_name, new_specialization, new_fee)
        doctor.name = new_name
        doctor.specialization = new_specialization
        doctor.consultation_fee = float(new_fee)
        print(f"Doctor {doctor_id} updated successfully.")
        return True
    except ValueError:
        print("Invalid input. Please enter valid numeric values.")
        return False


def update_appointment_record():
    try:
        index = int(input("Enter appointment index to update: ").strip())
        if not (0 <= index < len(appointment_service.appointments)):
            print("Invalid appointment index.")
            return False

        appointment = appointment_service.appointments[index]
        patient_id = input(f"New patient ID ({appointment.patient.patient_id}): ").strip() or appointment.patient.patient_id
        doctor_id = input(f"New doctor ID ({appointment.doctor.doctor_id}): ").strip() or appointment.doctor.doctor_id
        new_date = input(f"New date ({appointment.appointment_date}): ").strip() or appointment.appointment_date
        new_time = input(f"New time ({appointment.appointment_time}): ").strip() or appointment.appointment_time
        new_status = input(f"New status ({appointment.status}) [Confirmed/Cancelled/Pending]: ").strip() or appointment.status

        if appointment_service.update(index, patient_id, doctor_id, new_date, new_time, new_status):
            print(f"Appointment {index} updated successfully.")
            return True
        print("Unable to update that appointment.")
        return False
    except ValueError:
        print("Invalid appointment index. Please enter a valid number.")
        return False


def delete_patient():
    patient_id = input("Enter patient ID to delete: ").strip()
    patient = find_patient(patient_id)
    if patient is None:
        print(f"Patient with ID {patient_id} not found.")
        return False

    confirm = input(f"Delete patient {patient.name} ({patient_id})? (y/n): ").strip().lower()
    if confirm not in ("y", "yes"):
        print("Deletion cancelled.")
        return False

    patient_service.delete(patient_id)
    appointment_service.appointments = [a for a in appointment_service.appointments if str(a.patient.patient_id) != str(patient_id)]
    print(f"Patient {patient.name} deleted successfully.")
    return True


def delete_doctor():
    doctor_id = input("Enter doctor ID to delete: ").strip()
    doctor = find_doctor(doctor_id)
    if doctor is None:
        print(f"Doctor with ID {doctor_id} not found.")
        return False

    confirm = input(f"Delete doctor {doctor.name} ({doctor_id})? (y/n): ").strip().lower()
    if confirm not in ("y", "yes"):
        print("Deletion cancelled.")
        return False

    doctor_service.delete(doctor_id)
    appointment_service.appointments = [a for a in appointment_service.appointments if str(a.doctor.doctor_id) != str(doctor_id)]
    print(f"Doctor {doctor.name} deleted successfully.")
    return True


def delete_appointment_record():
    try:
        index = int(input("Enter appointment index to delete: ").strip())
        if not (0 <= index < len(appointment_service.appointments)):
            print("Invalid appointment index.")
            return False

        appointment = appointment_service.appointments[index]
        confirm = input(f"Delete appointment for {appointment.patient.name} with Dr. {appointment.doctor.name}? (y/n): ").strip().lower()
        if confirm not in ("y", "yes"):
            print("Deletion cancelled.")
            return False

        appointment_service.delete(index)
        print("Appointment deleted successfully.")
        return True
    except ValueError:
        print("Invalid input. Please enter a valid number.")
        return False


def display_database_records():
    print("\n=== DATABASE RECORDS ===")

    print("\nPatients:")
    rows = db.get_all_patients()
    if not rows:
        print("No patients in database.")
    else:
        for row in rows:
            print(dict(row))

    print("\nDoctors:")
    rows = db.get_all_doctors()
    if not rows:
        print("No doctors in database.")
    else:
        for row in rows:
            print(dict(row))

    print("\nAppointments:")
    rows = db.get_all_appointments()
    if not rows:
        print("No appointments in database.")
    else:
        for row in rows:
            print(dict(row))

    print("\nPayments:")
    rows = db.get_all_payments()
    if not rows:
        print("No payments in database.")
    else:
        for row in rows:
            print(dict(row))


def demonstrate_polymorphism():
    print("\n--- Polymorphism Demonstration ---")
    outpatient = Outpatient("Alice Wanjiru", "P-1001", "0712345678", 26, 10000)
    inpatient = Inpatient("Daniel Kimani", "P-1002", "0723456789", 42, 15000)
    outpatient.patient_type()
    inpatient.patient_type()
    outpatient.process_payment(2500)
    inpatient.process_payment(3500)
    print("--- End of Polymorphism Demo ---\n")


def main():
    global patient_service, doctor_service, appointment_service
    patient_service = PatientService(db)
    doctor_service = DoctorService(db)
    appointment_service = AppointmentService(db, patient_service, doctor_service)

    demonstrate_polymorphism()
    load_patients_from_db()
    load_doctors_from_db()
    load_appointments_from_db()

    while True:
        print("========================================")
        print("SMART HOSPITAL MANAGEMENT")
        print("========================================")
        print("1. Register Patient")
        print("2. Register Doctor")
        print("3. Display All Patients")
        print("4. Display All Doctors")
        print("5. Book Appointment")
        print("6. Display All Appointments")
        print("7. Search Patient")
        print("8. Search Doctor")
        print("9. Deposit Money")
        print("10. Withdraw Money")
        print("11. Process Patient Payment")
        print("12. Check Patient Balance")
        print("13. View Payment History")
        print("14. Cancel Appointment")
        print("15. View Database Records")
        print("16. Update Patient")
        print("17. Update Doctor")
        print("18. Update Appointment")
        print("19. Delete Patient")
        print("20. Delete Doctor")
        print("21. Delete Appointment")
        print("22. Exit")

        try:
            choice = input("Enter your choice: ").strip()
            if choice == "1":
                register_patient()
            elif choice == "2":
                register_doctor()
            elif choice == "3":
                display_patients()
            elif choice == "4":
                display_doctors()
            elif choice == "5":
                book_appointment()
            elif choice == "6":
                display_appointments()
            elif choice == "7":
                search_patient()
            elif choice == "8":
                search_doctor()
            elif choice == "9":
                patient_id = input("Enter patient ID: ").strip()
                patient = find_patient(patient_id)
                if patient is None:
                    print("Patient not found.")
                else:
                    try:
                        amount = float(input("Enter deposit amount: ").strip())
                        if patient.deposit_money(amount):
                            db.update_patient_balance(patient.patient_id, patient.check_balance())
                            db.add_payment(patient.patient_id, amount, "Deposit", description="Patient deposit")
                    except ValueError:
                        print("Invalid amount. Please enter a valid number.")
            elif choice == "10":
                patient_id = input("Enter patient ID: ").strip()
                patient = find_patient(patient_id)
                if patient is None:
                    print("Patient not found.")
                else:
                    try:
                        amount = float(input("Enter withdrawal amount: ").strip())
                        if patient.withdraw_money(amount):
                            db.update_patient_balance(patient.patient_id, patient.check_balance())
                            db.add_payment(patient.patient_id, amount, "Withdrawal", description="Patient withdrawal")
                    except ValueError:
                        print("Invalid amount. Please enter a valid number.")
            elif choice == "11":
                patient_id = input("Enter patient ID: ").strip()
                doctor_id = input("Enter doctor ID: ").strip()
                patient = find_patient(patient_id)
                doctor = find_doctor(doctor_id)

                if patient is None:
                    print("Patient not found.")
                elif doctor is None:
                    print("Doctor not found.")
                else:
                    if isinstance(patient, Outpatient):
                        total = doctor.consultation_fee + 100
                        if patient.process_payment(doctor.consultation_fee):
                            db.update_patient_balance(patient.patient_id, patient.check_balance())
                            db.add_payment(patient.patient_id, total, "Consultation", doctor.doctor_id, "Outpatient consultation")
                    elif isinstance(patient, Inpatient):
                        total = doctor.consultation_fee + 200
                        if patient.process_payment(doctor.consultation_fee):
                            db.update_patient_balance(patient.patient_id, patient.check_balance())
                            db.add_payment(patient.patient_id, total, "Consultation", doctor.doctor_id, "Inpatient consultation")
                    else:
                        print("Patient type not supported for payment.")
            elif choice == "12":
                patient_id = input("Enter patient ID: ").strip()
                patient = find_patient(patient_id)
                if patient is None:
                    print("Patient not found.")
                else:
                    print(f"Current balance for {patient.name}: Ksh {patient.check_balance():.2f}")
            elif choice == "13":
                view_patient_payment_history()
            elif choice == "14":
                appointment_id = input("Enter appointment index to cancel: ").strip()
                try:
                    index = int(appointment_id)
                    if 0 <= index < len(appointment_service.appointments):
                        appointment_service.cancel(index)
                    else:
                        print("Invalid appointment index.")
                except ValueError:
                    print("Invalid input. Please enter a valid number.")
            elif choice == "15":
                display_database_records()
            elif choice == "16":
                update_patient_record()
            elif choice == "17":
                update_doctor_record()
            elif choice == "18":
                update_appointment_record()
            elif choice == "19":
                delete_patient()
            elif choice == "20":
                delete_doctor()
            elif choice == "21":
                delete_appointment_record()
            elif choice == "22":
                print("Exiting SMART HOSPITAL MANAGEMENT system. Goodbye!")
                db.close()
                break
            else:
                print("Invalid choice. Please select a number from 1 to 22.")

            print()
        except Exception as error:
            print(f"An unexpected error occurred: {error}")


if __name__ == "__main__":
    main()
