from datetime import datetime
import sqlite3

from flask import Flask, flash, g, redirect, render_template, request, url_for


app = Flask(__name__)
app.config["SECRET_KEY"] = "cloth-donation-demo-key"
app.config["DATABASE"] = "cloth_donation.db"


def get_db():
  if "db" not in g:
    g.db = sqlite3.connect(app.config["DATABASE"])
    g.db.row_factory = sqlite3.Row
  return g.db


def init_db():
  db = get_db()
  db.executescript(
    """
    CREATE TABLE IF NOT EXISTS donations (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      donor_name TEXT NOT NULL,
      mobile TEXT NOT NULL,
      cloth_type TEXT NOT NULL,
      quantity INTEGER NOT NULL,
      address TEXT NOT NULL,
      created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS requests (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      applicant_name TEXT NOT NULL,
      category TEXT NOT NULL,
      people_count INTEGER NOT NULL,
      urgency TEXT NOT NULL,
      address TEXT NOT NULL,
      created_at TEXT NOT NULL
    );
    """
  )
  db.commit()


@app.before_request
def before_request():
  init_db()


@app.teardown_appcontext
def close_db(exception):
  db = g.pop("db", None)
  if db is not None:
    db.close()


@app.route("/")
def home():
  db = get_db()
  donation_count = db.execute("SELECT COUNT(*) AS total FROM donations").fetchone()["total"]
  request_count = db.execute("SELECT COUNT(*) AS total FROM requests").fetchone()["total"]
  return render_template(
    "index.html",
    donation_count=donation_count,
    request_count=request_count,
  )


@app.route("/donate", methods=["POST"])
def donate():
  donor_name = request.form["donor_name"].strip()
  mobile = request.form["mobile"].strip()
  cloth_type = request.form["cloth_type"].strip()
  quantity = request.form["quantity"].strip()
  address = request.form["address"].strip()

  db = get_db()
  db.execute(
    """
    INSERT INTO donations (donor_name, mobile, cloth_type, quantity, address, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """,
    (donor_name, mobile, cloth_type, int(quantity), address, datetime.now().strftime("%Y-%m-%d %H:%M")),
  )
  db.commit()
  flash("Donation submitted successfully.")
  return redirect(url_for("home") + "#donate")


@app.route("/request-clothes", methods=["POST"])
def request_clothes():
  applicant_name = request.form["applicant_name"].strip()
  category = request.form["category"].strip()
  people_count = request.form["people_count"].strip()
  urgency = request.form["urgency"].strip()
  address = request.form["address"].strip()

  db = get_db()
  db.execute(
    """
    INSERT INTO requests (applicant_name, category, people_count, urgency, address, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """,
    (applicant_name, category, int(people_count), urgency, address, datetime.now().strftime("%Y-%m-%d %H:%M")),
  )
  db.commit()
  flash("Cloth request submitted successfully.")
  return redirect(url_for("home") + "#request")


@app.route("/admin")
def admin():
  db = get_db()
  donations = db.execute(
    "SELECT * FROM donations ORDER BY id DESC"
  ).fetchall()
  requests = db.execute(
    "SELECT * FROM requests ORDER BY id DESC"
  ).fetchall()
  return render_template("admin.html", donations=donations, requests=requests)


if __name__ == "__main__":
  app.run(debug=True)
