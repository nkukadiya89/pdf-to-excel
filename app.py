from flask import Flask, render_template

from .routes.upload import upload_blueprint
from .routes.upload_pdf import upload_pdf_blueprint

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('main.html')

app.register_blueprint(upload_blueprint)
app.register_blueprint(upload_pdf_blueprint)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)