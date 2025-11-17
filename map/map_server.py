from flask import Flask, render_template, request, jsonify
import location_store
import os

app = Flask(__name__)

# Flask app hiển thị và cập nhật bản đồ vị trí xe vi phạm
@app.route("/")
def index():
    return render_template("map.html")

@app.route("/save_location", methods=["POST"])
def save_location():
    data = request.get_json()  # Ensure `get_json` is correctly used
    lat = data.get("lat")
    lon = data.get("lon")

    location_store.set_location(lat, lon)

    return jsonify({"status": "ok", "lat": lat, "lon": lon})

@app.route("/get_location", methods=["GET"])
def get_location():
    lat, lon = location_store.get_location()
    if lat is not None and lon is not None:
        return jsonify({"lat": lat, "lon": lon})
    else:
        return jsonify({"error": "No location found"}), 404

def start_server():
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    app.template_folder = template_dir
    print("Đang khởi động server Flask trên cổng 5001...")
    try:
        app.run(port=5001)
    except Exception as e:
        print(f"Lỗi khi khởi động server: {e}")
