from flask import Flask, render_template, request
import sqlite3
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "database", "threats.db")

os.makedirs(os.path.dirname(DATABASE), exist_ok=True)

app = Flask(__name__)

DATABASE = "database/threats.db"


# ================= DATABASE CONNECTION =================

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ================= INITIALIZE DATABASE =================

def initialize_database():

    conn = get_db_connection()

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

            (
                "Credential Leak",
                "Possible exposure of login credentials.",
                "HIGH",
                85,
                "2026-09-24",
                "Change passwords and enable 2FA."
            ),

            (
                "Phishing",
                "Suspicious phishing activity detected.",
                "MEDIUM",
                65,
                "2026-09-23",
                "Avoid suspicious links and verify websites."
            ),

           (
    "Malware",
    "Malicious software indicator identified.",
    "CRITICAL",
    90,
    "2026-09-22",
    "Scan the device and update security software."
),

            (
                "Suspicious Domain",
                "Domain associated with suspicious activity.",
                "LOW",
                35,
                "2026-09-21",
                "Avoid interacting with the domain."
            ),

            (
                "Data Breach",
                "Possible exposure of sensitive data.",
                "CRITICAL",
                95,
                "2026-09-20",
                "Secure affected accounts immediately."
            ),

            (
    "Ransomware",
    "Ransomware-related activity indicator detected.",
    "CRITICAL",
    95,
    "2026-09-19",
    "Isolate the affected system and restore from a safe backup."
)

        ]

        conn.executemany("""
            INSERT INTO threats
            (
                threat_type,
                description,
                risk_level,
                risk_score,
                detected_date,
                recommendation
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, sample_threats)

    conn.commit()
    conn.close()


# ================= DASHBOARD =================

@app.route("/")
def home():

    conn = get_db_connection()

    # Total threats
    total = conn.execute(
        "SELECT COUNT(*) FROM threats"
    ).fetchone()[0]

    # High threats
    high = conn.execute(
        "SELECT COUNT(*) FROM threats WHERE risk_level='HIGH'"
    ).fetchone()[0]

    # Medium threats
    medium = conn.execute(
        "SELECT COUNT(*) FROM threats WHERE risk_level='MEDIUM'"
    ).fetchone()[0]

    # Low threats
    low = conn.execute(
        "SELECT COUNT(*) FROM threats WHERE risk_level='LOW'"
    ).fetchone()[0]

    # Critical threats
    critical = conn.execute(
        "SELECT COUNT(*) FROM threats WHERE risk_level='CRITICAL'"
    ).fetchone()[0]

    # All threats
    threats = conn.execute(
        "SELECT * FROM threats ORDER BY id DESC"
    ).fetchall()

    # Threat analytics
    threat_types = conn.execute("""
        SELECT threat_type, COUNT(*) AS count
        FROM threats
        GROUP BY threat_type
    """).fetchall()

    # Risk analytics
    risk_data = conn.execute("""
        SELECT risk_level, COUNT(*) AS count
        FROM threats
        GROUP BY risk_level
    """).fetchall()

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

        threat_type = request.form["threat_type"]
        description = request.form["description"]

        risk_scores = {
    "Phishing": 65,
    "Credential Leak": 85,
    "Malware": 90,
    "Ransomware": 95,
    "Data Breach": 95,
    "Suspicious Domain": 35
}
        score = risk_scores.get(
            threat_type,
            30
        )

        # Risk level and recommendation

        if score >= 90:

            level = "CRITICAL"

            recommendation = (
                "Immediately isolate the affected system, "
                "change compromised credentials and enable "
                "multi-factor authentication."
            )

        elif score >= 70:

            level = "HIGH"

            recommendation = (
                "Avoid interacting with the suspicious indicator, "
                "change affected passwords and enable 2FA."
            )

        elif score >= 50:

            level = "MEDIUM"

            recommendation = (
                "Verify the source carefully and avoid "
                "suspicious links or downloads."
            )

        else:

            level = "LOW"

            recommendation = (
                "Continue monitoring the indicator and "
                "follow basic cybersecurity practices."
            )

        result = {

            "type": threat_type,

            "description": description,

            "score": score,

            "level": level,

            "recommendation": recommendation

        }

    return render_template(
        "analyzer.html",
        result=result
    )
# ================= REPORTS =================

@app.route("/reports")
def reports():

    conn = get_db_connection()

    threats = conn.execute(
        "SELECT * FROM threats ORDER BY id ASC"
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

# ================= RUN APPLICATION =================

if __name__ == "__main__":

    initialize_database()

    app.run(debug=True)