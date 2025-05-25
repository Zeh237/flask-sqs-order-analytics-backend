from flask import Flask, request, jsonify, render_template, redirect, url_for, Blueprint
from src.service.product import get_all_products, create_product, create_order
import os
from src import app
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = app.config['UPLOAD_FOLDER']
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


web = Blueprint("web", __name__)

@web.route('/')
def home():
    """
    Redirects to the products listing page.
    """
    return redirect(url_for('web.list_products'))

@web.route('/products', methods=['GET'])
def list_products():
    """
    Displays a list of all available products.
    """
    products = get_all_products()
    return render_template('products.html', products=products)

@web.route('/products/new', methods=['GET', 'POST'])
def new_product():
    """
    Handles displaying the form for creating a new product (GET)
    and processing the form submission (POST), including file upload.
    """
    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        
        # Default image filename
        image_filename = 'default.jpg'

        # Handle file upload
        if 'image_file' in request.files:
            file = request.files['image_file']
            if file.filename != '' and allowed_file(file.filename):
                # Secure the filename to prevent directory traversal attacks
                filename = secure_filename(file.filename)
                # Save the file to the UPLOAD_FOLDER
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                image_filename = filename # Use the saved filename for the database
            else:
                print(f"Warning: Invalid file type or no file selected for upload: {file.filename}")
                # You might want to return an error or flash a message here
                # For now, it will proceed with 'default.jpg' or previous image_filename

        if not name or not price:
            return "Error: Name and Price are required.", 400

        try:
            price = float(price)
        except ValueError:
            return "Error: Price must be a valid number.", 400

        # Pass the determined image_filename to the create_product function
        product = create_product(name, price, image_filename)
        if product:
            return redirect(url_for('web.list_products'))
        else:
            return "Error creating product. It might already exist.", 400
    
    # For GET request, display the form
    return render_template('new_product.html')


@web.route('/order/<int:product_id>', methods=['POST'])
def place_order(product_id):
    """
    Handles placing an order for a specific product.
    Expects quantity in the form data.
    """
    quantity = request.form.get('quantity', type=int, default=1)

    if quantity <= 0:
        return "Error: Quantity must be positive.", 400

    order = create_order(product_id, quantity)
    if order:
        return redirect(url_for('web.list_products'))
    else:
        return "Error placing order. Product might not exist.", 400


