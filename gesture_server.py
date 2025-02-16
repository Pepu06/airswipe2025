from flask import Flask, request, jsonify
import json
from tuya_connector import TuyaOpenAPI

app = Flask(__name__)

# Tuya IoT Platform credentials
ACCESS_ID = 'amtfgynh4weaypmkmpvf'
ACCESS_KEY = 'e99da483efd4487286feec129677b861'
DEVICE_ID = 'eb0ad63867a1eb1280t8hc'
API_ENDPOINT = 'https://openapi.tuyaus.com'

# Initialize Tuya API
openapi = TuyaOpenAPI(API_ENDPOINT, ACCESS_ID, ACCESS_KEY)
response = openapi.connect()

@app.route('/configurations', methods=['GET', 'POST'])
def handle_configurations():
    if request.method == 'POST':
        configurations = request.json
        print("Received configurations:", json.dumps(configurations, indent=2))
        with open('gesture_configurations.json', 'w') as f:
            json.dump(configurations, f)
        return jsonify({"status": "success"})
    else:
        try:
            with open('gesture_configurations.json', 'r') as f:
                configurations = json.load(f)
            return jsonify(configurations)
        except FileNotFoundError:
            return jsonify([])

@app.route('/execute_action', methods=['POST'])
def execute_action():
    try:
        gesture = request.json.get('gesture')
        if not gesture:
            return jsonify({"error": "No gesture provided"}), 400
            
        # Load configurations
        try:
            with open('gesture_configurations.json', 'r') as f:
                configurations = json.load(f)
        except FileNotFoundError:
            configurations = []
        
        # Find matching configuration
        for config in configurations:
            if config['gesture'].lower() == gesture.lower():
                # Execute action
                commands = {'commands': [{'code': 'switch_1', 'value': config['value']}]}
                response = openapi.post(f'/v1.0/iot-03/devices/{DEVICE_ID}/commands', commands)
                return jsonify({
                    "gesture": gesture,
                    "action": config['action'],
                    "status": "success"
                })
        
        return jsonify({
            "gesture": gesture,
            "status": "no_action_configured"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)