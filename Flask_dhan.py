from flask import Flask, request, jsonify
import json 
import os 

pipe_path  = "/tmp/jsonpipe"
app = Flask(__name__)


def send_json_data(data):
    if data is None: 
        return None 
    else: 
        with open(pipe_path,"w") as pipe:
            pipe.write(data)
            pipe.flush()

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if data is None:
        return jsonify({'error': 'Invalid JSON data'}), 400
    send_json_data(json.dumps(data)) # sending the received data into string format 
    print("Received JSON data:", data)
    return jsonify({'message': 'Received JSON data successfully.'}), 200

if __name__ == '__main__':
    os.mkfifo(pipe_path) if not os.path.exists(pipe_path) else None
    app.run(port=8000)