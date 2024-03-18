from flask import Flask, request, jsonify
from flasgger import Swagger
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)
swagger = Swagger(app)

# MongoDB connection
mongo_uri = os.getenv("MONGO_URI")
mongo_conn = MongoClient(mongo_uri)

# Specify the database and collection in MongoDB
mongo_db = mongo_conn.get_database('march_db')  
collection = mongo_db['march_table']

@app.route('/search', methods=['POST'])
def search_mongodb():
    """
    Endpoint to search MongoDB collection based on query and path.
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            query:
              type: string
              description: The search query.
            path:
              type: string
              description: The path where to search for the query.
    responses:
      200:
        description: Search results
      400:
        description: Bad request
    """
    try:
        request_data = request.get_json()

        query = request_data.get('query')
        path = request_data.get('path')

        if not query or not path:
            return jsonify({'error': 'Both query and path must be provided'}), 400

        result = collection.aggregate([
            {
                '$search': {
                    'index': 'march15',
                    'text': {
                        'query': query,
                        'path': path
                    }
                }
            }
        ])

        # Convert ObjectId to string representation for JSON serialization
        result_list = [{**item, '_id': str(item['_id'])} for item in result]

        return jsonify(result_list)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
