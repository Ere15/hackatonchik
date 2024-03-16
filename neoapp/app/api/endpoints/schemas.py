from pydantic import BaseModel
from typing import Optional
from typing import List
from datetime import date
from enum import Enum

# Схема данных для запроса аутентификации пользователя
class LoginRequest(BaseModel):
    Логин: str
    Пароль: str

# Схема данных для создания нового запроса
class RequestCreate(BaseModel):
    Тема: str
    Метки: str
    Описание: str
    Дата_запроса: Optional[date] = None
    Дата_ответа: Optional[date] = None
    Статус: Optional[str] = None
    Получатель: str

# Схема данных для редактирования запроса
class RequestEdit(BaseModel):
    Тема: Optional[str] = None
    Метки: Optional[str] = None
    Описание: Optional[str] = None
    Дата_запроса: Optional[date] = None
    Дата_ответа: Optional[date] = None
    Статус: Optional[str] = None
    id_сотрудника: Optional[int] = None

# Схема данных для профиля владельца
class OwnerProfile(BaseModel):
    id_владельца: int
    имя_пользователя: str
    электронная_почта: str

# Схема данных для сотрудника

class Employee(BaseModel):
    Фамилия: str
    Имя: str
    Должность: str

# Схема данных для просмотра запроса на рассмотрение
class RequestView(BaseModel):
    id: int
    тема: str
    метки: str
    описание: str
    дата_запроса: Optional[str] = None
    дата_ответа: Optional[str] = None
    статус: Optional[str] = None
    id_сотрудника: int

# Схема данных для просмотра рассмотренных запросов
class ReviewedRequestView(BaseModel):
    id: int
    тема: str
    метки: str
    описание: str
    дата_запроса: Optional[str] = None
    дата_ответа: Optional[str] = None
    статус: Optional[str] = None
    id_сотрудника: int

#для отправки запросов на утверждение владельцу после модерации для админа
class SendToOwnerRequest(BaseModel):
    id_запроса: List[int]


class RequestStatus(str, Enum):
    PENDING = "на рассмотрении"
    APPROVED = "одобрено"
    REJECTED = "отклонено"



class RequestHistory(BaseModel):
    id: int
    статус: str
    комментарий: Optional[str]

class AdminRequest(BaseModel):
    получатели: List[int]
    тема: str
    описание: str

class SendAdminRequest(BaseModel):
    сообщение: str