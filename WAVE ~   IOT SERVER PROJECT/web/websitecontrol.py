import threading
import datetime
import psutil
import os
from flask import Flask, render_template_string, request, session, redirect, url_for

def start_dashboard(active_dict, ip):
    app = Flask(__name__)
    app.secret_key = "enterprise_secure_key_99"

    def get_layout(content, active_page):
        # إضافة وسم viewport لإصلاح العرض على الهاتف + إضافة التحديث التلقائي
        base_style = """
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="refresh" content="2"> 
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            body { background-color: #f4f7f6; font-family: 'Segoe UI', sans-serif; margin: 0; padding: 0; }
            .sidebar { height: 100vh; width: 250px; position: fixed; background: #212529; color: white; padding-top: 20px; z-index: 1000; }
            .sidebar a { padding: 15px 25px; text-decoration: none; color: #adb5bd; display: block; border-left: 4px solid transparent; }
            .sidebar a:hover, .sidebar a.active { color: white; background: #343a40; border-left: 4px solid #0d6efd; }
            .content { margin-left: 250px; padding: 20px; transition: 0.3s; }
            .card { border: none; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); margin-bottom: 20px; }
            .log-text { background: #212529; color: #2ecc71; padding: 15px; border-radius: 8px; font-family: monospace; white-space: pre-wrap; font-size: 14px; }
            
            /* إصلاحات الهاتف */
            @media (max-width: 768px) {
                .sidebar { width: 60px; text-align: center; }
                .sidebar h5, .sidebar span, .sidebar hr { display: none; }
                .sidebar a { padding: 15px 0; }
                .sidebar i { margin: 0 !important; font-size: 20px; }
                .content { margin-left: 60px; padding: 15px; }
            }
        </style>
        """
        sidebar = f"""
        <div class="sidebar">
            <div class="text-center mb-4"><h5><i class="fas fa-wave-square me-2"></i>WAVE</h5></div>
            <hr class="mx-3">
            <a href="/" class="{'active' if active_page=='dash' else ''}" title="Connections"><i class="fas fa-network-wired me-2"></i> <span>Connections</span></a>
            <a href="/logs" class="{'active' if active_page=='logs' else ''}" title="Logs"><i class="fas fa-file-alt me-2"></i> <span>Logs</span></a>
            <a href="/system" class="{'active' if active_page=='sys' else ''}" title="System"><i class="fas fa-microchip me-2"></i> <span>Performance</span></a>
            <a href="/about" class="{'active' if active_page=='about' else ''}" title="About"><i class="fas fa-info-circle me-2"></i> <span>About</span></a>
            <div style="position: absolute; bottom: 20px; width: 100%;"><a href="/logout" class="text-danger"><i class="fas fa-sign-out-alt me-2"></i> <span>Logout</span></a></div>
        </div>
        """
        return base_style + sidebar + f'<div class="content">{content}</div>'

    @app.route('/')
    def index():
        if not session.get('logged'): return redirect(url_for('login'))
        rows = "".join([f'<tr><td><b>{id}</b></td><td><small>{info["ip"]}</small></td><td><span class="badge bg-success">Online</span></td><td><small>{info["last_seen"]}</small></td></tr>' for id, info in active_dict.items()])
        content = f'<h4>Devices</h4><div class="card p-3"><div class="table-responsive"><table class="table align-middle"><thead><tr><th>ID</th><th>IP</th><th>Status</th><th>Sync</th></tr></thead><tbody>{rows if rows else "<tr><td colspan=4 class=text-center>Waiting...</td></tr>"}</tbody></table></div></div>'
        return get_layout(content, 'dash')

    @app.route('/logs')
    @app.route('/logs/<filename>')
    def logs(filename=None):
        if not session.get('logged'): return redirect(url_for('login'))
        files = [f for f in os.listdir('.') if f.endswith('.txt')]
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content_text = f.read()
                content = f'<h5>{filename}</h5><a href="/logs" class="btn btn-sm btn-dark mb-3">Back</a><div class="log-text">{content_text}</div>'
            except: content = '<div class="alert alert-danger">Error</div>'
        else:
            list_items = "".join([f'<a href="/logs/{f}" class="list-group-item list-group-item-action"><i class="fas fa-file-lines me-2 text-primary"></i>{f}</a>' for f in files])
            content = f'<h4>Logs</h4><div class="card"><div class="list-group list-group-flush">{list_items if list_items else "<p class=p-3>No logs</p>"}</div></div>'
        return get_layout(content, 'logs')

    @app.route('/system')
    def system():
        if not session.get('logged'): return redirect(url_for('login'))
        cpu = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory().percent
        content = f"""
        <h4>Performance</h4>
        <div class="card p-3 mb-3">
            <h6>CPU Load: {cpu}%</h6>
            <div class="progress"><div class="progress-bar" style="width: {cpu}%"></div></div>
        </div>
        <div class="card p-3">
            <h6>RAM Usage: {ram}%</h6>
            <div class="progress"><div class="progress-bar bg-success" style="width: {ram}%"></div></div>
        </div>"""
        return get_layout(content, 'sys')

    @app.route('/about')
    def about():
        if not session.get('logged'): return redirect(url_for('login'))
        content = '<div class="card p-4"><h5>Wave IoT v2.9</h5><hr><p class="small text-muted">This system was programmed using the Python language \n It is intended only for Internet of Things devices \n version 1.9</p></div>'
        return get_layout(content, 'about')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST' and request.form['u'] == 'admin' and request.form['p'] == '123':
            session['logged'] = True; return redirect(url_for('index'))
        return '<meta name="viewport" content="width=device-width, initial-scale=1.0"><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet"><div class="container p-4 mt-5"><div class="card p-4 mx-auto" style="max-width:400px"><h3>Login</h3><form method="post"><input name="u" class="form-control mb-2" placeholder="User"><input name="p" type="password" class="form-control mb-3" placeholder="Pass"><button class="btn btn-primary w-100">Login</button></form></div></div>'

    @app.route('/logout')
    def logout():
        session.clear(); return redirect(url_for('login'))

    threading.Thread(target=lambda: app.run(host=f"{ip}", port=80, debug=False, use_reloader=False), daemon=True).start()