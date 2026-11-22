import csv
import io
import json
import secrets
from pathlib import Path

from flask import (
    Flask, Response, abort, flash, redirect,
    render_template_string, request, session, url_for
)

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

FLAGS_PATH = Path(__file__).with_name("flags.json")
records = []

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>A10 Feature Toggle QA</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f1f5f9;
            max-width: 800px;
            margin: 50px auto;
            color: #1e293b;
        }
        .card {
            background: white;
            padding: 24px;
            margin: 20px 0;
            border-radius: 12px;
            border: 1px solid #ddd;
        }
        button {
            padding: 10px 20px;
            background: #2563eb;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
        }
        input { padding: 10px; width: 65%; }
        .on { color: green; font-weight: bold; }
        .off { color: red; font-weight: bold; }
    </style>
</head>
<body>
    <h1>Assignment 10 - Feature Toggle QA</h1>
    <p>Role: QA | HDD & Feature Toggle Testing</p>

    <div class="card">
        <h2>Feature 1: Quick Submit</h2>
        <p>Status:
            {% if quick_on %}
                <span class="on">ON</span>
            {% else %}
                <span class="off">OFF</span>
            {% endif %}
        </p>

        <form method="post"
              action="{{ '/quick-submit' if quick_on else '/preview' }}">
            <input name="item" placeholder="Enter test data"
                   required maxlength="80">
            <button type="submit">
                {{ 'Quick Submit' if quick_on else 'Preview' }}
            </button>
        </form>

        {% if pending %}
            <h3>Preview: {{ pending }}</h3>
            <form method="post" action="/confirm">
                <button type="submit">Confirm Submission</button>
            </form>
        {% endif %}
    </div>

    <div class="card">
        <h2>Feature 2: CSV Export</h2>
        <p>Status:
            {% if csv_on %}
                <span class="on">ON</span>
            {% else %}
                <span class="off">OFF</span>
            {% endif %}
        </p>

        {% if csv_on %}
            <a href="/export">
                <button>Download CSV</button>
            </a>
        {% else %}
            <p>CSV Export is currently disabled.</p>
        {% endif %}
    </div>

    <div class="card">
        <h2>Submitted Records</h2>
        {% for item in records %}
            <p>{{ loop.index }}. {{ item }}</p>
        {% else %}
            <p>No records submitted.</p>
        {% endfor %}
    </div>

    {% for message in get_flashed_messages() %}
        <p class="on">{{ message }}</p>
    {% endfor %}
</body>
</html>
"""


def load_flags():
    with FLAGS_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def enabled(name):
    return load_flags().get(name, {}).get("enabled") is True


def show_page(pending=None):
    return render_template_string(
        HTML,
        quick_on=enabled("quick_submit"),
        csv_on=enabled("csv_export"),
        records=records,
        pending=pending
    )


def get_item():
    item = request.form.get("item", "").strip()
    if not item or len(item) > 80:
        abort(400)
    return item


@app.get("/")
def home():
    return show_page()


@app.post("/quick-submit")
def quick_submit():
    if not enabled("quick_submit"):
        abort(403)

    records.append(get_item())
    flash("Quick submission successful!")
    return redirect(url_for("home"))


@app.post("/preview")
def preview():
    if enabled("quick_submit"):
        abort(403)

    item = get_item()
    session["pending"] = item
    return show_page(pending=item)


@app.post("/confirm")
def confirm():
    if enabled("quick_submit"):
        abort(403)

    item = session.pop("pending", None)
    if item is None:
        abort(400)

    records.append(item)
    flash("Confirmed submission successful!")
    return redirect(url_for("home"))


@app.get("/export")
def export_csv():
    if not enabled("csv_export"):
        abort(403)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "record"])

    for number, item in enumerate(records, 1):
        writer.writerow([number, item])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=qa_results.csv"
        }
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
