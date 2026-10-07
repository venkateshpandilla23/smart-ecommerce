from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    WebSocket,
    WebSocketDisconnect
)

from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials
)
from sqlalchemy import or_

from sqlalchemy.orm import Session
import database
import models
import schemas
import bcrypt
from jose import jwt
from datetime import datetime, timedelta, timezone
from email_utils import send_email
from fastapi import FastAPI, Request, Depends
from auth0_server_python.store import StateStore, TransactionStore
from auth0_fastapi.config import Auth0Config
from auth0_server_python.auth_server.server_client import ServerClient
from fastapi.responses import RedirectResponse
import os
from dotenv import load_dotenv
load_dotenv()

class MemoryStateStore(StateStore):
    def __init__(self):
        self._data = {}

    async def get(self, key, options=None):
        return self._data.get(key)

    async def set(self, key, value, options=None):
        self._data[key] = value

    async def delete(self, key, options=None):
        self._data.pop(key, None)

    async def delete_by_logout_token(self, claims, options=None):
        pass


class MemoryTransactionStore(TransactionStore):
    def __init__(self):
        self._data = {}

    async def get(self, key, options=None):
        return self._data.get(key)

    async def set(self, key, value, options=None):
        self._data[key] = value

    async def delete(self, key, options=None):
        self._data.pop(key, None)

auth0_config = Auth0Config(
    domain=os.getenv("AUTH0_DOMAIN"),
    client_id=os.getenv("AUTH0_CLIENT_ID"),
    client_secret=os.getenv("AUTH0_CLIENT_SECRET"),
    secret=os.getenv("AUTH0_SECRET"),
    app_base_url=os.getenv("APP_BASE_URL")
)

auth_client = ServerClient(
    domain=os.getenv("AUTH0_DOMAIN"),
    client_id=os.getenv("AUTH0_CLIENT_ID"),
    client_secret=os.getenv("AUTH0_CLIENT_SECRET"),
    secret=os.getenv("AUTH0_SECRET"),
    state_store=MemoryStateStore(),
    transaction_store=MemoryTransactionStore(),
    authorization_params={
        "redirect_uri": os.getenv("APP_BASE_URL") + "/callback",
        "scope": "openid profile email"
    }
)

SECRET_KEY = "smart-ecommerce-secret-key-2026"

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):

    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(

        minutes=ACCESS_TOKEN_EXPIRE_MINUTES

    )

    to_encode.update({

        "exp": expire

    })

    encoded_jwt = jwt.encode(

        to_encode,

        SECRET_KEY,
        algorithm=ALGORITHM

    )

    return encoded_jwt
security = HTTPBearer()

def verify_token(

    credentials: HTTPAuthorizationCredentials = Depends(security)

):
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        return payload
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )
# VERIFY USER ACCESS
def verify_user_access(
    user_id: int,
    token_data: dict = Depends(verify_token)
):
    token_user_id = token_data.get("user_id")
    if token_user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You can access only your own account"
        )
    return token_data

# VERIFY ADMIN

def verify_admin(
    token_data: dict = Depends(verify_token)
):
    role = token_data.get("role")
    if role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    return token_data

# FASTAPI APP
app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        self.active_connections.pop(user_id, None)

    async def send_notification(self, user_id: int, message: str):
        websocket = self.active_connections.get(user_id)
        if websocket:
            await websocket.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(user_id, websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user_id)


# CREATE DATABASE TABLES



models.Base.metadata.create_all(

    bind=database.engine
)
# DATABASE SESSION
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()
# ROOT
@app.get("/")
def home():
    return {
        "message": "Smart E-Commerce FastAPI is running"
    }
