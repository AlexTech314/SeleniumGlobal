#!/bin/bash

# Define the curl command
curl_command() {
  curl -X POST https://x0rytui5fg.execute-api.us-east-1.amazonaws.com/prod \
  -H "x-api-key: W1GUQLhKejW4UE6GoiQ353tgiFUcoGU16FQkzGj2" \
  -H "Content-Type: application/json" \
  -d '{
    "state": "CA",
    "licenseType": "Psychologist",
    "licenseNumber": "33514",
    "firstName": "Susan",
    "lastName": "Lok"
  }'
}

# Run 10 instances in parallel
for i in {1..10}; do
  curl_command &  # Run in the background
done

# Wait for all background processes to complete
wait

echo "All requests completed."
