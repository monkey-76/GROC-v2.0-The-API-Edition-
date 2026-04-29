from passlib.context import CryptContext #config of password algorithm

pwd_config= CryptContext(schemes=["bcrypt"], deprecated="auto")#whats the meaning of deprecated

def hash_pwd(password : str):
    return pwd_config.hash(password)

def verify_pwd(plain_password: str, hash_pwd):#thise verification is not correct though the verification should be matched with fetched data from database right
    return pwd_config.verify(plain_password,hash_pwd)
