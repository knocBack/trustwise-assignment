from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy

from datetime import datetime
import json
import threading
from huggingface_models import predict_vectara, predict_education, predict_gibberish, predict_emotion, predict_toxicity
import threading
from queue import Queue




app = Flask(__name__, template_folder='/app')
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:password@db:3306/trustwise"
db = SQLAlchemy(app)

class RequestLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.String(100), nullable=True)
    timestamp = db.Column(db.DateTime, nullable=True)
    device_id = db.Column(db.String(100), nullable=True)
    input_string = db.Column(db.String(1000), nullable=False)
    vectara_score = db.Column(db.Float, nullable=True)
    toxicity_score = db.Column(db.Float, nullable=True)
    emotion_score = db.Column(db.Text, nullable=True) 
    gibberish_score = db.Column(db.Text, nullable=True) 
    education_score = db.Column(db.Float, nullable=True)


def predict_scores(text):
    scores = {}
    queue = Queue()

    def worker(func, text):
        queue.put((func.__name__, func(text)))

    threads = [
        threading.Thread(target=worker, args=(predict_vectara, text)),
        threading.Thread(target=worker, args=(predict_toxicity, text)),
        threading.Thread(target=worker, args=(predict_emotion, text)),
        threading.Thread(target=worker, args=(predict_gibberish, text)),
        threading.Thread(target=worker, args=(predict_education, text)),
    ]

    for thread in threads:
        thread.start()

    for _ in range(len(threads)):
        key, value = queue.get()
        scores[key.replace("predict_","")] = value

    return scores

# THREADS = {"vectara": None, "toxicity": None, "emotion": None, "gibberish": None, "education": None}

# def predict_scores(text):
#     score_names = ["vectara", "toxicity", "emotion", "gibberish", "education"]
#     predict_funcs = [predict_vectara, predict_toxicity, predict_emotion, predict_gibberish, predict_education]

#     for score_name, predict_func in zip(score_names, predict_funcs):
#         THREADS[score_name] = threading.Thread(target=predict_func, args=(text,))
#         THREADS[score_name].start()
    
#     for score_name in score_names:
#         THREADS[score_name].join()

#     scores = {
#         "vectara": predict_vectara(text),
#         "toxicity": predict_toxicity(text),
#         "emotion": predict_emotion(text),
#         "gibberish": predict_gibberish(text),
#         "education": predict_education(text),
#     }
#     return scores

# def predict_scores(text):
#     scores = {
#         "vectara": predict_vectara(text),
#         "toxicity": predict_toxicity(text),
#         "emotion": predict_emotion(text),
#         "gibberish": predict_gibberish(text),
#         "education": predict_education(text),
#     }
#     return scores

@app.route("/scores", methods=["POST"])
def create_score():
    data = request.get_json()
    text = data.get('text', '')
    scores = predict_scores(text)
    log = RequestLog(
        request_id=request.headers.get("X-Request-ID", "NA"),
        timestamp=datetime.now(),
        device_id=request.headers.get("X-Device-ID", "NA"),
        input_string=text,
        vectara_score=scores.get("vectara", None),
        toxicity_score=scores.get("toxicity", None),
        emotion_score=json.dumps(scores.get("emotion", {})),
        gibberish_score=json.dumps(scores.get("gibberish", {})),
        education_score=scores.get("education", None),
    )
    db.session.add(log)
    db.session.commit()
    return jsonify({
        "message": "Scores predicted and logged successfully", 
        "scores": scores,
        "log_id": log.id,
    }), 201

@app.route("/scores", methods=["GET"])
def get_all_scores():
    logs = RequestLog.query.all()
    logs_data = [
        {
            "id": log.id,
            "request_id": log.request_id,
            "input_string": log.input_string,
            "vectara_score": log.vectara_score,
            "toxicity_score": log.toxicity_score,
            "emotion_score": json.loads(log.emotion_score),
            "gibberish_score": json.loads(log.gibberish_score),
            "education_score": log.education_score,
            "timestamp": log.timestamp,
        } for log in logs
    ]
    return jsonify({"message": "All scores fetched successfully", "logs": logs_data})

@app.route("/scores/<int:score_id>", methods=["GET"])
def get_score(score_id):
    log = RequestLog.query.get(score_id)
    if log is None:
        return jsonify({"message": "Score not found"}), 404
    log_data = {
        "id": log.id,
        "request_id": log.request_id,
        "input_string": log.input_string,
        "vectara_score": log.vectara_score,
        "toxicity_score": log.toxicity_score,
        "emotion_score": json.loads(log.emotion_score),
        "gibberish_score": json.loads(log.gibberish_score),
        "education_score": log.education_score,
    }
    return jsonify({"message": "Score fetched successfully", "log": log_data})

@app.route("/scores/<int:score_id>", methods=["DELETE"])
def delete_score(score_id):
    log = RequestLog.query.get(score_id)
    if log is None:
        return jsonify({"message": "Score not found"}), 404
    db.session.delete(log)
    db.session.commit()
    return jsonify({"message": "Score deleted successfully"})

@app.route("/")
def index():
    return render_template("./static/index.html")

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.errorhandler(Exception)
def handle_internal_server_error(e):
    return jsonify({"message": "Internal Server Error"}), 500

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)