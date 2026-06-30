# ─────────────────────────────────────────────
#  app.py  –  Sweet Bites Cookie Store
#  Main Flask application file
# ─────────────────────────────────────────────

from flask import Flask, render_template, request, redirect, url_for, session, flash
from database.mongodb import get_db
from bson.objectid import ObjectId   # MongoDB uses ObjectId for _id fields

app = Flask(__name__)
app.secret_key = "sweetbites_secret_key_2024"   # needed for sessions; change in production

# Get the database instance (reused across all routes)
db = get_db()


# ──────────────────────────────────────────────────────────────────
#  HELPER: check if a user is logged in
# ──────────────────────────────────────────────────────────────────

def is_logged_in():
    return "user_id" in session

def is_admin():
    return session.get("role") == "admin"


# ──────────────────────────────────────────────────────────────────
#  AUTH ROUTES  –  Register / Login / Logout
# ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Redirect root URL to login page."""
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    GET  → show the register form
    POST → create a new user account (always 'customer' role)
    """
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()

        # Check if the username already exists
        existing_user = db.users.find_one({"username": username})
        if existing_user:
            flash("Username already taken. Please choose another.", "error")
            return redirect(url_for("register"))

        # Insert the new user with role 'customer'
        db.users.insert_one({
            "username": username,
            "password": password,   # NOTE: plain text for simplicity; use hashing in real projects
            "role": "customer"
        })
        flash("Account created! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    GET  → show the login form
    POST → verify credentials and start a session
    """
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()

        # Look for the user in the database
        user = db.users.find_one({"username": username, "password": password})

        if user:
            # Store user info in the session (like a cookie)
            session["user_id"]  = str(user["_id"])
            session["username"] = user["username"]
            session["role"]     = user["role"]

            # Send to the right page based on role
            if user["role"] == "admin":
                return redirect(url_for("admin_dashboard"))
            else:
                return redirect(url_for("home"))
        else:
            flash("Invalid username or password.", "error")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    """Clear the session and redirect to login."""
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


# ──────────────────────────────────────────────────────────────────
#  CUSTOMER ROUTES
# ──────────────────────────────────────────────────────────────────

@app.route("/home")
def home():
    """Show all cookie products to the logged-in customer."""
    if not is_logged_in():
        return redirect(url_for("login"))

    # Fetch every product from the products collection
    products = list(db.products.find())
    return render_template("home.html", products=products)


@app.route("/product/<product_id>")
def product_detail(product_id):
    """Show the full details of a single product."""
    if not is_logged_in():
        return redirect(url_for("login"))

    # Find the product by its MongoDB ObjectId
    product = db.products.find_one({"_id": ObjectId(product_id)})
    if not product:
        flash("Product not found.", "error")
        return redirect(url_for("home"))

    return render_template("product.html", product=product)


@app.route("/add_to_cart/<product_id>", methods=["POST"])
def add_to_cart(product_id):
    """
    Add a product to the customer's cart.
    If the product is already in the cart, increase its quantity.
    """
    if not is_logged_in():
        return redirect(url_for("login"))

    quantity = int(request.form.get("quantity", 1))
    user_id  = session["user_id"]

    # Check if this product is already in the cart for this user
    existing = db.cart.find_one({"user_id": user_id, "product_id": product_id})

    if existing:
        # Update (increment) the quantity
        db.cart.update_one(
            {"_id": existing["_id"]},
            {"$inc": {"quantity": quantity}}
        )
    else:
        # Insert a new cart entry
        db.cart.insert_one({
            "user_id":    user_id,
            "product_id": product_id,
            "quantity":   quantity
        })

    flash("Added to cart!", "success")
    return redirect(url_for("cart"))


@app.route("/buy_now/<product_id>", methods=["POST"])
def buy_now(product_id):
    """Add item to cart then go straight to the cart page."""
    if not is_logged_in():
        return redirect(url_for("login"))

    quantity = int(request.form.get("quantity", 1))
    user_id  = session["user_id"]

    existing = db.cart.find_one({"user_id": user_id, "product_id": product_id})
    if existing:
        db.cart.update_one({"_id": existing["_id"]}, {"$inc": {"quantity": quantity}})
    else:
        db.cart.insert_one({"user_id": user_id, "product_id": product_id, "quantity": quantity})

    return redirect(url_for("cart"))


@app.route("/cart")
def cart():
    """Show the current user's cart with product details and a total price."""
    if not is_logged_in():
        return redirect(url_for("login"))

    user_id = session["user_id"]

    # Fetch all cart items for this user
    cart_items = list(db.cart.find({"user_id": user_id}))

    # Enrich each cart item with the full product info
    enriched = []
    total = 0
    for item in cart_items:
        product = db.products.find_one({"_id": ObjectId(item["product_id"])})
        if product:
            subtotal = product["price"] * item["quantity"]
            total   += subtotal
            enriched.append({
                "cart_id":  str(item["_id"]),
                "product":  product,
                "quantity": item["quantity"],
                "subtotal": subtotal
            })

    return render_template("cart.html", cart_items=enriched, total=total)


