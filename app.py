from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
import os

app = Flask(__name__)

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "mypassword"),
            database=os.getenv("DB_NAME", "ecomv1")
        )
        return conn
    except mysql.connector.Error as e:
        print(f"Database connection failed: {e}")
        return None

@app.route('/')
def home():
    conn = get_db_connection()
    if conn is None:
        return "Database connection failed. Check the console for details."
    
    cursor = conn.cursor(dictionary=True)
    try:
        # Fetch categories
        cursor.execute("SELECT ProductCategoryId, ProductCategory FROM ProductCategory WHERE IsDeleted = 'N' or `IsDeleted`=''")
        categories = cursor.fetchall()
        print("Fetched categories:", categories)

        # Fetch subcategories
        cursor.execute("SELECT ProductSubCategoryId, ProductSubCategory, ProductCategory FROM ProductSubCategory WHERE IsDeleted = 'N' or `IsDeleted`=''")
        subcategories = cursor.fetchall()
        print("Fetched subcategories:", subcategories)
    finally:
        cursor.close()
        conn.close()

    # Organize subcategories under their respective categories
    category_map = {category['ProductCategoryId']: {'name': category['ProductCategory'], 'subcategories': []} for category in categories}
    for subcategory in subcategories:
        category_id = subcategory['ProductCategory']
        if category_id in category_map:
            category_map[category_id]['subcategories'].append({'id': subcategory['ProductSubCategoryId'], 'name': subcategory['ProductSubCategory']})

    return render_template("navbar.html", categories=category_map)

if __name__ == '__main__':
    app.run(debug=True, port=5002)
