from flask import Flask, render_template, request, redirect
import firebase_admin
from firebase_admin import credentials, db
import os

# Initialize Flask
app = Flask(__name__)

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("novo-mentalhealth-firebase-adminsdk-fbsvc-278a6922df.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://novo-mentalhealth-default-rtdb.firebaseio.com/'
    })

# Questions
questions_common = [
    ("I often feel anxious about the future, like grades or my career.", ["Stress", "Anxiety"]),
    ("I feel like I'm not good enough, no matter how hard I try.", ["Depression", "Anxiety"]),
    ("I find it hard to focus on schoolwork because of constant worrying or sadness.", ["Depression", "Anxiety"]),
    ("I feel overwhelmed by deadlines, tests, or homework.", ["Stress", "Anxiety"]),
    ("I feel like I have too many responsibilities and not enough time to relax.", ["Stress", "Depression"]),
    ("I've lost interest in things I used to enjoy, like sports or hobbies.", ["Depression", "Stress"]),
    ("I often feel like something bad is about to happen, even when things are okay.", ["Anxiety", "Depression"]),
    ("I feel isolated even when I'm around people.", ["Depression", "Anxiety"]),
    ("I sometimes feel like I don't belong at school or even at home.", ["Depression", "Anxiety"]),
]

questions_girl = [
    ("I feel confused or uncomfortable with the physical changes during puberty.", ["Anxiety", "Depression"]),
    ("I often prefer staying indoors and avoiding going out, even with friends.", ["Depression", "Anxiety"]),
    ("During exams, I struggle to remember things I studied well.", ["Stress", "Anxiety"]),
    ("I feel tired and just want to rest, but there's never enough time.", ["Stress", "Depression"]),
    ("I don't feel like eating much, but I'm okay with just fruits or light snacks.", ["Depression", "Anxiety"]),
    ("Sometimes I question if all this studying and stress is even worth it.", ["Depression", "Anxiety"]),
    ("I feel extra pressure to “look good” or act a certain way because I'm a girl.", ["Anxiety", "Stress"]),
    ("I avoid talking to teachers or classmates due to fear of being judged or misunderstood.", ["Anxiety", "Depression"]),
    ("I feel like people expect me to be emotionally strong all the time, even when I'm not okay.", ["Depression", "Anxiety"]),
]

questions_boy = [
    ("I feel like I can't show emotions because it's seen as weak.", ["Anxiety", "Depression"]),
    ("I'm expected to be strong or competitive all the time, and it's exhausting.", ["Stress", "Depression"]),
    ("I often hide my stress because I don't want others to think I can't handle things.", ["Anxiety", "Stress"]),
    ("I get angry or frustrated easily, even over small things.", ["Stress", "Anxiety"]),
    ("I avoid asking for help because I think I should figure it out myself.", ["Anxiety", "Depression"]),
    ("I sometimes feel like no one really understands what I'm going through.", ["Depression", "Anxiety"]),
    ("I worry that my performance in school defines my value.", ["Stress", "Depression"]),
    ("I feel pressure to succeed, especially in sports or other 'masculine' areas.", ["Anxiety", "Stress"]),
    ("I act like everything is fine even when I'm struggling inside.", ["Depression", "Anxiety"]),
]

score_values = [3, 2, 1, 0, -1, -2, -3]

# Routes
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        name = request.form.get("name")
        gender = request.form.get("gender")
        responses = {}

        # Collect responses
        for key in request.form.keys():
            if key.startswith("q_"):
                responses[key] = int(request.form[key])

        # Save to Firebase
        data = {
            "name": name,
            "gender": gender,
            **responses
        }
        ref = db.reference('/responses')
        ref.push(data)

        # Calculate scores
        questions = questions_common + (questions_girl if gender == "Girl" else questions_boy if gender == "Boy" else [])
        scores = {"Depression": 0, "Anxiety": 0, "Stress": 0}

        for idx, (_, categories) in enumerate(questions):
            key = f"q_{idx}"
            if key in responses:
                score = score_values[responses[key]]
                for cat in categories:
                    scores[cat] += score

        # Interpret results
        results = {}
        for cat, score in scores.items():
            results[cat] = interpret_risk(score, cat)

        return render_template("results.html", name=name, scores=scores, results=results)

    return render_template("form.html")


def interpret_risk(score, category):
    if category == "Depression":
        if score < -12:
            return "Low"
        elif score < 6:
            return "Moderate"
        else:
            return "High"
    elif category == "Anxiety":
        if score < -10:
            return "Low"
        elif score < 8:
            return "Moderate"
        else:
            return "High"
    elif category == "Stress":
        if score < -8:
            return "Low"
        elif score < 8:
            return "Moderate"
        else:
            return "High"

if __name__ == "__main__":
    app.run(debug=True)