@app.route("/remove_from_cart/<cart_id>")
def remove_from_cart(cart_id):
    """Delete a single item from the cart."""
    if not is_logged_in():
        return redirect(url_for("login"))

    db.cart.delete_one({"_id": ObjectId(cart_id)})
    flash("Item removed from cart.", "success")
    return redirect(url_for("cart"))


# ──────────────────────────────────────────────────────────────────
#  ADMIN ROUTES
# ──────────────────────────────────────────────────────────────────

@app.route("/admin")
def admin_dashboard():
    """Admin dashboard: list all products."""
    if not is_admin():
        flash("Access denied.", "error")
        return redirect(url_for("login"))

    products = list(db.products.find())
    return render_template("admin.html", products=products)


@app.route("/admin/add_product", methods=["GET", "POST"])
def add_product():
    """
    GET  → show the Add Product form
    POST → save new product to the database
    """
    if not is_admin():
        flash("Access denied.", "error")
        return redirect(url_for("login"))

    if request.method == "POST":
        name        = request.form.get("name").strip()
        description = request.form.get("description").strip()
        price       = float(request.form.get("price"))
        image_url   = request.form.get("image_url").strip()

        db.products.insert_one({
            "name":        name,
            "description": description,
            "price":       price,
            "image_url":   image_url
        })
        flash(f'"{name}" has been added!', "success")
        return redirect(url_for("admin_dashboard"))

    return render_template("add_product.html")


@app.route("/admin/delete_product/<product_id>")
def delete_product(product_id):
    """Delete a product and remove it from all carts."""
    if not is_admin():
        flash("Access denied.", "error")
        return redirect(url_for("login"))

    # Remove the product
    db.products.delete_one({"_id": ObjectId(product_id)})
    # Also remove any cart entries that reference this product
    db.cart.delete_many({"product_id": product_id})

    flash("Product deleted.", "success")
    return redirect(url_for("admin_dashboard"))


# ──────────────────────────────────────────────────────────────────
#  SEED DATA  –  Creates admin + sample cookies on first run
# ──────────────────────────────────────────────────────────────────

def seed_data():
    """Insert default admin user and sample products if they don't exist yet."""

    # Default admin account
    if not db.users.find_one({"username": "admin"}):
        db.users.insert_one({"username": "admin", "password": "admin123", "role": "admin"})
        print("✅  Admin user created  →  username: admin | password: admin123")

    # Sample cookie products
    if db.products.count_documents({}) == 0:
        sample_products = [
            {
                "name": "Classic Chocolate Chip",
                "description": "Our signature cookie packed with rich semi-sweet chocolate chips. Golden edges, soft centre — pure comfort in every bite.",
                "price": 3.50,
                "image_url": "https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=400"
            },
            {
                "name": "Double Fudge Brownie",
                "description": "Intensely chocolatey with a fudgy, almost-brownie texture. Topped with a glossy dark-chocolate drizzle.",
                "price": 4.00,
                "image_url": "https://images.unsplash.com/photo-1606313564200-e75d5e30476c?w=400"
            },
            {
                "name": "Strawberry Shortcake",
                "description": "Light vanilla cookie swirled with real strawberry jam and a cream-cheese frosting dot on top.",
                "price": 3.75,
                "image_url": "https://images.unsplash.com/photo-1499636136210-6f4ee915583e?w=400"
            },
            {
                "name": "Snickerdoodle",
                "description": "Classic cinnamon-sugar rolled cookie with a crinkly top and a warm, cosy aroma straight from the oven.",
                "price": 3.00,
                "image_url": "https://images.unsplash.com/photo-1611293388250-580b08c4a145?w=400"
            },
            {
                "name": "Lemon Zest Delight",
                "description": "Bright and citrusy with real lemon zest, finished with a tangy lemon glaze. Refreshingly different.",
                "price": 3.50,
                "image_url": "https://images.unsplash.com/photo-1568051243858-533a607809a5?w=400"
            },
            {
                "name": "Peanut Butter Dream",
                "description": "Rich, dense peanut butter cookie with a classic fork-pressed top. A nutty treat that satisfies every craving.",
                "price": 3.25,
                "image_url": "https://images.unsplash.com/photo-1590080875515-8a3a8dc5735e?w=400"
            },
        ]
        db.products.insert_many(sample_products)
        print(f"✅  {len(sample_products)} sample products inserted.")


# ──────────────────────────────────────────────────────────────────
#  RUN THE APP
# ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    seed_data()          # populate the DB with starter data
    app.run(debug=True)  # debug=True gives helpful error pages; turn off in production
