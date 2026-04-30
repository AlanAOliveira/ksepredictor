from http.client import HTTPException
from flask import Flask, render_template, request
import logging
import os
from pydantic import BaseModel
import dataFunctions

class KseRequest(BaseModel):
    partnumber: str
    ordernumber: str


# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)


app = Flask(__name__)

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering index.html: {e}")
        return "Index file not found", 404

@app.route('/geto')
def geto():
    return {"getok":100}

@app.route("/api/iek", methods=['POST'])
async def get_iek_data():
    kse_request = request.get_json()
    try:
        return dataFunctions.findNextOrderLane(kse_request['partnumber'], kse_request['ordernumber'])
    except Exception as e:
        logger.error(f"Error fetching IEK data: {e}")
        return {'error': 'Error fetching IEK data'}, 500

@app.route("/api/send-kse", methods=['POST'])
async def send_kse():
    kse_request = request.get_json()
    try:
        response = dataFunctions.sendKSEtoExcel(
            partNumber=kse_request['partnumber'],
            OrderLane=kse_request['ordernumber'],
        )
        logger.info(f"KSE data sent successfully: {response}")
        return {"status": "success", "response": response}
    except Exception as e:
        logger.error(f"Error sending KSE data: {e}")
        return {'error': "Error sending KSE data"}, 500


if __name__ == '__main__':
    host = os.getenv('FLASK_RUN_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_RUN_PORT', 8000))

    app.run(debug=True, host=host, port=port)
    logger.info(f"Flask app running on http://{host}:{port}")



