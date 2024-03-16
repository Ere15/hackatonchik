from sqlalchemy.orm import Session
from neoapp.app.api.models.employee import Сотрудники 


def get_first_five_employees(db: Session):
    # Получение первых 5 записей о сотрудниках из базы данных
    employees = db.query(Сотрудники).limit(5).all()
    
    # Вывод информации о каждом сотруднике в консоль
    for employee in employees:
        print(f"ID: {employee.id_сотрудника}, Имя: {employee.имя}, Фамилия: {employee.фамилия}, Должность: {employee.должность}")


db = Session()  
get_first_five_employees(db)

