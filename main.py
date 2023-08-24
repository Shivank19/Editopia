from flask import Flask, render_template, request, flash
from werkzeug.utils import secure_filename
import os
import cv2

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


@app.route("/compress")
def compress():
    return render_template("utils/compress.html")


@app.route("/watermark")
def watermark():
    return render_template("utils/watermark.html")


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


app.run(debug=True)
