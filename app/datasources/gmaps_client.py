import os
import requests
import time
from typing import Dict, List, Optional, Tuple

class GoogleMapsClient:
    """Google Maps API client for Geocoding and Places operations"""

    def __init__(self):
        self.api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        if not self.api_key:
            raise RuntimeError("GOOGLE_MAPS_API_KEY environment variable is required")

        self.base_url = "https://maps.googleapis.com/maps/api"
        self.session = requests.Session()

    def geocode(self, address: str, region: str = "th") -> Optional[Tuple[float, float]]:
        """
        Convert address to latitude, longitude coordinates

        Args:
            address: Address to geocode (e.g., "หมู่บ้านกาญจนทรัพย์ แกรนด์ หาดใหญ่")
            region: Country code for bias (default: "th" for Thailand)

        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        url = f"{self.base_url}/geocode/json"
        params = {
            "address": address,
            "region": region,
            "key": self.api_key
        }

        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data["status"] == "OK" and data["results"]:
                location = data["results"][0]["geometry"]["location"]
                return (location["lat"], location["lng"])
            else:
                print(f"Geocoding failed for '{address}': {data.get('status', 'Unknown error')}")
                return None

        except requests.RequestException as e:
            print(f"Geocoding request failed for '{address}': {e}")
            return None

    def find_nearby_places(
        self,
        lat: float,
        lng: float,
        keyword: str = "7-Eleven",
        radius: int = 3000,
        place_type: str = "convenience_store"
    ) -> List[Dict]:
        """
        Find nearby places using Google Places API

        Args:
            lat: Latitude of center point
            lng: Longitude of center point
            keyword: Search keyword (default: "7-Eleven")
            radius: Search radius in meters (default: 3000m)
            place_type: Google Places type (default: "convenience_store")

        Returns:
            List of place dictionaries with name, place_id, address, distance
        """
        url = f"{self.base_url}/place/nearbysearch/json"
        params = {
            "location": f"{lat},{lng}",
            "radius": radius,
            "keyword": keyword,
            "type": place_type,
            "key": self.api_key
        }

        try:
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            if data["status"] == "OK":
                places = []
                for result in data.get("results", []):
                    place_info = {
                        "name": result.get("name", ""),
                        "place_id": result.get("place_id", ""),
                        "address": result.get("vicinity", ""),
                        "rating": result.get("rating", 0),
                        "user_ratings_total": result.get("user_ratings_total", 0),
                        "types": result.get("types", []),
                        "geometry": result.get("geometry", {}),
                        "price_level": result.get("price_level"),
                        "permanently_closed": result.get("permanently_closed", False)
                    }

                    # Calculate distance from original point
                    if "geometry" in result and "location" in result["geometry"]:
                        place_lat = result["geometry"]["location"]["lat"]
                        place_lng = result["geometry"]["location"]["lng"]
                        distance = self._calculate_distance(lat, lng, place_lat, place_lng)
                        place_info["distance_km"] = round(distance, 2)

                    places.append(place_info)

                # Sort by distance
                places.sort(key=lambda x: x.get("distance_km", float('inf')))
                return places
            else:
                print(f"Places search failed: {data.get('status', 'Unknown error')}")
                return []

        except requests.RequestException as e:
            print(f"Places search request failed: {e}")
            return []

    def get_place_details(self, place_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific place

        Args:
            place_id: Google Place ID

        Returns:
            Detailed place information or None if not found
        """
        url = f"{self.base_url}/place/details/json"
        params = {
            "place_id": place_id,
            "fields": "name,formatted_address,geometry,rating,user_ratings_total,opening_hours,types,price_level",
            "key": self.api_key
        }

        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data["status"] == "OK" and "result" in data:
                return data["result"]
            else:
                print(f"Place details failed for {place_id}: {data.get('status', 'Unknown error')}")
                return None

        except requests.RequestException as e:
            print(f"Place details request failed: {e}")
            return None

    @staticmethod
    def _calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """
        Calculate distance between two coordinates using Haversine formula

        Returns:
            Distance in kilometers
        """
        import math

        # Convert to radians
        lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])

        # Haversine formula
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
        c = 2 * math.asin(math.sqrt(a))
        r = 6371  # Earth's radius in kilometers

        return r * c

