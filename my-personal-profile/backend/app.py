import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client

app = Flask(__name__)
# Crucial for allowing your frontend (e.g., Vercel) to talk to this Render backend
CORS(app) 

# --- Supabase Setup ---
# Ensure these keys are added to your Render Environment Variables dashboard
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("Error: SUPABASE_URL or SUPABASE_KEY not found in environment variables.")

supabase: Client = create_client(url, key)

# --- Routes ---

@app.route('/')
def home():
    """Root route to prevent 404 on deployment URL and verify health."""
    return jsonify({
        "status": "online",
        "message": "Guestbook API is running successfully",
        "endpoints": ["/guestbook"]
    }), 200

@app.route('/guestbook', methods=['GET'])
def get_entries():
    try:
        response = supabase.table("guestbook").select("*").order("created_at", desc=True).execute()
        return jsonify(response.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/guestbook', methods=['POST'])
def add_entry():
    try:
        data = request.json
        response = supabase.table("guestbook").insert(data).execute()
        return jsonify(response.data), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/guestbook/<id>', methods=['PUT'])
def update_entry(id):
    try:
        data = request.json
        response = supabase.table("guestbook").update(data).eq("id", id).execute()
        return jsonify(response.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/guestbook/<id>', methods=['DELETE'])
def delete_entry(id):
    try:
        supabase.table("guestbook").delete().eq("id", id).execute()
        return jsonify({"message": "Deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# --- Server Start ---
if __name__ == '__main__':
    # Use the PORT variable provided by Render, default to 5000 for local dev
    port = int(os.environ.get("PORT", 5000))
    # Must bind to 0.0.0.0 for Render to detect the port
    app.run(host='0.0.0.0', port=port)
