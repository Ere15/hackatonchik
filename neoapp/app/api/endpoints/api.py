from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import schemas
from . import crud
from .crud import RequestStatus, get_current_user,ten_percent_approval_condition, fifty_percent_approval_condition, ninety_percent_approval_condition, hundred_percent_approval_condition,  get_request_history_by_id,  create_access_token, update_request_status, get_token_from_header, get_owner_profile, authenticate_user, get_owner_pending_requests, create_owner_request, send_requests_to_owner, get_all_employees
from .schemas import LoginRequest, RequestCreate, RequestEdit, OwnerProfile, Employee
from neoapp.app.db.base_class import get_db
from fastapi import Header
from typing import List
from sqlalchemy.sql import text
from neoapp.app.api.models.employee import Сотрудники
from neoapp.app.api.models.request import Запросы
import jwt
from jwt import PyJWTError
from dotenv import load_dotenv
import os
from typing import Callable
# Загрузка переменных среды из файла .env
load_dotenv()

# Получение значения SECRET_KEY из переменных среды
SECRET_KEY = os.getenv("SECRET_KEY")

ALGORITHM = os.getenv("ALGORITHM", "HS256")


router = APIRouter()

# Эндпоинт для аутентификации пользователей
@router.post("/")
def login(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    print('hellow')
    user = crud.authenticate_user(db, request.Логин, request.Пароль)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Генерируем токен в зависимости от роли пользователя
    access_token = None
    if user.Роль_на_сайте == "admin":
        access_token = create_access_token(data={"sub": user.id_сотрудника, "role": "admin"})
    elif user.Роль_на_сайте == "director":
        access_token = create_access_token(data={"sub": user.id_сотрудника, "role": "director"})
    else:
        access_token = create_access_token(data={"sub": user.id_сотрудника, "role": "default"})
    
    return {"access_token": access_token}



# Эндпоинт для просмотра запросов на рассмотрении 
@router.get("/owner/requests/pending", response_model=list[schemas.RequestView])
def get_owner_pending_requests(db: Session = Depends(get_db)):
    return crud.get_owner_pending_requests(db=db)

# Эндпоинт для просмотра рассмотренных запросов 
@router.get("/owner/requests/reviewed", response_model=list[schemas.ReviewedRequestView])
def get_owner_reviewed_requests(db: Session = Depends(get_db)):
    return crud.get_owner_reviewed_requests(db=db)


# Эндпоинт для создания нового запроса 
@router.post("/owner/requests/", response_model=schemas.RequestCreate)
def create_owner_request(request: schemas.RequestCreate, db: Session = Depends(get_db), token: str = Header(...)):
    try:
        #Декодирование токена и извлечение данных о пользователе
        decoded_token = get_token_from_header(token)
        current_user_id = decoded_token.get("sub")
        if current_user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        print("Current user ID:", current_user_id) 
        # Получаем объект текущего пользователя
        current_user = crud.get_current_user(db, current_user_id)
        if current_user is None:
            raise HTTPException(status_code=404, detail="Current user not found")
        print("Current user:", current_user)  
    except PyJWTError as e:
        print("Error decoding token:", e)  
        raise HTTPException(status_code=401, detail="Could not decode token")
    
    #Создаем запрос с указанием объекта текущего пользователя
    request_created = crud.create_owner_request(db=db, request=request)

    return request_created



# Эндпоинт для редактирования запроса (одобрение, отклонение, добавление комментария)
@router.put("/owner/requests/{request_id}/", response_model=schemas.RequestEdit)
def edit_owner_request(request_id: int, request: schemas.RequestEdit, db: Session = Depends(get_db)):
    existing_request = crud.get_request_by_id(db, request_id)
    if not existing_request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")

    if request.Описание:
        existing_request.Описание = request.Описание

    if request.Статус:
        if request.Статус == RequestStatus.APPROVED.value:
            #Обновляем статус запроса на "одобрено"
            update_request_status(db=db, request_id=request_id, new_status=RequestStatus.APPROVED, comment=request.comment)
        elif request.Статус == RequestStatus.REJECTED.value:
            if not request.comment:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Comment is required for rejected request")
            # Обновляем статус запроса на "отклонено"
            update_request_status(db=db, request_id=request_id, new_status=RequestStatus.REJECTED, comment=request.comment)

    db.commit()
    db.refresh(existing_request)
    return existing_request




# Эндпоинт для просмотра личного кабинета
@router.get("/owner/profile", response_model=schemas.OwnerProfile)
def get_owner_profile(db: Session = Depends(get_db)):
    return crud.get_owner_profile(db=db)

# Эндпоинт для отправки запросов на утверждение владельцу после модерации для админа
@router.post("/editor/requests/send_to_owner/", response_model=schemas.SendToOwnerRequest)
def send_requests_to_owner(request_ids: List[int], db: Session = Depends(get_db)):
    return crud.send_requests_to_owner(db=db, request_ids=request_ids)

# Эндпоинт для просмотра всех сотрудников из базы данных
@router.get("/admin/employees", response_model=list[schemas.Employee])
def get_all_employees(db: Session = Depends(get_db)):
    return crud.get_all_employees(db=db)


# Эндпоинт для проверки подключения к базе данных
@router.get("/check_db_connection", status_code=status.HTTP_200_OK)
def check_db_connection(db: Session = Depends(get_db)):
    try:
        #Попытка выполнения запроса к базе данных
        db.execute(text("SELECT 1"))
        return {"message": "Database connection is successful"}
    except Exception as e:
        # В случае ошибки возвращаем соответствующий статус и сообщение
        return {"message": f"Failed to connect to database: {str(e)}"}, status.HTTP_500_INTERNAL_SERVER_ERROR
    
# Эндпоинт для прочмотра истории запроса
@router.get("/owner/requests/{request_id}/history", response_model=List[schemas.RequestHistory])
def get_request_history(request_id: int, db: Session = Depends(get_db)):
    request_history = get_request_history_by_id(db=db, request_id=request_id)
    if not request_history:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request history not found")
    return request_history

# Эндпоинт для просмотра запросов, которые были рассмотренв
def get_owner_reviewed_requests(db: Session) -> List[schemas.ReviewedRequestView]:
    
    reviewed_requests = db.query(Запросы).filter(Запросы.Статус == "reviewed").all()
    
    # Преобразуем полученные данные в список объектов ReviewedRequestView
    reviewed_requests_views = []
    for request in reviewed_requests:
        reviewed_request_view = schemas.ReviewedRequestView(
            id=request.id,
            description=request.description,
            status=request.status,
            # Другие необхожимые поля
        )
        reviewed_requests_views.append(reviewed_request_view)
    
    return reviewed_requests_views

# Словарт условий
approval_conditions = {
    "10_percent": ten_percent_approval_condition,
    "50_percent": fifty_percent_approval_condition,
    "90_percent": ninety_percent_approval_condition,
    "100_percent": hundred_percent_approval_condition
}

# Эндпоинт для отправки запросов администратором с выбором условий одобрения
@router.post("/admin/requests/send/", response_model=schemas.SendAdminRequest)
def send_admin_request(
    request: schemas.AdminRequest,
    condition: str,  # Параметр, определяющий выбранное условие одобрения
    db: Session = Depends(get_db)
):
    # Проверяем, что указанное условие одобрения допустимо
    if condition not in approval_conditions:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid approval condition")

    # Получаем выбранную функцию для условия одобрения
    approval_condition_function: Callable[[schemas.AdminRequest], bool] = approval_conditions[condition]

    # Проверяем, что запрос содержит список получателей
    if not request.recipients:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No recipients provided")

    # Проверяем, что хотя бы один получатель указан
    if len(request.recipients) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No recipients provided")

    # Отправляем запрос каждому получателю
    for recipient_id in request.recipients:
        recipient = crud.get_employee_by_id(db, recipient_id)
        if not recipient:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Recipient with ID {recipient_id} not found")
        
        # Отправляем запрос с указанием получателя
        if approval_condition_function(request):
            # Если условие выполнено, отправляем запрос
            crud.send_request_to_employee(db=db, recipient_id=recipient_id, request=request)
        else:
            # Если условие не выполнено, отклоняем запрос
            crud.reject_request(db=db, recipient_id=recipient_id, request=request)

    return {"message": "Requests sent successfully"}