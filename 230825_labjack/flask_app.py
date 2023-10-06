# app.py
from flask import Flask, render_template, send_file
from load_data import schedule_report_plot
import datetime

app = Flask(__name__)


@app.route("/")
def index():
    try:
        img_filename = schedule_report_plot()
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return render_template(
            "index.html", img_filename=img_filename, current_time=current_time
        )
    except Exception as e:
        print(str(e))
        return render_template("index.html", img_filename=None, current_time=None)


@app.route("/image/<filename>")
def get_image(filename):
    return send_file(filename, mimetype="image/png")


if __name__ == "__main__":
    app.run(debug=False,host="192.168.0.135",port=5000)
