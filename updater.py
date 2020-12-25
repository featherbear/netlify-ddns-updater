#!/usr/bin/python3
import os
import requests
import sys

SITE_ID  = os.getenv('SITE_ID')
HOSTNAME = os.getenv('HOSTNAME')
API_KEY  = os.getenv('API_KEY')

if not SITE_ID:
  print("Error: SITE_ID not supplied!")
  sys.exit(1)
if not HOSTNAME:
  print("Error: HOSTNAME not supplied!")
  sys.exit(1)
if not API_KEY:
  print("Error: API_KEY not supplied!")
  sys.exit(1)

class Client:
  API_BASE = "https://api.netlify.com/api/v1/dns_zones/"
  
  def __init__(self, apiKey):
    self.__headers = {"Authorization": f"Bearer {apiKey}", "Content-Type": "application/json" }
  
  def get(self, path):
    return requests.get(Client.API_BASE + path, headers=self.__headers).json()
  
  def post(self, path, data):
    return requests.post(Client.API_BASE + path, json=data, headers=self.__headers).json()

  def delete(self, path, data = None):
    return requests.delete(Client.API_BASE + path, json=data, headers=self.__headers)

NetlifyClient = Client(API_KEY)

# Get current IP
myIP = requests.get("https://api.ipify.org?format=json").json()["ip"]
print("Current IP: " + myIP)

# Get record IP
try:
  entry = next(filter(lambda x: x['hostname'] == HOSTNAME, NetlifyClient.get(f"{SITE_ID}/dns_records")))
  if entry["value"] != myIP:
    print("IP changed, updating record")
    NetlifyClient.delete(f"{SITE_ID}/dns_records/{entry['value']}")
  else:
    print("IP unchanged, exiting")
    sys.exit()
except Exception:
  print("No DNS record exists, creating record")

# Now add the record
NetlifyClient.post(f"{SITE_ID}/dns_records", {
  "hostname": HOSTNAME,
  "ttl": 3600,
  "type": "A",
  "value": myIP
})
print(f"A record added: {HOSTNAME} -> {myIP}")