# Convenience functions for Agent 2 workflow
def find_nearest_convenience_store_for_residential_analysis(lat: float, lng: float, excluded_place_ids: set = None) -> Optional[Dict]:
    """
    Enhanced POI search for residential timing analysis with multi-level strategy.
    Searches convenience stores, supermarkets, and includes confidence levels.

    LOGIC: Store busy times = Residential activity times (good for door-to-door sales)
    - High confidence (0-1km): Convenience stores only
    - Medium confidence (1-2km): Convenience stores + Supermarkets
    - Low confidence (2-3km): All retail types

    Args:
        lat: Latitude of center point
        lng: Longitude of center point
        excluded_place_ids: Set of Place IDs to exclude from results

    Returns:
        Dictionary with nearest POI info including confidence level or None if not found
    """
    client = GoogleMapsClient()

    if excluded_place_ids is None:
        excluded_place_ids = set()

    try:
        # Enhanced multi-tier search strategy with confidence zones
        search_strategies = [
            # High confidence zone: 0-1km convenience stores
            {
                "zone": "HIGH",
                "max_distance": 1.0,
                "searches": [
                    {"keyword": "7-Eleven", "radius": 1000, "type": "convenience_store"},
                    {"keyword": "เซเว่น", "radius": 1000, "type": "convenience_store"},
                    {"keyword": "FamilyMart", "radius": 1000, "type": "convenience_store"},
                    {"keyword": "Lotus Express", "radius": 1000, "type": "convenience_store"},
                    {"keyword": "CP Freshmart", "radius": 1000, "type": "convenience_store"},
                    {"keyword": "Big C Mini", "radius": 1000, "type": "convenience_store"}
                ]
            },
            # Medium confidence zone: 1-2km convenience + supermarkets
            {
                "zone": "MEDIUM",
                "max_distance": 2.0,
                "searches": [
                    {"keyword": "7-Eleven", "radius": 2000, "type": "convenience_store"},
                    {"keyword": "Big C", "radius": 2000, "type": "supermarket"},
                    {"keyword": "Lotus", "radius": 2000, "type": "supermarket"},
                    {"keyword": "Makro", "radius": 2000, "type": "supermarket"},
                    {"keyword": "Tesco", "radius": 2000, "type": "supermarket"},
                    {"keyword": "ห้างสรรพสินค้า", "radius": 2000, "type": "shopping_mall"}
                ]
            },
            # Low confidence zone: 2-3km all retail
            {
                "zone": "LOW",
                "max_distance": 3.0,
                "searches": [
                    {"keyword": "convenience store", "radius": 3000, "type": "convenience_store"},
                    {"keyword": "supermarket", "radius": 3000, "type": "supermarket"},
                    {"keyword": "ตลาด", "radius": 3000, "type": "establishment"},
                    {"keyword": "ร้านค้า", "radius": 3000, "type": "store"},
                    {"keyword": "shopping mall", "radius": 3000, "type": "shopping_mall"}
                ]
            }
        ]

        # Try each confidence zone
        for strategy in search_strategies:
            zone_places = []

            # Perform all searches for this confidence zone
            for search in strategy["searches"]:
                try:
                    places = client.find_nearby_places(
                        lat=lat,
                        lng=lng,
                        keyword=search["keyword"],
                        radius=search["radius"],
                        place_type=search["type"]
                    )
                    if places:
                        for place in places:
                            place['search_keyword'] = search["keyword"]
                            place['search_type'] = search["type"]
                        zone_places.extend(places)
                except Exception as e:
                    print(f"    Search failed for {search['keyword']}: {e}")
                    continue

            if not zone_places:
                continue

            # Filter and deduplicate
            valid_places = {}
            for place in zone_places:
                place_id = place.get('place_id')
                if place_id and place_id not in valid_places and place_id not in excluded_place_ids:
                    # Calculate distance
                    geometry = place.get('geometry', {})
                    location = geometry.get('location', {})
                    place_lat = location.get('lat')
                    place_lng = location.get('lng')

                    if place_lat and place_lng:
                        distance = client._calculate_distance(lat, lng, place_lat, place_lng)

                        # Only include if within zone distance
                        if distance <= strategy["max_distance"]:
                            place['distance_km'] = distance
                            place['confidence_level'] = strategy["zone"]
                            valid_places[place_id] = place

            if valid_places:
                # Find best POI in this zone (prefer convenience stores, then by distance)
                best_poi = None
                best_score = float('inf')

                for place in valid_places.values():
                    # Scoring: convenience stores get priority, then distance
                    score = place['distance_km']
                    place_types = place.get('types', [])
                    name = place.get('name', '').upper()

                    # Priority scoring
                    if 'convenience_store' in place_types or any(brand in name for brand in ["7-ELEVEN", "เซเว่น", "CP", "LOTUS"]):
                        score -= 0.5  # Convenience stores get 500m bonus
                    elif 'supermarket' in place_types:
                        score -= 0.2  # Supermarkets get 200m bonus

                    if score < best_score:
                        best_score = score
                        best_poi = place

                if best_poi:
                    confidence_level = strategy["zone"]
                    distance = best_poi['distance_km']

                    print(f"    Found {confidence_level} confidence POI: {best_poi['name']} ({distance:.2f}km)")

                    return {
                        **best_poi,  # Include all original place data
                        "confidence_level": confidence_level,
                        "poi_name": best_poi['name'],
                        "poi_address": best_poi.get('address', ''),
                        "poi_distance_km": distance,
                        "poi_place_id": best_poi.get('place_id', ''),
                        "poi_rating": best_poi.get('rating', 0),
                        "poi_types": best_poi.get('types', [])
                    }

        # No POI found in any zone
        print(f"    No POI found within 3km (excluded: {len(excluded_place_ids)} places)")
        return None

    except Exception as e:
        print(f"    Error finding POI: {e}")
        return None

