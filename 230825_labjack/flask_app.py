# app.py
from flask import Flask, render_template
from load_data import schedule_report
import mpld3

app = Flask(__name__)


@app.route("/")
def index():
    # Call the generate_plot function from load_data.py
    plot = schedule_report()

    # Convert the Matplotlib plot to an interactive D3.js plot using mpld3
    interactive_plot = mpld3.fig_to_html(plot, template_type="simple")

    # Pass the interactive plot to the template for rendering
    return render_template("index.html", plot=interactive_plot)


if __name__ == "__main__":
    app.run(debug=True)
