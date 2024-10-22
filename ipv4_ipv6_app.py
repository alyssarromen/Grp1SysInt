from flask import Flask, render_template_string, jsonify, request
import requests
import speedtest

app = Flask(__name__)

# HTML template with IP info, a button to trigger speed test, input form for custom IP, and a button to show own IP info
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IP Info with Speed Test</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Montserrat', sans-serif;
            font-size: 15px;
            background-color: #f8f9fa;
            color: #343a40;
            padding: 20px;
            margin: 0;
        }
        h1 {
            font-size: 30px;
            color: #009113;
            text-align: center;
            margin-bottom: 20px;
        }
        .container {
            max-width: 800px;
            margin: auto;
            padding: 20px;
            background-color: #ffffff;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        .info {
            background-color: #e9ecef;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
        }
        .info div {
            flex: 1;
            margin: 0 10px;
        }
        .info h2 {
            color: #495057;
        }
        .info p {
            margin: 5px 0;
        }
        .error {
            color: #dc3545;
        }
        #map {
            height: 400px;
            width: 100%;
            border-radius: 8px;
            margin-top: 20px;
        }
        footer {
            text-align: center;
            margin-top: 20px;
            font-size: 0.9em;
            color: #6c757d;
        }
        .speedtest-section {
            margin-top: 20px;
        }
        button {
            background-color: #009113;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 15px;
        }
        button:hover {
            background-color: #007c0d;
        }
        form {
            margin-bottom: 20px;
        }
        input[type="text"] {
            padding: 10px;
            width: 70%;
            font-size: 15px;
            border-radius: 5px;
            border: 1px solid #ccc;
        }
        input[type="submit"] {
            padding: 10px 15px;
            font-size: 15px;
            background-color: #009113;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        .return-button {
            margin-top: 20px;
            background-color: #007bff;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 5px;
            cursor: pointer;
            text-align: center;
            font-size: 15px;
        }
        .return-button:hover {
            background-color: #0056b3;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Public IP Information</h1>
        <form action="/get_ip_info" method="POST">
            <input type="text" name="input_ip" placeholder="Enter an IPv4 or IPv6 address">
            <input type="submit" value="Get IP Info">
        </form>

        <button class="return-button" onclick="window.location.href='/'">Show My IP Info</button>

        <div class="info">
            <div>
                {% if ipv4_error %}
                    <p class="error">{{ ipv4_error }}</p>
                {% else %}
                    <h2>IPv4 Information</h2>
                    <p><strong>IP Address:</strong> {{ ipv4_info.get('ip') }}</p>
                    <p><strong>City:</strong> {{ ipv4_info.get('city') }}</p>
                    <p><strong>Region:</strong> {{ ipv4_info.get('region') }}</p>
                    <p><strong>Country:</strong> {{ ipv4_info.get('country_name') }}</p>
                    <p><strong>Latitude:</strong> {{ ipv4_info.get('latitude') }}</p>
                    <p><strong>Longitude:</strong> {{ ipv4_info.get('longitude') }}</p>
                    <p><strong>ISP:</strong> {{ ipv4_info.get('org') }}</p>
                    <p><strong>ASN:</strong> {{ ipv4_info.get('asn') }}</p>
                {% endif %}
            </div>

            <div>
                {% if ipv6_error %}
                    <p class="error">{{ ipv6_error }}</p>
                {% else %}
                    <h2>IPv6 Information</h2>
                    <p><strong>IP Address:</strong> {{ ipv6_info.get('ip') }}</p>
                    <p><strong>City:</strong> {{ ipv6_info.get('city') }}</p>
                    <p><strong>Region:</strong> {{ ipv6_info.get('region') }}</p>
                    <p><strong>Country:</strong> {{ ipv6_info.get('country_name') }}</p>
                    <p><strong>Latitude:</strong> {{ ipv6_info.get('latitude') }}</p>
                    <p><strong>Longitude:</strong> {{ ipv6_info.get('longitude') }}</p>
                    <p><strong>ISP:</strong> {{ ipv6_info.get('org') }}</p>
                    <p><strong>ASN:</strong> {{ ipv6_info.get('asn') }}</p>
                {% endif %}
            </div>
        </div>

        <div class="speedtest-section">
            <h2>Internet Speed Test</h2>
            <button onclick="runSpeedTest()">Run Speed Test</button>
            <p id="speed-result"></p>
        </div>

        <div id="map"></div>
    </div>

    <footer>
        <p>4ITF Group 1 System Integration and Architecture</p>
    </footer>

    <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
    <script>
        var latitude = {{ ipv4_info.get('latitude') or ipv6_info.get('latitude') or 0 }};
        var longitude = {{ ipv4_info.get('longitude') or ipv6_info.get('longitude') or 0 }};

        var map = L.map('map').setView([latitude, longitude], 13);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 18,
            attribution: 'OpenStreetMap'
        }).addTo(map);

        {% if ipv4_info %}
        L.marker([{{ ipv4_info.get('latitude') }}, {{ ipv4_info.get('longitude') }}]).addTo(map)
            .bindPopup("<b>IPv4 Location:</b><br>{{ ipv4_info.get('city') }}, {{ ipv4_info.get('region') }}.")
            .openPopup();
        {% endif %}

        {% if ipv6_info %}
        L.marker([{{ ipv6_info.get('latitude') }}, {{ ipv6_info.get('longitude') }}]).addTo(map)
            .bindPopup("<b>IPv6 Location:</b><br>{{ ipv6_info.get('city') }}, {{ ipv6_info.get('region') }}.")
            .openPopup();
        {% endif %}

        function runSpeedTest() {
            document.getElementById("speed-result").textContent = "Running speed test...";
            fetch('/run_speedtest')
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        document.getElementById("speed-result").textContent = "Error: " + data.error;
                    } else {
                        document.getElementById("speed-result").textContent = 
                            "Download Speed: " + data.download_speed + " Mbps, " +
                            "Upload Speed: " + data.upload_speed + " Mbps";
                    }
                });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def get_ip_info():
    ipv4_url = 'https://api.ipify.org?format=json'
    ipv6_url = 'https://api64.ipify.org?format=json'

    try:
        # Get IPv4 and IPv6 information
        ipv4_response = requests.get(ipv4_url)
        ipv4_address = ipv4_response.json().get('ip') if ipv4_response.status_code == 200 else None
        ipv4_info = requests.get(f'https://ipapi.co/{ipv4_address}/json/').json() if ipv4_address else None
        ipv4_error = None if ipv4_info else "Failed to retrieve IPv4 information"

        ipv6_response = requests.get(ipv6_url)
        ipv6_address = ipv6_response.json().get('ip') if ipv6_response.status_code == 200 else None
        ipv6_info = requests.get(f'https://ipapi.co/{ipv6_address}/json/').json() if ipv6_address else None
        ipv6_error = None if ipv6_info else "Failed to retrieve IPv6 information"

        return render_template_string(html_template, ipv4_info=ipv4_info, ipv4_error=ipv4_error,
                                      ipv6_info=ipv6_info, ipv6_error=ipv6_error)

    except Exception as e:
        return render_template_string(html_template, ipv4_info=None, ipv4_error=f"Error occurred: {e}",
                                      ipv6_info=None, ipv6_error=f"Error occurred: {e}")


@app.route('/get_ip_info', methods=['POST'])
def get_custom_ip_info():
    input_ip = request.form.get('input_ip')
    try:
        ip_info = requests.get(f'https://ipapi.co/{input_ip}/json/').json()
        if 'error' in ip_info:
            return render_template_string(html_template, ipv4_info=None, ipv6_info=None, ipv4_error=ip_info['reason'], ipv6_error=ip_info['reason'])
        else:
            return render_template_string(html_template, ipv4_info=ip_info, ipv6_info=ip_info)
    except Exception as e:
        return render_template_string(html_template, ipv4_info=None, ipv6_info=None, ipv4_error=f"Error occurred: {e}", ipv6_error=f"Error occurred: {e}")


@app.route('/run_speedtest')
def run_speedtest():
    try:
        st = speedtest.Speedtest()
        download_speed = round(st.download() / 10**6, 2)  # Convert to Mbps
        upload_speed = round(st.upload() / 10**6, 2)  # Convert to Mbps
        return jsonify(download_speed=download_speed, upload_speed=upload_speed)
    except Exception as e:
        return jsonify(error=str(e))


if __name__ == "__main__":
    app.run(debug=True)
