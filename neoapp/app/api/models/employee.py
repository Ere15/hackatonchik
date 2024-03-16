from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from neoapp.app.db.base_class import Base

class Сотрудники(Base):
    __tablename__ = "Сотрудники"

    id_сотрудника = Column(Integer, primary_key=True, index=True, unique=True, autoincrement=True, nullable=False)
    Фамилия = Column(String, nullable=False)
    Имя = Column(String, nullable=False)
    Должность = Column(String, nullable=False)
    Логин = Column(String, unique=True, index=True, nullable=False)
    Пароль = Column(String, nullable=False)
    Роль_на_сайте = Column(String, nullable=False)

    # Определение обратного отношения один-ко-многим с таблицей "Запросы"
    запросы = relationship("Запросы", back_populates="сотрудники")