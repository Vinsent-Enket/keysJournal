# main.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from peewee import DoesNotExist

import models
from models import Shelf, ShelfOwner, Employee, Key, EmployeeKey, KeyStatus, db

# -----------------------------------------------------------------
# 1. Инициализация БД
# -----------------------------------------------------------------
models.create_tables()

# -----------------------------------------------------------------
# 2. Окно приложения
# -----------------------------------------------------------------
root = tk.Tk()
root.title("Storage Manager")
root.geometry("900x600")

# -----------------------------------------------------------------
# 3. Вкладки
# -----------------------------------------------------------------
tab_control = ttk.Notebook(root)
tab_control.pack(expand=1, fill='both')


# -----------------------------------------------------------------
# Вкладка "Шкафы"
# -----------------------------------------------------------------
def refresh_shelves():
    shelves_list.delete(*shelves_list.get_children())
    for shelf in Shelf.select():
        owners = ", ".join([o.employee.last_name + " " + o.employee.first_name
                            for o in ShelfOwner.select().where(ShelfOwner.shelf == shelf)])
        keys = ", ".join([f"{k.number}" for k in Key.select().where(Key.shelf == shelf)])
        shelves_list.insert('', 'end', values=(shelf.number, owners, keys, shelf.notes or ""))


def add_shelf():
    number = simpledialog.askstring("Add Shelf", "Номер шкафа:")
    if not number: return
    notes = simpledialog.askstring("Add Shelf", "Заметки:")
    try:
        Shelf.create(number=number, notes=notes)
        refresh_shelves()
    except Exception as e:
        messagebox.showerror("Error", f"Не удалось добавить: {e}")


def edit_shelf():
    sel = shelves_list.selection()
    if not sel:
        messagebox.showwarning("Select", "Выберите шкафчик")
        return
    item = shelves_list.item(sel[0])
    number = item['values'][0]
    shelf = Shelf.get(Shelf.number == number)
    new_number = simpledialog.askstring("Edit Shelf", "Номер шкафа:", initialvalue=shelf.number)
    new_notes = simpledialog.askstring("Edit Shelf", "Заметки:", initialvalue=shelf.notes or "")
    try:
        shelf.number = new_number
        shelf.notes = new_notes
        shelf.save()
        refresh_shelves()
    except Exception as e:
        messagebox.showerror("Error", f"Не удалось обновить: {e}")


def delete_shelf():
    sel = shelves_list.selection()
    if not sel:
        messagebox.showwarning("Select", "Выберите шкафчик")
        return
    if not messagebox.askyesno("Delete", "Удалить выбранный шкафчик?"):
        return
    item = shelves_list.item(sel[0])
    number = item['values'][0]

    try:
        Shelf.delete().where(Shelf.number == number).execute()
        refresh_shelves()
    except Exception as e:
        messagebox.showerror("Error", f"Не удалось удалить: {e}")


# -----------------------------------------------------------------
# 5. Вкладка «Шкафчики»
# -----------------------------------------------------------------
shelves_frame = ttk.Frame(tab_control)
tab_control.add(shelves_frame, text='Шкафчики')

# Таблица
columns = ('number', 'owners', 'keys', 'notes')
shelves_list = ttk.Treeview(shelves_frame, columns=columns, show='headings')
for col in columns:
    shelves_list.heading(col, text=col.capitalize())
shelves_list.pack(fill='both', expand=True, side='left')
shelves_list.bind('<<TreeviewSelect>>', lambda e: None)

# Сайдбар
shelf_btn_frame = ttk.Frame(shelves_frame)
shelf_btn_frame.pack(fill='y', side='right')

ttk.Button(shelf_btn_frame, text='Добавить', command=add_shelf).pack(fill='x', pady=2)
ttk.Button(shelf_btn_frame, text='Изменить', command=edit_shelf).pack(fill='x', pady=2)
ttk.Button(shelf_btn_frame, text='Удалить', command=delete_shelf).pack(fill='x', pady=2)

refresh_shelves()

# -----------------------------------------------------------------
# 6. Вкладка «Сотрудники»
# -----------------------------------------------------------------
employees_frame = ttk.Frame(tab_control)
tab_control.add(employees_frame, text='Сотрудники')


