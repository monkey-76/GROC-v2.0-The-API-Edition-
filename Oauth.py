import os #whats thise module for is it for managing what operating system go to files open files etc 
from dotenv import load_dotenv #is thise a preinstalled ython library which already excists and whats thise for 
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer # what a password berer
import orm

load_dotenv() # Injects your .env variables

# Load secrets from the "Safe"
SECRET_KEY = os.getenv("SECRET_KEY")#os helps look it for us so why we using dotenv okay to import it hee automatically wy not import manually
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

# Tells FastAPI the "Login" route is where to get the token # okay thise is a fetcher we call encod_jwt in login route thise function fetches thise jwt tokenfom there for veriification and assign it to the header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

#now what 
def create_access_token(data: dict):
    to_encode = data.copy()

    #thise sequence were code executes is eally suspiciouse lok firt not creation firt expiation then updating hu you need to create one before setting expiration and updating thise is more like refreshing token 
    # 1. SET THE EXPIRATION
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)#whats utc and time delta though
    to_encode.update({"exp": expire})
    
    # 2. SIGN THE TOKEN(is thise the creation )
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)#creation which onlybecomes raed only(sign) except the user who has jwt token
    #whers the creation step
    return encoded_jwt

#one more doubt jwt is 1 way lock its not rwo way and expires after 30 minutes means user have only 30 minutes to go through the website or the theft guy  aftr 30 min the user is kicked 

def get_current_user(token: str = Depends(oauth2_scheme)):
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
    

def require_seller(current_user: orm.User = Depends(get_current_user)):
    if not current_user.is_seller:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only sellers can perform this action."
        )
    return current_user