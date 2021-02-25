from os import listdir
from flask import Flask, render_template, redirect, request, url_for, session, Response, flash
from camera import VideoCamera
import os
from mole_inspector import is_border_clear, is_symetric, is_colored
import json
from datetime import datetime


app = Flask(__name__)
app.secret_key = "efrat and adva"

video_stream = VideoCamera()

UPLOAD_FOLDER = "static/captures/"
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}


def area_of_rectangle(tuple_a, tuple_b):
    return abs((tuple_a[0]*tuple_a[1]) < (tuple_b[0]*tuple_b[1]))


def check_size_change(path):
    mole_id = indexing[path]
    for mole in image_data[mole_id]:
        if mole != path and area_of_rectangle(image_data[mole_id][mole], image_data[mole_id][path]):
            return False
    return True


def check_diameter(path):
    mole_id = indexing[path]
    size = image_data[mole_id][path]
    if size[0] > 6 or size[1] > 6:
        return False
    return True


@app.route('/results/', methods=['GET', 'POST'])
def inspect_mole():
    if request.method == 'POST':
        if request.form["submit_button"] == "Take picture":
            return redirect(url_for("take_picture"))
        elif request.form["submit_button"] == "Upload picture":
            return redirect(url_for("upload_image"))
        elif request.form["submit_button"] == "Show pictures":
            return redirect(url_for("show_images"))
    mole_id = indexing[session["image_path"]]
    return render_template("show_results.html", mole_imgs=image_data[mole_id], img_path=session["image_path"], sym = session["symmetric"], border = session["borders"], size = image_data[mole_id][session["image_path"]], change = session["change"], diameter=session['diameter'], color=session['color'])


@app.route('/capture/<params>')
def capture(params):
    stamp = video_stream.capture()
    image_data[params[1]] = {}
    image_data[params[1]][stamp+".jpg"] = params[0]
    return redirect(url_for('show_images'))


@app.route('/show_images/', methods=['GET', 'POST'])
def show_images():
    if request.method == 'POST':
        if request.form["submit_button"] == "Take picture":
            return redirect(url_for("take_picture"))
        elif request.form["submit_button"] == "Upload picture":
            return redirect(url_for("upload_image"))
        else:
            im_path = request.form["submit_button"]
            session["image_path"] = im_path
            session["symmetric"] = is_symetric(im_path)
            session["borders"] = is_border_clear(im_path)
            session["change"] = check_size_change(im_path)
            session['diameter'] = check_diameter(im_path)
            session['color'] = is_colored(im_path)
            return redirect(url_for("inspect_mole"))
    return render_template("show_images.html", images=indexing)


def gen(camera):
    while True:
        frame = camera.get_feed()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(gen(video_stream), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/take_picture', methods=['GET', 'POST'])
def take_picture():
    if request.method == 'POST':
        with open('index.txt', 'w') as index_file:
            json.dump(indexing, index_file)
        with open('data.txt', 'w') as jsonfile:
            json.dump(image_data, jsonfile)
        return redirect(url_for("capture",size=[(int(request.form["length"]), int(request.form["width"])), request.form["mole_id"]]))
    return render_template("take_picture.html")


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload_image', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            # filename = file.filename
            filename = datetime.now().strftime("%m-%d-%Y-%H-%M-%S")+".jpg"
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            mole_id = request.form["mole_id"]
            if mole_id not in image_data:
                image_data[mole_id] = {}
            image_data[mole_id][filename] = (int(request.form["length"]), int(request.form["width"]))
            indexing[filename] = mole_id
            with open('index.txt', 'w') as index_file:
                json.dump(indexing, index_file)
            with open('data.txt', 'w') as jsonfile:
                json.dump(image_data, jsonfile)
            return redirect(url_for("show_images"))
    return render_template("upload_image.html")


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if request.form["submit_button"] == "Take picture":
            return redirect(url_for("take_picture"))
        elif request.form["submit_button"] == "Upload picture":
            return redirect(url_for("upload_image"))
        elif request.form["submit_button"] == "Show pictures":
            return redirect(url_for("show_images"))
    return render_template("index.html")


if __name__ == '__main__':
    image_data = {}
    indexing = {}
    with open('index.txt', 'r') as index_file:
        indexing = json.load(index_file)
    with open('data.txt', 'r') as jsonfile:
        image_data = json.load(jsonfile)
    app.run()