def find_nearest_convenience_store(lat: float, lng: float, excluded_place_ids: set = None) -> Optional[Dict]:
    """
    Legacy function - now uses convenience store search for residential analysis
    """
    return find_nearest_convenience_store_for_residential_analysis(lat, lng, excluded_place_ids)

def find_nearest_7eleven(lat: float, lng: float, excluded_place_ids: set = None) -> Optional[Dict]:
    """
    Legacy function - now uses convenience store search for door-to-door sales timing
    """
    return find_nearest_convenience_store_for_residential_analysis(lat, lng, excluded_place_ids)

def get_poi_for_village(village_name: str, lat: float, lng: float, excluded_place_ids: set = None) -> Dict:
    """
    Enhanced Agent 2 function: Get multi-level POI for door-to-door sales analysis with confidence levels

    Finds nearby convenience stores/supermarkets that reflect residential activity patterns.
    Uses confidence-based approach:
    - HIGH confidence (0-1km): Convenience stores only
    - MEDIUM confidence (1-2km): Convenience stores + Supermarkets
    - LOW confidence (2-3km): All retail types

    Args:
        village_name: Name of the village
        lat: Village latitude
        lng: Village longitude
        excluded_place_ids: Set of Place IDs to exclude from results

    Returns:
        Dictionary with enhanced POI information including confidence level
    """
    result = {
        "Village_Name": village_name,
        "Indicator_POI": "",
        "Indicator_Place_ID": "",
        "Indicator_Address": "",
        "Confidence_Level": "NONE",
        "Confidence_Description": "",
        "POI_Distance_km": 0,
        "POI_Types": "",
        "Search_Keyword": "",
        "Rating": 0,
        "Last_Updated": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    # Use enhanced POI search with confidence levels
    nearest_poi = find_nearest_convenience_store_for_residential_analysis(lat, lng, excluded_place_ids)

    if nearest_poi:
        confidence = nearest_poi.get('confidence_level', 'UNKNOWN')
        distance = nearest_poi.get('distance_km', 0)

        # Enhanced confidence description
        confidence_desc = {
            'HIGH': f'High confidence ({distance:.1f}km convenience store)',
            'MEDIUM': f'Medium confidence ({distance:.1f}km retail store)',
            'LOW': f'Low confidence ({distance:.1f}km fallback POI)'
        }.get(confidence, f'Unknown confidence ({distance:.1f}km)')

        result.update({
            "Indicator_POI": nearest_poi["name"],
            "Indicator_Place_ID": nearest_poi.get("place_id", ""),
            "Indicator_Address": nearest_poi.get("address", ""),
            "Confidence_Level": confidence,
            "Confidence_Description": confidence_desc,
            "POI_Distance_km": distance,
            "POI_Types": ', '.join(nearest_poi.get('types', [])),
            "Search_Keyword": nearest_poi.get('search_keyword', ''),
            "Rating": nearest_poi.get('rating', 0)
        })
        print(f"OK: Found {confidence} confidence POI for {village_name}: {nearest_poi['name']} ({distance:.1f}km)")
    else:
        result["Confidence_Description"] = "No POI found within 3km"
        print(f"WARNING: No POI found near {village_name}")

    return result
