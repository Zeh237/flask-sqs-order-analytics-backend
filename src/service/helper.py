import boto3
from decouple import config
import os

aws_url = config("SQS_QUEUE_URL", default="")
aws_region = config("AWS_REGION", default="eu-north-1")

client = boto3.client('sqs', region_name=aws_region)

def send_message_to_sqs(message_body: str) -> dict:
    """
    Sends a message to the pre-configured AWS SQS queue.
    """
    try:
        response = client.send_message(
            QueueUrl=aws_url,
            MessageBody=message_body
        )
        print(f"Message sent successfully! Message ID: {response.get('MessageId')}")
        return {
            "status": "success",
            "message_id": response.get('MessageId'),
            "md5_of_message_body": response.get('MD5OfMessageBody')
        }
    except Exception as e:
        print(f"Failed to send message to SQS: {e}")
        return {"status": "error", "message": str(e)}
    
    
def receive_sqs_messages(max_number_of_messages: int = 5, wait_time_seconds: int = 5) -> list:
    """
    Receives messages from the pre-configured AWS SQS queue.
    """
    received_messages = []
    try:
        response = client.receive_message(
            QueueUrl=aws_url,
            MaxNumberOfMessages=max_number_of_messages,
            WaitTimeSeconds=wait_time_seconds,
            MessageAttributeNames=['All']
        )

        messages = response.get('Messages', [])
        if messages:
            print(f"Received {len(messages)} message(s) from SQS.")
            for message in messages:
                received_messages.append({
                    'Body': message['Body'],
                    'ReceiptHandle': message['ReceiptHandle']
                })
        else:
            print("No new messages available in the queue.")

    except Exception as e:
        print(f"Error receiving messages from SQS: {e}")

    return received_messages


def delete_sqs_message(receipt_handle: str) -> bool:
    """
    Deletes a message from the SQS queue using its receipt handle.
    """
    try:
        client.delete_message(
            QueueUrl=aws_url,
            ReceiptHandle=receipt_handle
        )
        print(f"Message with receipt handle '{receipt_handle[:10]}...' deleted successfully.")
        return True
    except Exception as e:
        print(f"Error deleting message from SQS: {e}")
        return False

if __name__ == '__main__':
    # test_message_1 = "Hello, this is a test message from my flask app"
    # print(f"\nAttempting to send message: '{test_message_1}'")
    # result_1 = send_message_to_sqs(test_message_1)
    # print("Result 1:", result_1)

    # test_message_2 = "Another message for the queue."
    # print(f"\nAttempting to send message: '{test_message_2}'")
    # result_2 = send_message_to_sqs(test_message_2)
    # print("Result 2:", result_2)
    messages_to_process = receive_sqs_messages(max_number_of_messages=5, wait_time_seconds=10)
    print(len(messages_to_process))
    if messages_to_process:
        for i, msg in enumerate(messages_to_process):
            print(f"\nProcessing Message {i+1}:")
            print(f"  Body: {msg['Body']}")
            print(f"  ReceiptHandle: {msg['ReceiptHandle']}...")
            delete_sqs_message(msg['ReceiptHandle'])
    else:
        print("No messages to process.")