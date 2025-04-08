from fastapi import FastAPI, Query
from pydantic import BaseModel
import socket
import dns.resolver
from typing import List, Optional

app = FastAPI()

class DNSRecord(BaseModel):
    type: str
    value: str
    ttl: Optional[int] = None

class DNSInfo(BaseModel):
    fqdn: str
    ip_address: str
    records: List[DNSRecord]

@app.get("/dns-lookup", response_model=DNSInfo)
async def dns_lookup(
    fqdn: str = Query(..., description="Fully Qualified Domain Name (e.g., example.com)"),
    record_types: str = Query("A,MX,TXT,NS", description="Comma-separated list of DNS record types to query")
):
    try:
        # Get IP address
        ip_address = socket.gethostbyname(fqdn)
        
        # Initialize DNS resolver
        resolver = dns.resolver.Resolver()
        
        # Parse record types
        types = [t.strip().upper() for t in record_types.split(",")]
        
        # Collect DNS records
        records = []
        
        for record_type in types:
            try:
                answers = resolver.resolve(fqdn, record_type)
                for rdata in answers:
                    records.append(DNSRecord(
                        type=record_type,
                        value=str(rdata),
                        ttl=rdata.ttl if hasattr(rdata, 'ttl') else None
                    ))
            except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
                continue
            except Exception as e:
                records.append(DNSRecord(
                    type=record_type,
                    value=f"Error: {str(e)}",
                    ttl=None
                ))
        
        return DNSInfo(
            fqdn=fqdn,
            ip_address=ip_address,
            records=records
        )
    except socket.gaierror:
        return {"error": "Invalid domain or unable to resolve."}
    except Exception as e:
        return {"error": str(e)}
