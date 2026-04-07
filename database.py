import enum
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime, Enum, Index
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.sql import func

SQLALCHEMY_DATABASE_URL = "sqlite:///./abandoned_cart.db"

# Platform-specific check_same_thread needed only for SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class CartStatus(str, enum.Enum):
    active = "active"
    abandoned = "abandoned"
    purchased = "purchased"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now(), server_default=func.now())

    carts = relationship("Cart", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="user", cascade="all, delete-orphan")

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    price = Column(Float, nullable=False)
    description = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now(), server_default=func.now())

    carts = relationship("Cart", back_populates="product", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="product", cascade="all, delete-orphan")


class Cart(Base):
    __tablename__ = "carts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    status = Column(Enum(CartStatus), default=CartStatus.active, nullable=False)
    added_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now(), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="carts")
    product = relationship("Product", back_populates="carts")

# Add index on user_id and added_at per requirements
Index('ix_cart_user_added_at', Cart.user_id, Cart.added_at)

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False) 
    total_amount = Column(Float, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="orders")


class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    cart_id = Column(Integer, ForeignKey("carts.id", ondelete="CASCADE"), nullable=False)
    message = Column(String, nullable=False)
    sent_at = Column(DateTime, server_default=func.now())
    is_read = Column(Integer, default=0)

    user = relationship("User", back_populates="notifications")


class Recommendation(Base):
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    reason = Column(String)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="recommendations")
    product = relationship("Product", back_populates="recommendations")


def init_db():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    if db.query(User).first():
        print("Database already contains records. Skipping sample data.")
        db.close()
        return

    print("Inserting sample data...")
    
    # 1. Users
    u1 = User(username="alice", email="alice@example.com")
    u2 = User(username="bob", email="bob@example.com")
    u3 = User(username="charlie", email="charlie@example.com")
    db.add_all([u1, u2, u3])
    db.commit()

    # 2. Products
    p1 = Product(name="Laptop", price=1200.00, description="High performance laptop")
    p2 = Product(name="Headphones", price=150.00, description="Wireless noise-canceling headphones")
    p3 = Product(name="Mouse", price=50.00, description="Ergonomic wireless mouse")
    db.add_all([p1, p2, p3])
    db.commit()

    # 3. Carts
    now = datetime.utcnow()
    
    # Active Cart (Added 2 days ago)
    c_active = Cart(user_id=u1.id, product_id=p1.id, quantity=1, status=CartStatus.active, added_at=now - timedelta(days=2))
    
    # Abandoned Cart (Added 14 days ago - past the 12 day limit)
    c_abandoned = Cart(user_id=u2.id, product_id=p2.id, quantity=2, status=CartStatus.abandoned, added_at=now - timedelta(days=14))
    
    # Purchased Cart (Added 5 days ago)
    c_purchased = Cart(user_id=u3.id, product_id=p3.id, quantity=1, status=CartStatus.purchased, added_at=now - timedelta(days=5))
    
    db.add_all([c_active, c_abandoned, c_purchased])
    db.commit()

    # 4. Orders
    o1 = Order(user_id=u3.id, cart_id=c_purchased.id, total_amount=p3.price * c_purchased.quantity)
    db.add(o1)
    db.commit()

    # 5. Notifications
    n1 = Notification(user_id=u2.id, cart_id=c_abandoned.id, message="You left some items in your cart! Complete your purchase.")
    db.add(n1)
    db.commit()

    # 6. Recommendations
    r1 = Recommendation(user_id=u2.id, product_id=p3.id, reason="Pairs well with headphones")
    db.add(r1)
    db.commit()

    db.close()
    print("Sample data populated successfully.")

if __name__ == "__main__":
    init_db()