def refresh_employees():
    employees_list.delete(*employees_list.get_children())
    for emp in Employee.select():
        shelves = ", ".join([str(o.shelf.number) for o in ShelfOwner.select().where(ShelfOwner.employee == emp)])
        hand_keys = ", ".join([f"{k.key.number}" for k in EmployeeKey.select().where(EmployeeKey.employee == emp)])
        employees_list.insert('', 'end', values=(
        emp.id, emp.last_name, emp.first_name, emp.patronymic or "", shelves, hand_keys, emp.notes or ""))


def add_employee():
    first = simpledialog.askstring("Add Employee", "Имя:")
    last = simpledialog.askstring("Add Employee", "Фамилия:")
    patronymic = simpledialog.askstring("Add Employee", "Отчество:")
    notes = simpledialog.askstring("Add Employee", "Заметки:")
    if not first or not last:
        messagebox.showwarning("Error", "Имя и фамилия обязательны")
        return
    try:
        Employee.create(first_name=first, last_name=last,
                        patronymic=patronymic, notes=notes)
        refresh_employees()
    except Exception as e:
        messagebox.showerror("Error", f"Не удалось добавить: {e}")


def edit_employee():
    sel = employees_list.selection()
    if not sel:
        messagebox.showwarning("Select", "Выберите сотрудника")
        return
    item = employees_list.item(sel[0])
    emp_id = item['values'][0]
    emp = Employee.get(Employee.id == emp_id)
    first = simpledialog.askstring("Edit Employee", "Имя:", initialvalue=emp.first_name)
    last = simpledialog.askstring("Edit Employee", "Фамилия:", initialvalue=emp.last_name)
    patronymic = simpledialog.askstring("Edit Employee", "Отчество:", initialvalue=emp.patronymic or "")
    notes = simpledialog.askstring("Edit Employee", "Заметки:", initialvalue=emp.notes or "")
    try:
        emp.first_name = first
        emp.last_name = last
        emp.patronymic = patronymic
        emp.notes = notes
        emp.save()
        refresh_employees()
    except Exception as e:
        messagebox.showerror("Error", f"Не удалось обновить: {e}")


def delete_employee():
    sel = employees_list.selection()
    if not sel:
        messagebox.showwarning("Select", "Выберите сотрудника")
        return
    if not messagebox.askyesno("Delete", "Удалить выбранного сотрудника?"):
        return
    item = employees_list.item(sel[0])
    emp_id = item['values'][0]
    try:
        Employee.delete().where(Employee.id == emp_id).execute()
        refresh_employees()
    except Exception as e:
        messagebox.showerror("Error", f"Не удалось удалить: {e}")


# Таблица сотрудников
emp_columns = ('id', 'last', 'first', 'patronymic', 'shelves', 'hand_keys', 'notes')
employees_list = ttk.Treeview(employees_frame, columns=emp_columns, show='headings')
for col in emp_columns:
    employees_list.heading(col, text=col.upper())
employees_list.pack(fill='both', expand=True, side='left')

emp_btn_frame = ttk.Frame(employees_frame)
emp_btn_frame.pack(fill='y', side='right')
ttk.Button(emp_btn_frame, text='Добавить', command=add_employee).pack(fill='x', pady=2)
ttk.Button(emp_btn_frame, text='Изменить', command=edit_employee).pack(fill='x', pady=2)
ttk.Button(emp_btn_frame, text='Удалить', command=delete_employee).pack(fill='x', pady=2)

refresh_employees()

# -----------------------------------------------------------------
# 7. Вкладка «Ключи»
# -----------------------------------------------------------------
keys_frame = ttk.Frame(tab_control)
tab_control.add(keys_frame, text='Ключи')


def refresh_keys():
    keys_list.delete(*keys_list.get_children())
    for key in Key.select():
        owner_name = f"{key.owner.last_name} {key.owner.first_name}"
        status = 'Основной' if key.status == KeyStatus.PRIMARY else 'Резервный'
        keys_list.insert('', 'end', values=(key.id, key.number, key.shelf.number, owner_name, status, key.notes or ""))


