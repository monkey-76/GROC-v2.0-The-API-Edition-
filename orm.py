import uuid
from datetime import date, time
from sqlalchemy import String, Boolean, text, CheckConstraint, ForeignKey, Integer, Numeric, Date, Time
from sqlalchemy.dialects.postgresql import UUID,JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from database import SessionLocal

class Base(DeclarativeBase):
    pass

class Tenants(Base):
    __tablename__="tenants"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),primary_key=True,server_default=text("uuid_generate_v4()"))
    app_name:Mapped[str] = mapped_column(String, nullable=False)
    owner_email:Mapped[str] = mapped_column(String, unique=True, nullable= False)
    owner_password:Mapped[str] = mapped_column(String, nullable= False)


class User(Base):
    __tablename__ = "users"

    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), index=True)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("uuid_generate_v4()")
    )
    u_name: Mapped[str] = mapped_column(String, nullable=False)
    e_mail: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    is_seller: Mapped[bool] = mapped_column(Boolean, server_default=text("false"), default=False)

    __table_args__ = (
        CheckConstraint('char_length(password) >= 8', name='users_password_check'),
    )

class Inventory(Base):
    __tablename__ = "inventory" 

    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), index=True)

    p_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("uuid_generate_v4()")
    )
    p_name: Mapped[str] = mapped_column(String, nullable=False)
    qty: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    s_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.user_id"), # not the python class eferences og table.column name 
        nullable=False,
        index=True
    )
    img_caption:Mapped[dict] = mapped_column(JSONB,nullable=False)
    __table_args__ = (
        CheckConstraint('qty >= 0', name='inventory_qty_check'), #used for check constraints
    )

class Orders(Base):
    __tablename__ = "orders"

    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), index=True)

    o_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("uuid_generate_v4()")
    )
    p_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("inventory.p_id"), nullable=False)
    u_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    
    # Correct types for Postgres 'time without time zone' and 'date'
    o_time: Mapped[time] = mapped_column(Time, nullable=False)
    o_date: Mapped[date] = mapped_column(Date, nullable=False)
    
    status: Mapped[str] = mapped_column(String, server_default=text("'pending'"))
    qty: Mapped[int] = mapped_column(Integer,nullable=False)
    
class Cart(Base):
    __tablename__ = "cart"

    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), index=True)

    cart_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("uuid_generate_v4()")
    )
    p_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("inventory.p_id"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.user_id"), nullable=False)

class ApiKey(Base):
    __tablename__ = "api_keys"

    key_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        server_default=text("uuid_generate_v4()")
    )#thise is actuall api key
    # Links this key to the specific business/developer
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    
    # The actual key string (e.g., "sk_live_12345...")
    key_string: Mapped[str] = mapped_column(String, unique=True, nullable=False)# whats thise  is thise is also api key but in str formatt
    
    # Allows a developer to pause a key without deleting it
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=text("true"), default=True)

def main():

    def trying():

        db = SessionLocal()

        try:
            # 2. Try to fetch the very first user from your 'users' table
            # This is the Python version of: SELECT * FROM users LIMIT 1;
            first_user = db.query(User).first()
            
            if first_user:
                print(f"🚀 Connection Successful! Hello, {first_user.u_name}")
            else:
                print("✅ Connected to Postgres, but the 'users' table is empty!")

        except Exception as e:
            print(f"❌ Connection Failed: {e}")

        finally:
            # 3. Always close the session to free up memory!
            db.close()
    trying()

if  __name__ == "__main__":
    main()