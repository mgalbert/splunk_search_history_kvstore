#!/usr/bin/env python3
#
# Thu Nov 14 09:35:51 PM UTC 2024 - malbert
# Used for when Splunk is configured to save user search history in KVstore to allow for replication across members.
# Configured through limits.conf under [search] as search_history_storage_mode = kvstore
#
# Script to parse SearchHistory backup of Splunk into per user archives so they can be restored into proper user context.
# Once broken down, you can restore/migrate using the following:
# curl -k -u admin:$splunkpw -X POST -H "Content-Type: application/json" \
# https://localhost:8089/servicesNS/<specific_user>/system/storage/collections/data/SearchHistory/batch_save -d@SearchHistory0-<specific_user>.json
#
# Tested on Splunk 9.1.5 Search Head Cluster and Stand alone instances.
#
import json
import os
import sys

# Check for filename argument
if len(sys.argv) != 2:
    print("Usage: python script.py <input_filename>")
    sys.exit(1)

input_filename = sys.argv[1]

# Verify the file exists
if not os.path.isfile(input_filename):
    print(f"File '{input_filename}' not found!")
    sys.exit(1)

# Extract base name of input file (without extension)
input_base = os.path.splitext(os.path.basename(input_filename))[0]

# Read JSON data from the specified file
with open(input_filename, 'r') as file:
    data = json.load(file)

# Group data by _user
user_data = {}

for entry in data:
    user = entry.get("_user")
    if user:
        user_data.setdefault(user, []).append({
            "history": entry.get("history"),
            "timestamp": entry.get("timestamp"),
            "user": user,
            "key": entry.get("_key")
        })

# Write each user's data to a file
for user, records in user_data.items():
    # Make a filename-safe version of the user email
    safe_user = user.replace("@", "_").replace(".", "_")
    filename = f"{input_base}_{safe_user}.json"

    # Write the JSON array to the file
    with open(filename, 'w') as file:
        json.dump(records, file, indent=4)

    print(f"Data for user {user} written to {filename}")

