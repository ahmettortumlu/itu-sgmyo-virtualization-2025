# While running application:  
# export S3_BUCKET=my-ssl-bucket
# python ssl_lookup_api.py


import os
import ssl
import socket
import boto3
import json
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

def get_ssl_info(hostname: str, port: int = 443):
    context = ssl.create_default_context()
    with socket.create_connection((hostname, port), timeout=5) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            cert = ssock.getpeercert()
            return {
                "subject": dict(x[0] for x in cert.get("subject", [])),
                "issuer": dict(x[0] for x in cert.get("issuer", [])),
                "notBefore": cert.get("notBefore"),
                "notAfter": cert.get("notAfter"),
                "expired": datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z") < datetime.utcnow()
            }

def upload_to_s3(bucket_name: str, key: str, data: dict):
    s3 = boto3.client("s3")
    s3.put_object(
        Bucket=bucket_name,
        Key=key,
        Body=json.dumps(data),
        ContentType="application/json"
    )

@app.route("/ssl-lookup", methods=["GET"])
def ssl_lookup():
    domain = request.args.get("domain", "")
    if not domain:
        return jsonify({"error": "Please provide a domain parameter"}), 400

    bucket_name = os.getenv("S3_BUCKET")
    if not bucket_name:
        return jsonify({"error": "S3_BUCKET environment variable not set"}), 500

    try:
        cert_info = get_ssl_info(domain)
        s3_key = f"{domain}.json"
        upload_to_s3(bucket_name, s3_key, cert_info)
        return jsonify({
            "message": f"SSL info uploaded to s3://{bucket_name}/{s3_key}",
            "data": cert_info
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5050)
