from flask import (
    Flask,
    request,
    redirect,
    render_template,
    render_template_string,
    session,
    url_for,
)
from werkzeug.utils import secure_filename
from data_manager import load_data, save_data
import logging
try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    def load_dotenv(*args, **kwargs):
        print("Warning: python-dotenv not installed; .env file will be ignored")
import os

load_dotenv()

logging.basicConfig(
    filename=os.getenv('DEBUG_LOG', 'debug.log'),
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    filemode='a'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.getenv('ADMIN_PASSWORD', 'change-me')


def require_login(func):
    def wrapper(*args, **kwargs):
        if not session.get('logged_in'):
            logger.debug('Unauthorized access attempt to %s', request.path)
            return redirect('/')
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        logger.debug('Login attempt')
        if request.form.get('password') == os.getenv('ADMIN_PASSWORD', 'change-me'):
            session['logged_in'] = True
            logger.debug('Login successful')
            return redirect('/inventory')
        logger.debug('Login failed')
    return render_template('index.html')


@app.route('/inventory')
@require_login
def inventory():
    logger.debug('Rendering inventory list')
    data = load_data()
    return render_template('inventory.html', data=data)


@app.route('/embed-builder', methods=['GET', 'POST'])
@require_login
def embed_builder():
    logger.debug('Accessing embed builder')
    data = load_data()
    embed = data.get('embed', {})
    if request.method == 'POST':
        embed = {
            'title': request.form.get('title', ''),
            'description': request.form.get('description', ''),
            'button_label': request.form.get('button_label', 'Explore'),
            'color': request.form.get('color', '#ffffff'),
            'thumbnail': request.form.get('thumbnail', ''),
            'image': request.form.get('image', ''),
            'footer': request.form.get('footer', ''),
        }
        data['embed'] = embed
        save_data(data)
    return render_template('embed_builder.html', embed=embed)


@app.route('/settings', methods=['GET', 'POST'])
@require_login
def settings():
    logger.debug('Accessing settings')
    data = load_data()
    settings = data.get('settings', {})
    if request.method == 'POST':
        settings = {
            'inventory_channel_id': request.form.get('inventory_channel_id', ''),
            'claims_channel_id': request.form.get('claims_channel_id', ''),
            'image_channel_id': request.form.get('image_channel_id', ''),
            'grid_size': int(request.form.get('grid_size', '3')),
        }
        data['settings'] = settings
        save_data(data)
    return render_template('settings.html', settings=settings)


@app.route('/add-category', methods=['GET', 'POST'])
@require_login
def add_category():
    data = load_data()
    if request.method == 'POST':
        name = request.form.get('name')
        logger.debug('Adding category %s', name)
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


@app.route('/delete-category/<cat_id>', methods=['POST'])
@require_login
def delete_category(cat_id):
    data = load_data()
    logger.debug('Deleting category %s', cat_id)
    data['categories'] = [c for c in data['categories'] if c['id'] != cat_id]
    save_data(data)
    return redirect('/inventory')


@app.route('/category/<cat_id>', methods=['GET', 'POST'])
@require_login
def manage_category(cat_id):
    logger.debug('Managing category %s', cat_id)
    data = load_data()
    cat = next((c for c in data['categories'] if c['id'] == cat_id), None)
    if not cat:
        logger.debug('Category %s not found', cat_id)
        return 'Category not found', 404
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add-card':
            card = {
                'id': str(len(cat['cards']) + 1),
                'name': request.form.get('name'),
                'front': request.form.get('front'),
                'back': request.form.get('back'),
                'claimed_by': None,
            }
            logger.debug('Adding card %s to category %s', card['name'], cat_id)
            cat['cards'].append(card)
            save_data(data)
        elif action == 'batch-add':
            names = [n.strip() for n in request.form.get('names', '').splitlines() if n.strip()]
            files = request.files.getlist('images')
            logger.debug('Batch adding %s cards with %s images', len(names), len(files))
            upload_dir = os.path.join('static', 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            for idx, name in enumerate(names):
                front_file = files[2*idx] if len(files) > 2*idx else None
                back_file = files[2*idx+1] if len(files) > 2*idx+1 else None
                front_path = back_path = ''
                if front_file:
                    fname = secure_filename(front_file.filename)
                    front_path = os.path.join(upload_dir, f'f_{len(cat["cards"])}_{fname}')
                    front_file.save(front_path)
                if back_file:
                    fname = secure_filename(back_file.filename)
                    back_path = os.path.join(upload_dir, f'b_{len(cat["cards"])}_{fname}')
                    back_file.save(back_path)
                card = {
                    'id': str(len(cat['cards']) + 1),
                    'name': name,
                    'front': '/' + front_path if front_path else '',
                    'back': '/' + back_path if back_path else '',
                    'claimed_by': None,
                }
                logger.debug('Batch add card %s', card['name'])
                cat['cards'].append(card)
            save_data(data)
        elif action == 'delete-card':
            card_id = request.form.get('card_id')
            logger.debug('Deleting card %s from category %s', card_id, cat_id)
            cat['cards'] = [c for c in cat['cards'] if c['id'] != card_id]
            save_data(data)
    return render_template('category.html', category=cat)


if __name__ == '__main__':
    logger.info('Starting Flask app')
    app.run(debug=True)
