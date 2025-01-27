from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from huggingface_models import predict_vectara, predict_education, predict_gibberish, predict_emotion, predict_toxicity

app = Flask(__name__, template_folder='/app')
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:password@db:3306/trustwise"
db = SQLAlchemy(app)

class RequestLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.String(100), nullable=True)
    timestamp = db.Column(db.DateTime, nullable=True)
    device_id = db.Column(db.String(100), nullable=True)
    input_string = db.Column(db.String(1000), nullable=False)
    score_1 = db.Column(db.Float, nullable=False)
    score_2 = db.Column(db.Float, nullable=False)
    score_3 = db.Column(db.Float, nullable=False)
    score_4 = db.Column(db.Float, nullable=False)
    score_5 = db.Column(db.Float, nullable=False)

@app.route("/log-request", methods=["POST"])
def log_request():
    data = request.get_json()
    log = RequestLog(
        request_id=request.headers.get("X-Request-ID", "NA"),
        timestamp=datetime.now(),
        device_id=request.headers.get("X-Device-ID", "NA"),
        input_string=data.get("input_string", ""),
        score_1=data.get("score_1", 0.0),
        score_2=data.get("score_2", 0.0),
        score_3=data.get("score_3", 0.0),
        score_4=data.get("score_4", 0.0),
        score_5=data.get("score_5", 0.0),
    )
    db.session.add(log)
    db.session.commit()
    
    logs = RequestLog.query.all()
    logs_data = [{"id": log.id, "request_id": log.request_id, "input_string": log.input_string} for log in logs]

    return jsonify({"message": "Request logged successfully", "all": logs_data})

@app.route("/")
def index():
    return render_template("index.html")

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)