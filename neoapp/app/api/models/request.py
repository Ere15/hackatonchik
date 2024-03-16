from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from neoapp.app.db.base_class import Base
from sqlalchemy import func 
from .employee import Сотрудники 

class Запросы(Base):
    __tablename__ = "Запросы"

    id_запроса = Column(Integer, primary_key=True, index=True, unique=True, autoincrement=True, nullable=False)
    Тема = Column(String, nullable=False)
    Метки = Column(String, nullable=False)
    Описание = Column(String, nullable=False)
    Дата_запроса = Column(Date, nullable=False, default=func.current_date()) 
    Дата_ответа = Column(Date)
    Статус = Column(String, nullable=False)
    id_сотрудника = Column(Integer, ForeignKey('Сотрудники.id_сотрудника'), nullable=False)
    id_получателя = Column(Integer, nullable=False)

    # Определение отношения многие-к-одному с таблицей "Сотрудники"
    сотрудники = relationship("Сотрудники", back_populates="запросы")


