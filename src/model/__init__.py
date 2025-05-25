

# Dummy data during project initialization

# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#         print("Database tables created (or already exist).")

#         if not Product.query.filter_by(name='Laptop').first():
#             laptop = Product(name='Laptop', price=1200.00)
#             phone = Product(name='Smartphone', price=800.00)
#             headphones = Product(name='Headphones', price=150.00)

#             db.session.add_all([laptop, phone, headphones])
#             db.session.commit()
#             print("Added example products.")
#         else:
#             print("Example products already exist.")

        # # Retrieve products to use for orders
        # laptop = Product.query.filter_by(name='Laptop').first()
        # phone = Product.query.filter_by(name='Smartphone').first()

        # print("\nAdding example orders...")
        # order1 = Order(product_id=laptop.id, quantity=1)
        # order2 = Order(product_id=phone.id, quantity=2)
        # order3 = Order(product_id=laptop.id, quantity=1)

        # db.session.add_all([order1, order2, order3])
        # db.session.commit()
        # print("Added example orders.")

        # # --- Querying Data ---
        # print("\n--- All Products ---")
        # all_products = Product.query.all()
        # for product in all_products:
        #     print(product)

        # print("\n--- All Orders ---")
        # all_orders = Order.query.all()
        # for order in all_orders:
        #     print(order)
        #     # Access related product information
        #     if order.product: # Check if the product relationship is loaded
        #         print(f"  -> Product Name: {order.product.name}, Price: ${order.product.price:.2f}")

        # print("\n--- Orders for Laptop ---")
        # laptop_orders = Order.query.filter_by(product_id=laptop.id).all()
        # for order in laptop_orders:
        #     print(order)