def add_key():
    # Выбор шкафа
    shelf_nums = [s.number for s in Shelf.select()]
    if not shelf_nums:
        messagebox.showwarning("No Shelves", "Создайте шкафчик сначала")
        return
    shelf_no = simpledialog.askstring("Add Key", f"Номер шкафа {shelf_nums}:", initialvalue=shelf_nums[0])
    try:
        shelf = Shelf.get(Shelf.number == shelf_no)
    except DoesNotExist:
        messagebox.showerror("Error", "Такой шкафчик не найден")
        return
    # Владелец
    emp_names = [f"{e.id}:{e.last_name} {e.first_name}" for e in Employee.select()]
    if not emp_names:
        messagebox.showwarning("No Employees", "Создайте сотрудника сначала")
        return
    emp_str = simpledialog.askstring("Add Key", f"Владелец {emp_names}:", initialvalue=emp_names[0])
    emp_id = int(emp_str.split(":")[0])
    try:
        owner = Employee.get(Employee.id == emp_id)
    except DoesNotExist:
        messagebox.showerror("Error", "Такой сотрудник не найден")
        return
    number = simpledialog.askstring("Add Key", "Номер ключа:")
    status_str = simpledialog.askstring("Add Key", "Статус (1 – Основной, 2 – Резервный):", initialvalue="1")
    status = KeyStatus.PRIMARY if status_str.strip() == '1' else KeyStatus.BACKUP
    notes = simpledialog.askstring("Add Key", "Заметки:")
    try:
        Key.create(number=number, shelf=shelf, owner=owner, status=status, notes=notes)
        refresh_keys()
    except Exception as e:
        messagebox.showerror("Error", f"Не удалось добавить: {e}")


def edit_key():
    sel = keys_list.selection()
    if not sel:
        messagebox.showwarning("Select", "Выберите ключ")
        return
    item = keys_list.item(sel[0])
    key_id = item['values'][0]
    key = Key.get(Key.id == key_id)
    # Взаимодействие с пользователем
    number = simpledialog.askstring("Edit Key", "Номер ключа:", initialvalue=key.number)
    shelf_no = simpledialog.askstring("Edit Key", "Номер шкафа:", initialvalue=str(key.shelf.number))
    try:
        shelf = Shelf.get(Shelf.number == shelf_no)
    except DoesNotExist:
        messagebox.showerror("Error", "Такой шкафчик не найден")
        return
    owner_str = simpledialog.askstring("Edit Key", "Владелец (id:name):",
                                       initialvalue=f"{key.owner.id}:{key.owner.last_name} {key.owner.first_name}")
    owner_id = int(owner_str.split(":")[0])
    try:
        owner = Employee.get(Employee.id == owner_id)
    except DoesNotExist:
        messagebox.showerror("Error", "Такой сотрудник не найден")
        return
    status_str = simpledialog.askstring("Edit Key", "Статус (1 – Основной, 2 – Резервный):",
                                        initialvalue="1" if key.status == KeyStatus.PRIMARY else "2")
    status = KeyStatus.PRIMARY if status_str.strip() == '1' else KeyStatus.BACKUP
    notes = simpledialog.askstring("Edit Key", "Заметки:", initialvalue=key.notes or "")
    try:
        key.number = number
        key.shelf = shelf
        key.owner = owner
        key.status = status
        key.notes = notes
        key.save()
        refresh_keys()
    except Exception as e:
        messagebox.showerror("Error", f"Не удалось обновить: {e}")


def delete_key():
    sel = keys_list.selection()
    if not sel:
        messagebox.showwarning("Select", "Выберите ключ")
        return
    if not messagebox.askyesno("Delete", "Удалить выбранный ключ?"):
        return
    item = keys_list.item(sel[0])
    key_id = item['values'][0]
    try:
        Key.delete().where(Key.id == key_id).execute()
        refresh_keys()
    except Exception as e:
        messagebox.showerror("Error", f"Не удалось удалить: {e}")


# Таблица ключей
key_columns = ('id', 'number', 'shelf', 'owner', 'status', 'notes')
keys_list = ttk.Treeview(keys_frame, columns=key_columns, show='headings')
for col in key_columns:
    keys_list.heading(col, text=col.upper())
keys_list.pack(fill='both', expand=True, side='left')

key_btn_frame = ttk.Frame(keys_frame)
key_btn_frame.pack(fill='y', side='right')
ttk.Button(key_btn_frame, text='Добавить', command=add_key).pack(fill='x', pady=2)
ttk.Button(key_btn_frame, text='Изменить', command=edit_key).pack(fill='x', pady=2)
ttk.Button(key_btn_frame, text='Удалить', command=delete_key).pack(fill='x', pady=2)

refresh_keys()

# -----------------------------------------------------------------
# 8. Запуск
# -----------------------------------------------------------------
root.mainloop()
