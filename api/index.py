from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Your JWT is hardcoded here as requested
JWT = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOiI1ODM4NTgzMzg4IiwianRpIjoiNjkzMGRhMjctOTBjNi00OTcyLTlkYjYtMjdhOTI2NzQxYjU5IiwiZXhwIjoxNzg1NDE1OTk0fQ.rZJMVGi-o-PmTH-GkpvOBowqrY_FflHVxRuW1-Ro27y2uNTiSwLXR0ohDoFXPcBdmwyyy70fjfUHU89By7_eVtpKZMH5hganj0PngE8r_ZxzvrmJApYlpKKjDP4SWPtNDLSFi30e9FOXUva1hihJxoGUUibTDAwX_vEM8fZQ_8E"

@app.route("/")
def home():
    return jsonify({
        "status": "online",
        "message": "API is running. Use /user-details?user=ID to fetch data."
    })

@app.route("/user-details")
def user_details():
    user_id = request.args.get("user")

    if not user_id:
        return jsonify({"success": False, "error": "Missing user ID parameter"}), 400

    url = f"https://funstat.info/api/v1/users/{user_id}/stats_min"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {JWT}"
    }

    try:
        # Added a timeout so the function doesn't hang forever
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return jsonify({"success": True, "data": response.json()})
        else:
            return jsonify({
                "success": False, 
                "error": "External API error", 
                "status_code": response.status_code,
                "details": response.text
            }), response.status_code
    
    except requests.exceptions.RequestException as e:
        return jsonify({"success": False, "error": f"Connection error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": f"Internal error: {str(e)}"}), 500

# DO NOT add app.run() here for Vercel
