from fastapi import FastAPI,Depends,HTTPException,File,UploadFile,Form
from sqlalchemy.orm import Session
import database ,orm
import uuid
import datetime
from schemas import update_inventory as ui
from schemas import img_caption
from schemas import  U_details
from hash import hash_pwd, verify_pwd
import Oauth
from fastapi.security import OAuth2PasswordRequestForm
import shutil
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 1. Define who is allowed to talk to your server# really thise is enouph no need for guard right 
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to exactly this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



def get_db():
    db=database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/login")
def sign_in(credentials: OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_db),):
    record=db.query(orm.User).filter(orm.User.e_mail==credentials.username).first()
    if not record or not verify_pwd(credentials.password,record.password):
       raise HTTPException(status_code=400 , detail="Invalid credentials")
    
    access_token=Oauth.create_access_token(data={"user_id":str(record.user_id)})
    return {"access_token": access_token, "token_type": "bearer"}#hwats bearer here what are the other types

@app.post("/sign_up")
def sign_up(data: U_details ,db: Session=Depends(get_db)):
    hashed_pwd=hash_pwd(data.password)
    details = orm.User(
        u_name=data.u_name,
        e_mail=data.e_mail,
        password=hashed_pwd
    )

    db.add(details)
    db.commit()

@app.put("/ineventory/user/upgrade")
def to_be_seller(db : Session=Depends(get_db),current_user_id : str=Depends(Oauth.get_current_user)):
    record=db.query(orm.User).filter(orm.User.user_id==current_user_id).first()
    if not record:
       raise HTTPException(status_code=400 , detail="not authorized user")
    
    if record.is_seller == True:
        return { "msg": "youre already a seller"}
    
    record.is_seller=True

    db.commit()

    return{"msg":"operation sucessfull youre officialy a seller now you can list products"}


    



#buying

@app.get("/inventory")
def get_inventory(db : Session=Depends(get_db)):
    data = db.query(orm.Inventory).all()#select * from inventory
    return data#i think faatapi convert the relation to json format using the Session which has pydantic modell
    

@app.get("/inventory/{p_id}")
    
def get_product(p_id : str ,db: Session=Depends(get_db)):
    data=db.query(orm.Inventory).filter(orm.Inventory.p_id == p_id).first()
    if not data:
        raise HTTPException(status_code=404, detail="Product not found in inventory")
    return data

"""should need to refactor pydantic schema"""        
@app.post("/inventory/buy/{qty}") 

def place_order(p_id :uuid.UUID, qty :int, db : Session=Depends(get_db), current_user_id: str=Depends(Oauth.get_current_user)):
    record=db.query(orm.Inventory).filter(orm.Inventory.p_id==p_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Product not found in inventory")
    
    record.qty=record.qty-qty 
    

    new_order=orm.Order(
        u_id=current_user_id,#then whats thise we are literally storing th jwt instead uuid based user which postgres generated automatically when a record is crated 
        p_id=p_id,
        qty=qty,
        o_time=datetime.datetime.now().time(),
        o_date=datetime.date.today(),
        status="success"
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return {"message": "Order placed successfully"}
    

#seller

@app.get("/inventory/{s_id}")#doese thise security leakage probably need to use the pydantic schemas here but i need to know how to structure pydantic schemas it messyly structure
def get_products(s_id: uuid.UUID, db: Session = Depends(get_db)):
    records = db.query(orm.Inventory).filter(orm.Inventory.s_id == s_id).all()
    
    if not records:
        return {"inventory": [], "alert": "No products listed"}

    # Logic check: find items with zero quantity
    oos_items = [r.p_name for r in records if r.qty == 0]# r did you meant records.p_name #is thise list comprhension if yes give me the syntax

    return {
        "inventory": records,
        "alert": f"Out of stock: {', '.join(oos_items)}" if oos_items else None,
        "solution": "Restock or delete out-of-stock items" if oos_items else None
    }

@app.post("/inventory")
async def list_product(
    p_name: str = Form(...), 
    qty: int = Form(...), 
    price: float = Form(...), 
    caption: str = Form(...),
    img: UploadFile = File(...),
    s_id: str = Depends(Oauth.get_current_user),
    current_user: orm.User = Depends(Oauth.require_seller),
    db: Session = Depends(get_db)
):
    # 1. Handle the file upload
    file_path = f"static/uploads/{img.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(img.file, buffer)
    
    # 2. Save to database (Note: the comma after price!)
    new_item = orm.Inventory(
        s_id=s_id,
        p_name=p_name,
        qty=qty,
        price=price,
        img_caption={"img": f"/{file_path}", "caption": caption}
    )

    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    
    return {"message": "Product listed!", "p_id": new_item.p_id}
    

@app.put("/inventory/{p_id}")
def update_product(p_id: uuid.UUID,data : ui ,db :Session=Depends(get_db)):
    record=db.query(orm.Inventory).filter(orm.Inventory.p_id==p_id).first()
    if not record:
         raise HTTPException(status_code=404, detail="Product not found in inventory")
    if  record.s_id != data.s_id:
        raise HTTPException(status_code=403, detail="you doesnt own thise product")

    
    record.p_name=data.p_name
    record.qty=data.qty
    record.price=data.price

    db.commit()
    return {"msg": "update succesfull"}

@app.delete("/inventory/{p_id}")
def delete_product(p_id:uuid.UUID,db : Session=Depends(get_db),current_user_id: str = Depends(Oauth.get_current_user)): # Injected from JWT
    record=db.query(orm.Inventory).filter(orm.Inventory.p_id==p_id).first()
    if not record:
        raise HTTPException(status_code=404 , desciption="no product found")
    db.delete(record)
    db.commit()