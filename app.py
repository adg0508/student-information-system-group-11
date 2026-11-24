"""CMPE341 Student Information System: PostgreSQL insert, update and delete."""
import os
import secrets
from pathlib import Path

import click
import psycopg
from psycopg import sql
from psycopg.rows import dict_row
from werkzeug.security import check_password_hash
from flask import session, Flask, abort, redirect, render_template, request, url_for

app = Flask(__name__)


app.secret_key = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# These two accounts are for the public course demonstration.
ACCOUNTS = {
    'admin': ('admin', 'scrypt:32768:8:1$ayAdDFjlbnaGRpCH$5959ef0a8bf66b716fad92011992c40f780a542ca4ec0c24df55e36f255a8ba5c4b76a44c9bd79ae91370cd33c5e33d1f6b86301f49be03d0269643d968f5026'),
    'reader': ('reader', 'scrypt:32768:8:1$AQ875Bs3xuuHqbKf$7a6bccad3b01f1e65b389533f3cc8e376f781ea7658a3ccbd80b3486300e7b78fe2c8b8eb4528dca318e7e83cec9e5781d6afa59424d2cb718e3ec85379d5a8b'),
}


@app.before_request
def protect_forms():
    if request.method == 'POST':
        token = request.form.get('csrf', '')
        if not token or not secrets.compare_digest(session.get('csrf', ''), token):
            abort(403)
    if 'csrf' not in session:
        session['csrf'] = secrets.token_urlsafe(24)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        account = ACCOUNTS.get(username)
        if account and check_password_hash(account[1], request.form.get('password', '')):
            session.clear()
            session.update(username=username, csrf=secrets.token_urlsafe(24))
            return redirect(url_for('index'), code=303)
        error = 'Incorrect username or password.'
    return render_template('login.html', error=error), 401 if error else 200


@app.post('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'), code=303)


# Field: database column, visible label, input type, optional foreign table.
TABLES = {
    'department': ('Departments', 'department_id', [
        ('code', 'Code', 'text', None), ('name', 'Name', 'text', None)]),
    'student': ('Students', 'student_id', [
        ('student_no', 'Student number', 'text', None),
        ('first_name', 'First name', 'text', None),
        ('last_name', 'Last name', 'text', None),
        ('email', 'Email', 'email', None),
        ('department_id', 'Department', 'number', 'department')]),
    'instructor': ('Instructors', 'instructor_id', [
        ('staff_no', 'Staff number', 'text', None),
        ('first_name', 'First name', 'text', None),
        ('last_name', 'Last name', 'text', None),
        ('email', 'Email', 'email', None),
        ('department_id', 'Department', 'number', 'department')]),
    'course': ('Courses', 'course_id', [
        ('code', 'Code', 'text', None), ('title', 'Title', 'text', None),
        ('credits', 'Credits', 'number', None),
        ('department_id', 'Department', 'number', 'department')]),
    'semester': ('Semesters', 'semester_id', [
        ('academic_year', 'Academic year', 'text', None),
        ('term', 'Term', 'text', None),
        ('start_date', 'Start date', 'date', None),
        ('end_date', 'End date', 'date', None)]),
    'course_section': ('Course sections', 'section_id', [
        ('course_id', 'Course', 'number', 'course'),
        ('instructor_id', 'Instructor', 'number', 'instructor'),
        ('semester_id', 'Semester', 'number', 'semester'),
        ('section_no', 'Section number', 'number', None)]),
    'enrollment': ('Enrollments', 'enrollment_id', [
        ('student_id', 'Student', 'number', 'student'),
        ('section_id', 'Course section', 'number', 'course_section'),
        ('grade', 'Grade (optional)', 'number', None)])
}


def connect():
    # libpq also accepts PGHOST, PGPORT, PGDATABASE, PGUSER and PGPASSWORD.
    return psycopg.connect(os.environ.get('DATABASE_URL', ''), row_factory=dict_row)


def rows_for(conn, table):
    _, pk, _ = TABLES[table]
    return conn.execute(sql.SQL('SELECT * FROM {} ORDER BY {}').format(
        sql.Identifier('sis', table), sql.Identifier(pk))).fetchall()


def option_label(table, row):
    if table in ('student', 'instructor'):
        return f"{row.get('student_no', row.get('staff_no'))}: {row['first_name']} {row['last_name']}"
    if table == 'semester':
        return f"{row['academic_year']} {row['term']}"
    if table == 'course_section':
        return f"Section ID {row['section_id']} / Course ID {row['course_id']} / Semester ID {row['semester_id']} / No. {row['section_no']}"
    return f"{row['code']}: {row.get('name', row.get('title'))}"