# REGISTER
@app.post("/register")
def register(
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = db.query(
        models.User
    ).filter(
        models.User.email == user.email
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    hashed_password = bcrypt.hashpw(
        user.password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")
    new_user = models.User(
        name=user.name,
        email=user.email,
        password=hashed_password,
        role="customer"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {
        "message": "User registered successfully",
        "user_id": new_user.id
    }
# LOGIN
@app.post("/login")
def login(
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = db.query(
        models.User
    ).filter(
        models.User.email == user.email







    ).first()















    if not existing_user:















        raise HTTPException(







            status_code=401,







            detail="Invalid email or password"







        )















    password_match = bcrypt.checkpw(







        user.password.encode("utf-8"),







        existing_user.password.encode("utf-8")







    )















    if not password_match:















        raise HTTPException(







            status_code=401,







            detail="Invalid email or password"







        )















    token = create_access_token({







        "user_id": existing_user.id,







        "email": existing_user.email,







        "role": existing_user.role







    })















    return {







        "message": "Login successful",







        "access_token": token,







        "token_type": "bearer",







        "user_id": existing_user.id,







        "role": existing_user.role







    }























# ============================================================







# VIEW PROFILE







# ============================================================















@app.get("/profile/{user_id}")







def profile(







    user_id: int,







    db: Session = Depends(get_db),







    token_data: dict = Depends(verify_user_access)







):















    user = db.query(







        models.User







    ).filter(







        models.User.id == user_id







    ).first()















    if not user:















        raise HTTPException(







            status_code=404,







            detail="User not found"







        )















    return {







        "id": user.id,







        "name": user.name,







        "email": user.email,







        "role": user.role







    }























# ============================================================







# EDIT PROFILE







# ============================================================















@app.put("/edit-profile/{user_id}")







def edit_profile(







    user_id: int,







    user_data: schemas.UserUpdate,







    db: Session = Depends(get_db),







    token_data: dict = Depends(verify_user_access)







):















    user = db.query(







        models.User







    ).filter(







        models.User.id == user_id







    ).first()















    if not user:















        raise HTTPException(







            status_code=404,







            detail="User not found"







        )















    user.name = user_data.name







    user.email = user_data.email















    db.commit()















    db.refresh(user)















    return {







        "message": "Profile updated successfully",







        "user": {







            "id": user.id,







            "name": user.name,







            "email": user.email,







            "role": user.role







        }







    }























# ============================================================







# CHANGE PASSWORD







# ============================================================















@app.put("/change-password/{user_id}")

def change_password(
    user_id: int,
    password_data: schemas.ChangePassword,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_user_access)
):
    user = db.query(
       models.User
    ).filter(
       models.User.id == user_id
    ).first()
    if not user:
       raise HTTPException(
           status_code=404,
           detail="User not found"
        )
    password_match = bcrypt.checkpw(
        password_data.current_password.encode("utf-8"),
       user.password.encode("utf-8")
    )
    if not password_match:
        raise HTTPException(
          status_code=400,
            detail="Current password is incorrect"
        )
    new_hashed_password = bcrypt.hashpw(
        password_data.new_password.encode("utf-8"),
       bcrypt.gensalt()
    ).decode("utf-8")
    user.password = new_hashed_password
    db.commit()
    return {
        "message": "Password changed successfully"
    }





















# DELETE ACCOUNT
















@app.delete("/delete-account/{user_id}")







def delete_account(







    user_id: int,







    db: Session = Depends(get_db),







    token_data: dict = Depends(verify_user_access)







):















    user = db.query(







        models.User







    ).filter(







        models.User.id == user_id







    ).first()















    if not user:















        raise HTTPException(







            status_code=404,







            detail="User not found"







        )















    db.delete(user)















    db.commit()















    return {







        "message": "Account deleted successfully"







    }























# ============================================================







# ADMIN TEST







# ============================================================















@app.get("/admin-test")







def admin_test(







    token_data: dict = Depends(verify_admin)







):















    return {







        "message": "Admin access successful"







    }























# ============================================================







# ADMIN - VIEW USERS

@app.get("/admin/users")








def get_all_users(







    db: Session = Depends(get_db),







    token_data: dict = Depends(verify_admin)







):















    users = db.query(







        models.User







    ).all()















    return {







        "total_users": len(users),







        "users": [







            {







                "id": user.id,







                "name": user.name,







                "email": user.email,







                "role": user.role







            }







            for user in users







        ]







    }























# ============================================================







# ADMIN - CREATE PRODUCT







# ============================================================















@app.post("/admin/products")







def create_product(







    product: schemas.ProductCreate,







    db: Session = Depends(get_db),







    token_data: dict = Depends(verify_admin)







):















    new_product = models.Product(







        name=product.name,







        description=product.description,







        price=product.price,







        stock=product.stock,







        category=product.category







    )















    db.add(new_product)















    db.commit()















    db.refresh(new_product)















    return {







        "message": "Product created successfully",







        "product": {







            "id": new_product.id,







            "name": new_product.name,







            "description": new_product.description,







            "price": new_product.price,







            "stock": new_product.stock,







            "category": new_product.category







        }







    }























# ============================================================







# VIEW ALL PRODUCTS







# ============================================================















@app.get("/products")







def get_products(







    search: str | None = None,

    category: str | None = None,

    min_price: float | None = None,

    max_price: float | None = None,

    sort: str | None = None,

    db: Session = Depends(get_db)







):















    query = db.query(







        models.Product







    )















    # Search by product name or description







    if search:







        search_value = f"%{search}%"







        query = query.filter(







            or_(







                models.Product.name.ilike(search_value),







                models.Product.description.ilike(search_value)







            )







        )















    # Filter by category







    if category:

        query = query.filter(

            models.Product.category.ilike(category)

        )



    if min_price is not None:

        query = query.filter(

        models.Product.price >= min_price

        )



# Filter by maximum price

    if max_price is not None:

        query = query.filter(

        models.Product.price <= max_price

        )

# Sort products by price

    if sort == "price_low_to_high":

        query = query.order_by(

        models.Product.price.asc()

    )



    elif sort == "price_high_to_low":

        query = query.order_by(

        models.Product.price.desc()

    )

    elif sort == "name_a_to_z":

        query = query.order_by(

        models.Product.name.asc()

    )



    elif sort == "name_z_to_a":

        query = query.order_by(

        models.Product.name.desc()

    )





# Get products

    products = query.all()



















    return {







        "total_products": len(products),







        "products": [







            {







                "id": product.id,







                "name": product.name,







                "description": product.description,







                "price": product.price,







                "stock": product.stock,







                "category": product.category







            }







            for product in products







        ]







    }























# ============================================================







# VIEW SINGLE PRODUCT







# ============================================================















@app.get("/products/{product_id}")







def get_single_product(







    product_id: int,







    db: Session = Depends(get_db)







):















    product = db.query(







        models.Product







    ).filter(







        models.Product.id == product_id







    ).first()















    if not product:















        raise HTTPException(







            status_code=404,







            detail="Product not found"







        )















    return {







        "id": product.id,







        "name": product.name,







        "description": product.description,







        "price": product.price,







        "stock": product.stock,







        "category": product.category







    }























# ============================================================







# ADMIN - UPDATE PRODUCT







# ============================================================















@app.put("/admin/products/{product_id}")







def update_product(







    product_id: int,







    product_data: schemas.ProductCreate,







    db: Session = Depends(get_db),







    token_data: dict = Depends(verify_admin)







):















    product = db.query(







        models.Product







    ).filter(







        models.Product.id == product_id







    ).first()















    if not product:















        raise HTTPException(







            status_code=404,







            detail="Product not found"







        )















    product.name = product_data.name







    product.description = product_data.description







    product.price = product_data.price







    product.stock = product_data.stock







    product.category = product_data.category















    db.commit()















    db.refresh(product)















    return {







        "message": "Product updated successfully",







        "product": {







            "id": product.id,







            "name": product.name,







            "description": product.description,







            "price": product.price,







            "stock": product.stock,







            "category": product.category







        }







    }























# ============================================================







# ADMIN - DELETE PRODUCT







# ============================================================















@app.delete("/admin/products/{product_id}")







def delete_product(







    product_id: int,







    db: Session = Depends(get_db),







    token_data: dict = Depends(verify_admin)







):















    product = db.query(







        models.Product







    ).filter(







        models.Product.id == product_id







    ).first()















    if not product:















        raise HTTPException(







            status_code=404,







            detail="Product not found"







        )















    db.delete(product)















    db.commit()















    return {







        "message": "Product deleted successfully"







    }























# ============================================================







# ADD TO CART
@app.post("/cart")
async def add_to_cart(
    cart_data: schemas.CartCreate,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    user_id = token_data.get("user_id")

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid user token"
        )

    # Find product
    product = db.query(
        models.Product
    ).filter(
        models.Product.id == cart_data.product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    # Validate quantity
    if cart_data.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than 0"
        )

    # Check stock
    if cart_data.quantity > product.stock:
        raise HTTPException(
            status_code=400,
            detail="Insufficient stock"
        )

    # Check whether product is already in cart
    existing_cart = db.query(
        models.Cart
    ).filter(
        models.Cart.user_id == user_id,
        models.Cart.product_id == cart_data.product_id
    ).first()

    # Update existing cart
    if existing_cart:

        new_quantity = (
            existing_cart.quantity +
            cart_data.quantity
        )

        if new_quantity > product.stock:
            raise HTTPException(
                status_code=400,
                detail="Insufficient stock"
            )

        existing_cart.quantity = new_quantity

        db.commit()
        db.refresh(existing_cart)

        # WebSocket cart update
        await manager.send_notification(
            user_id,
            f"Cart updated: {product.name} quantity is now {existing_cart.quantity}."
        )

        return {
            "message": "Cart quantity updated",
            "cart_id": existing_cart.id,
            "product_id": existing_cart.product_id,
            "quantity": existing_cart.quantity
        }

    # Create new cart item
    new_cart = models.Cart(
        user_id=user_id,
        product_id=cart_data.product_id,
        quantity=cart_data.quantity
    )

    db.add(new_cart)

    db.commit()

    db.refresh(new_cart)

    # WebSocket cart update
    await manager.send_notification(
        user_id,
        f"{product.name} was added to your cart."
    )

    return {
        "message": "Product added to cart",
        "cart_id": new_cart.id,
        "product_id": new_cart.product_id,
        "quantity": new_cart.quantity
    }






















# ============================================================







# VIEW CART







# ============================================================















@app.get("/cart")







def get_cart(







    db: Session = Depends(get_db),







    token_data: dict = Depends(verify_token)







):















    user_id = token_data.get("user_id")















    if not user_id:















        raise HTTPException(







            status_code=401,







            detail="Invalid user token"







        )















    cart_items = db.query(







        models.Cart







    ).filter(







        models.Cart.user_id == user_id







    ).all()















    if not cart_items:















        return {







            "message": "Cart is empty",







            "cart": []







        }















    result = []















    total_amount = 0















    for cart_item in cart_items:















        product = db.query(







            models.Product







        ).filter(







            models.Product.id == cart_item.product_id







        ).first()















        if not product:















            continue















        item_total = (







            product.price *







            cart_item.quantity







        )















        total_amount += item_total















        result.append({







            "cart_id": cart_item.id,







            "product_id": product.id,







            "product_name": product.name,







            "price": product.price,







            "quantity": cart_item.quantity,







            "item_total": item_total







        })















    return {







        "cart": result,







        "total_amount": total_amount







    }























# ============================================================







# UPDATE CART QUANTITY







# ============================================================















@app.put("/cart/{cart_id}")
async def update_cart(
    cart_id: int,
    cart_data: schemas.CartUpdate,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    user_id = token_data.get("user_id")

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid user token"
        )

    cart_item = db.query(
        models.Cart
    ).filter(
        models.Cart.id == cart_id,
        models.Cart.user_id == user_id
    ).first()

    if not cart_item:
        raise HTTPException(
            status_code=404,
            detail="Cart item not found"
        )

    if cart_data.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than 0"
        )

    product = db.query(
        models.Product
    ).filter(
        models.Product.id == cart_item.product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    if cart_data.quantity > product.stock:
        raise HTTPException(
            status_code=400,
            detail="Insufficient stock"
        )

    cart_item.quantity = cart_data.quantity

    db.commit()
    db.refresh(cart_item)

    await manager.send_notification(
        user_id,
        f"Cart updated: {product.name} quantity is now {cart_item.quantity}."
    )

    return {
        "message": "Cart updated successfully",
        "cart_id": cart_item.id,
        "product_id": cart_item.product_id,
        "quantity": cart_item.quantity
    }
# REMOVE CART ITEM



@app.delete("/cart/clear")
async def clear_cart(
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    user_id = token_data.get("user_id")

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid user token"
        )

    cart_items = db.query(
        models.Cart
    ).filter(
        models.Cart.user_id == user_id
    ).all()

    if not cart_items:
        return {
            "message": "Cart is already empty"
        }

    for cart_item in cart_items:
        db.delete(cart_item)

    db.commit()

    await manager.send_notification(
        user_id,
        "Your cart has been cleared."
    )

    return {
        "message": "Cart cleared successfully"
    }


# CLEAR CART

@app.delete("/cart/clear")
async def clear_cart(
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    user_id = token_data.get("user_id")

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid user token"
        )

    cart_items = db.query(
        models.Cart
    ).filter(
        models.Cart.user_id == user_id
    ).all()

    if not cart_items:
        return {
            "message": "Cart is already empty"
        }

    for cart_item in cart_items:
        db.delete(cart_item)

    db.commit()

    await manager.send_notification(
        user_id,
        "Your cart has been cleared."
    )

    return {
        "message": "Cart cleared successfully"
    }


# REMOVE CART ITEM

@app.delete("/cart/{cart_id}")
async def remove_cart_item(
    cart_id: int,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    user_id = token_data.get("user_id")

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid user token"
        )

    cart_item = db.query(
        models.Cart
    ).filter(
        models.Cart.id == cart_id,
        models.Cart.user_id == user_id
    ).first()

    if not cart_item:
        raise HTTPException(
            status_code=404,
            detail="Cart item not found"
        )

    product = db.query(
        models.Product
    ).filter(
        models.Product.id == cart_item.product_id
    ).first()

    product_name = product.name if product else "Product"

    db.delete(cart_item)
    db.commit()

    await manager.send_notification(
        user_id,
        f"{product_name} was removed from your cart."
    )

    return {
        "message": "Product removed from cart"
    }






# PLACE ORDER
@app.post("/orders")







def place_order(







    db: Session = Depends(get_db),







    token_data: dict = Depends(verify_token)







):















    user_id = token_data.get("user_id")















    if not user_id:















        raise HTTPException(







            status_code=401,







            detail="Invalid user token"







        )















    cart_items = db.query(







        models.Cart







    ).filter(







        models.Cart.user_id == user_id







    ).all()















    if not cart_items:















        raise HTTPException(







            status_code=400,







            detail="Your cart is empty"







        )















    total_amount = 0















    order_items_data = []















    for cart_item in cart_items:















        product = db.query(







            models.Product







        ).filter(







            models.Product.id == cart_item.product_id







        ).first()















        if not product:















            raise HTTPException(







                status_code=404,







                detail=f"Product {cart_item.product_id} not found"







            )















        if cart_item.quantity > product.stock:















            raise HTTPException(







                status_code=400,







                detail=f"Insufficient stock for {product.name}"







            )















        item_total = (







            product.price *







            cart_item.quantity







        )















        total_amount += item_total















        order_items_data.append({







            "product_id": product.id,







            "quantity": cart_item.quantity,







            "price": product.price







        })















    new_order = models.Order(







        user_id=user_id,







        total_amount=total_amount,







        status="pending"







    )















    db.add(new_order)















    db.flush()















    for item_data in order_items_data:















        new_order_item = models.OrderItem(







            order_id=new_order.id,







            product_id=item_data["product_id"],







            quantity=item_data["quantity"],







            price=item_data["price"]







        )















        db.add(new_order_item)















        product = db.query(







            models.Product







        ).filter(







            models.Product.id == item_data["product_id"]







        ).first()















        product.stock -= item_data["quantity"]















    for cart_item in cart_items:















        db.delete(cart_item)















    db.commit()















    db.refresh(new_order)















    return {







        "message": "Order placed successfully",







        "order_id": new_order.id,







        "user_id": new_order.user_id,







        "total_amount": new_order.total_amount,







        "status": new_order.status,







        "items": [







            {







                "product_id": item["product_id"],







                "quantity": item["quantity"],







                "price": item["price"]







            }







            for item in order_items_data







        ]







    }























# ============================================================







# VIEW MY ORDERS







# ============================================================















@app.get("/orders")







def get_my_orders(







    db: Session = Depends(get_db),







    token_data: dict = Depends(verify_token)







):















    user_id = token_data.get("user_id")















    if not user_id:















        raise HTTPException(







            status_code=401,







            detail="Invalid user token"







        )















    orders = db.query(







        models.Order







    ).filter(







        models.Order.user_id == user_id







    ).all()















    if not orders:















        return {







            "message": "No orders found",







            "orders": []







        }















    result = []















    for order in orders:















        order_items = db.query(







            models.OrderItem







        ).filter(







            models.OrderItem.order_id == order.id







        ).all()















        result.append({







            "order_id": order.id,







            "user_id": order.user_id,







            "total_amount": order.total_amount,







            "status": order.status,







            "items": [







                {







                    "order_item_id": item.id,







                    "product_id": item.product_id,







                    "quantity": item.quantity,







                    "price": item.price







                }







                for item in order_items







            ]







        })















    return {







        "total_orders": len(orders),







        "orders": result







    }























# ============================================================







# VIEW SINGLE ORDER







# ============================================================















@app.get("/orders/{order_id}")







def get_single_order(







    order_id: int,







    db: Session = Depends(get_db),







    token_data: dict = Depends(verify_token)







):















    user_id = token_data.get("user_id")















    if not user_id:















        raise HTTPException(







            status_code=401,







            detail="Invalid user token"







        )















    order = db.query(







        models.Order







    ).filter(







        models.Order.id == order_id,







        models.Order.user_id == user_id







    ).first()















    if not order:















        raise HTTPException(







            status_code=404,







            detail="Order not found"







        )















    order_items = db.query(







        models.OrderItem







    ).filter(







        models.OrderItem.order_id == order.id







    ).all()















    return {







        "order_id": order.id,







        "user_id": order.user_id,







        "total_amount": order.total_amount,







        "status": order.status,







        "items": [







            {







                "order_item_id": item.id,







                "product_id": item.product_id,







                "quantity": item.quantity,







                "price": item.price







            }







            for item in order_items







        ]







    }























# ============================================================







# CANCEL ORDER







# ============================================================















@app.put("/orders/{order_id}/cancel")







async def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    user_id = token_data.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid user token"
        )
    order = db.query(
        models.Order
    ).filter(
        models.Order.id == order_id,
        models.Order.user_id == user_id
    ).first()
    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )
    if order.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="Only pending orders can be cancelled"
        )
    order_items = db.query(
        models.OrderItem
    ).filter(
        models.OrderItem.order_id == order.id
    ).all()
    for item in order_items:
        product = db.query(
            models.Product
        ).filter(
            models.Product.id == item.product_id
        ).first()
        if product:
            product.stock += item.quantity

    order.status = "cancelled"

    notification = models.Notification(
        user_id=user_id,
        title="Order Cancelled",
        message=f"Your order #{order.id} has been cancelled."
)
    db.add(notification)

    await manager.send_notification(
        user_id,
        f"Your order #{order.id} has been cancelled."
)

    db.commit()
    db.refresh(order)
    return {
        "message": "Order cancelled successfully",
        "order_id": order.id,
        "status": order.status,
        "total_amount": order.total_amount
    }

# PAYMENT - MOCK PAYMENT
@app.post("/payments", response_model=schemas.PaymentResponse)
async def create_payment(
    payment_data: schemas.PaymentCreate,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    user_id = token_data.get("user_id")

    # Find the order belonging to the logged-in user
    order = db.query(models.Order).filter(
        models.Order.id == payment_data.order_id,
        models.Order.user_id == user_id
    ).first()

    # Find the user
    user = db.query(models.User).filter(
        models.User.id == user_id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found or does not belong to you"
        )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if order.status == "cancelled":
        raise HTTPException(
            status_code=400,
            detail="Cancelled orders cannot be paid"
        )

    # Check whether the order has already been successfully paid
    existing_payment = db.query(models.Payment).filter(
        models.Payment.order_id == order.id,
        models.Payment.payment_status == "success"
    ).first()

    if existing_payment:
        raise HTTPException(
            status_code=400,
            detail="This order has already been paid"
        )

    # Create mock payment
    payment = models.Payment(
        order_id=order.id,
        user_id=user_id,
        amount=order.total_amount,
        payment_method=payment_data.payment_method,
        payment_status=payment_data.payment_status,
        transaction_id=f"MOCK_TXN_ORDER_{order.id}"
    )

    db.add(payment)

    # Handle successful payment
    if payment_data.payment_status == "success":

        if order.status == "pending":
            order.status = "confirmed"

        notification = models.Notification(
            user_id=user_id,
            title="Payment Successful",
            message=f"Payment for order #{order.id} was successful."
        )

        db.add(notification)

        await manager.send_notification(
            user_id,
            f"Payment for order #{order.id} was successful."
        )

        await send_email(
            user.email,
            "Payment Successful",
            f"Your payment for order #{order.id} was successful.\n\n"
            f"Amount: ₹{order.total_amount}\n\n"
            f"Thank you for your order!"
        )

    # Handle failed payment
    elif payment_data.payment_status == "failed":

        notification = models.Notification(
            user_id=user_id,
            title="Payment Failed",
            message=f"Payment for order #{order.id} failed."
        )

        db.add(notification)

        await manager.send_notification(
            user_id,
            f"Payment for order #{order.id} failed."
        )

        await send_email(
            user.email,
            "Payment Failed",
            f"Your payment for order #{order.id} failed.\n\n"
            f"Amount: ₹{order.total_amount}\n\n"
            f"Please try the payment again."
        )

    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid payment status. Use 'success' or 'failed'."
        )

    db.commit()
    db.refresh(payment)

    return payment

# ============================================================
# VIEW MY PAYMENTS
# ============================================================

@app.get("/payments/{payment_id}", response_model=schemas.PaymentResponse)
def get_payment_details(
    payment_id: int,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    user_id = token_data.get("user_id")

    payment = db.query(models.Payment).filter(
        models.Payment.id == payment_id,
        models.Payment.user_id == user_id
    ).first()

    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Payment not found"
        )

    return payment

@app.get("/payments", response_model=list[schemas.PaymentResponse])
def get_my_payments(
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    user_id = token_data.get("user_id")

    payments = db.query(models.Payment).filter(
        models.Payment.user_id == user_id
    ).all()

    return payments













# ADMIN - VIEW ALL ORDERS







# ============================================================















@app.get("/admin/orders")







def get_all_orders(







    db: Session = Depends(get_db),







    token_data: dict = Depends(verify_admin)







):















    orders = db.query(







        models.Order







    ).all()















    if not orders:















        return {







            "message": "No orders found",







            "orders": []







        }















    result = []















    for order in orders:















        order_items = db.query(







            models.OrderItem







        ).filter(







            models.OrderItem.order_id == order.id







        ).all()















        user = db.query(







            models.User







        ).filter(







            models.User.id == order.user_id







        ).first()















        result.append({







            "order_id": order.id,







            "user_id": order.user_id,







            "customer_name": user.name if user else None,







            "customer_email": user.email if user else None,







            "total_amount": order.total_amount,







            "status": order.status,







            "items": [







                {







                    "order_item_id": item.id,







                    "product_id": item.product_id,







                    "quantity": item.quantity,







                    "price": item.price







                }







                for item in order_items







            ]







        })















    return {







        "total_orders": len(orders),







        "orders": result







    }























# ============================================================







# ADMIN - VIEW SINGLE ORDER







# ============================================================















@app.get("/admin/orders/{order_id}")







def get_admin_single_order(







    order_id: int,







    db: Session = Depends(get_db),







    token_data: dict = Depends(verify_admin)







):















    order = db.query(







        models.Order







    ).filter(







        models.Order.id == order_id







    ).first()















    if not order:















        raise HTTPException(







            status_code=404,







            detail="Order not found"







        )















    user = db.query(







        models.User







    ).filter(







        models.User.id == order.user_id







    ).first()















    order_items = db.query(







        models.OrderItem







    ).filter(







        models.OrderItem.order_id == order.id







    ).all()















    return {







        "order_id": order.id,







        "user_id": order.user_id,







        "customer_name": user.name if user else None,







        "customer_email": user.email if user else None,







        "total_amount": order.total_amount,







        "status": order.status,







        "items": [







            {







                "order_item_id": item.id,







                "product_id": item.product_id,







                "quantity": item.quantity,







                "price": item.price







            }







            for item in order_items







        ]







    }























# ============================================================







# ADMIN - UPDATE ORDER STATUS







# ============================================================















@app.put("/admin/orders/{order_id}/status")







async def update_order_status(
    order_id: int,
    status_data: schemas.OrderStatusUpdate,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_admin)
):
    order = db.query(
        models.Order
    ).filter(
        models.Order.id == order_id
    ).first()
    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )
    allowed_statuses = [
        "pending",
        "confirmed",
        "shipped",
        "delivered",
        "cancelled"
    ]
    new_status = status_data.status.lower()
    if new_status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid order status"
        )
    if order.status == "cancelled":
        raise HTTPException(
            status_code=400,
            detail="Cancelled orders cannot be updated"
        )
    order.status = new_status

    notification = models.Notification(
        user_id=order.user_id,
        title="Order Status Updated",
        message=f"Your order #{order.id} is now {new_status}."
    )

    db.add(notification)

    await manager.send_notification(
        order.user_id,
        f"Your order #{order.id} is now {new_status}."
)

    db.commit()

    db.refresh(order)
    return {
        "message": "Order status updated successfully",
        "order_id": order.id,
        "status": order.status
    }
