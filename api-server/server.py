from flask import Flask, request, jsonify
import os
import sys
from flask_cors import CORS
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data_query_system.query import query_studies 

app = Flask(__name__)
CORS(app)


@app.route('/search', methods=['POST'])
def search_studies():
    data = request.json
    user_query = data.get('query', '')
    limit = data.get('limit', 3)

    if not user_query:
        return jsonify({"error": "No query provided"}), 400

    try:
        results = query_studies(user_query, limit)
        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Running on port 5001 to avoid common macOS AirPlay conflicts on 5000
    app.run(debug=True, port=5001)