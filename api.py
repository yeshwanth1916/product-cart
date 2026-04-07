# ================== IMPORTS ==================
import enum
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime, Enum, Index
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, Session
from sqlalchemy.sql import func

# ================== DATABASE ==================
SQLALCHEMY_DATABASE_URL = "sqlite:///./abandoned_cart.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ================== ENUM ==================
class CartStatus(str, enum.Enum):
    active = "active"
    abandoned = "abandoned"
    purchased = "purchased"

# ================== MODELS ==================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)

    carts = relationship("Cart", back_populates="user")
    orders = relationship("Order", back_populates="user")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    description = Column(String)

class Cart(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=1)
    status = Column(Enum(CartStatus), default=CartStatus.active)
    added_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="carts")

Index('ix_cart_user_added_at', Cart.user_id, Cart.added_at)

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    cart_id = Column(Integer, ForeignKey("carts.id"))
    total_amount = Column(Float)

    user = relationship("User", back_populates="orders")

# ================== SCHEMAS ==================
class UserCreate(BaseModel):
    username: str
    email: str

class ProductCreate(BaseModel):
    name: str
    price: float
    description: str

class CartCreate(BaseModel):
    user_id: int
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    user_id: int
    cart_id: int
    total_amount: float

# ================== FASTAPI ==================
app = FastAPI(title="Abandoned Cart API 🚀")

# ================== DB DEPENDENCY ==================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ================== CREATE TABLES ==================
Base.metadata.create_all(bind=engine)

# ================== APIs ==================

# 🔹 Root
@app.get("/")
def root():
    return {"message": "API Running Successfully 🚀"}

# 🔹 Create User
@app.post("/users/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(username=user.username, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# 🔹 Create Product
@app.post("/products/")
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

# 🔹 Add to Cart
@app.post("/cart/")
def add_to_cart(cart: CartCreate, db: Session = Depends(get_db)):
    db_cart = Cart(**cart.dict())
    db.add(db_cart)
    db.commit()
    db.refresh(db_cart)
    return db_cart

# 🔹 Get All Carts
@app.get("/cart/")
def get_all_carts(db: Session = Depends(get_db)):
    return db.query(Cart).all()

# 🔹 Get Abandoned Carts (>12 days)
@app.get("/cart/abandoned")
def get_abandoned_carts(db: Session = Depends(get_db)):
    threshold = datetime.utcnow() - timedelta(days=12)

    carts = db.query(Cart).filter(
        Cart.added_at < threshold,
        Cart.status == CartStatus.active
    ).all()

    return carts

# 🔹 Create Order
@app.post("/orders/")
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    db_order = Order(**order.dict())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order
