from flask import Flask, render_template, request, redirect, url_for,session,flash,jsonify,send_file
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView

import datetime
from io import BytesIO
from PIL import Image

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///appvelox.db'

db=SQLAlchemy(app)



class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status=db.Column(db.String(80),nullable=False)
   

admin = Admin(app)
admin.add_view(ModelView(Log, db.session))


allowed_ex=['png','jpg']
ex_dict={
    'png':'PNG',
    'jpg':'JPEG'
}

@app.route('/upload',methods=['POST'])
def upload():
    log=Log(status='start')
    db.session.add(log)
    db.session.commit()
    json=request.get_json()
    #file=request.files['file']
    height = request.form.get('height',0)
    width = request.form.get('width',0)
    file_data=request.files.get('file')
    ex=file_data.filename.split('.')[-1]
    if ex not in allowed_ex:
        log.status='wrong extension'
        db.session.commit()
        raise InvalidUsage('wrong extension', status_code=410)
    if int(width) not in range(1,9999) and int(height) not in range(1,9999):
        log.status='width or heigth are wrong'
        db.session.commit()
        raise InvalidUsage('width or heigth are wrong', status_code=410)
    if not file_data:
        log.status='haven\'t file'
        db.session.commit()
        raise InvalidUsage('haven\'t file', status_code=410)
    img = Image.open(BytesIO(file_data.read()))
    img_io = BytesIO()
    new_img = img.resize((int(width),int(height)))
    new_img.save(img_io,ex_dict[ex], quality=100)
    img_io.seek(0)
    log.status='success'
    db.session.commit()
   
    
    #return file_data.filename
    return send_file(img_io,attachment_filename=file_data.filename,as_attachment=True)

@app.route('/status')
def status():
    query=request.get_json().get('query')
    print(request.get_json())
    if query:
        log=Log.query.get(query)
        if log:
            raise InvalidUsage(log.status, status_code=200)
        else:
            raise InvalidUsage('doesn\'t exist', status_code=410)
    raise InvalidUsage('doesn\'t exist', status_code=410)

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=7001,debug=True)
