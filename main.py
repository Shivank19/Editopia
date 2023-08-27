from flask import Flask, render_template, request, flash
from werkzeug.utils import secure_filename
import os
import cv2
import numpy as np

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

app = Flask(__name__)
app.secret_key = "super secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def processImage(filename, operation):
    print(f"The operation is: {operation} and the file is: {filename}")
    img = cv2.imread(f"uploads/{filename}")
    match operation:
        case "cgray":
            processedImg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            newFilename = f"static/{filename}"
            print(
                f"The operation is: {operation} and the file is: {newFilename}")
            cv2.imwrite(newFilename, processedImg)
            return newFilename
        case "cwebp":
            newFilename = f"static/{filename.split('.')[0]}.webp"
            cv2.imwrite(newFilename, img)
            return newFilename
        case "cjpg":
            newFilename = f"static/{filename.split('.')[0]}.jpg"
            cv2.imwrite(newFilename, img)
            return newFilename
        case "cpng":
            newFilename = f"static/{filename.split('.')[0]}.png"
            cv2.imwrite(newFilename, img)
            return newFilename
        case "watermark":
            if request.method == "POST":
                if 'watermark' not in request.files:
                    flash('No Watermark part')
                    return "Error"
                watermark = request.files['watermark']

                if watermark.filename == '':
                    flash('No selected watermark')
                    return "Error: No watermark selected"
                if watermark and allowed_file(watermark.filename):
                    watermarkname = secure_filename(
                        watermark.filename)  # type: ignore
                    watermark.save(os.path.join(
                        app.config['UPLOAD_FOLDER'], watermarkname))
                    wm = cv2.imread(f"uploads/{watermarkname}")

                    h_img, w_img = img.shape[:2]
                    h_wm, w_wm = wm.shape[:2]

                    center_x = int(w_img/2)
                    center_y = int(h_img/2)

                    top_y = center_y - int(h_wm/2)
                    left_x = center_x - int(w_wm/2)
                    bottom_y = top_y + h_wm
                    right_x = left_x + w_wm

                    roi = img[top_y:bottom_y, left_x:right_x]
                    result = cv2.addWeighted(roi, 1, wm, 0.3, 0)
                    img[top_y:bottom_y, left_x:right_x] = result

                    newFilename = f"static/{filename.split('.')[0]}.png"
                    cv2.imwrite(newFilename, img)
                    return newFilename
        case "blur":
            newFilename = f"static/{filename.split('.')[0]}.png"
            img = cv2.GaussianBlur(img, (45, 45), 15)
            cv2.imwrite(newFilename, img)
            return newFilename
        case "resize":
            newFilename = f"static/{filename.split('.')[0]}.png"
            if request.method == "POST":
                perc = request.form.get("resize")
                height, width, channels = img.shape
                sizePerc = int(perc) / 100  # type: ignore
                new_width = int(width * sizePerc)
                new_height = int(height * sizePerc)
                resized_img = cv2.resize(img, (new_width, new_height))
                cv2.imwrite(newFilename, resized_img)
                return newFilename
        case "edge":
            newFilename = f"static/{filename.split('.')[0]}.png"
            edges = cv2.Canny(img, 50, 150)
            cv2.imwrite(newFilename, edges)
            return newFilename
        case "sharp":
            newFilename = f"static/{filename.split('.')[0]}.png"
            kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
            sharpened = cv2.filter2D(img, -1, kernel)
            cv2.imwrite(newFilename, sharpened)
            return newFilename


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/docs")
def docs():
    return render_template("docs.html")


@app.route("/grayscale")
def gray():
    return render_template("utils/gray.html")


@app.route("/png")
def png():
    return render_template("utils/png.html")


@app.route("/jpg")
def jpg():
    return render_template("utils/jpg.html")


@app.route("/webp")
def webp():
    return render_template("utils/webp.html")


@app.route("/watermark")
def watermark():
    return render_template("utils/watermark.html")


@app.route("/blur")
def blur():
    return render_template("utils/blur.html")


@app.route("/resize")
def resize():
    return render_template("utils/resize.html")


@app.route("/edge")
def edge():
    return render_template("utils/edge.html")


@app.route("/sharp")
def sharp():
    return render_template("utils/sharp.html")


@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "POST":
        operation = request.form.get("operation")
        if 'file' not in request.files:
            flash('No file part')
            # return redirect(request.url)
            return "Error"
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            # return redirect(request.url)
            return "Error: No file selected"
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)  # type: ignore
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            pImg = processImage(filename, operation)
            flash(
                f"Your Processed Image is available <a href='/{pImg}' target='_blank'>here</a>.")
            # return redirect(url_for('download_file', name=filename))
            return render_template('index.html')
    return render_template("index.html")


app.run(host="0.0.0.0", port=5000)
# app.run(debug=True)
