import os 
from dotenv import load_dotenv
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer # what a password berer
from sqlalchemy.orm import Session
import database
import orm

def get_db():
    db=database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

load_dotenv() # Injects your .env variables

# Load secrets from the "Safe"
SECRET_KEY = os.getenv("SECRET_KEY")#os helps look it for us so why we using dotenv okay to import it hee automatically wy not import manually
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

#whats thise can you tell me 
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def create_access_token(data: dict):#okay you should pass json data here right is thats the reason ypu gave dict
    to_encode = data.copy()

    # 1. SET THE EXPIRATION
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)#look we are only setting the time not the time verification for expiratiion
    to_encode.update({"exp": expire})
    
    # 2. SIGN THE TOKEN(is thise the creation )
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)#creation which onlybecomes raed only(sign) except the user who has jwt token
    #whers the creation step
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme)):#whats oauth2scheme there we have not even stored token as variabl yet 
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},#whats thise saying though meaning 
    )
    try:
        # Decode checks the signature AND the expiration automatically
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")#is the get here is it the dictionary function right to get the user why not use payload["user_id"] instead
        if user_id is None:
            raise credentials_exception
        return user_id
    except JWTError:
        raise credentials_exception
    

def require_seller(current_user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    # 1. Fetch the user using the string ID from the token
    record = db.query(orm.User).filter(orm.User.user_id == current_user_id).first()
    
    # 2. Safety Check: Does the user still exist in the database?
    if not record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="User no longer exists."
        )
        
    # 3. Permission Check: Are they a seller?
    if not record.is_seller:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only sellers can perform this action."
        )
        
    # 4. Return the full ORM User object!
    return record