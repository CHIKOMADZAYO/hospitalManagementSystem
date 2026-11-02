from abc import ABC, abstractmethod
from datetime import datetime


patients = []
doctors = []
appointments = []


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


def find_patient(patient_id):
    for patient in patients:
        if str(patient.patient_id) == str(patient_id):
            return patient
    return None


def find_doctor(doctor_id):
    for doctor in doctors:
        if str(doctor.doctor_id) == str(doctor_id):
            return doctor
    return None


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

        if any(str(existing.patient_id) == str(patient_id) for existing in patients):
            print(f"Patient ID {patient_id} already exists. Please use a unique ID.")
            return

        if age <= 0:
            print("Age must be greater than zero.")
            return

        if balance < 0:
            print("Balance cannot be negative.")
            return

        if patient_type_choice == "1":
            patient = Outpatient(name, patient_id, phone, age, balance)
        elif patient_type_choice == "2":
            patient = Inpatient(name, patient_id, phone, age, balance)
        else:
            print("Invalid patient type selected.")
            return

        patients.append(patient)
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

        if any(str(existing.doctor_id) == str(doctor_id) for existing in doctors):
            print(f"Doctor ID {doctor_id} already exists. Please use a unique ID.")
            return

        if consultation_fee < 0:
            print("Consultation fee cannot be negative.")
            return

        doctor = Doctor(name, doctor_id, specialization, consultation_fee)
        doctors.append(doctor)
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

        appointment = Appointment(patient, doctor, appointment_date, appointment_time)
        appointments.append(appointment)
        appointment.confirm_appointment()
        print("Appointment booked successfully.")
        return appointment
    except ValueError:
        print("Invalid date format. Please use YYYY-MM-DD.")


def display_patients():
    if not patients:
        print("No patients registered yet.")
        return

    print("\nRegistered Patients")
    for patient in patients:
        patient.display_details()
        print("-" * 20)


def display_doctors():
    if not doctors:
        print("No doctors registered yet.")
        return

    print("\nRegistered Doctors")
    for doctor in doctors:
        doctor.display_details()
        print("-" * 20)


def display_appointments():
    if not appointments:
        print("No appointments booked yet.")
        return

    print("\nAppointments")
    for appointment in appointments:
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


def demonstrate_polymorphism():
    print("\n--- Polymorphism Demonstration ---")

    outpatient = Outpatient("Alice Wanjiru", "P-1001", "0712345678", 26, 10000)
    inpatient = Inpatient("Daniel Kimani", "P-1002", "0723456789", 42, 15000)

    outpatient.patient_type()
    inpatient.patient_type()

    outpatient.process_payment(2500)
    inpatient.process_payment(3500)

    print("--- End of Polymorphism Demo ---\n")


demonstrate_polymorphism()


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
    print("8. Deposit Money")
    print("9. Withdraw Money")
    print("10. Process Patient Payment")
    print("11. Check Patient Balance")
    print("12. Cancel Appointment")
    print("13. Exit")

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
            patient_id = input("Enter patient ID: ").strip()
            patient = find_patient(patient_id)
            if patient is None:
                print("Patient not found.")
            else:
                try:
                    amount = float(input("Enter deposit amount: ").strip())
                    patient.deposit_money(amount)
                except ValueError:
                    print("Invalid amount. Please enter a valid number.")
        elif choice == "9":
            patient_id = input("Enter patient ID: ").strip()
            patient = find_patient(patient_id)
            if patient is None:
                print("Patient not found.")
            else:
                try:
                    amount = float(input("Enter withdrawal amount: ").strip())
                    patient.withdraw_money(amount)
                except ValueError:
                    print("Invalid amount. Please enter a valid number.")
        elif choice == "10":
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
                    patient.process_payment(doctor.consultation_fee)
                elif isinstance(patient, Inpatient):
                    patient.process_payment(doctor.consultation_fee)
                else:
                    print("Patient type not supported for payment.")
        elif choice == "11":
            patient_id = input("Enter patient ID: ").strip()
            patient = find_patient(patient_id)
            if patient is None:
                print("Patient not found.")
            else:
                print(f"Current balance for {patient.name}: Ksh {patient.check_balance():.2f}")
        elif choice == "12":
            appointment_id = input("Enter appointment index to cancel: ").strip()
            try:
                index = int(appointment_id)
                if 0 <= index < len(appointments):
                    appointments[index].cancel_appointment()
                else:
                    print("Invalid appointment index.")
            except ValueError:
                print("Invalid input. Please enter a valid number.")
        elif choice == "13":
            print("Exiting SMART HOSPITAL MANAGEMENT system. Goodbye!")
            break
        else:
            print("Invalid choice. Please select a number from 1 to 13.")

        print()
    except Exception as error:
        print(f"An unexpected error occurred: {error}")




    


    



