from sqlalchemy import DateTime, String, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase



# Base model
class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class Uni(Base):
    __tablename__ = 'uni'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    full_name: Mapped[str] = mapped_column(String(250), nullable=False)
    city: Mapped[str] = mapped_column(String(150), nullable=False)
    count_of_students: Mapped[int] = mapped_column(nullable=False, default=0)

    
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
    project_iterator: Mapped[int] = mapped_column(nullable=True, default=0)
    request_iterator: Mapped[int] = mapped_column(nullable=True, default=0)
    uni_id: Mapped[int] = mapped_column(ForeignKey('uni.id', ondelete='CASCADE'), nullable=True)
    
    uni: Mapped['Uni'] = relationship(backref='user')

    
    

class Filter(Base):
    __tablename__ = 'filter'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(unique=True)
    target: Mapped[str] = mapped_column(String(150), nullable=True)
    sex_target: Mapped[int] = mapped_column(nullable=True)
    uni_id: Mapped[int] = mapped_column(ForeignKey('uni.id', ondelete='CASCADE'), nullable=True)
    
    uni: Mapped['Uni'] = relationship(backref='filter')



class Like(Base):
    __tablename__ = 'like'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column()
    liked_users_id: Mapped[str] = mapped_column()
    
    
class Project(Base):
    __tablename__ = 'project'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column()
    uni_id: Mapped[int] = mapped_column(ForeignKey('uni.id', ondelete='CASCADE'), nullable=True)
    project_name: Mapped[str] = mapped_column()
    project_description: Mapped[str] = mapped_column()
    project_requirements: Mapped[str] = mapped_column()
    project_image: Mapped[str] = mapped_column()


class Request(Base):
    __tablename__ = 'request'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column()
    project_id: Mapped[int] = mapped_column(ForeignKey('project.id', ondelete='CASCADE'), nullable=True)
    creator_id: Mapped[int] = mapped_column()
    
    project: Mapped['Project'] = relationship(backref='request')
