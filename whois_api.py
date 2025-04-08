from fastapi import FastAPI, Query
import whois

app = FastAPI()

@app.get("/whois")
async def get_whois(domain: str = Query(..., description="Domain name to perform WHOIS lookup")):
    try:
        result = whois.whois(domain)
        return result
    except Exception as e:
        return {"error": str(e)}