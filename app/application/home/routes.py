import simplejson as json
from flask import request, Response, redirect, make_response, url_for
from flask import current_app as app
from flask import render_template
from app.application import mysql
from app.application.home.forms import ContactForm
from flask import Blueprint
from datetime import datetime as dt
from flask import current_app as app
from .models import db, User

@app.route('/', methods=['GET'])
def user_records():
    """Create a user via query string parameters."""
    username = request.args.get('user')
    email = request.args.get('email')
    if username and email:
        existing_user = User.query.filter(
            User.username == username or User.email == email
        ).first()
        if existing_user:
            return make_response(
                f'{username} ({email}) already created!'
            )
        new_user = User(
            username=username,
            email=email,
            created=dt.now(),
            bio="In West Philadelphia born and raised, \
            on the playground is where I spent most of my days",
            admin=False
        )  # Create an instance of the User class
        db.session.add(new_user)  # Adds new User record to database
        db.session.commit()  # Commits all changes
        redirect(url_for('user_records'))
    return render_template(
        'users.jinja2',
        users=User.query.all(),
        title="Show Users"
    )
@app.route('/', methods=['GET'])
def create_user():
    """Create a user."""
    ...
    return render_template(
        'users.jinja2',
        users=User.query.all(),
        title="Show Users"
    )

main_bp = Blueprint(
    'main_bp', __name__,
    template_folder='templates'

@main_bp.route('/', methods=['GET'])
def index():
    user = {'username': "MLB Project"}
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM mlbteamsTbl')
    result = cursor.fetchall()
    return render_template('index.html', title='Home', user=user, teams=result)


@main_bp.route('/view/<int:team_id>', methods=['GET'])
def record_view(team_id):
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM mlbteamsTbl WHERE id=%s', team_id)
    result = cursor.fetchall()
    return render_template('view.html', title='View Form', team=result[0])


@main_bp.route('/edit/<int:team_id>', methods=['GET'])
def form_edit_get(team_id):
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM mlbteamsTbl WHERE id=%s', team_id)
    result = cursor.fetchall()
    return render_template('edit.html', title='Edit Form', team=result[0])


@main_bp.route('/edit/<int:team_id>', methods=['POST'])
def form_update_post(team_id):
    cursor = mysql.get_db().cursor()
    inputData = (request.form.get('Team'), request.form.get('Payroll_millions'), request.form.get('Wins'),team_id)
    sql_update_query = """UPDATE mlbteamsTbl t SET t.Team = %s, t.Payroll_millions = %s, t.Wins = %s WHERE t.id = %s """
    cursor.execute(sql_update_query, inputData)
    mysql.get_db().commit()
    return redirect("/", code=302)

@main_bp.route('/teams/new', methods=['GET'])
def form_insert_get():
    return render_template('new.html', title='New Team Form')


@main_bp.route('/teams/new', methods=['POST'])
def form_insert_post():
    cursor = mysql.get_db().cursor()
    inputData = (request.form.get('Team'), request.form.get('Payroll_millions'), request.form.get('Wins'))
    sql_insert_query = """INSERT INTO mlbteamsTbl (Team,Payroll_millions,Wins) VALUES (%s, %s,%s) """
    cursor.execute(sql_insert_query, inputData)
    mysql.get_db().commit()
    return redirect("/", code=302)

@main_bp.route('/delete/<int:team_id>', methods=['POST'])
def form_delete_post(team_id):
    cursor = mysql.get_db().cursor()
    sql_delete_query = """DELETE FROM mlbteamsTbl WHERE id = %s """
    cursor.execute(sql_delete_query, team_id)
    mysql.get_db().commit()
    return redirect("/", code=302)


@main_bp.route('/api/v1/teams', methods=['GET'])
def api_browse() -> str:
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM mlbteamsTbl')
    result = cursor.fetchall()
    json_result = json.dumps(result);
    resp = Response(json_result, status=200, mimetype='application/json')
    return resp


@main_bp.route('/api/v1/teams/<int:team_id>', methods=['GET'])
def api_retrieve(team_id) -> str:
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM mlbteamsTbl WHERE id=%s', team_id)
    result = cursor.fetchall()
    json_result = json.dumps(result);
    resp = Response(json_result, status=200, mimetype='application/json')
    return resp

@main_bp.route('/api/v1/teams/<int:team_id>', methods=['PUT'])
def api_edit(team_id) -> str:
    cursor = mysql.get_db().cursor()
    content = request.json
    inputData = (content['Team'], content['Payroll_millions'], content['Wins'],team_id)
    sql_update_query = """UPDATE mlbteamsTbl t SET t.Team = %s, t.Payroll_millions = %s, t.Wins = %s WHERE t.id = %s """
    cursor.execute(sql_update_query, inputData)
    mysql.get_db().commit()
    resp = Response(status=200, mimetype='application/json')
    return resp

@main_bp.route('/api/v1/teams/', methods=['POST'])
def api_add() -> str:

    content = request.json

    cursor = mysql.get_db().cursor()
    inputData = (content['Team'], content['Payroll_millions'], content['Wins'],)
    sql_insert_query = """INSERT INTO mlbteamsTbl (Team,Payroll_millions,Wins) VALUES (%s, %s,%s) """
    cursor.execute(sql_insert_query, inputData)
    mysql.get_db().commit()
    resp = Response(status=201, mimetype='application/json')
    return resp

@main_bp.route('/api/v1/teams/<int:team_id>', methods=['DELETE'])
def api_delete(team_id) -> str:
    cursor = mysql.get_db().cursor()
    sql_delete_query = """DELETE FROM mlbteamsTbl WHERE id = %s """
    cursor.execute(sql_delete_query, team_id)
    mysql.get_db().commit()
    resp = Response(status=200, mimetype='application/json')
    return resp

@main_bp.errorhandler(404)
def not_found():
    """Page not found."""
    return make_response(
        'SORRY. THIS PAGE IS NOT FOUND.',
        404
     )

@main_bp.errorhandler(400)
def bad_request():
    """Bad request."""
    return make_response(
        'BAD REQUEST! THIS SERVER DOES NOT SUPPORT YOUR REQUEST.',
        400
    )

@main_bp.errorhandler(500)
def server_error():
    """Internal server error."""
    return make_response(
        'INTERNAL SERVER ERROR.',
        500
    )
