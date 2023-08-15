from flask import Flask, redirect, render_template, request, session, make_response
from flask_debugtoolbar import DebugToolbarExtension
from surveys import surveys as survey

app = Flask(__name__)
app.config['SECRET_KEY'] = "1234"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

RESPONSE  = "responses"
SURVEY_ID = "surveykey"
COMMENTS = "comments"

@app.route('/')
def _home():
    return render_template('home.html', surveys=survey)


@app.route('/', methods=["POST"])
def start_question():
    
    survey_key = request.form["survey_key"]
    if request.cookies.get(f"finished {survey_key}") == "True":
        return render_template('already_completed.html')
    survey_to_take = survey[survey_key]
    session[SURVEY_ID] = survey_key
    
    return render_template('pick_survey.html', survey=survey_to_take)

@app.route('/reset')
def reset_survey():
    # survey_key = session[SURVEY_ID]
    # request.cookies.pop(f"finished {survey_key}")
    # response = make_response('cookies cleared')
    # response.set_cookie(f'finished {survey_key}', "False")
    survey_key = session[SURVEY_ID]
        
    # Create a response
    response = make_response(redirect('/'))
    
    # Clear the "finished" cookie by setting its value to an empty string and expiration to a past date
    response.set_cookie(f'finished {survey_key}', '')
    
    return response

@app.route('/begin', methods=["POST"])
def begin():
    session[RESPONSE] = []
    return redirect('/question/0')


@app.route('/question/<int:qid>')
def show_question(qid):

    survey_key = session[SURVEY_ID]
    
    len_response = len(session[RESPONSE])

    if len_response is None:
        return redirect('/')
    if len(survey[survey_key].questions) == len_response:
        return redirect('/complete')
    if len_response != qid:
        return redirect(f"/question/{len_response}")
    question = survey[survey_key].questions[qid]

    return render_template('question.html', question=question)

   

@app.route('/answer', methods=["POST"])
def handle_answer():
    answer = request.form["answer"]
    user_comment= request.form.get("user_comment", "")
    
    # This is how session append its list
    answers = session[RESPONSE]
    answers.append({"answer": answer ,"comment": user_comment})
    session[RESPONSE]= answers
    # if len(responses_list["cur_sur_ans"]) >= len(survey.questions):
    #     responses_list.clear()
    #     return redirect('/complete')
    # else:
    return redirect(f'/question/{len(session[RESPONSE])}')


@app.route('/complete')
def end_survey():
    
    survey_key = session[SURVEY_ID]
    survey_to_take = survey[survey_key]
    responses = session[RESPONSE]
    
    html = render_template("complete.html", survey = survey_to_take, responses = responses)
    
    res = make_response(html)
    res.set_cookie(f"finished {survey_key}", "True")
    return res