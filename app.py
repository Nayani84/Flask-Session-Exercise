from flask import Flask, request, render_template, redirect, flash, session, make_response
from flask_debugtoolbar import DebugToolbarExtension
from surveys import surveys

RESPONSES_KEY = "responses"
SURVEY_KEY = "current_survey"

app = Flask(__name__)
app.config["SECRET_KEY"] = "ABCDE"
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False

debug = DebugToolbarExtension(app)

@app.route("/")
def show_pick_survey_form():
    """Show pick-a-survey form."""

    return render_template("pick_survey.html", surveys=surveys)


@app.route("/" , methods=["POST"])
def pick_survey():
    """Select the survey"""

    survey_id = request.form['survey_code']
    if request.cookies.get(f"completed_{survey_id}"):
        return render_template("survey_done.html")
    
    survey = surveys[survey_id]
    session[SURVEY_KEY] = survey_id

    return render_template("sur_start.html" , survey=survey)


@app.route("/begin", methods=["POST"])
def start_survey():
    """clears the responses"""

    session[RESPONSES_KEY] = []
    return redirect("/questions/0")


@app.route("/answer" , methods=["POST"])
def handle_responses():
    """Save response and go to next question"""

    # get the choice that the user selects
    choice = request.form["answer"]
    text = request.form.get("text" , "")

    responses = session[RESPONSES_KEY]
    responses.append({"choice" : choice , "text" : text})
    session[RESPONSES_KEY] = responses

    survey_code = session[SURVEY_KEY]
    survey = surveys[survey_code]

    if len(responses) == len(survey.questions):
        return redirect("/complete")
    else:
        return redirect(f"/questions/{len(responses)}")
    

@app.route("/questions/<int:id>")
def show_question(id):
    """Display current question"""

    # get the responses session list
    responses = session.get(RESPONSES_KEY)
    survey_code = session[SURVEY_KEY]
    survey = surveys[survey_code]

    if responses is None:
        return redirect("/")
    
    if (len(responses) != id):
        flash(f"Invalid question id: {id}")
        return redirect(f"/questions/{len(responses)}")
    
    if (len(responses) == len(survey.questions)):
        return redirect("/complete")
    
    question = survey.questions[id]
    return render_template("question.html" , question=question , question_num=id)
    

@app.route("/complete")
def thank_survey():
    """Thank for completing the survey"""

    survey_id = session[SURVEY_KEY]
    survey = surveys[survey_id]
    responses = session[RESPONSES_KEY]


    html = render_template("complete.html" , survey=survey , responses=responses)

    response = make_response(html)
    response.set_cookie(f"completed_{survey_id}", "yes")
    return response