# app.py
from flask import Flask, render_template, send_file
from load_data import schedule_report_plot
import datetime
import threading

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


def run_192_168_0_135():
    app.run(host="192.168.0.135", port=5000, debug=False)


def run_128_32_48_112():
    app.run(host="128.32.48.112", port=5000, debug=False)


if __name__ == "__main__":
    # Start each Flask app instance in a separate thread
    thread1 = threading.Thread(target=run_192_168_0_135)
    thread2 = threading.Thread(target=run_128_32_48_112)

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()
