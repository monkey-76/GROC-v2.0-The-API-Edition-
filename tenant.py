from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session 
from main import get_db
import orm
from hash import hash_pwd, verify_pwd
from fastapi.staticfiles import OAuth2PasswordRequestForm
import Oauth
from pydantic import EmailStr
import secrets
from fastapi import Depends
from sqlalchemy.orm import Session
import orm
from hash import hash_pwd, verify_pwd


app=FastAPI()

@app.post("/admin/register")
def register_tenant(app_name: str, email: EmailStr, password: str, db: Session = Depends(get_db)):
    # 1. Check if the tenant email already exists
    existing = db.query(orm.Tenants).filter(orm.Tenants.owner_email == email).first()
    if existing:
        raise HTTPException(status_code=400, detail="This email is already registered to a tenant.")

    # 2. Hash the owner's password
    hashed_password = hash_pwd(password)

    #advance payment here 
    #use timedelta to track the subscription 

    # 3. Create the tenant record
    new_tenant = orm.Tenants(
        app_name=app_name,
        owner_email=email,
        owner_password=hashed_password
    )
    
    db.add(new_tenant)
    db.commit()
    db.refresh(new_tenant)
    
    return {"msg": "Tenant registered successfully", "tenant_id": new_tenant.id}



# Note: You should protect this route so only a logged-in Tenant admin can hit it! #should use jwt authentication here
@app.post("/admin/generate-api-key")
def create_api_key(tenant_id: str, db: Session = Depends(get_db),):
    
    # 1. Generate a secure, 32-character random URL-safe string
    raw_key = secrets.token_urlsafe(32)
    formatted_key = f"sk_live_{raw_key}" # 'sk' stands for secret key
    hashed_api_key=hash_pwd(formatted_key)
    
    # 2. Save it to the database
    new_api_key = orm.ApiKey(
        tenant_id=tenant_id,
        key_string=hashed_api_key
    )
    
    db.add(new_api_key)
    db.commit()
    
    # 3. Show it to the developer ONCE
    return {
        "message": "Save this key now. You will not be able to see it again.",
        "api_key": formatted_key
    }

@app.post("/admin/login")
def admin_login(credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Look in the 'tenants' table, not 'users'
    tenant = db.query(orm.Tenants).filter(orm.Tenants.owner_email == credentials.username).first()
    
    if not tenant or not verify_pwd(credentials.password, tenant.owner_password):
        raise HTTPException(status_code=401, detail="Invalid Admin credentials")

    # Issue a token that identifies them as a Tenant Owner
    access_token = Oauth.create_access_token(data={
        "sub": str(tenant.id),
        "role": "tenant_admin"
    })
    
    return {"access_token": access_token, "token_type": "bearer"}