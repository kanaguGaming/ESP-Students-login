from flask import Flask, request, jsonify, send_from_directory
import json
import os
import redis

app = Flask(__name__)

# Vercel KV Setup (Environment Variables mulama automatic-a connect aagum)
# Local testing-kku venumna unga Redis URL a hardcode pannikalam, aana Vercel la automatic a eduthukkum.
redis_url = os.getenv('KV_URL', 'redis://localhost:6379')
r = redis.Redis.from_url(redis_url, decode_responses=True)

# 1. PUDHU ROUTE: Data-va feed pandrathukku (POST request)
@app.route('/api/feed_data', methods=['POST'])
def feed_data():
    try:
        data = request.json
        exam_date = data.get("exam_date")
        
        if not exam_date:
            return jsonify({"error": "JSON-la 'exam_date' missing"}), 400
        
        redis_key = f"exam_data_{exam_date}"
        
        # Redis-la save pandrom. 'ex=86400' na exactly 24 hours (86400 seconds) la auto-delete aagidum.
        r.set(redis_key, json.dumps(data), ex=86400)
        
        return jsonify({"status": "success", "message": f"{exam_date} thethikkana data save aagivittathu. 24 mani nerathil azhinthu vidum."})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 2. EXISTING ROUTE: Students data check pandrathukku (GET request)
@app.route('/api/get_seat', methods=['GET'])
def get_seat():
    roll_no = request.args.get('roll')
    if not roll_no:
        return jsonify({"status": "error", "message": "Roll Number enter pannunga."})

    input_roll = str(roll_no).strip()
    student_exams = []
    student_profile = None

    try:
        # Redis-la irukka ella data-vaiyum edukkurom (Multiple JSONs)
        keys = r.keys("exam_data_*")
        
        if not keys:
            return jsonify({"status": "error", "message": "Server-la ippothaikku entha Exam Data-vum illai (allathu) palaiya data azhindhu vittathu."})

        for key in keys:
            feed_str = r.get(key)
            if feed_str:
                feed = json.loads(feed_str)
                students_list = feed.get("students", [])
                
                # Andha roll number kku math aagudha nu check pandrom
                for student in students_list:
                    if str(student.get('reg_number')).strip() == input_roll:
                        student_exams.append(student)
                        if not student_profile:
                            student_profile = {
                                "name": student.get("name", "N/A"),
                                "roll": student.get("reg_number", "N/A"),
                                "dept": student.get("department", "N/A"),
                                "batch": student.get("batch", "N/A"),
                                "gender": student.get("gender", "N/A")
                            }

        if len(student_exams) > 0:
            return jsonify({
                "status": "success",
                "student": student_profile,
                "exams": student_exams
            })
        else:
            return jsonify({"status": "error", "message": "Indha Roll Number-kku entha Exam data-vum kidaikavillai."})

    except Exception as e:
        print("Redis Error:", e)
        return jsonify({"status": "error", "message": "Database connection error."})

# --- FRONTEND LOAD PANDRA ROUTES ---
@app.route('/')
def serve_index():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    return send_from_directory(os.path.join(base_dir, 'public'), 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    base_dir = os.path.dirname(os.path.dirname(__file__))
    return send_from_directory(os.path.join(base_dir, 'public'), filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)