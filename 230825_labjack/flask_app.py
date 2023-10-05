# app.py
from flask import Flask, render_template
from load_data import schedule_report_plot
import datetime

app = Flask(__name__)


@app.route("/")
def index():
    img_filename = schedule_report_plot()
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return render_template(
        "index.html", img_filename=img_filename, current_time=current_time
    )


if __name__ == "__main__":
    app.run(debug=False)
