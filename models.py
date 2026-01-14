# models.py
import datetime
from peewee import *
from peewee import SqliteDatabase

db = SqliteDatabase('storage.db')  # ← экземпляр Database


class BaseModel(Model):
    class Meta:
        database = db


# ----------------------------------------------------------
# 1. Шкафчики
# ----------------------------------------------------------
print(type(BaseModel._meta.database))
class Shelf(BaseModel):
    number = CharField(unique=True)  # номер шкафа
    notes = TextField(null=True)  # заметки





# ----------------------------------------------------------
# 2. Сотрудники
# ----------------------------------------------------------
class Employee(BaseModel):
    first_name = CharField()
    last_name = CharField()
    patronymic = CharField(null=True)
    notes = TextField(null=True)

class ShelfOwner(BaseModel):
    shelf = ForeignKeyField(Shelf, backref='owners')
    employee = ForeignKeyField(Employee, backref='shelves')
# ----------------------------------------------------------
# 3. Ключи
# ----------------------------------------------------------
class KeyStatus:
    PRIMARY = 0
    BACKUP = 1


class Key(BaseModel):
    number = CharField()  # номер ключа
    shelf = ForeignKeyField(Shelf)  # к какому шкафчику относится
    owner = ForeignKeyField(Employee)  # «основной» владелец
    status = IntegerField(default=KeyStatus.PRIMARY)
    notes = TextField(null=True)

    class Meta:
        indexes = (
            (('number', 'shelf'), True),  # уникальный номер + шкаф
        )


# ----------------------------------------------------------
# 4. Ключи, которые держит сотрудник (в руке)
# ----------------------------------------------------------
class EmployeeKey(BaseModel):
    employee = ForeignKeyField(Employee, backref='hand_keys')
    key = ForeignKeyField(Key, backref='hand_employees')


# ----------------------------------------------------------
# Создание таблиц
# ----------------------------------------------------------
def create_tables():
    db.connect()
    db.create_tables([Shelf, ShelfOwner, Employee, Key, EmployeeKey])
