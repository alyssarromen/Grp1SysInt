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
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f4f4; color: #333; padding: 20px; }
        h1 { color: #6a0dad; }
        .info { background-color: #e0f7fa; padding: 15px; border-radius: 10px; margin-bottom: 20px; }
        .info p { margin: 5px 0; }
        .error { color: red; }
        #map { height: 400px; width: 100%; border-radius: 10px; }
    </style>
</head>
<body>
    <h1>Public IP Information</h1>
    <div class="info">
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

    <div id="map"></div>  <!-- Map container -->

    <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
    <script>
        // Initialize the map
        var map = L.map('map').setView([{{ ipv4_info.get('latitude') or ipv6_info.get('latitude') }},
                                         {{ ipv4_info.get('longitude') or ipv6_info.get('longitude') }}], 13);

        // Load and display tile layer from OpenStreetMap
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 18,
            attribution: '© OpenStreetMap'
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

if __name__ == "__main__":
    app.run(debug=True)
