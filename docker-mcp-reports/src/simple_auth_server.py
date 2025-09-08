from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, Dict, Any
import jwt
import os
from datetime import datetime, timedelta
import json

app = FastAPI(title="Simple Auth Server", version="1.0.0")
security = HTTPBearer()

# Конфигурация
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 24 * 60  # 24 часа

# Хардкодированные пользователи
USERS = {
    "admin": {
        "username": "admin",
        "password": "adminpass",
        "role": "admin",
        "daily_token_limit": None  # Без ограничений
    },
    "user": {
        "username": "user", 
        "password": "userpass",
        "role": "user",
        "daily_token_limit": 100  # 100 токенов в день
    }
}

# Счетчики токенов (в реальном приложении - в БД)
token_usage = {}

# Модели данных
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_role: str
    daily_token_limit: Optional[int] = None

class TokenUsageResponse(BaseModel):
    used_tokens: int
    daily_limit: Optional[int] = None
    remaining_tokens: Optional[int] = None

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Создает JWT токен"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Проверяет JWT токен"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return username
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_user_role(username: str) -> str:
    """Получает роль пользователя"""
    user = USERS.get(username)
    if user:
        return user["role"]
    return "user"

def update_token_usage(username: str, tokens_used: int):
    """Обновляет счетчик использованных токенов"""
    today = datetime.now().strftime("%Y-%m-%d")
    usage_key = f"{username}_{today}"
    token_usage[usage_key] = token_usage.get(usage_key, 0) + tokens_used

@app.get("/")
async def root():
    return {"message": "Simple Auth Server is running"}

@app.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):
    """Эндпоинт для входа в систему"""
    user = USERS.get(login_data.username)
    
    if not user or user["password"] != login_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Создаем токен
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": login_data.username}, expires_delta=access_token_expires
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user_role=user["role"],
        daily_token_limit=user["daily_token_limit"]
    )

@app.get("/token-usage", response_model=TokenUsageResponse)
async def get_token_usage(username: str = Depends(verify_token)):
    """Получает информацию об использовании токенов"""
    today = datetime.now().strftime("%Y-%m-%d")
    usage_key = f"{username}_{today}"
    used_tokens = token_usage.get(usage_key, 0)
    
    user = USERS.get(username)
    daily_limit = user.get("daily_token_limit") if user else None
    
    remaining_tokens = None
    if daily_limit is not None:
        remaining_tokens = max(0, daily_limit - used_tokens)
    
    return TokenUsageResponse(
        used_tokens=used_tokens,
        daily_limit=daily_limit,
        remaining_tokens=remaining_tokens
    )

@app.post("/reset-limits")
async def reset_limits(username: str = Depends(verify_token)):
    """Сбрасывает лимиты токенов (только для админа)"""
    user_role = get_user_role(username)
    if user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can reset limits"
        )
    
    # Сбрасываем все счетчики
    global token_usage
    token_usage = {}
    
    return {"message": "Token limits reset successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

