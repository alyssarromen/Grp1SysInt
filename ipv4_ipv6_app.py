from flask import Flask, render_template_string
import requests

app = Flask(__name__)

# HTML template with the map using Leaflet.js
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IP Information with Map</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400&display=swap" rel="stylesheet"> <!-- Montserrat Font -->
    <style>
        body {
            font-family: 'Montserrat', sans-serif; /* Use Montserrat font */
            font-size: 15px; /* Set body font size */
            background-color: #f8f9fa;
            color: #343a40;
            padding: 20px;
            margin: 0;
        }
        h1 {
            font-size: 30px; /* Set header font size */
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
            margin: 0 10px; /* Add margin between columns */
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
    </style>
</head>
<body>
    <div class="container">
        <h1>Public IP Information</h1>
        <div class="info">
            <div> <!-- IPv4 Column -->
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
                    <p><strong >ASN:</strong> {{ ipv4_info.get('asn') }}</p>
                {% endif %}
            </div>

            <div> <!-- IPv6 Column -->
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

        <div id="map"></div>  <!-- Map container -->
    </div>

    <footer>
        <p>Powered by Flask and Leaflet.js</p>
    </footer>

    <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
    <script>
        // Initialize the map
        var map = L.map('map').setView([{{ ipv4_info.get('latitude') or ipv6_info.get('latitude') }},
                                         {{ ipv4_info.get('longitude') or ipv6_info.get('longitude') }}], 13);

        // Load and display tile layer from OpenStreetMap
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 18,
            attribution: 'OpenStreetMap'
        }).addTo(map);

        // Add a marker for IPv4 if available
        {% if ipv4_info %}
        L.marker([{{ ipv4_info.get('latitude') }}, {{ ipv4_info.get('longitude') }}]).addTo(map)
            .bindPopup("<b>IPv4 Location:</b><br>{{ ipv4_info.get('city') }}, {{ ipv4_info.get('region') }}.")
            .openPopup();
        {% endif %}

        // Add a marker for IPv6 if available
        {% if ipv6_info %}
        L.marker([{{ ipv6_info.get('latitude') }}, {{ ipv6_info.get('longitude') }}]).addTo(map)
            .bindPopup("<b>IPv6 Location:</b><br>{{ ipv6_info.get('city') }}, {{ ipv6_info.get('region') }}.")
            .openPopup();
        {% endif %}
    </script>
</body>
</html>
"""

@app.route('/')
def get_ip_info():
    # API endpoints for IPv4 and IPv6
    ipv4_url = 'https://api.ipify.org?format=json'  # Explicit IPv4
    ipv6_url = 'https://api64.ipify.org?format=json'  # Explicit IPv6

    try:
        # Get IPv4 address
        ipv4_response = requests.get(ipv4_url)
        ipv4_address = ipv4_response.json().get('ip') if ipv4_response.status_code == 200 else None

        # Fetch full details for IPv4 from ipapi
        ipv4_info = requests.get(f'https://ipapi.co/{ipv4_address}/json/').json() if ipv4_address else None
        ipv4_error = None if ipv4_info else "Failed to retrieve IPv4 information"

        # Get IPv6 address
        ipv6_response = requests.get(ipv6_url)
        ipv6_address = ipv6_response.json().get('ip') if ipv6_response.status_code == 200 else None

        # Fetch full details for IPv6 from ipapi
        ipv6_info = requests.get(f'https://ipapi.co/{ipv6_address}/json/').json() if ipv6_address else None
        ipv6_error = None if ipv6_info else "Failed to retrieve IPv6 information"

        # Render the template with the IPv4 and IPv6 data
        return render_template_string(html_template, ipv4_info=ipv4_info, ipv4_error=ipv4_error, ipv6_info=ipv6_info, ipv6_error=ipv6_error)
    except Exception as e:
        return render_template_string(html_template, ipv4_info=None, ipv4_error=f"Error occurred: {e}",
                                      ipv6_info=None, ipv6_error=f"Error occurred: {e}")

if __name__ == "_main_":
    app.run(debug=True)