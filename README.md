# itu-sgmyo-virtualization-2025
itu-sgmyo-virtualization-2025

# Running the application
```bash
pip3 install -r requirements.txt && python3 -m uvicorn main:app --reload --port 8002
```

Then go to `localhost:8000/docs` for swagger endpoint.

You will need to make api request for the tests. 

Example test:
```bash
curl "http://localhost:8002/dns-lookup?fqdn=google.com"
```
