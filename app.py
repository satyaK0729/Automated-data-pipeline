from flask import Flask, render_template, request, redirect, url_for, flash
from google.cloud import storage
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

# GCP CONFIG
BUCKET_NAME = "my-csv-upload-bucket"
SERVICE_ACCOUNT_FILE = "service_account_key.json"

# Initialize GCS client
storage_client = storage.Client.from_service_account_json(
    SERVICE_ACCOUNT_FILE
)
bucket = storage_client.bucket(BUCKET_NAME)

ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if 'files' not in request.files:
            flash("No file part")
            return redirect(request.url)

        files = request.files.getlist("files")

        if not files or files[0].filename == "":
            flash("No files selected")
            return redirect(request.url)

        for file in files:
            if file and allowed_file(file.filename):
                blob = bucket.blob(file.filename)
                blob.upload_from_file(file, content_type="text/csv")

        flash("CSV files uploaded successfully to GCP!")
        return redirect(url_for("index"))

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
