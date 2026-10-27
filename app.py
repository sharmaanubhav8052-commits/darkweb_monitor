from flask import Flask, render_template, request
import sqlite3
import os
import sys
from datetime import date

# ================= APPLICATION PATHS =================

app = Flask(__name__)

if getattr(sys, "frozen", False):
    # Packaged Windows application
    APP_DIR = os.path.dirname(sys.executable)
    portable_marker = os.path.join(APP_DIR, "portable.mode")

    if os.path.isfile(portable_marker):
        # Portable edition: keep data beside the application
        DATA_DIR = os.path.join(APP_DIR, "data")
    else:
        # Installed edition: keep writable data in the user's profile
        DATA_DIR = os.path.join(
            os.environ.get("LOCALAPPDATA", os.path.expanduser("~")),
            "DarkWebThreatMonitor"
        )
else:
    # Development edition: keep the existing project database location
    APP_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(APP_DIR, "database")

os.makedirs(DATA_DIR, exist_ok=True)
DATABASE = os.path.join(DATA_DIR, "threats.db")


# ================= THREAT INFORMATION =================

THREAT_DATA = {
    "Phishing": {
        "description": "Suspicious phishing activity detected.",
        "score": 65
    },
    "Credential Leak": {
        "description": "Possible exposure of login credentials.",
        "score": 85
    },
    "Malware": {
        "description": "Malicious software indicator identified.",
        "score": 90
    },
    "Ransomware": {
        "description": "Ransomware-related activity indicator detected.",
        "score": 95
    },
    "Data Breach": {
        "description": "Possible exposure of sensitive data.",
        "score": 95
    },
    "Suspicious Domain": {
        "description": "Domain associated with suspicious activity.",
        "score": 35
    }
}


# ================= DATABASE CONNECTION =================

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ================= INITIALIZE DATABASE =================

def initialize_database():
    conn = get_db_connection()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS threats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                threat_type TEXT NOT NULL,
                description TEXT NOT NULL,
                risk_level TEXT NOT NULL,
                risk_score INTEGER NOT NULL,
                detected_date TEXT NOT NULL,
                recommendation TEXT NOT NULL
            )
        """)

        existing = conn.execute(
            "SELECT COUNT(*) FROM threats"
        ).fetchone()[0]

        if existing == 0:
            sample_threats = [
                ("Credential Leak",
                 "Possible exposure of login credentials.",
                 "HIGH", 85, "2026-09-24",
                 "Change passwords and enable 2FA."),
                ("Phishing",
                 "Suspicious phishing activity detected.",
                 "MEDIUM", 65, "2026-09-23",
                 "Avoid suspicious links and verify websites."),
                ("Malware",
                 "Malicious software indicator identified.",
                 "CRITICAL", 90, "2026-09-22",
                 "Scan the device and update security software."),
                ("Suspicious Domain",
                 "Domain associated with suspicious activity.",
                 "LOW", 35, "2026-09-21",
                 "Avoid interacting with the domain."),
                ("Data Breach",
                 "Possible exposure of sensitive data.",
                 "CRITICAL", 95, "2026-09-20",
                 "Secure affected accounts immediately."),
                ("Ransomware",
                 "Ransomware-related activity indicator detected.",
                 "CRITICAL", 95, "2026-09-19",
                 "Isolate the affected system and restore from a safe backup.")
            ]

            conn.executemany("""
                INSERT INTO threats (
                    threat_type, description, risk_level,
                    risk_score, detected_date, recommendation
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, sample_threats)

        conn.commit()
    finally:
        conn.close()


# ================= RISK ANALYSIS =================

