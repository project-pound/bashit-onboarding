import json
import sqlite3
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, redirect, render_template_string, request, url_for

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "onboarding.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vendors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                phone TEXT,
                email TEXT,
                address TEXT,
                city TEXT,
                category TEXT,
                gstin TEXT,
                tin TEXT,
                pan TEXT,
                aadhaar TEXT,
                status TEXT DEFAULT 'pending',
                rating REAL DEFAULT 0,
                service_history TEXT,
                partner_contract TEXT,
                documents TEXT,
                created_at TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS captains (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                phone TEXT,
                email TEXT,
                address TEXT,
                city TEXT,
                category TEXT,
                pan TEXT,
                aadhaar TEXT,
                police_verification TEXT,
                background_check TEXT,
                status TEXT DEFAULT 'pending',
                rating REAL DEFAULT 0,
                service_history TEXT,
                partner_contract TEXT,
                documents TEXT,
                created_at TEXT
            )
            """
        )


def parse_json(value):
    if not value:
        return []
    try:
        return json.loads(value)
    except Exception:
        return []


@app.route("/")
def dashboard():
    with get_connection() as conn:
        vendor_count = conn.execute("SELECT COUNT(*) AS c FROM vendors").fetchone()["c"]
        captain_count = conn.execute("SELECT COUNT(*) AS c FROM captains").fetchone()["c"]
        vendor_pending = conn.execute("SELECT COUNT(*) AS c FROM vendors WHERE status = 'pending'").fetchone()["c"]
        captain_pending = conn.execute("SELECT COUNT(*) AS c FROM captains WHERE status = 'pending'").fetchone()["c"]
        recent_vendors = conn.execute("SELECT * FROM vendors ORDER BY created_at DESC LIMIT 5").fetchall()
        recent_captains = conn.execute("SELECT * FROM captains ORDER BY created_at DESC LIMIT 5").fetchall()

    return render_template_string(
        '''
        <html>
        <head>
            <title>BashIt Onboarding Dashboard</title>
            <style>
                :root {
                    --bg: #f3f7fb;
                    --panel: #ffffff;
                    --panel-alt: #f8fafc;
                    --primary: #111827;
                    --secondary: #0f766e;
                    --accent: #f59e0b;
                    --muted: #64748b;
                    --line: #e2e8f0;
                    --success: #10b981;
                    --warning: #f59e0b;
                    --danger: #ef4444;
                }
                * { box-sizing: border-box; }
                body {
                    margin: 0; font-family: Arial, Helvetica, sans-serif; background: linear-gradient(135deg, #f8fafc, #eef5ff);
                    color: var(--primary);
                }
                .wrap { max-width: 1280px; margin: 0 auto; padding: 28px 20px 50px; }
                .topbar {
                    display: flex; justify-content: space-between; align-items: center; gap: 20px; background: var(--panel); border: 1px solid var(--line);
                    border-radius: 18px; padding: 18px 24px; box-shadow: 0 12px 30px rgba(15, 23, 42, 0.05);
                }
                .brand h1 { margin: 0; font-size: 28px; }
                .brand span { color: var(--secondary); font-weight: bold; }
                .nav { display: flex; gap: 12px; flex-wrap: wrap; }
                .btn { display: inline-block; padding: 10px 16px; border-radius: 10px; text-decoration: none; font-weight: 700; border: 1px solid transparent; }
                .btn.primary { background: var(--primary); color: white; }
                .btn.secondary { background: var(--panel-alt); border-color: var(--line); color: var(--primary); }
                .grid {
                    display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 18px; margin: 24px 0;
                }
                .card {
                    background: var(--panel); border: 1px solid var(--line); border-radius: 18px; padding: 20px; box-shadow: 0 10px 22px rgba(15, 23, 42, 0.04);
                }
                .tiny { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; }
                .num { font-size: 32px; font-weight: 800; margin-top: 8px; }
                .muted { color: var(--muted); }
                .panel {
                    background: var(--panel); border: 1px solid var(--line); border-radius: 18px; padding: 22px; margin-top: 24px; box-shadow: 0 10px 22px rgba(15, 23, 42, 0.04);
                }
                .panel h2 { margin-top: 0; }
                table { width: 100%; border-collapse: collapse; }
                th, td { text-align: left; border-bottom: 1px solid var(--line); padding: 12px 10px; }
                th { background: var(--panel-alt); }
                .badge {
                    display: inline-block; padding: 5px 9px; border-radius: 999px; font-size: 12px; font-weight: 700;
                    background: #ecfeff; color: #0f766e;
                }
                .badge.pending { background: #fef3c7; color: #92400e; }
                .badge.approved { background: #dcfce7; color: #166534; }
                .badge.rejected { background: #fee2e2; color: #991b1b; }
                @media (max-width: 700px) {
                    .topbar { flex-direction: column; align-items: flex-start; }
                    .nav { width: 100%; }
                    .nav .btn { flex: 1; text-align: center; }
                }
            </style>
        </head>
        <body>
            <div class="wrap">
                <div class="topbar">
                    <div class="brand">
                        <h1><span>BashIt</span> Onboarding</h1>
                    </div>
                    <div class="nav">
                        <a class="btn secondary" href="/vendor">Add Vendor</a>
                        <a class="btn secondary" href="/captain">Add Captain</a>
                        <a class="btn primary" href="/records">View Records</a>
                    </div>
                </div>

                <div class="grid">
                    <div class="card">
                        <div class="tiny">Total vendors</div>
                        <div class="num">{{ vendor_count }}</div>
                    </div>
                    <div class="card">
                        <div class="tiny">Total captains</div>
                        <div class="num">{{ captain_count }}</div>
                    </div>
                    <div class="card">
                        <div class="tiny">Vendor pending</div>
                        <div class="num">{{ vendor_pending }}</div>
                    </div>
                    <div class="card">
                        <div class="tiny">Captain pending</div>
                        <div class="num">{{ captain_pending }}</div>
                    </div>
                </div>

                <div class="panel">
                    <h2>Recent vendor onboarding</h2>
                    <table>
                        <tr><th>Name</th><th>Category</th><th>GSTIN</th><th>Status</th></tr>
                        {% for item in recent_vendors %}
                        <tr>
                            <td>{{ item['name'] or '-' }}</td>
                            <td>{{ item['category'] or '-' }}</td>
                            <td>{{ item['gstin'] or '-' }}</td>
                            <td><span class="badge {{ item['status'] or 'pending' }}">{{ item['status'] or 'pending' }}</span></td>
                        </tr>
                        {% endfor %}
                    </table>
                </div>

                <div class="panel">
                    <h2>Recent captain onboarding</h2>
                    <table>
                        <tr><th>Name</th><th>Category</th><th>Police check</th><th>Status</th></tr>
                        {% for item in recent_captains %}
                        <tr>
                            <td>{{ item['name'] or '-' }}</td>
                            <td>{{ item['category'] or '-' }}</td>
                            <td>{{ item['police_verification'] or '-' }}</td>
                            <td><span class="badge {{ item['status'] or 'pending' }}">{{ item['status'] or 'pending' }}</span></td>
                        </tr>
                        {% endfor %}
                    </table>
                </div>
            </div>
        </body>
        </html>
        ''',
        vendor_count=vendor_count,
        captain_count=captain_count,
        vendor_pending=vendor_pending,
        captain_pending=captain_pending,
        recent_vendors=recent_vendors,
        recent_captains=recent_captains,
    )


@app.route("/records")
def records():
    with get_connection() as conn:
        vendors = conn.execute("SELECT * FROM vendors ORDER BY created_at DESC").fetchall()
        captains = conn.execute("SELECT * FROM captains ORDER BY created_at DESC").fetchall()
    return render_template_string(
        '''
        <html>
        <head>
            <title>BashIt Records</title>
            <style>
                body { font-family: Arial, sans-serif; background: #f4f7fb; margin: 0; padding: 24px; color: #111827; }
                .wrap { max-width: 1200px; margin: 0 auto; }
                .top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 22px; }
                .panel { background: white; border: 1px solid #e2e8f0; border-radius: 18px; padding: 20px; margin-bottom: 24px; box-shadow: 0 12px 30px rgba(15, 23, 42, 0.05); }
                table { width: 100%; border-collapse: collapse; }
                th, td { padding: 10px; text-align: left; border-bottom: 1px solid #e2e8f0; }
                th { background: #f8fafc; }
                a { color: #0f766e; text-decoration: none; font-weight: bold; }
                .badge { display: inline-block; padding: 4px 8px; border-radius: 999px; font-size: 12px; background: #ecfeff; color: #0f766e; }
            </style>
        </head>
        <body>
            <div class="wrap">
                <div class="top">
                    <h1>Onboarding Records</h1>
                    <a href="/">Back to dashboard</a>
                </div>

                <div class="panel">
                    <h2>Vendors</h2>
                    <table>
                        <tr><th>Name</th><th>Category</th><th>GSTIN</th><th>City</th><th>Status</th></tr>
                        {% for item in vendors %}
                        <tr><td>{{ item['name'] or '-' }}</td><td>{{ item['category'] or '-' }}</td><td>{{ item['gstin'] or '-' }}</td><td>{{ item['city'] or '-' }}</td><td><span class="badge">{{ item['status'] or 'pending' }}</span></td></tr>
                        {% endfor %}
                    </table>
                </div>

                <div class="panel">
                    <h2>Captains</h2>
                    <table>
                        <tr><th>Name</th><th>Category</th><th>Police verification</th><th>City</th><th>Status</th></tr>
                        {% for item in captains %}
                        <tr><td>{{ item['name'] or '-' }}</td><td>{{ item['category'] or '-' }}</td><td>{{ item['police_verification'] or '-' }}</td><td>{{ item['city'] or '-' }}</td><td><span class="badge">{{ item['status'] or 'pending' }}</span></td></tr>
                        {% endfor %}
                    </table>
                </div>
            </div>
        </body>
        </html>
        ''',
        vendors=vendors,
        captains=captains,
    )


@app.route("/vendor", methods=["GET", "POST"])
def vendor_onboarding():
    if request.method == "POST":
        payload = {
            "name": request.form.get("name", "").strip(),
            "phone": request.form.get("phone", "").strip(),
            "email": request.form.get("email", "").strip(),
            "address": request.form.get("address", "").strip(),
            "city": request.form.get("city", "").strip(),
            "category": request.form.get("category", "").strip(),
            "gstin": request.form.get("gstin", "").strip(),
            "tin": request.form.get("tin", "").strip(),
            "pan": request.form.get("pan", "").strip(),
            "aadhaar": request.form.get("aadhaar", "").strip(),
            "status": request.form.get("status", "pending").strip(),
            "rating": request.form.get("rating", "0").strip(),
            "service_history": request.form.get("service_history", "").strip(),
            "partner_contract": request.form.get("partner_contract", "").strip(),
            "documents": json.dumps({
                "gst_certificate": request.form.get("documents_gst", ""),
                "pan_document": request.form.get("documents_pan", ""),
                "aadhaar_document": request.form.get("documents_aadhaar", ""),
                "contract": request.form.get("documents_contract", ""),
            }),
            "created_at": datetime.utcnow().isoformat(),
        }
        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO vendors (name, phone, email, address, city, category, gstin, tin, pan, aadhaar, status, rating, service_history, partner_contract, documents, created_at)
                VALUES (:name, :phone, :email, :address, :city, :category, :gstin, :tin, :pan, :aadhaar, :status, :rating, :service_history, :partner_contract, :documents, :created_at)
                """,
                payload,
            )
        return redirect(url_for("dashboard"))

    return render_template_string(
        '''
        <html>
        <head><title>Vendor Onboarding</title>
        <style>
            body { font-family: Arial, sans-serif; background: #f4f7fb; padding: 24px; color: #111827; }
            form { background: white; padding: 24px; border-radius: 18px; box-shadow: 0 10px 28px rgba(15, 23, 42, 0.08); max-width: 840px; margin: auto; }
            .grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
            .field { display: flex; flex-direction: column; margin-bottom: 12px; }
            input, select, textarea { padding: 10px; border: 1px solid #dfe7f3; border-radius: 10px; font-size: 14px; }
            textarea { min-height: 80px; }
            button { padding: 12px 18px; border: none; background: #111827; color: white; border-radius: 10px; font-weight: bold; }
            a { color: #0f766e; text-decoration: none; font-weight: bold; }
            @media (max-width: 700px) { .grid { grid-template-columns: 1fr; } }
        </style>
        </head>
        <body>
            <h1>Vendor Onboarding</h1>
            <form method="post">
                <div class="grid">
                    <div class="field"><label>Name</label><input name="name" required></div>
                    <div class="field"><label>Phone</label><input name="phone"></div>
                    <div class="field"><label>Email</label><input name="email" type="email"></div>
                    <div class="field"><label>City</label><input name="city"></div>
                    <div class="field"><label>Category</label><input name="category"></div>
                    <div class="field"><label>Status</label><select name="status"><option value="pending">Pending</option><option value="approved">Approved</option><option value="rejected">Rejected</option></select></div>
                    <div class="field"><label>GSTIN</label><input name="gstin"></div>
                    <div class="field"><label>TIN</label><input name="tin"></div>
                    <div class="field"><label>Pan</label><input name="pan"></div>
                    <div class="field"><label>Aadhaar</label><input name="aadhaar"></div>
                    <div class="field"><label>Rating</label><input name="rating" type="number" min="0" max="5" step="0.1"></div>
                    <div class="field"><label>Partner Contract</label><input name="partner_contract"></div>
                    <div class="field" style="grid-column:1/-1"><label>Address</label><textarea name="address"></textarea></div>
                    <div class="field" style="grid-column:1/-1"><label>Service History</label><textarea name="service_history"></textarea></div>
                    <div class="field" style="grid-column:1/-1"><label>GST Certificate Ref</label><input name="documents_gst"></div>
                    <div class="field"><label>PAN Document Ref</label><input name="documents_pan"></div>
                    <div class="field"><label>Aadhaar Document Ref</label><input name="documents_aadhaar"></div>
                    <div class="field" style="grid-column:1/-1"><label>Contract Document Ref</label><input name="documents_contract"></div>
                </div>
                <div style="margin-top: 16px;"><button type="submit">Save vendor onboarding</button> <a href="/" style="color:#0f766e;text-decoration:none; margin-left: 10px;">Back to dashboard</a></div>
            </form>
        </body>
        </html>
        '''
    )