def error_message(exc):
    if isinstance(exc, psycopg.errors.UniqueViolation):
        return 'This record duplicates an existing unique value or relationship.'
    if isinstance(exc, psycopg.errors.ForeignKeyViolation):
        return 'A related record is missing, or this record is still referenced. Remove dependent records first.'
    if isinstance(exc, psycopg.errors.CheckViolation):
        return 'A value is outside the allowed range or format. Check the entered values.'
    if isinstance(exc, psycopg.OperationalError):
        return 'Cannot connect to PostgreSQL. Check the connection settings and database service.'
    return 'The values could not be saved. Check required fields, dates, numbers and text lengths.'


@app.get('/')
def index():
    return redirect(url_for('records', table='student'))


@app.route('/<table>', methods=['GET', 'POST'])
def records(table):
    if table not in TABLES:
        abort(404)
    account = ACCOUNTS.get(session.get('username'))
    if account is None:
        return redirect(url_for('login'), code=303)
    can_edit = account[0] == 'admin'
    if not can_edit and (request.method == 'POST' or 'edit' in request.args):
        abort(403)
    title, pk, fields = TABLES[table]
    error = None
    status = 200
    form = {}
    editing = request.args.get('edit', type=int)
    try:
        with connect() as conn:
            if request.method == 'POST':
                form = request.form.to_dict()
                action = form.get('action')
                try:
                    record_id = int(form['record_id']) if form.get('record_id') else None
                except ValueError:
                    abort(400)
                if action not in ('insert', 'update', 'delete'):
                    abort(400)
                if action != 'insert' and record_id is None:
                    abort(400)
                try:
                    with conn.transaction():
                        if action == 'delete':
                            result = conn.execute(sql.SQL('DELETE FROM {} WHERE {} = %s').format(
                                sql.Identifier('sis', table), sql.Identifier(pk)), (record_id,))
                        else:
                            values = []
                            for column, _, _, _ in fields:
                                value = form.get(column, '').strip()
                                if column != 'grade' and not value:
                                    raise ValueError('Missing required value')
                                values.append(value if value else None)
                            if action == 'insert':
                                result = conn.execute(sql.SQL('INSERT INTO {} ({}) VALUES ({})').format(
                                    sql.Identifier('sis', table),
                                    sql.SQL(', ').join(sql.Identifier(f[0]) for f in fields),
                                    sql.SQL(', ').join(sql.Placeholder() for _ in fields)), values)
                            else:
                                result = conn.execute(sql.SQL('UPDATE {} SET {} WHERE {} = %s').format(
                                    sql.Identifier('sis', table),
                                    sql.SQL(', ').join(sql.SQL('{} = %s').format(sql.Identifier(f[0])) for f in fields),
                                    sql.Identifier(pk)), values + [record_id])
                        if result.rowcount != 1:
                            abort(404)
                    return redirect(url_for('records', table=table, saved=action), code=303)
                except (psycopg.Error, ValueError) as exc:
                    error, status = error_message(exc), 400
                    editing = record_id if action == 'update' else None
            data = rows_for(conn, table)
            if editing is not None and request.method == 'GET':
                selected = next((r for r in data if r[pk] == editing), None)
                if selected is None:
                    abort(404)
                form = {key: '' if value is None else str(value) for key, value in selected.items()}
            options = {}
            for column, _, _, foreign in fields:
                if foreign:
                    foreign_pk = TABLES[foreign][1]
                    options[column] = [(r[foreign_pk], option_label(foreign, r)) for r in rows_for(conn, foreign)]
        return render_template('records.html', tables=TABLES, table=table, title=title,
                               can_edit=can_edit, pk=pk, fields=fields, rows=data, form=form, options=options,
                               editing=editing, error=error), status
    except psycopg.Error as exc:
        return render_template('records.html', tables=TABLES, table=table, title=title,
                               pk=pk, fields=[], rows=[], form={}, options={},
                               editing=None, error=error_message(exc)), 503


@app.cli.command('init-db')
def init_db():
    """Create the project tables and load the supplied sample records once."""
    with connect() as conn:
        exists = conn.execute("SELECT to_regnamespace('sis') AS name").fetchone()['name']
        if exists:
            raise click.ClickException('The sis schema already exists. Use a new empty database; existing data was not changed.')
        conn.execute(Path(__file__).with_name('database.sql').read_text(encoding='utf-8'), prepare=False)
    click.echo('Created seven tables and loaded the sample records.')


@app.cli.command('ensure-db')
def ensure_db():
    """Initialize a new hosted database and keep existing records on redeploy."""
    script = Path(__file__).with_name('database.sql').read_text(encoding='utf-8')
    statements = [line for line in script.splitlines() if line.strip() not in ('BEGIN;', 'COMMIT;')]
    with connect() as conn:
        conn.execute('SELECT pg_advisory_xact_lock(341, 11)')
        exists = conn.execute("SELECT to_regnamespace('sis') AS schema").fetchone()['schema']
        if exists is None:
            conn.execute('\n'.join(statements), prepare=False)
        else:
            for table in TABLES:
                conn.execute(sql.SQL('SELECT 1 FROM {} LIMIT 0').format(sql.Identifier('sis', table)))
    click.echo('The seven project tables are ready.')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
