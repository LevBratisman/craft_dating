from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.init import Base

    
class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(unique=True)
    username: Mapped[str] = mapped_column(String(150), nullable=True)
    sex: Mapped[int] = mapped_column(nullable=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    age: Mapped[int] = mapped_column(nullable=False)
    city: Mapped[str] = mapped_column(String(150), nullable=False)
    photo: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    iterator: Mapped[int] = mapped_column(nullable=True, default=0)
    like_iterator: Mapped[int] = mapped_column(nullable=True, default=0)
    
    

class Filter(Base):
    __tablename__ = 'filter'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(unique=True)
    target: Mapped[str] = mapped_column(String(150), nullable=True)
    sex_target: Mapped[int] = mapped_column(nullable=True)
    city: Mapped[str] = mapped_column(String(150), nullable=True)
    age_from: Mapped[int] = mapped_column(nullable=True)
    age_to: Mapped[int] = mapped_column(nullable=True)    



class Like(Base):
    __tablename__ = 'like'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column()
    liked_users_id: Mapped[str] = mapped_column()

    