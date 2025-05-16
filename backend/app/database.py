from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

#すべてのコードが同じデータベースに接続するため。
from sqlalchemy.orm import sessionmaker

# PostgreSQL URL構成: postgresql://ユーザー名:パスワード@ホスト:ポート/データベース名
SQLALCHEMY_DATABASE_URL = "postgresql://myuser:mypass@db:5432/mydb"

#SessionLocal や Base.metadata.create_all() で使われ、DBとのやり取りの基盤になるものです。
engine = create_engine(SQLALCHEMY_DATABASE_URL)

#データベースとのやりとり（クエリなど）を行う「セッション」を作成する。
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#SQLAlchemyのモデルを定義するための「ベースクラス」を作る。
Base = declarative_base()

# FastAPIで使うための依存関数, DBセッションを取得して返す関数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
