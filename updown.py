from flask import Flask, render_template, redirect, url_for, request,flash, send_file,flash
from sqlalchemy.exc import IntegrityError
from flask_sqlalchemy import SQLAlchemy
import os
import re
import datetime
from io import BytesIO
from werkzeug.utils import secure_filename

#initialise flask application
app = Flask(__name__)

#adding sqlite database
project_dir = os.path.dirname(os.path.abspath(__file__))
print("path:",project_dir)
database_file = "sqlite:///{}".format(os.path.join(project_dir, "flaskfiledatabase.db"))
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'

#initialise connection to database
db = SQLAlchemy(app)

#Creating model File_Storage that holds key: file name, value: file and file information.
class File_Storage(db.Model):
    __tablename__ = 'File_Storage'
    key = db.Column(db.String(80), unique=True, nullable=False, primary_key=True)
    value = db.Column(db.LargeBinary)
    ftype=db.Column(db.String(80),unique=False, nullable=False)
    uptime = db.Column(db.String(30),nullable=False)


@app.route('/', methods=["GET", "POST"])
def set():
    record = None
    di={".docx":"Microsoft word document",".xlsx":"Excel sheet", ".pdf":"PDF document",".JPG":"JPG image",".PNG":"PNG file",".ipynb":"ipynb file",".txt":"Text file",".html":"HTML file"}
    print("set")
    if request.form:
        #print("request")
        try:
            #print("try")
            file = request.files['value']
            #print("fn1",file.filename)

            file_name=secure_filename(file.filename)
            pat = re.compile(r".(\w)+$")
            ext = re.search(pat,file_name)[0]
            #print("ext:", ext,di[ext])
            currtym=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            #print("time:",currtym, type(currtym))
            if ext in di.keys():ft = di[ext]
            else: ft="Unknown file format"
            record = File_Storage(key=file_name, value=file.read(),ftype=ft,uptime=currtym)
            #record = File_Storage(key=request.form.get("key"),value=request.files['value'].read())
            db.session.add(record)
            db.session.commit()

            #print("end try")
        except IntegrityError:
            #print("Failed to add record")
            db.session.rollback()
            return "<h3> File already exists go back to add new file.</h3>"
        except:
            return "<h3> Failed to upload file, go back to choose a file to upload</h3>"
    record = File_Storage.query.all()
    #print("in home")
    return render_template("set.html", record=record)

#Deletes records
@app.route("/delete", methods=["POST"])
def delete():
    #print("in delete")
    key = request.form.get("key")
    #key = request.files['value'].filename
    #print(key)
    record = File_Storage.query.filter_by(key=key).first()
    db.session.delete(record)
    db.session.commit()
    return redirect("/")
#downloads file
@app.route("/download", methods=["POST"])
def download():
    #print("in download")
    key = request.form.get("key")
    #print("key:",key)
    pat = re.compile(r".(\w)+$")
    #print("ext:", re.search(pat,key)[0])
    record = File_Storage.query.filter_by(key=key).first()
    #print(type(record.value),len(record.value))#,record.value)
    return send_file(BytesIO(record.value),attachment_filename=key,as_attachment=True)
if __name__ == "__main__":
    app.run(debug=True)