@app.post("/notifications", response_model=schemas.NotificationResponse)
def create_notification(
    notification_data: schemas.NotificationCreate,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    user_id = token_data.get("user_id")

    notification = models.Notification(
        user_id=user_id,
        title=notification_data.title,
        message=notification_data.message
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    return notification

@app.get("/notifications", response_model=list[schemas.NotificationResponse])
def get_my_notifications(
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    user_id = token_data.get("user_id")

    notifications = db.query(models.Notification).filter(
        models.Notification.user_id == user_id
    ).order_by(models.Notification.created_at.desc()).all()

    return notifications


@app.get("/callback")
async def auth0_callback(request: Request, db: Session = Depends(get_db)):
    result = await auth_client.complete_interactive_login(str(request.url))
    user_info = result.get("state_data", {}).get("user")
    if not user_info:
        raise HTTPException(status_code=400, detail="Auth0 user information not found")
    email = user_info.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Auth0 email not found")
    existing_user = db.query(models.User).filter(
        models.User.email == email
    ).first()
    if not existing_user:
        existing_user = models.User(
            name=user_info.get("name", "Auth0 User"),
            email=email,
            password="AUTH0_USER",
            role="customer"
        )
        db.add(existing_user)
        db.commit()
        db.refresh(existing_user)
    access_token = create_access_token({
        "user_id": existing_user.id,
        "role": existing_user.role
    })
    return {
        "message": "Auth0 login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": existing_user.id,
            "name": existing_user.name,
            "email": existing_user.email,
            "role": existing_user.role
        }
    }

@app.get("/auth0/login")
async def auth0_login():
    authorization_url = await auth_client.start_interactive_login()
    return RedirectResponse(url=authorization_url)


@app.put("/notifications/{notification_id}/read", response_model=schemas.NotificationResponse)
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    user_id = token_data.get("user_id")

    notification = db.query(models.Notification).filter(
        models.Notification.id == notification_id,
        models.Notification.user_id == user_id
    ).first()

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )

    notification.is_read = True

    db.commit()
    db.refresh(notification)

    return notification