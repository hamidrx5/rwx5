# pages.py

LOGIN_HTML = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ورود به پنل X4G</title>
    <style>
        body { font-family: system-ui, sans-serif; background: #0f172a; color: #fff; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }
        .card { background: #1e293b; padding: 2rem; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); width: 100%; max-width: 320px; text-align: center; }
        input { width: 100%; padding: 10px; margin: 12px 0; border-radius: 6px; border: 1px solid #334155; background: #0f172a; color: #fff; box-sizing: border-box; }
        button { width: 100%; padding: 10px; background: #2563eb; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; }
        button:hover { background: #1d4ed8; }
    </style>
</head>
<body>
    <div class="card">
        <h2>ورود به پنل X4G</h2>
        <input type="password" id="pw" placeholder="رمز عبور">
        <button onclick="login()">ورود</button>
    </div>
    <script>
        async function login() {
            const pw = document.getElementById('pw').value;
            const res = await fetch('/api/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({password: pw})
            });
            if (res.ok) window.location.href = '/dashboard';
            else alert('رمز عبور اشتباه است');
        }
    </script>
</body>
</html>"""

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>داشبورد X4G</title>
    <style>
        body { font-family: system-ui, sans-serif; background: #0f172a; color: #fff; padding: 20px; margin: 0; }
        .container { max-width: 800px; margin: 0 auto; }
        .card { background: #1e293b; padding: 1.5rem; border-radius: 10px; margin-bottom: 20px; }
        h1 { color: #38bdf8; }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h1>مدیریت پنل X4G</h1>
            <p>پروژه با موفقیت فعال شد.</p>
        </div>
    </div>
</body>
</html>"""

def get_public_page_html(uuid_key: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>اشتراک X4G</title>
    <style>
        body {{ font-family: system-ui, sans-serif; background: #0f172a; color: #fff; padding: 20px; text-align: center; }}
        .box {{ background: #1e293b; padding: 20px; border-radius: 10px; display: inline-block; }}
    </style>
</head>
<body>
    <div class="box">
        <h2>صفحه اشتراک اختصاصی</h2>
        <p>شناسه: {uuid_key}</p>
    </div>
</body>
</html>"""
