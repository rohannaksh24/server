<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instagram Message Sender</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #fff;
            padding: 20px;
            min-height: 100vh;
        }

        .container {
            max-width: 600px;
            margin: 0 auto;
        }

        h1 {
            text-align: center;
            font-size: 2.5rem;
            margin-bottom: 1rem;
            background: linear-gradient(45deg, #ff6b6b, #feca57, #48dbfb, #ff9ff3);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .form-container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 2rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            margin-bottom: 1rem;
        }

        .form-group {
            margin-bottom: 1rem;
        }

        label {
            display: block;
            margin-bottom: 0.5rem;
            color: #333;
            font-weight: 600;
        }

        input, button {
            width: 100%;
            padding: 12px;
            border-radius: 8px;
            border: 2px solid #ddd;
            font-size: 16px;
            transition: all 0.3s ease;
        }

        input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 10px rgba(102, 126, 234, 0.3);
        }

        button {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border: none;
            cursor: pointer;
            font-weight: 600;
            margin-top: 1rem;
        }

        button:hover {
            background: linear-gradient(45deg, #764ba2, #667eea);
            transform: translateY(-2px);
        }

        .message {
            background: rgba(255, 255, 255, 0.9);
            color: #333;
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
            text-align: center;
            border-left: 4px solid #667eea;
        }

        .status-check {
            text-align: center;
            margin: 1rem 0;
        }

        .status-btn {
            background: linear-gradient(45deg, #f093fb, #f5576c);
            padding: 10px 20px;
            border-radius: 25px;
            width: auto;
            margin: 0.5rem;
        }

        .status-result {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
            border-left: 4px solid #28a745;
        }

        .warning {
            background: #fff3cd;
            color: #856404;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
            text-align: center;
            border-left: 4px solid #ffc107;
        }

        @media (max-width: 600px) {
            h1 {
                font-size: 2rem;
            }
            .form-container {
                padding: 1rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Instagram Message Sender</h1>

        {% if message %}
        <div class="message">
            <h3>{{ message }}</h3>
            {% if request_id %}
            <div class="status-check">
                <button class="status-btn" onclick="checkStatus('{{ request_id }}')">🔄 Check Status</button>
                <div id="statusResult"></div>
            </div>
            {% endif %}
        </div>
        {% endif %}

        <div class="warning">
            ⚠️ Important: Use responsibly. Ensure you have permission to send messages.
        </div>

        <div class="form-container">
            <form action="/" method="POST" enctype="multipart/form-data">
                <div class="form-group">
                    <label for="username">Instagram Username</label>
                    <input type="text" name="username" required placeholder="Your Instagram username">
                </div>

                <div class="form-group">
                    <label for="password">Instagram Password</label>
                    <input type="password" name="password" required placeholder="Your Instagram password">
                </div>

                <div class="form-group">
                    <label for="recipient">Target Username</label>
                    <input type="text" name="recipient" required placeholder="Target Instagram username">
                </div>

                <div class="form-group">
                    <label for="interval">Interval (seconds)</label>
                    <input type="number" name="interval" required value="10" min="5" placeholder="Seconds between messages">
                </div>

                <div class="form-group">
                    <label for="haters_name">Sender Name</label>
                    <input type="text" name="haters_name" required placeholder="Name to show in messages">
                </div>

                <div class="form-group">
                    <label for="message_file">Message File (.txt)</label>
                    <input type="file" name="message_file" accept=".txt" required>
                </div>

                <button type="submit">🚀 Start Sending Messages</button>
            </form>
        </div>
    </div>

    <script>
        function checkStatus(requestId) {
            fetch('/status/' + requestId)
                .then(response => response.json())
                .then(data => {
                    const statusDiv = document.getElementById('statusResult');
                    statusDiv.innerHTML = `<div class="status-result">${data.status}</div>`;
                })
                .catch(error => {
                    document.getElementById('statusResult').innerHTML = 
                        '<div style="color: red; padding: 10px;">Error checking status</div>';
                });
        }

        {% if request_id %}
        setTimeout(() => checkStatus('{{ request_id }}'), 3000);
        setInterval(() => checkStatus('{{ request_id }}'), 5000);
        {% endif %}
    </script>
</body>
</html>
