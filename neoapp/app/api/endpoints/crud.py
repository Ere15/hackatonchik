from sqlalchemy.orm import Session
from . import schemas
from neoapp.app.db.base_class import Base 
from neoapp.app.api.models.employee import  Сотрудники 
from neoapp.app.api.models.request import Запросы
from typing import List

from fastapi import HTTPException, status, Header
from datetime import datetime, timedelta
from typing import Optional
import jwt
from dotenv import load_dotenv
import os
from neoapp.app.api.models.employee import Сотрудники
from .schemas import Employee as DBEmployee
from .schemas import Employee, RequestStatus

# Загрузка переменных среды из файла .env
load_dotenv()

# Получение значения SECRET_KEY из переменных среды
SECRET_KEY = os.getenv("SECRET_KEY")

ALGORITHM = os.getenv("ALGORITHM", "HS256")


# Функция для аутентификации пользователя
def authenticate_user(db: Session, username: str, password: str):
    print('asd')
    return db.query(Сотрудники).filter(Сотрудники.Логин == username, Сотрудники.Пароль == password).first()


# Функция для создания запроса
def create_owner_request(db: Session, request: schemas.RequestCreate, current_user_id: int):
    # Создаем запрос с указанием статуса "на рассмотрении" и идентификатора текущего пользователя
    request_data = request.dict()
    request_data['Статус'] = "на рассмотрении"
    request_data['id_сотрудника'] = current_user_id
    
    # Создаем объект запроча и добавляем его в сессию
    db_request = Запросы(**request_data)
    db.add(db_request)
    db.commit()
    db.refresh(db_request)

    # Обновляем статус созданного запроса на на рассмотрении
    update_request_status(db, db_request.id_запроса, new_status=RequestStatus.PENDING)

    return db_request



# Функция для редактирования запроса владельцем
def create_owner_request(db: Session, request: schemas.RequestCreate):
    # Создаем запрос с указанием статуса на рассмотрении
    request_data = request.dict()
    request_data['Статус'] = "на рассмотрении"
    
    # Получаем текущего пользователя
    current_user = get_current_user(db, id) 
    if current_user is None:
        raise HTTPException(status_code=404, detail="Current user not found")
    
    # Создаем объект запроса и добавляем его в сессию
    db_request = Запросы(**request_data, id_сотрудника=current_user.id_сотрудника)  
    db.add(db_request)
    db.commit()
    db.refresh(db_request)

    # Обновляем статус созданного запроса на на рассмотрении
    update_request_status(db, db_request.id_запроса, new_status=RequestStatus.PENDING)

    return db_request


# Функция для получения всех сотрудников с заполненными обязательными полями
def get_all_employees(db: Session) -> List[schemas.Employee]:
    employees = db.query(Сотрудники).all()
    return [schemas.Employee(Фамилия=emp.Фамилия, Имя=emp.Имя, Должность=emp.Должность) for emp in employees]


# Функция получения роли из бд
def get_user_role_from_database(user_id: int, db: Session):
    employee = db.query(Сотрудники).filter(Сотрудники.id_сотрудника == user_id).first()
    if employee:
        return employee.Роль_на_сайте
    else:
        return None

# Функция для получения текущего пользователя из бд
def get_current_user(db: Session, id: int):
    return db.query(Сотрудники).filter(Сотрудники.id_сотрудника == id).first()

# Функция для получения статуса запроса
def get_owner_pending_requests(db: Session):
    return db.query(Запросы).filter(Запросы.Статус == "pending").all()

# Функция для получения профиля владельца системы
def get_owner_profile(db: Session):
    owner_profile = db.query(Сотрудники).filter(Сотрудники.Роль_на_сайте == "owner").first()
    return owner_profile

def send_requests_to_owner(db: Session, request_ids: List[int]):
    # Получаем владельца
    owner = get_owner_profile(db)

    # отправка запросов на утверждение владельцу
    
    for request_id in request_ids:
        request = db.query(Запросы).filter(Запросы.id_запроса == request_id).first()
        if request:
            request.status = "pending"
            request.владелец = owner.id_сотрудника
            db.commit()
            db.refresh(request)
    return "Requests sent to owner successfully"


def update_request_status(db: Session, request_id: int, new_status: RequestStatus, comment: str = None):
    request = db.query(Запросы).filter(Запросы.id_запроса == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    request.Статус = new_status.value
    if comment:
        request.Комментарий = comment
    db.commit()
    db.refresh(request)
    return request

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)  
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  
    return encoded_jwt


def get_token_from_header(authorization: str = Header(...)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header. Bearer token required")
    
    token = authorization.replace("Bearer ", "")
    print("Received token:", token)  # Добавляем отладочный вывод
    
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_token
    except Exception as e:
        print("Error decoding token:", e)  # Добавляем вывод ошибки
        raise HTTPException(status_code=401, detail="Could not decode token")


def get_request_by_id(db: Session, request_id: int) -> Запросы:
    return db.query(Запросы).filter(Запросы.id_запроса == request_id).first()

def get_owner_reviewed_requests(db: Session) -> List[Запросы]:
    return db.query(Запросы).filter(Запросы.Статус == "reviewed").all()


def get_request_history_by_id(db: Session, request_id: int):
    # Извлекаем все записи из таблицы Запросы, относящиеся к указанному запросу
    request_history = db.query(Запросы).filter(Запросы.id_запроса == request_id).all()
    return request_history


# Функции для проверки условий одобрения запроса администратором
def ten_percent_approval_condition(request: schemas.AdminRequest) -> bool:
    # Получаем количество получателей
    num_recipients = len(request.recipients)
    # Определяем количество получателей, которые должны проголосовать (10%)
    num_votes_required = num_recipients * 0.1
    # Проверяем, что количество получателей, проголосовавших, больше или равно количеству, необходимому для одобрения запроса
    return len(request.votes) >= num_votes_required


def fifty_percent_approval_condition(request: schemas.AdminRequest) -> bool:
    # Получаем количество получателей
    num_recipients = len(request.recipients)
    # Определяем количество получателей, которые должны проголосовать (50%)
    num_votes_required = num_recipients * 0.5
    # Проверяем, что количество получателей, проголосовавших, больше или равно количеству, необходимому для одобрения запроса
    return len(request.votes) >= num_votes_required


def ninety_percent_approval_condition(request: schemas.AdminRequest) -> bool:
    # Получаем количество получателей
    num_recipients = len(request.recipients)
    # Определяем количество получателей, которые должны проголосовать (90%)
    num_votes_required = num_recipients * 0.9
    # Проверяем, что количество получателей, проголосовавших, больше или равно количеству, необходимому для одобрения запроса
    return len(request.votes) >= num_votes_required


def hundred_percent_approval_condition(request: schemas.AdminRequest) -> bool:
    # Получаем количество получателей
    num_recipients = len(request.recipients)
    # Определяем количество получателей, которые должны проголосовать (100%)
    num_votes_required = num_recipients
    # Проверяем, что количество получателей, проголосовавших, больше или равно количеству, необходимому для одобрения запроса
    return len(request.votes) >= num_votes_required
