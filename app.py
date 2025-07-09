from flask import Flask, request, redirect, render_template, render_template_string, session
from data_manager import load_data, save_data
try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    def load_dotenv(*args, **kwargs):
        print("Warning: python-dotenv not installed; .env file will be ignored")
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('ADMIN_PASSWORD', 'change-me')


def require_login(func):
    def wrapper(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect('/')
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if request.form.get('password') == os.getenv('ADMIN_PASSWORD'):
            session['logged_in'] = True
            return redirect('/inventory')
    return render_template('index.html')


@app.route('/inventory')
@require_login
def inventory():
    data = load_data()
    return render_template('inventory.html', data=data)


@app.route('/add-category', methods=['GET', 'POST'])
@require_login
def add_category():
    data = load_data()
    if request.method == 'POST':
        name = request.form.get('name')
        cat_id = str(len(data['categories']) + 1)
        data['categories'].append({'id': cat_id, 'name': name, 'cards': []})
        save_data(data)
        return redirect('/inventory')
    return render_template_string('''\
        {% extends 'layout.html' %}
        {% block content %}
        <h2>Add Category</h2>
        <form method="post">
            <label>Name: <input type="text" name="name"></label>
            <button type="submit" class="button">Save</button>
        </form>
        {% endblock %}
    ''')


@app.route('/category/<cat_id>', methods=['GET', 'POST'])
@require_login
def manage_category(cat_id):
    data = load_data()
    cat = next((c for c in data['categories'] if c['id'] == cat_id), None)
    if not cat:
        return 'Category not found', 404
    if request.method == 'POST' and request.form.get('action') == 'add-card':
        card = {
            'id': str(len(cat['cards']) + 1),
            'name': request.form.get('name'),
            'front': request.form.get('front'),
            'back': request.form.get('back'),
            'claimed_by': None
        }
        cat['cards'].append(card)
        save_data(data)
    return render_template('category.html', category=cat)


if __name__ == '__main__':
    app.run(debug=True)
