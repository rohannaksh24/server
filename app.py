import os
import requests
import time
import random
from flask import Flask, request, render_template_string, session
from threading import Thread

app = Flask(__name__)
app.secret_key = 'your_secret_key_here_12345'

user_sessions = {}
stop_flags = {}

user_name = "𝐀𝐀𝐇𝐀𝐍"
whatsapp_no = "+8542869382"
facebook_link = "https://www.facebook.com/profile.php?id=61581357481812"

def read_comments_from_file(uploaded_file):
    comments = uploaded_file.read().decode("utf-8").splitlines()
    return [comment.strip() for comment in comments if comment.strip()]

def read_tokens_from_file(uploaded_file=None):
    tokens = []
    if uploaded_file:
        lines = uploaded_file.read().decode("utf-8").splitlines()
        tokens = [line.strip() for line in lines if line.strip()]
    else:
        token_files = ['tokens.txt', 'rishi.txt', 'token_file.txt']
        for token_file in token_files:
            if os.path.exists(token_file):
                with open(token_file, 'r') as file:
                    tokens = [line.strip() for line in file if line.strip()]
                break
    return tokens

def read_cookies_from_file(uploaded_file=None):
    cookies = []
    if uploaded_file:
        lines = uploaded_file.read().decode("utf-8").splitlines()
        cookies = [line.strip() for line in lines if line.strip()]
    else:
        cookie_files = ['cookies.txt', 'cookie_file.txt']
        for cookie_file in cookie_files:
            if os.path.exists(cookie_file):
                with open(cookie_file, 'r') as file:
                    cookies = [line.strip() for line in file if line.strip()]
                break
    return cookies

def post_comment(user_id):
    while True:
        user_data = user_sessions.get(user_id, {})
        if not user_data:
            print(f"User {user_id} data not found!")
            time.sleep(10)
            continue

        post_id = user_data.get("post_id")
        speed = user_data.get("speed", 60)
        target_name = user_data.get("target_name")
        comments = user_data.get("comments", [])
        tokens = user_data.get("tokens", [])
        cookies = user_data.get("cookies", [])

        if not comments:
            print("No comments found. Waiting for comments...")
            time.sleep(10)
            continue

        comment_index = 0
        token_index = 0
        cookie_index = 0
        base_retry_delay = 600
        max_retry_delay = 1800

        while True:
            if stop_flags.get(user_id, False):
                print(f"User {user_id} stopped commenting.")
                return

            raw_comment = comments[comment_index % len(comments)]
            comment_index += 1

            # Target Name logic
            if target_name:
                if "{name}" in raw_comment:
                    comment = raw_comment.replace("{name}", target_name)
                else:
                    comment = f"{target_name} {raw_comment}"
            else:
                comment = raw_comment

            # Use tokens or cookies
            if tokens:
                token = tokens[token_index % len(tokens)]
                token_index += 1
                params = {"message": comment, "access_token": token}
                url = f"https://graph.facebook.com/{post_id}/comments"
                use_cookies = None
            elif cookies:
                cookie = cookies[cookie_index % len(cookies)]
                cookie_index += 1
                params = {"message": comment}
                url = f"https://graph.facebook.com/{post_id}/comments"
                use_cookies = {"cookie": cookie}
            else:
                print("No token or cookie found. Retrying in 30 seconds...")
                time.sleep(30)
                break

            current_retry_delay = base_retry_delay

            while True:
                try:
                    if tokens:
                        response = requests.post(url, params=params, timeout=10)
                    else:
                        response = requests.post(url, params=params, cookies=use_cookies, timeout=10)
                    if response.status_code == 200:
                        print(f"[{user_id}] Comment posted: {comment}")
                        current_retry_delay = base_retry_delay
                        break
                    else:
                        print(f"[{user_id}] Failed: {response.text}")
                        if '"code":368' in response.text:
                            print(f"Rate limit hit! Waiting for {current_retry_delay//60} minutes...")
                            time.sleep(current_retry_delay)
                            current_retry_delay = min(current_retry_delay * 2, max_retry_delay)
                            continue
                        else:
                            time.sleep(current_retry_delay)
                            current_retry_delay = min(current_retry_delay * 2, max_retry_delay)
                            continue
                except Exception as e:
                    print(f"[{user_id}] Network error: {str(e)}, retrying in {current_retry_delay}s")
                    time.sleep(current_retry_delay)
                    current_retry_delay = min(current_retry_delay * 2, max_retry_delay)
                    continue

            rand_delay = random.randint(speed, speed + 60)
            print(f"[{user_id}] Waiting {rand_delay} seconds before next comment...")
            time.sleep(rand_delay)

