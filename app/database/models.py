from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.init import Base

    
class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(unique=True)
    username: Mapped[str] = mapped_column(String(150), nullable=True)
    target: Mapped[str] = mapped_column(String(150), nullable=True)
    sex: Mapped[int] = mapped_column(nullable=True)
    sex_target: Mapped[int] = mapped_column(nullable=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    age: Mapped[int] = mapped_column(nullable=False)
    city: Mapped[str] = mapped_column(String(150), nullable=False)
    photo: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    liked_users: Mapped[str] = mapped_column(nullable=True)
    
    
    


    