from flask import Flask
import threading
import webbrowser

app = Flask(__name__)

# كل id يخزن بياناته بشكل منفصل
_data_store = {}

@app.route("/")
def index():
    cards = ""
    for uid, info in _data_store.items():
        headers = "".join(f"<th>{n}</th>" for n in info['namelist'])
        cells = "".join(f"<td>{d}</td>" for d in info['datalist'])

        cards += f"""
        <div class="card">
            <div class="ui-id">ui_id: {info['ui_id']}</div>
            <div class="id-val">id: {uid}</div>
            <table>
                <thead><tr>{headers}</tr></thead>
                <tbody><tr>{cells}</tr></tbody>
            </table>
        </div>
        """

    html = f"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>IoT Dashboard</title>

    <!-- ❌ تم حذف التحديث التلقائي -->

    <style>
        body {{
            font-family: Arial, sans-serif;
            background: #1e1e2e;
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            justify-content: center;
            padding: 30px;
            margin: 0;
        }}
        .card {{
            background: #2b2b3b;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.4);
            min-width: 280px;
        }}
        .ui-id {{
            color: #888;
            font-size: 13px;
            margin-bottom: 4px;
        }}
        .id-val {{
            color: #f0a500;
            font-size: 22px;
            font-weight: bold;
            margin-bottom: 20px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            border-radius: 8px;
            overflow: hidden;
        }}
        th {{
            background: #4a90d9;
            color: white;
            padding: 10px 16px;
            text-align: center;
            font-size: 14px;
        }}
        td {{
            background: #3c3f55;
            color: #e0e0e0;
            padding: 10px 16px;
            text-align: center;
            border-top: 1px solid #444;
            font-size: 14px;
        }}
        tr:hover td {{
            background: #505070;
        }}
    </style>
</head>
<body>
    {cards}
</body>
</html>
"""
    return html


def start_interactive_site(id, ui_id, namelist, datalist):
    # كل id يحفظ بياناته بشكل منفصل
    _data_store[id] = {
        'ui_id': ui_id,
        'namelist': namelist,
        'datalist': list(datalist)
    }

    if not hasattr(start_interactive_site, '_started'):
        start_interactive_site._started = True

        thread = threading.Thread(
            target=lambda: app.run(debug=False, port=5000)
        )
        thread.daemon = True
        thread.start()

        webbrowser.open("http://localhost:5000")

        print("✅ الموقع يعمل على http://localhost:5000")

    else:
        print(f"🔄 تم تحديث بيانات id: {id}")