from flask import Flask, request, jsonify
import ssl
import socket
from datetime import datetime

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

@app.route("/ssl-lookup", methods=["GET"])
def ssl_lookup():
    domain = request.args.get("domain", "")
    if not domain:
        return jsonify({"error": "Please provide a domain parameter"}), 400
    try:
        cert_info = get_ssl_info(domain)
        return jsonify(cert_info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5050)