def start_commenting(user_id):
    thread = Thread(target=post_comment, args=(user_id,))
    thread.daemon = True
    thread.start()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_id = session.get('user_id')
        if not user_id:
            user_id = str(time.time())
            session['user_id'] = user_id

        action = request.form.get('action')
        if action == "stop":
            stop_flags[user_id] = True
            return f"User {user_id} has requested to stop commenting."

        post_id = request.form["post_id"]
        speed = int(request.form["speed"])
        speed = max(speed, 60)
        target_name = request.form["target_name"]

        tokens = []
        if request.form.get('single_token'):
            tokens = [request.form.get('single_token')]
        elif 'tokens_file' in request.files and request.files['tokens_file'].filename:
            tokens = read_tokens_from_file(request.files['tokens_file'])
        else:
            tokens = read_tokens_from_file()

        cookies = []
        if request.form.get('single_cookie'):
            cookies = [request.form.get('single_cookie')]
        elif 'cookies_file' in request.files and request.files['cookies_file'].filename:
            cookies = read_cookies_from_file(request.files['cookies_file'])
        else:
            cookies = read_cookies_from_file()

        comments = []
        if 'comments_file' in request.files and request.files['comments_file'].filename:
            comments = read_comments_from_file(request.files['comments_file'])
        else:
            if os.path.exists('comments.txt'):
                with open('comments.txt', 'r', encoding='utf-8') as f:
                    comments = [line.strip() for line in f if line.strip()]

        user_sessions[user_id] = {
            "post_id": post_id,
            "speed": speed,
            "target_name": target_name,
            "comments": comments,
            "tokens": tokens,
            "cookies": cookies
        }

        stop_flags[user_id] = False
        start_commenting(user_id)

        return f"User {user_id} started posting comments!"

    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>🌐 SOCIAL POST SERVER</title>
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            margin: 0;
            padding: 20px;
            background: 
                radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.3) 0%, transparent 50%),
                radial-gradient(circle at 40% 40%, rgba(120, 219, 255, 0.2) 0%, transparent 50%),
                linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
            min-height: 100vh;
            font-family: 'Rajdhani', sans-serif;
            color: #ffffff;
            display: flex;
            flex-direction: column;
            align-items: center;
            position: relative;
            overflow-x: hidden;
        }

        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                linear-gradient(90deg, transparent 79px, rgba(255,255,255,0.03) 81px, transparent 82px),
                linear-gradient(transparent 79px, rgba(255,255,255,0.03) 81px, transparent 82px);
            background-size: 82px 82px;
            pointer-events: none;
            z-index: -1;
        }

        .cyber-grid {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                linear-gradient(90deg, transparent 99px, rgba(0, 255, 255, 0.02) 101px, transparent 102px),
                linear-gradient(transparent 99px, rgba(0, 255, 255, 0.02) 101px, transparent 102px);
            background-size: 102px 102px;
            pointer-events: none;
            z-index: -1;
        }

        .main-container {
            width: 95vw;
            max-width: 500px;
            margin: 20px auto;
            background: rgba(15, 15, 25, 0.85);
            border-radius: 20px;
            box-shadow: 
                0 0 0 1px rgba(0, 255, 255, 0.1),
                0 8px 32px rgba(0, 0, 0, 0.8),
                inset 0 0 20px rgba(0, 255, 255, 0.05);
            padding: 30px 25px;
            border: 1px solid rgba(0, 255, 255, 0.2);
            backdrop-filter: blur(10px);
            position: relative;
            overflow: hidden;
        }

        .main-container::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 2px;
            background: linear-gradient(90deg, transparent, #00ffff, #ff00ff, #00ffff, transparent);
            animation: scanline 3s linear infinite;
        }

        @keyframes scanline {
            0% { left: -100%; }
            100% { left: 100%; }
        }

        h2 {
            font-family: 'Orbitron', sans-serif;
            font-size: 2.4rem;
            background: linear-gradient(135deg, #00ffff 0%, #ff00ff 50%, #00ff88 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 1rem;
            font-weight: 900;
            letter-spacing: 2px;
            text-align: center;
            text-shadow: 0 0 30px rgba(0, 255, 255, 0.5);
            text-transform: uppercase;
            position: relative;
        }

        h2::after {
            content: '';
            position: absolute;
            bottom: -10px;
            left: 50%;
            transform: translateX(-50%);
            width: 100px;
            height: 3px;
            background: linear-gradient(90deg, transparent, #00ffff, #ff00ff, transparent);
            border-radius: 2px;
        }

        .header {
            font-family: 'Orbitron', sans-serif;
            font-size: 1.3rem;
            font-weight: 600;
            margin-bottom: 2rem;
            letter-spacing: 1px;
            text-align: center;
            color: #00ffff;
            text-shadow: 0 0 20px rgba(0, 255, 255, 0.5);
        }

        form {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        .input-group {
            position: relative;
        }

        input[type="text"], input[type="number"], input[type="file"] {
            font-size: 1.1rem;
            padding: 18px 16px;
            border-radius: 12px;
            border: 2px solid rgba(0, 255, 255, 0.3);
            outline: none;
            background: rgba(10, 10, 20, 0.8);
            color: #ffffff;
            width: 100%;
            transition: all 0.3s ease;
            font-family: 'Rajdhani', sans-serif;
            font-weight: 500;
        }

        input:focus {
            border-color: #ff00ff;
            box-shadow: 
                0 0 20px rgba(255, 0, 255, 0.4),
                inset 0 0 20px rgba(255, 0, 255, 0.1);
            transform: translateY(-2px);
        }

        input::placeholder {
            color: rgba(255, 255, 255, 0.5);
        }

        label {
            font-size: 1.1rem;
            color: #00ff88;
            font-weight: 600;
            margin-bottom: 8px;
            display: block;
            text-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
            font-family: 'Orbitron', sans-serif;
            letter-spacing: 1px;
        }

        .btn-row {
            display: flex;
            gap: 15px;
            margin-top: 25px;
        }

        button {
            flex: 1;
            font-size: 1.2rem;
            font-weight: 700;
            padding: 20px 0;
            border: none;
            border-radius: 15px;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            font-family: 'Orbitron', sans-serif;
            letter-spacing: 1px;
            text-transform: uppercase;
        }

        button::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
            transition: left 0.5s;
        }

        button:hover::before {
            left: 100%;
        }

        .start-btn {
            background: linear-gradient(135deg, #00b09b 0%, #96c93d 100%);
            color: #000;
            box-shadow: 0 8px 25px rgba(0, 176, 155, 0.4);
        }

        .start-btn:hover {
            transform: translateY(-3px) scale(1.02);
            box-shadow: 0 12px 35px rgba(0, 176, 155, 0.6);
        }

        .stop-btn {
            background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%);
            color: #fff;
            box-shadow: 0 8px 25px rgba(255, 65, 108, 0.4);
        }

        .stop-btn:hover {
            transform: translateY(-3px) scale(1.02);
            box-shadow: 0 12px 35px rgba(255, 65, 108, 0.6);
        }

        .footer {
            margin-top: 35px;
            font-size: 1.1rem;
            text-align: center;
            padding: 25px;
            background: rgba(10, 10, 20, 0.8);
            border-radius: 15px;
            width: 95vw;
            max-width: 500px;
            border: 1px solid rgba(0, 255, 255, 0.2);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
            position: relative;
        }

        .footer::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, transparent, #00ffff, #ff00ff, #00ffff, transparent);
        }

        .footer .lime {
            color: #39ff14;
            font-size: 1.2rem;
            font-weight: bold;
            margin-top: 1em;
            display: block;
            letter-spacing: 1.5px;
            text-shadow: 0 0 20px rgba(57, 255, 20, 0.7);
            font-family: 'Orbitron', sans-serif;
        }

        .footer .contact-row {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
            margin-bottom: 15px;
            padding: 12px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            margin: 12px 0;
            border: 1px solid rgba(0, 255, 255, 0.1);
        }

        .footer .contact-row .fa-whatsapp {
            color: #25d366;
            font-size: 1.8em;
            filter: drop-shadow(0 0 10px rgba(37, 211, 102, 0.5));
        }

        .footer .contact-row .fa-facebook {
            color: #1877f3;
            font-size: 1.8em;
            filter: drop-shadow(0 0 10px rgba(24, 119, 243, 0.5));
        }

        .footer .fb-link {
            color: #00ffff;
            text-decoration: none;
            font-weight: 600;
            margin-left: 5px;
            transition: all 0.3s ease;
            text-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
        }

        .footer .fb-link:hover {
            color: #ff00ff;
            text-shadow: 0 0 15px rgba(255, 0, 255, 0.7);
        }

        .glow-text {
            text-shadow: 0 0 10px currentColor;
        }

        @media (max-width: 600px) {
            .main-container {
                padding: 20px 15px;
                max-width: 90vw;
                border-radius: 15px;
            }
            h2 { font-size: 1.8rem; }
            .header { font-size: 1.1rem; }
            button, input { 
                font-size: 1rem; 
                padding: 16px 14px; 
            }
            .footer {
                padding: 20px;
                margin-top: 25px;
            }
        }

        /* Cyberpunk animations */
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
        }

        .main-container {
            animation: float 6s ease-in-out infinite;
        }

        .pulse {
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(0, 255, 255, 0.4); }
            70% { box-shadow: 0 0 0 15px rgba(0, 255, 255, 0); }
            100% { box-shadow: 0 0 0 0 rgba(0, 255, 255, 0); }
        }
    </style>
