from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import os

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to Number Info API",
        "usage": "/info?number=PHONE_NUMBER"
    })

@app.route('/info', methods=['GET'])
def number_info():
    phone_number = request.args.get('number')
    if not phone_number:
        return jsonify({"error": "Please provide ?number= parameter"}), 400

    if not phone_number.isdigit() and not (phone_number.startswith('+') and phone_number[1:].isdigit()):
        return jsonify({"error": "Invalid phone number format"}), 400

    try:
        url = "https://calltracer.in"
        headers = {
            "Host": "calltracer.in",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://calltracer.in",
            "Referer": "https://calltracer.in/"
        }
        payload = {
            "country": "IN",
            "q": phone_number
        }

        session = requests.Session()
        session.get(url, headers=headers, timeout=10) 
        response = session.post(url, headers=headers, data=payload, timeout=15)

        if response.status_code != 200:
            return jsonify({"error": f"Failed to fetch data. HTTP {response.status_code}"}), 500

        soup = BeautifulSoup(response.text, 'html.parser')

        def get_value(label):
            cell = soup.find(string=lambda t: t and label.lower() in t.lower())
            if cell:
                tr = cell.find_parent("tr")
                if tr and tr.find_all("td"):
                    tds = tr.find_all("td")
                    if len(tds) > 1:
                        return tds[1].get_text(strip=True)
            return "N/A"

        data = {
            "Number": phone_number,
            "Complaints": get_value("Complaints"),
            "Owner Name": get_value("Owner Name"),
            "Alternative Number": get_value("Alternative Number"),
            "SIM Card": get_value("SIM card"),
            "Mobile State": get_value("Mobile State"),
            "IMEI Number": get_value("IMEI number"),
            "MAC Address": get_value("MAC address"),
            "Connection": get_value("Connection"),
            "IP Address": get_value("IP address"),
            "Owner Address": get_value("Owner Address"),
            "Hometown": get_value("Hometown"),
            "Reference City": get_value("Refrence City"),
            "Owner Personality": get_value("Owner Personality"),
            "Language": get_value("Language"),
            "Mobile Locations": get_value("Mobile Locations"),
            "Country": get_value("Country"),
            "Tracking History": get_value("Tracking History"),
            "Tracker ID": get_value("Tracker Id"),
            "Tower Locations": get_value("Tower Locations"),
        }

        if all(v == "N/A" for v in data.values()):
            return jsonify({"error": "No data found for this number."}), 404

        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Required for local testing, but Vercel will ignore this
if __name__ == '__main__':
    app.run(debug=True)
