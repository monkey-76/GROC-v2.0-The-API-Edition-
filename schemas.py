from pydantic import BaseModel,EmailStr,AnyHttpUrl
import uuid

class Base(BaseModel):
    pass

class update_inventory(Base):
    qty:int
    price:float
    p_name:str
    s_id:uuid.UUID
    
class login(Base):
    e_mail:EmailStr
    password:str

class U_details(Base):
    u_name:str
    e_mail:EmailStr
    password:str

class img_caption(Base):
    img:AnyHttpUrl#or you can use field like eg: Field(pattern=r"^https?://[^\s/$.?#].[^\s]*$")
    caption:str

