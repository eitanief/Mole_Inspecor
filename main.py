import os
from flask import Flask, render_template, redirect, request, url_for, session, Response
from camera import VideoCamera
# import cv2


app = Flask(__name__)
app.secret_key = "efrat and adva"

video_stream = VideoCamera()


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(gen(video_stream), mimetype='multipart/x-mixed-replace; boundary=frame')

#
# @app.route('/', methods=['GET', 'POST'])
# def home():
#     if request.method == 'POST':
#         search_word = request.form["search bar"]
#         result = search(search_word)
#         session["result"] = result
#         if result:
#             return redirect(url_for("result_found"))
#         return "not found"
#     else:
#         return render_template("search.html")


if __name__ == '__main__':
    app.run()