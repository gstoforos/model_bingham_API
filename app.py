from flask import Flask, request, jsonify
from model_bingham import fit_bingham

app = Flask(__name__)

@app.route("/fit", methods=["POST"])
def fit():
    try:
        data = request.get_json(force=True)
        result = fit_bingham(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

