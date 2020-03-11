from flask import Flask, render_template
from api import get_user_bp, login_bp, mypage_init_bp, data_update_bp
import os


app = Flask(__name__, static_folder='../dist/static', template_folder='../dist')
#app = Flask(__name__, static_folder='../frontend/dist/static', template_folder='../frontend/dist')
#app = Flask(__name__, static_folder='../frontend', template_folder='../frontend')

app.register_blueprint(get_user_bp)
app.register_blueprint(login_bp)
app.register_blueprint(mypage_init_bp)
app.register_blueprint(data_update_bp)
app.config['SECRET_KEY'] = "random_secret_key"

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    return render_template('index.html')

if __name__ == '__main__':
    app.run()