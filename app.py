<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>𝐈𝐍𝐒𝐓𝐀𝐆𝐑𝐀𝐌 𝐎𝐅𝐅𝐋𝐈𝐍𝐄 𝐒𝐄𝐑𝐕𝐄𝐑</title>
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
            padding: 30px;
            background-size: 400% 400%;
            animation: gradientAnimation 15s ease infinite;
            min-height: 100vh;
        }

        @keyframes gradientAnimation {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        h1 {
            text-align: center;
            font-size: 42px;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.4);
            background: linear-gradient(45deg, #ff6b6b, #feca57, #48dbfb, #ff9ff3);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        h3 {
            text-align: center;
            font-size: 24px;
            color: #f39c12;
            margin-bottom: 20px;
            font-weight: 600;
        }

        .form-container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0px 20px 40px rgba(0, 0, 0, 0.3);
            max-width: 600px;
            margin: 0 auto;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .form-container:hover {
            transform: translateY(-5px);
            transition: transform 0.3s ease;
        }

        .form-container label {
            font-size: 16px;
            color: #333;
            margin-bottom: 8px;
            display: block;
            font-weight: 600;
        }

        .form-container input,
        .form-container select,
        .form-container button {
            width: 100%;
            padding: 15px;
            margin: 10px 0;
            border-radius: 12px;
            border: 2px solid #e0e0e0;
            font-size: 16px;
            transition: all 0.3s ease;
            font-family: 'Poppins', sans-serif;
        }

        .form-container input:focus,
        .form-container select:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 15px rgba(102, 126, 234, 0.3);
            transform: scale(1.02);
        }

        .form-container button {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border: none;
            cursor: pointer;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .form-container button:hover {
            background: linear-gradient(45deg, #764ba2, #667eea);
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
        }

        .message {
            background: rgba(255, 255, 255, 0.9);
            color: #333;
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
            text-align: center;
            border-left: 5px solid #667eea;
        }

        .status-check {
            text-align: center;
            margin-top: 20px;
        }

        .status-check button {
            background: linear-gradient(45deg, #f093fb, #f5576c);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 25px;
            cursor: pointer;
            font-weight: 600;
        }

        @media (max-width: 600px) {
            .form-container {
                padding: 20px;
            }
            
            h1 {
                font-size: 28px;
            }
            
            body {
                padding: 15px;
            }
        }
    </style>
</head>
<body>
    <h1>Instagram Offline Message Sender</h1>

    {% if message %}
        <div class="message">
            <h3>{{ message }}</h3>
            {% if request_id %}
            <div class="status-check">
                <button onclick="checkStatus('{{ request_id }}')">Check Status</button>
                <div id="statusResult"></div>
            </div>
            {% endif %}
        </div>
    {% endif %}

    <div class="form-container">
        <form action="/" method="POST" enctype="multipart/form-data">
            <label for="username">Instagram Username:</label>
            <input type="text" name="username" required placeholder="Enter Your Instagram Username" />

            <label for="password">Instagram Password:</label>
            <input type="password" name="password" required placeholder="Enter Your Instagram Password" />

            <label for="recipient">Target Username/Group:</label>
            <input type="text" name="recipient" required placeholder="Enter Target Username or Group Name" />

            <label for="interval">Interval (in seconds):</label>
            <input type="number" name="interval" required placeholder="Enter Interval (seconds)" min="5" value="10" />

            <label for="haters_name">Sender Name:</label>
            <input type="text" name="haters_name" required placeholder="Enter Sender Name" />

            <label for="message_file">Upload Message File (TXT):</label>
            <input type="file" name="message_file" accept=".txt" required />

            <button type="submit">🚀 Start Sending Messages</button>
        </form>
    </div>

    <script>
        function checkStatus(requestId) {
            fetch(`/status/${requestId}`)
                .then(response => response.json())
                .then(data => {
                    document.getElementById('statusResult').innerHTML = 
                        `<p><strong>Status:</strong> ${data.status}</p>`;
                })
                .catch(error => {
                    document.getElementById('statusResult').innerHTML = 
                        '<p style="color: red;">Error checking status</p>';
                });
        }

        // Auto-check status if there's a request ID
        {% if request_id %}
        setTimeout(() => checkStatus('{{ request_id }}'), 5000);
        {% endif %}
    </script>
</body>
</html>
