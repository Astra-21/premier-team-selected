from datetime import datetime, timedelta, timezone
import logging
from typing import Optional
from jose import JWTError, jwt 
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

oauth2_schema = OAuth2PasswordBearer(tokenUrl="token")

class TokenData(BaseModel):
    google_id: Optional[str] = None


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    logging.debug(f"expires_delta:{expires_delta}")
    
    to_encode = data.copy()
    
    #jwtの有効期限を設定（defaultは15分）
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    #to_encode: トークンのペイロード（sub, exp など）
    to_encode.update({"exp": expire})
    
    #JWT を作成、 HMAC（またはRSAなど）で署名して文字列にエンコード
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

#クライアントからのデータより誰がログインしているか確認
def get_current_user(token: str = Depends(oauth2_schema)):

    #print(type(HTTPException))

    credentials_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = "Could not validate credantials",
        headers = {"WWW-Authenticate" : "Bearer"},
    )

    try:

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        google_id: str = payload.get("sub")

        if google_id is None:
            raise credentials_exception
        
        token_data = TokenData(google_id=google_id)
    
    except JWTError:
        raise credentials_exception
    
    return token_data
