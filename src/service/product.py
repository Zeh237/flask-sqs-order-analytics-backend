from src.model.product import Product, Order
from src import app, db
from src.service.helper import send_message_to_sqs
import json


def create_product(name: str, price: float, image: str = 'default.jpg') -> Product | None:
    """
    Creates a new product
    """
    with app.app_context():
        existing_product = Product.query.filter_by(name=name).first()
        if existing_product:
            print(f"Error: Product '{name}' already exists.")
            return None

        new_product = Product(name=name, price=price, image=image)
        try:
            db.session.add(new_product)
            db.session.commit()
            print(f"Product '{name}' created successfully with ID: {new_product.id}")
            return new_product
        except Exception as e:
            db.session.rollback()
            print(f"Error creating product '{name}': {e}")
            return None
        
        
def get_all_products() -> list[Product]:
    """
    Retrieves all products from the database.
    """
    with app.app_context():
        products = Product.query.all()
        return products
    

def create_order(product_id: int, quantity: int = 1) -> Order | None:
    """
    Creates a new order for a specific product and sends the order details to sqs queue for analytics
    """
    with app.app_context():
        product = Product.query.get(product_id)
        if not product:
            print(f"Error: Product with ID {product_id} not found. Cannot create order.")
            return None

        new_order = Order(product_id=product_id, quantity=quantity)
        try:
            db.session.add(new_order)
            db.session.commit()
            print(f"Order created successfully for Product ID {product_id}, Quantity: {quantity}")

            order_details = {
                "order_id": new_order.id,
                "product_id": new_order.product_id,
                "product_name": product.name,
                "product_price": product.price,
                "quantity": new_order.quantity,
                "order_date": new_order.order_date.isoformat(),
                "product_image": product.image
            }
            message_body_json = json.dumps(order_details)
            print(f"Attempting to send order details to SQS: {message_body_json}")
            sqs_send_result = send_message_to_sqs(message_body_json)
            if sqs_send_result.get("status") == "success":
                print(f"Order details sent to SQS: Message ID {sqs_send_result.get('message_id')}")
            else:
                print(f"Failed to send order details to SQS: {sqs_send_result.get('message')}")

            return new_order
        except Exception as e:
            db.session.rollback()
            print(f"Error creating order for Product ID {product_id}: {e}")
            return None
