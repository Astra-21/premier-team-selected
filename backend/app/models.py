from sqlalchemy import Column, String, Integer
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    google_id = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, default="未設定 右上の設定ボタンから変更できます")
    favorite_team = Column(String, default="未設定 右上の設定ボタンから変更できます")
    favorite_player = Column(String, default="未設定 右上の設定ボタンから変更できます")
    logo_url = Column(String, default="")



class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    logo_url = Column(String, nullable=False)