</head>
<body>
    <div class="cyber-grid"></div>
    
    <div class="main-container pulse">
        <h2>🚀 POST SERVER PRO</h2>
        <div class="header">CYBER SOCIAL AUTOMATION SYSTEM<br>Developer: <span class="glow-text" style="color: #00ffff;">𝐀𝐀𝐇𝐀𝐍</span></div>
        <form action="/" method="post" enctype="multipart/form-data">
            <div class="input-group">
                <label>📱 POST ID</label>
                <input type="text" name="post_id" placeholder="Enter Facebook Post ID" required>
            </div>

            <div class="input-group">
                <label>⏱️ SPEED (Seconds)</label>
                <input type="number" name="speed" placeholder="Enter Speed (Minimum 60)" min="60" value="60" required>
            </div>

            <div class="input-group">
                <label>🎯 TARGET NAME</label>
                <input type="text" name="target_name" placeholder="Enter Target Username" required>
            </div>

            <div class="input-group">
                <label>🔑 SINGLE TOKEN (Optional)</label>
                <input type="text" name="single_token" placeholder="Enter Facebook Token">
            </div>

            <div class="input-group">
                <label>📁 TOKEN FILE</label>
                <input type="file" name="tokens_file" accept=".txt">
            </div>

            <div class="input-group">
                <label>🍪 SINGLE COOKIE (Optional)</label>
                <input type="text" name="single_cookie" placeholder="Enter Facebook Cookie">
            </div>

            <div class="input-group">
                <label>📁 COOKIE FILE</label>
                <input type="file" name="cookies_file" accept=".txt">
            </div>

            <div class="input-group">
                <label>💬 COMMENTS FILE</label>
                <input type="file" name="comments_file" accept=".txt" required>
            </div>

            <div class="btn-row">
                <button type="submit" name="action" value="start" class="start-btn">
                    <i class="fas fa-rocket"></i> LAUNCH
                </button>
                <button type="submit" name="action" value="stop" class="stop-btn">
                    <i class="fas fa-stop"></i> ABORT
                </button>
            </div>
        </form>
    </div>

    <div class="footer">
        <div class="contact-row">
            <i class="fab fa-whatsapp glow-text"></i>
            <span>CONTACT: <b class="glow-text" style="color: #25d366;">8542869382</b></span>
        </div>
        <div class="contact-row">
            <i class="fab fa-facebook glow-text"></i>
            <a class="fb-link" href="https://www.facebook.com/profile.php?id=61581357481812" target="_blank">
                FACEBOOK PROFILE
            </a>
        </div>
        <span class="lime">⚡ CYBER AUTOMATION SYSTEM ⚡</span>
    </div>
</body>
</html>
''')

@app.route("/health")
def health_check():
    return "Server is running!"

if __name__ == "__main__":
    port = os.getenv("PORT", 5000)
    app.run(host="0.0.0.0", port=int(port), debug=False, threaded=True)
