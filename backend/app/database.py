from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# PostgreSQL URL構成: postgresql://ユーザー名:パスワード@ホスト:ポート/データベース名
SQLALCHEMY_DATABASE_URL = "postgresql://myuser:mypass@db:5432/mydb"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# FastAPIで使うための依存関数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
