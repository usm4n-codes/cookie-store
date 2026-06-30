# 🍪 Sweet Bites Cookie Store

A beginner-friendly Flask + MongoDB web application for a university semester project.

---

## Project Structure

```
sweet_bites/
│
├── app.py                  ← Main Flask application (all routes live here)
├── requirements.txt        ← Python packages needed
│
├── static/
│   └── css/
│       └── style.css       ← All styling
│
├── templates/
│   ├── login.html          ← Login page
│   ├── register.html       ← Registration page
│   ├── home.html           ← Customer product listing
│   ├── product.html        ← Single product detail + add to cart
│   ├── cart.html           ← Shopping cart
│   ├── admin.html          ← Admin dashboard (view + delete products)
│   └── add_product.html    ← Admin: add new product
│
└── database/
    ├── __init__.py
    └── mongodb.py          ← MongoDB connection helper
```

---

## Prerequisites

- Python 3.9+
- MongoDB running locally on port 27017

---

## Setup & Run

### 1. Install MongoDB
Download and install from https://www.mongodb.com/try/download/community  
Make sure the `mongod` service is running.

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac / Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the app
```bash
python app.py
```

The first run will automatically create:
- A default **admin** account (`username: admin`, `password: admin123`)
- 6 sample cookie products

### 5. Open in browser
```
http://localhost:5000
```

---

## Default Accounts

| Role     | Username | Password  |
|----------|----------|-----------|
| Admin    | admin    | admin123  |
| Customer | *(register your own)* | — |

---

## Database Collections

| Collection | Fields |
|------------|--------|
| `users`    | `username`, `password`, `role` |
| `products` | `name`, `description`, `price`, `image_url` |
| `cart`     | `user_id`, `product_id`, `quantity` |

---

## Features

### Customer
- Register and log in
- Browse all cookie products
- View full product details
- Add to cart with quantity selector
- Buy Now (goes straight to cart)
- Remove items from cart
- See order total

### Admin
- Log in to a dedicated admin dashboard
- Add new cookie products (with live image preview)
- Delete products (also cleans up cart entries)
- View all products in a table

---

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: MongoDB via PyMongo
- **Templating**: Jinja2
- **Frontend**: HTML + CSS (no JavaScript frameworks)
- **Auth**: Flask Sessions
