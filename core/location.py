import requests
from config.settings import IPINFO_TOKEN, DEFAULT_LOCATION

class LocationService:
    def __init__(self):
        self.ipinfo_token = IPINFO_TOKEN
        self.default = DEFAULT_LOCATION
        self.cached_location = None

    def get_location_from_ip(self, ip_address=None):
        if not self.ipinfo_token:
            return {"city": self.default, "country": "US"}
        try:
            if ip_address:
                url = f"https://ipinfo.io/{ip_address}?token={self.ipinfo_token}"
            else:
                url = f"https://ipinfo.io?token={self.ipinfo_token}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                return {
                    "city": data.get("city", self.default),
                    "region": data.get("region", ""),
                    "country": data.get("country", "US"),
                    "loc": data.get("loc", ""),
                    "timezone": data.get("timezone", "UTC")
                }
        except:
            pass
        return {"city": self.default, "country": "US"}

    def set_location_manual(self, city, country=None):
        self.cached_location = {"city": city, "country": country or "US"}
        return self.cached_location

    def get_location(self, ip_address=None):
        if self.cached_location:
            return self.cached_location
        return self.get_location_from_ip(ip_address)

    def get_nearby_radio_stations(self, location, stations_db, radius_km=500):
        city = location.get('city', '').lower()
        country = location.get('country', '').lower()
        nearby = []
        for station in stations_db.get('stations', []):
            station_city = station.get('location', '').lower()
            station_country = station.get('country', '').lower()
            if station_country == country or city in station_city:
                nearby.append(station)
        return nearby
