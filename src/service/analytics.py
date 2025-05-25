from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import boto3
import os
import threading
import time
import json
from decouple import config

app = Flask(__name__)
app.config['SECRET_KEY'] = config('FLASK_SECRET_KEY', 'a_very_secret_key_for_dev')
socketio = SocketIO(app, cors_allowed_origins="*")


POLL_INTERVAL_SECONDS = 1 

aws_url = config("SQS_QUEUE_URL", default="")
aws_region = config("AWS_REGION", default="eu-north-1")

client = boto3.client('sqs', region_name=aws_region)

realtime_analytics_data = {
    "total_orders_processed": 0,
    "total_revenue": 0.0,
    "product_sales_count": {},
    "latest_order_summary": "No orders processed yet."
}

def receive_sqs_messages(max_number_of_messages: int = 10, wait_time_seconds: int = 20) -> list:
    """
    Receives messages from the pre-configured AWS SQS queue using the global client.
    """
    received_messages = []
    if client is None:
        return []

    try:
        response = client.receive_message(
            QueueUrl=aws_url,
            MaxNumberOfMessages=max_number_of_messages,
            WaitTimeSeconds=wait_time_seconds,
            MessageAttributeNames=['All']
        )

        messages = response.get('Messages', [])
        if messages:
            print(f"Consumer: Received {len(messages)} message(s) from SQS.")
            for message in messages:
                received_messages.append({
                    'Body': message['Body'],
                    'ReceiptHandle': message['ReceiptHandle']
                })
        # else:
            # print("Consumer: No new messages available in the queue (long polling).")

    except Exception as e:
        print(f"Consumer: Error receiving messages from SQS: {e}")

    return received_messages

def delete_sqs_message(receipt_handle: str) -> bool:
    """
    Deletes a message from the SQS queue using its receipt handle.
    """
    if client is None:
        return False
    try:
        client.delete_message(
            QueueUrl=aws_url,
            ReceiptHandle=receipt_handle
        )
        print(f"Consumer: Message with receipt handle '{receipt_handle[:10]}...' deleted successfully.")
        return True
    except Exception as e:
        print(f"Consumer: Error deleting message from SQS: {e}")
        return False
    
def sqs_consumer_thread():
    """
    This function runs in a separate thread, continuously polling SQS
    and updating the real-time analytics data.
    """
    print("Consumer thread started. Waiting for messages...")
    while True:
        if client is None:
            print("Consumer thread: SQS client not available. Retrying in 10 seconds...")
            time.sleep(10)
            continue

        messages = receive_sqs_messages(max_number_of_messages=10, wait_time_seconds=20)

        if messages:
            for message in messages:
                try:
                    order_details = json.loads(message['Body'])
                    print(f"Consumer: Processing order: {order_details.get('order_id')}")

                    realtime_analytics_data["total_orders_processed"] += 1
                    
                    product_price = order_details.get("product_price", 0.0)
                    quantity = order_details.get("quantity", 1)
                    order_revenue = product_price * quantity
                    realtime_analytics_data["total_revenue"] += order_revenue

                    product_name = order_details.get("product_name", "Unknown Product")
                    realtime_analytics_data["product_sales_count"][product_name] = \
                        realtime_analytics_data["product_sales_count"].get(product_name, 0) + quantity
                    
                    realtime_analytics_data["latest_order_summary"] = (
                        f"Order #{order_details.get('order_id')}: "
                        f"{product_name} (x{quantity}) for ${order_revenue:.2f} "
                        f"on {order_details.get('order_date', '').split('T')[0]}"
                    )

                    socketio.emit('realtime_dashboard_update', realtime_analytics_data)
                    print("Consumer: Emitted dashboard update via WebSocket.")

                    delete_sqs_message(message['ReceiptHandle'])

                except json.JSONDecodeError:
                    print(f"Consumer: Error decoding JSON from message body: {message['Body']}")
                    delete_sqs_message(message['ReceiptHandle'])
                except Exception as e:
                    print(f"Consumer: Error processing message: {e}")
                    delete_sqs_message(message['ReceiptHandle']) 
                    
        time.sleep(POLL_INTERVAL_SECONDS)

@app.route('/')
def index():
    """
    Renders the main dashboard HTML page.
    Passes the initial analytics data to the template.
    """
    return render_template('analytics_dashboard.html', initial_data=realtime_analytics_data)

@socketio.on('connect')
def handle_connect():
    """
    Handles new client connections. Sends the current analytics data to the new client.
    """
    print(f"Client connected: {request.sid}")
    emit('realtime_dashboard_update', realtime_analytics_data)

@socketio.on('disconnect')
def handle_disconnect():
    """
    Handles client disconnections.
    """
    print(f"Client disconnected: {request.sid}")

if __name__ == '__main__':
    consumer_thread = threading.Thread(target=sqs_consumer_thread, daemon=True)
    consumer_thread.start()

    socketio.run(app, debug=True, allow_unsafe_werkzeug=True, port=5001)
