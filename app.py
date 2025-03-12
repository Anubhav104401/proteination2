import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import bcrypt
import jwt
import datetime
from bson import ObjectId
from functools import wraps  # Required for decorators
from dotenv import load_dotenv
from flask import Flask, send_file
from flask import Flask, render_template

load_dotenv()

app = Flask(__name__, static_folder='static')
CORS(app)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")  # Use a strong secret key

@app.route('/')
def index():
    return render_template('main.html')  # Or any default page you want

@app.route('/Login')
def login():
    return render_template('Login.html')

@app.route('/content')
def content():
    return render_template('content.html')

@app.route('/products')
def products():
    return render_template('products.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/blaze-details')
def blaze_details():
    return render_template('blaze-details.html')

@app.route('/nitrotech-details')
def nitr_details():
    return render_template('nitrotech-details.html')

@app.route('/on-details')
def on_details():
    return render_template('on-details.html')

@app.route('/forgot.html')
def forgot():
    return render_template('forgot.html')

@app.route('/Register')
def Register():
    return render_template('Register.html')

# MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["ecommerce"]
users_collection = db["users"]
products_collection = db["products"]
cart_collection = db["cart"]

# User Registration
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    existing_user = users_collection.find_one({"email": data["email"]})
    
    if existing_user:
        return jsonify({"message": "User already exists"}), 400
    
    if len(data["password"]) < 6:
        return jsonify({"message": "Password must be at least 6 characters"}), 400
    
    hashed_password = bcrypt.hashpw(data["password"].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    users_collection.insert_one({"email": data["email"], "password": hashed_password})
    
    return jsonify({"message": "User registered successfully"}), 200

# User Login
@app.route('/login', methods=['POST'])
def login_user():
    data = request.json
    user = users_collection.find_one({"email": data["email"]})
    
    if user and bcrypt.checkpw(data["password"].encode('utf-8'), user["password"]):


        token = jwt.encode(
            {"email": data["email"], "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=1)}, 
            app.config['SECRET_KEY'], algorithm="HS256"
        )
        return jsonify({"token": token})
    
    return jsonify({"message": "Invalid credentials"}), 401

# Middleware: Verify JWT token
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"message": "Token is missing or invalid!"}), 401
        
        token = auth_header.split(" ")[1]

        try:
            decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            request.user_email = decoded["email"]  # Store email for later use
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Session has expired!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Dear user please log in to use our services"}), 401

        return f(*args, **kwargs)

    return decorated

# Add to Cart
@app.route('/add-to-cart', methods=['POST'])
@token_required  # Ensures only authenticated users can add to the cart
def add_to_cart():
    data = request.json
    product_id = data.get("product_id")
    quantity = int(data.get("quantity", 1))

    if not product_id or quantity < 1:
        return jsonify({"message": "Invalid request"}), 400

    # Query using string _id (not ObjectId)
    product = products_collection.find_one({"_id": product_id})

    if not product:
        return jsonify({"message": "Product not found"}), 400

    if product["stock"] < quantity:
        return jsonify({"message": "Not enough stock available"}), 400

    # Insert into cart
    cart_collection.insert_one({
        "email": request.user_email,
        "product_id": product_id,
        "quantity": quantity
    })

    # Reduce stock
    products_collection.update_one({"_id": product_id}, {"$inc": {"stock": -quantity}})

    return jsonify({"message": "Product added to cart"}), 200


    # Reduce stock
    products_collection.update_one({"_id": ObjectId(product_id)}, {"$inc": {"stock": -quantity}})
    
    return jsonify({"message": "Product added to cart"}), 200

# Check Stock
@app.route('/check-stock/<product_id>', methods=['GET'])
def check_stock(product_id):
    try:
        product = products_collection.find_one({"_id": ObjectId(product_id)})
        if not product:
            return jsonify({"message": "Product not found"}), 404
        return jsonify({"stock": product["stock"]})
    except:
        return jsonify({"message": "Invalid product ID"}), 400
    
# Get User's Cart
@app.route('/get-cart', methods=['GET'])
@token_required
def get_cart():
    cart_items = list(cart_collection.find({"email": request.user_email}))

    if not cart_items:
        return jsonify({"cart": []})  # Return empty cart if no items

    # Fetch product details for each item
    cart_with_products = []
    for item in cart_items:
        product = products_collection.find_one({"_id": item["product_id"]})
        if product:
            cart_with_products.append({
                "product_id": product["_id"],
                "name": product["name"],
                "price": product["price"],
                "quantity": item["quantity"]
            })

    return jsonify({"cart": cart_with_products})


# Remove Item from Cart
@app.route('/remove-from-cart', methods=['POST'])
@token_required
def remove_from_cart():
    data = request.json
    product_id = data.get("product_id")

    if not product_id:
        return jsonify({"message": "Invalid request"}), 400

    cart_collection.delete_one({"email": request.user_email, "product_id": product_id})

    return jsonify({"message": "Item removed from cart"}), 200

# Clear Cart
@app.route('/clear-cart', methods=['POST'])
@token_required
def clear_cart():
    cart_collection.delete_many({"email": request.user_email})
    return jsonify({"message": "Cart cleared"}), 200


if __name__ == '__main__':
    print(app.url_map)
    app.run(debug=True)




