import json
from main import handler

# Simulate the Lambda event
event = {
    "body": json.dumps({
        "state": "CA",
        "licenseType": "Psychologist",
        "licenseNumber": "33514",
        "firstName": "Susan",
        "lastName": "Lok"
    }),  # No Base64 encoding
    "resource": "/",
    "path": "/",
    "httpMethod": "POST",
    "isBase64Encoded": False
}

# Simulate the Lambda context (can be empty for local testing)
context = {}

# Invoke the handler function
response = handler(event, context)

# Print the response
print(f"Status Code: {response['statusCode']}")
print(f"Body: {response['body']}")