@app.route("/captain", methods=["GET", "POST"])
def captain_onboarding():
    if request.method == "POST":
        payload = {
            "name": request.form.get("name", "").strip(),
            "phone": request.form.get("phone", "").strip(),
            "email": request.form.get("email", "").strip(),
            "address": request.form.get("address", "").strip(),
            "city": request.form.get("city", "").strip(),
            "category": request.form.get("category", "").strip(),
            "pan": request.form.get("pan", "").strip(),
            "aadhaar": request.form.get("aadhaar", "").strip(),
            "police_verification": request.form.get("police_verification", "").strip(),
            "background_check": request.form.get("background_check", "").strip(),
            "status": request.form.get("status", "pending").strip(),
            "rating": request.form.get("rating", "0").strip(),
            "service_history": request.form.get("service_history", "").strip(),
            "partner_contract": request.form.get("partner_contract", "").strip(),
            "documents": json.dumps({
                "police_record": request.form.get("documents_police", ""),
                "background_document": request.form.get("documents_background", ""),
                "pan_document": request.form.get("documents_pan", ""),
                "aadhaar_document": request.form.get("documents_aadhaar", ""),
                "contract": request.form.get("documents_contract", ""),
            }),
            "created_at": datetime.utcnow().isoformat(),
        }
        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO captains (name, phone, email, address, city, category, pan, aadhaar, police_verification, background_check, status, rating, service_history, partner_contract, documents, created_at)
                VALUES (:name, :phone, :email, :address, :city, :category, :pan, :aadhaar, :police_verification, :background_check, :status, :rating, :service_history, :partner_contract, :documents, :created_at)
                """,
                payload,
            )
        return redirect(url_for("dashboard"))

    return render_template_string(
        '''
        <html>
        <head><title>Captain Onboarding</title>
        <style>
            body { font-family: Arial, sans-serif; background: #f4f7fb; padding: 24px; color: #111827; }
            form { background: white; padding: 24px; border-radius: 18px; box-shadow: 0 10px 28px rgba(15, 23, 42, 0.08); max-width: 840px; margin: auto; }
            .grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
            .field { display: flex; flex-direction: column; margin-bottom: 12px; }
            input, select, textarea { padding: 10px; border: 1px solid #dfe7f3; border-radius: 10px; font-size: 14px; }
            textarea { min-height: 80px; }
            button { padding: 12px 18px; border: none; background: #111827; color: white; border-radius: 10px; font-weight: bold; }
            a { color: #0f766e; text-decoration: none; font-weight: bold; }
            @media (max-width: 700px) { .grid { grid-template-columns: 1fr; } }
        </style>
        </head>
        <body>
            <h1>Captain Onboarding</h1>
            <form method="post">
                <div class="grid">
                    <div class="field"><label>Name</label><input name="name" required></div>
                    <div class="field"><label>Phone</label><input name="phone"></div>
                    <div class="field"><label>Email</label><input name="email" type="email"></div>
                    <div class="field"><label>City</label><input name="city"></div>
                    <div class="field"><label>Category</label><input name="category"></div>
                    <div class="field"><label>Status</label><select name="status"><option value="pending">Pending</option><option value="approved">Approved</option><option value="rejected">Rejected</option></select></div>
                    <div class="field"><label>Pan</label><input name="pan"></div>
                    <div class="field"><label>Aadhaar</label><input name="aadhaar"></div>
                    <div class="field"><label>Police Verification</label><input name="police_verification"></div>
                    <div class="field"><label>Background Check</label><input name="background_check"></div>
                    <div class="field"><label>Rating</label><input name="rating" type="number" min="0" max="5" step="0.1"></div>
                    <div class="field"><label>Partner Contract</label><input name="partner_contract"></div>
                    <div class="field" style="grid-column:1/-1"><label>Address</label><textarea name="address"></textarea></div>
                    <div class="field" style="grid-column:1/-1"><label>Service History</label><textarea name="service_history"></textarea></div>
                    <div class="field"><label>Police Record Ref</label><input name="documents_police"></div>
                    <div class="field"><label>Background Check Ref</label><input name="documents_background"></div>
                    <div class="field"><label>PAN Document Ref</label><input name="documents_pan"></div>
                    <div class="field"><label>Aadhaar Document Ref</label><input name="documents_aadhaar"></div>
                    <div class="field" style="grid-column:1/-1"><label>Contract Document Ref</label><input name="documents_contract"></div>
                </div>
                <div style="margin-top: 16px;"><button type="submit">Save captain onboarding</button> <a href="/" style="color:#0f766e;text-decoration:none; margin-left: 10px;">Back to dashboard</a></div>
            </form>
        </body>
        </html>
        '''
    )


@app.route("/api/vendors")
def api_vendors():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM vendors ORDER BY created_at DESC").fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/api/captains")
def api_captains():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM captains ORDER BY created_at DESC").fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/health")
def health():
    return {"status": "ok", "database": str(DB_PATH)}


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=8005, debug=True)