def get_risk_details(score):
    if score >= 90:
        return (
            "CRITICAL",
            "Immediately isolate the affected system, change "
            "compromised credentials and enable multi-factor "
            "authentication."
        )
    if score >= 70:
        return (
            "HIGH",
            "Avoid interacting with the suspicious indicator, "
            "change affected passwords and enable 2FA."
        )
    if score >= 50:
        return (
            "MEDIUM",
            "Verify the source carefully and avoid suspicious "
            "links or downloads."
        )
    return (
        "LOW",
        "Continue monitoring the indicator and follow basic "
        "cybersecurity practices."
    )


# ================= DASHBOARD =================

@app.route("/")
def home():
    conn = get_db_connection()
    try:
        total = conn.execute(
            "SELECT COUNT(*) FROM threats"
        ).fetchone()[0]
        high = conn.execute(
            "SELECT COUNT(*) FROM threats WHERE risk_level='HIGH'"
        ).fetchone()[0]
        medium = conn.execute(
            "SELECT COUNT(*) FROM threats WHERE risk_level='MEDIUM'"
        ).fetchone()[0]
        low = conn.execute(
            "SELECT COUNT(*) FROM threats WHERE risk_level='LOW'"
        ).fetchone()[0]
        critical = conn.execute(
            "SELECT COUNT(*) FROM threats WHERE risk_level='CRITICAL'"
        ).fetchone()[0]

        threats = conn.execute(
            "SELECT * FROM threats ORDER BY id DESC"
        ).fetchall()
        threat_types = conn.execute("""
            SELECT threat_type, COUNT(*) AS count
            FROM threats GROUP BY threat_type
        """).fetchall()
        risk_data = conn.execute("""
            SELECT risk_level, COUNT(*) AS count
            FROM threats GROUP BY risk_level
        """).fetchall()
    finally:
        conn.close()

    return render_template(
        "index.html",
        total=total,
        high=high,
        medium=medium,
        low=low,
        critical=critical,
        threats=threats,
        threat_types=threat_types,
        risk_data=risk_data
    )


# ================= THREAT ANALYZER =================

@app.route("/analyzer", methods=["GET", "POST"])
def analyzer():
    result = None

    if request.method == "POST":
        threat_type = request.form.get("threat_type", "").strip()

        # Only process the threat types supported by this project.
        if threat_type in THREAT_DATA:
            description = THREAT_DATA[threat_type]["description"]
            score = THREAT_DATA[threat_type]["score"]
            level, recommendation = get_risk_details(score)

            result = {
                "type": threat_type,
                "description": description,
                "score": score,
                "level": level,
                "recommendation": recommendation
            }

            conn = get_db_connection()
            try:
                conn.execute("""
                    INSERT INTO threats (
                        threat_type, description, risk_level,
                        risk_score, detected_date, recommendation
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    threat_type,
                    description,
                    level,
                    score,
                    date.today().isoformat(),
                    recommendation
                ))
                conn.commit()
            finally:
                conn.close()

    return render_template("analyzer.html", result=result)


# ================= REPORTS =================

@app.route("/reports")
def reports():
    conn = get_db_connection()
    try:
        threats = conn.execute(
            "SELECT * FROM threats ORDER BY id DESC"
        ).fetchall()
        total = conn.execute(
            "SELECT COUNT(*) FROM threats"
        ).fetchone()[0]
        critical = conn.execute(
            "SELECT COUNT(*) FROM threats WHERE risk_level='CRITICAL'"
        ).fetchone()[0]
        high = conn.execute(
            "SELECT COUNT(*) FROM threats WHERE risk_level='HIGH'"
        ).fetchone()[0]
        medium = conn.execute(
            "SELECT COUNT(*) FROM threats WHERE risk_level='MEDIUM'"
        ).fetchone()[0]
        low = conn.execute(
            "SELECT COUNT(*) FROM threats WHERE risk_level='LOW'"
        ).fetchone()[0]
    finally:
        conn.close()

    return render_template(
        "reports.html",
        threats=threats,
        total=total,
        critical=critical,
        high=high,
        medium=medium,
        low=low
    )


if __name__ == "__main__":
    initialize_database()
    app.run(debug=True)
