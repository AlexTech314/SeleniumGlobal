#!/bin/bash

# Define the curl command
curl_command() {
  start_time=$(date '+%Y-%m-%d %H:%M:%S')  # Capture start time
  echo "Request $1 started at: $start_time"

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

  echo ""

  end_time=$(date '+%Y-%m-%d %H:%M:%S')  # Capture end time
  echo "Request $1 ended at: $end_time"
}

# Run 10 instances in parallel
for i in {1..20}; do
  echo "Starting request $i"
  curl_command $i &  # Pass request number and run in the background
done

# Wait for all background processes to complete
wait

echo "All requests completed."
