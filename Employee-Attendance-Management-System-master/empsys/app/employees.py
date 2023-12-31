import csv
import datetime
from ..data import db_connect
from tkinter import *
from tkinter import messagebox


class Employee:
    TITLES = ('Manager', 'Senior', 'Junior')

    def __init__(self, emp_id: str, name: str, title: str, phone: str, birthday):
        self.id = str(emp_id)
        self.name = name
        self.title = title
        if "-" not in phone:
            if len(phone) == 9:
                phone = phone[0:2] + '-' + phone[2:]
            else:
                phone = phone[0:3] + '-' + phone[3:]
        self.phone = phone
        if type(birthday) is str:
            birthday = datetime.datetime.strptime(birthday, "%d-%m-%Y").date()
        self.birthday = birthday

        self._age = None
        self._age_last_recalculated = None

        self._recalculate_age()

    def _recalculate_age(self):
        today = datetime.date.today()
        age = today.year - self.birthday.year
        if today < datetime.date(today.year, self.birthday.month, self.birthday.day):
            age -= 1
        self._age = age
        self._age_last_recalculated = today

    def age(self):
        if datetime.date.today() > self._age_last_recalculated:
            self._recalculate_age()
        return self._age

    def __str__(self):
        return f"ID Number: {self.id}\nName: {self.name}\nTitle: {self.title}\nPhone: {self.phone}\nAge: {self._age}"

    # Functions related to Employee

    @staticmethod
    def load_employee_dic(user_path=None):
        # Used as a helper for adding employees from file
        with open(user_path, mode='r') as csv_file:
            dic = {}
            csv_reader = csv.reader(csv_file, delimiter=',')
            if csv_reader is None:
                messagebox.showwarning("Add Employees by File", 'The file was empty')
                return dic, 0
            line_count = 0
            for row in csv_reader:
                if line_count != 0 and len(row) == 5:
                    message = ""
                    if not(row[0].isdecimal() and len(row[0])):
                        message += 'The ID should include 9 digits\n'
                    name = Employee.check_name(row[1])
                    message += name[1] + '\n'
                    if not (row[2] in Employee.TITLES):
                        message += f'The title should be one of: {Employee.TITLES}' + '\n'
                    phone = Employee.check_phone(row[3])
                    birthday = Employee.check_birthday(row[4])
                    message += phone[1] + '\n' + birthday[1]
                    if len(message) > 3:
                        messagebox.showwarning("Add Employees by File", f'The data in row {line_count} does not' +
                                               '\ncorrespond to the requirements:\n' + message)
                        return None, None
                    else:
                        dic[row[0]] = Employee(row[0], row[1], row[2], row[3], row[4])
                else:
                    if line_count > 0:
                        messagebox.showwarning("Add Employees by File",
                                               f'The data in row {line_count} doesn\'t' +
                                               '\ncorrespond to the requirement.\n'
                                               'Make sure to include:\n'
                                               'ID, name, title, phone and birthday.')
                        return None, None
                line_count += 1
            return dic, (line_count - 1)

    @staticmethod
    def check_id(cur=None, e_id=None):
        # Checks if the ID is valid and if we have it in our database
        message = ""
        new_id = 0  # a flag for right input
        color = ""
        valid_id = 0
        if len(e_id) == 9:
            valid_id = sum(sum(map(int, str(int(a) * (i % 2 + 1)))) for i, a in enumerate(e_id, 0)) % 10 == 0
        if e_id is None or len(e_id) == 0:
            message = "Please enter ID to proceed."
            color = "black"
        elif not e_id.isdecimal() or (len(e_id) != 9):
            message = "The ID should be an integer of 9 digits."
            color = "red"
        elif not valid_id:
            message = "The ID isn't valid."
            color = "red"
        elif cur is not None:  # 9 digit ID
            if db_connect.check_id_exist(cur, e_id):
                message = "Employee name is %s." % db_connect.employee_name(cur, e_id)
                color = "blue"
            else:
                message = "Let's add the employee"
                color = "green"
                new_id = 1
        return new_id, message, color

    @staticmethod
    def check_name(name):  # part of add_employee_manually
        """Recieves the user input name, and checks it's a string of chars only."""
        message = ""
        correct = 0
        if not re.match("^[A-Za-z][A-Za-z'\-]+([ ][A-Za-z][A-Za-z'\-]+)*$", name):
            if name == '':
                message = "Please enter Employee Name to proceed."
            elif '  ' in name:
                message = 'Only one consecutive space allowed.'
            else:
                message = 'The name should consist of letters only\n and include 2 consecutive letters at least.'
        else:
            correct = 1
        return correct, message

    @staticmethod
    def check_phone(phone: str):  # part of add_employee_manually
        message = ""
        correct = 0     # a flag for right input
        if not re.match('0[1-9]{1,2}-?[1-9]{7}$', phone):
            if phone == "":
                message = "Please enter Phone to proceed."
            else:
                message = "Make sure you follow the template(0xx-xxxxxxx)\n and enter numbers only."
        else:
            correct = 1
        return correct, message

    @staticmethod
    def check_birthday(birthday):  # part of add_employee_manually
        message = ""
        try:
            if type(birthday) is str:
                birthday = datetime.datetime.strptime(birthday, "%d-%m-%Y").date()
        except Exception as ex:
            print(ex)
            message = 'The date should be in the format dd-mm-yyyy'
            correct = 0
        else:
            age = datetime.date.today().year - birthday.year
            if not (15 <= age <= 99):
                message = 'Please check the date. your employee is %d years old' % age
                correct = 0
            else:
                correct = 1
        return correct, message

    @staticmethod
    def add_employee_from_file(cur, file_path):
        # Runs the load dictionary to load the new rows and if the file is proper adds the values to the DB
        new_dic, num = Employee.load_employee_dic(file_path)
        count = 0
        message = ''
        if num is not None and num > 0:
            for employee in new_dic.values():
                if not db_connect.check_id_exist(cur, employee.id):
                    db_connect.add_employee(cur, employee)
                    count += 1
            if num > count:
                message = '\nNumber of employees that already\n' + f' existed in the database: {num - count}.'
            messagebox.showinfo("Add Employees by File", f'Number of added employees: {count}.' + message)
        return

    @staticmethod
    def delete_employee_manually(cur, e_id=None):
        # The function allows to delete an employee by ID
        messagebox.askokcancel("Delete Employee", "You are going to loose all the information about employee %s.\n"
                                                  "Do you want to proceed?" % e_id)
        db_connect.delete_employee(cur, e_id)
        messagebox.showinfo("Delete Employee", "Employee with ID %s was deleted." % e_id)

    @staticmethod
    def load_employees_dic_to_delete(user_path):
        # Helper function, reads the IDs and makes sure that the IDs are valid
        with open(user_path, mode='r') as csv_file:
            delete_ids_array = []
            csv_reader = csv.reader(csv_file, delimiter=',')
            if csv_reader is None:
                messagebox.showwarning("Delete Employees by File", 'The file was empty')
                return delete_ids_array, 0
            line_count = 0
            for row in csv_reader:
                if line_count != 0:
                    if len(row) == 1:
                        e_id = str(row[0])
                        if e_id.isdecimal() and len(e_id) == 9:
                            delete_ids_array.append(e_id)
                        else:
                            messagebox.showwarning("Delete Employees by File", f'The data in row {line_count}' +
                                                   '\n doesn\'t correspond to an ID.')
                            return None, None
                    else:
                        messagebox.showwarning("Delete Employees by File", f'There is extra data in row {line_count}.')
                        return None, None
                line_count += 1
            return delete_ids_array, (line_count - 1)

    @staticmethod
    def delete_employee_from_file(cur, file_path):
        # Deletes the employees by ID from the database and reflects how many were deleted.
        # Also prompt about the IDs that didn't exist in our employee file.
        del_arr, num = Employee.load_employees_dic_to_delete(file_path)
        if num is not None and num > 0:
            non_exist = []
            for e_id in del_arr:
                if db_connect.check_id_exist(cur, e_id):
                    db_connect.delete_employee(cur, e_id)
                else:
                    non_exist.append(e_id)
            if len(non_exist) == num:
                messagebox.showinfo("Delete Employees by File", 'There were no employees with those IDs in our company.')
            elif len(non_exist) == 0:
                messagebox.showinfo("Delete Employees by File", f'Number of employees deleted: {num}.')
            else:
                messagebox.showinfo("Delete Employees by File", f'Number of employees deleted: {num - len(non_exist)}' +
                                                                '\n The following employees didn\'t'
                                                                ' exist in our company:\n'
                                                                + '%s' % ',\n'.join(non_exist))
        return
