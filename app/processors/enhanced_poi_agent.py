"""
Enhanced POI Agent for Happy Block Precision Targeting
Integrates with L2 database and provides fallback POI search
"""

import os
import sys
from typing import Dict, List, Optional, Tuple
import time
import math

# Add app directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from datasources.gmaps_client import GoogleMapsClient

class EnhancedPOIAgent:
    """Enhanced POI discovery agent with Happy Block precision and fallback search"""

    def __init__(self):
        """Initialize Enhanced POI Agent"""
        self.gmaps_client = GoogleMapsClient()
        self.search_cache = {}  # Cache for repeated searches

    def find_poi_for_happy_block(self, happy_block_id: str, lat_hb: float, lng_hb: float,
                                excluded_place_ids: set = None) -> Dict:
        """
        Find POI for Happy Block with fallback to nearby blocks

        Args:
            happy_block_id: Happy Block ID (e.g., "09320-099700")
            lat_hb: Happy Block latitude
            lng_hb: Happy Block longitude
            excluded_place_ids: Set of Place IDs to exclude

        Returns:
            Dictionary with POI information and search details
        """
        if excluded_place_ids is None:
            excluded_place_ids = set()

        print(f"Searching POI for Happy Block {happy_block_id}")

        # Step 1: Search current Happy Block (500m radius)
        poi_result = self._search_poi_in_radius(lat_hb, lng_hb, radius=350, search_type="current")

        if poi_result:
            return {
                **poi_result,
                'happy_block_id': happy_block_id,
                'search_status': 'found_current',
                'poi_remark': 'POI found in current Happy Block',
                'distance_from_hb': poi_result.get('distance_km', 0)
            }

        # Step 2: Fallback search in nearby Happy Blocks
        print(f"   No POI in current block, searching nearby...")
        nearby_blocks = self._generate_nearby_happy_blocks(happy_block_id)

        for nearby_id, nearby_lat, nearby_lng in nearby_blocks:
            poi_result = self._search_poi_in_radius(nearby_lat, nearby_lng, radius=350, search_type="nearby")

            if poi_result:
                # Calculate distance from original Happy Block
                distance_from_hb = self._calculate_distance(lat_hb, lng_hb, nearby_lat, nearby_lng)

                return {
                    **poi_result,
                    'happy_block_id': happy_block_id,
                    'search_status': 'found_nearby',
                    'poi_remark': f'No POI (nearby happyblock: {nearby_id}, distance: {distance_from_hb:.1f}km)',
                    'distance_from_hb': distance_from_hb,
                    'source_happy_block': nearby_id
                }

        # Step 3: No POI found anywhere
        return {
            'happy_block_id': happy_block_id,
            'search_status': 'not_found',
            'poi_remark': 'No POI found within 2km radius',
            'poi_name': '',
            'poi_address': '',
            'poi_place_id': '',
            'confidence_level': 'NONE',
            'distance_from_hb': 0
        }

    def _search_poi_in_radius(self, lat: float, lng: float, radius: int = 350,
                             search_type: str = "current") -> Optional[Dict]:
        """
        Search for POI within specified radius using multiple strategies

        Args:
            lat: Latitude
            lng: Longitude
            radius: Search radius in meters
            search_type: "current" or "nearby" for logging

        Returns:
            POI information dictionary or None
        """
        try:
            # Community-focused search strategy (no large malls/supercenters)
            search_strategies = [
                # Priority 1: 7-Eleven community stores
                {"keyword": "7-Eleven", "type": "convenience_store", "priority": 1},
                {"keyword": "เซเว่น", "type": "convenience_store", "priority": 1},
                {"keyword": "Seven Eleven", "type": "convenience_store", "priority": 1},

                # Priority 2: Other convenience stores
                {"keyword": "FamilyMart", "type": "convenience_store", "priority": 2},
                {"keyword": "Family Mart", "type": "convenience_store", "priority": 2},

                # Priority 3: Small format Lotus
                {"keyword": "Lotus Go Fresh", "type": "convenience_store", "priority": 3},
                {"keyword": "Lotus Express", "type": "convenience_store", "priority": 3},
                {"keyword": "Lotus Mini", "type": "convenience_store", "priority": 3},

                # Priority 4: Small format Big C
                {"keyword": "Big C Go Fresh", "type": "convenience_store", "priority": 4},
                {"keyword": "Big C Mini", "type": "convenience_store", "priority": 4},

                # Priority 5: Other community stores
                {"keyword": "CP Freshmart", "type": "convenience_store", "priority": 5},
                {"keyword": "Mini Mart", "type": "convenience_store", "priority": 5},
                {"keyword": "108 Shop", "type": "convenience_store", "priority": 5},
                {"keyword": "Lawson", "type": "convenience_store", "priority": 5},
            ]

            all_places = []

            # Perform searches
            for strategy in search_strategies:
                try:
                    places = self.gmaps_client.find_nearby_places(
                        lat=lat,
                        lng=lng,
                        keyword=strategy["keyword"],
                        radius=radius,
                        place_type=strategy["type"]
                    )

                    # Add priority and search info to each place, filter out large malls
                    for place in places:
                        place_name = place.get('name', '').upper()

                        # Filter out large malls/supercenters
                        exclude_keywords = ['CENTRAL', 'ROBINSON', 'MALL', 'PLAZA', 'FESTIVAL',
                                          'SUPERCENTER', 'HYPERMARKET', 'DEPARTMENT', 'SHOPPING CENTER']

                        if any(keyword in place_name for keyword in exclude_keywords):
                            continue  # Skip large malls

                        place['search_priority'] = strategy['priority']
                        place['search_keyword'] = strategy['keyword']
                        place['search_type'] = strategy['type']
                        place['is_community_store'] = True

                    # Filter places before adding
                    filtered_places = []
                    for place in places:
                        place_name = place.get('name', '').upper()
                        exclude_keywords = ['CENTRAL', 'ROBINSON', 'MALL', 'PLAZA', 'FESTIVAL',
                                          'SUPERCENTER', 'HYPERMARKET', 'DEPARTMENT', 'SHOPPING CENTER']

                        if not any(keyword in place_name for keyword in exclude_keywords):
                            place['search_priority'] = strategy['priority']
                            place['search_keyword'] = strategy['keyword']
                            place['search_type'] = strategy['type']
                            place['is_community_store'] = True
                            filtered_places.append(place)

                    all_places.extend(filtered_places)

                except Exception as e:
                    print(f"      Search failed for {strategy['keyword']}: {e}")
                    continue

            if not all_places:
                return None

            # Deduplicate by place_id and find best POI
            unique_places = {}
            for place in all_places:
                place_id = place.get('place_id')
                if place_id and place_id not in unique_places:
                    unique_places[place_id] = place

            if not unique_places:
                return None

            # Find best POI using priority and distance
            best_poi = self._select_best_poi(list(unique_places.values()))

            if best_poi:
                confidence_level = self._determine_confidence_level(best_poi)

                return {
                    'poi_name': best_poi['name'],
                    'poi_address': best_poi.get('address', best_poi.get('vicinity', '')),
                    'poi_place_id': best_poi.get('place_id', ''),
                    'distance_km': best_poi.get('distance_km', 0),
                    'confidence_level': confidence_level,
                    'search_keyword': best_poi.get('search_keyword', ''),
                    'rating': best_poi.get('rating', 0),
                    'types': best_poi.get('types', [])
                }

            return None

        except Exception as e:
            print(f"      Error in POI search: {e}")
            return None

    def _select_best_poi(self, places: List[Dict]) -> Optional[Dict]:
        """Select best POI based on priority and distance"""
        if not places:
            return None

        # Sort by priority (lower is better), then by distance
        best_poi = None
        best_score = float('inf')

        for place in places:
            # Scoring: priority (weighted) + distance
            priority = place.get('search_priority', 10)
            distance = place.get('distance_km', 10)

            # Score calculation: priority is more important than distance
            score = (priority * 2) + distance

            if score < best_score:
                best_score = score
                best_poi = place

        return best_poi

    def _determine_confidence_level(self, poi: Dict) -> str:
        """Determine confidence level based on POI type and distance"""
        distance = poi.get('distance_km', 10)
        types = poi.get('types', [])
        name = poi.get('name', '').upper()

        # High confidence criteria
        if distance <= 0.5:  # Very close
            if 'convenience_store' in types or any(brand in name for brand in ["7-ELEVEN", "เซเว่น"]):
                return "HIGH"

        # Medium confidence criteria
        if distance <= 1.0:
            if 'convenience_store' in types or 'supermarket' in types:
                return "MEDIUM"

        # Low confidence for everything else
        return "LOW"

    def _generate_nearby_happy_blocks(self, current_id: str) -> List[Tuple[str, float, float]]:
        """
        Generate nearby Happy Block IDs for fallback search

        Args:
            current_id: Current Happy Block ID (e.g., "09320-099700")

        Returns:
            List of (happy_block_id, lat, lng) tuples for nearby blocks
        """
        try:
            # Parse Happy Block ID: "09320-099700" → (9320, 99700)
            lat_str, lng_str = current_id.split('-')
            lat_base = int(lat_str)
            lng_base = int(lng_str)

            nearby_blocks = []

            # Generate nearby blocks in expanding rings
            # Ring 1: Direct neighbors (4 blocks)
            ring1_offsets = [(-5, 0), (5, 0), (0, -5), (0, 5)]

            # Ring 2: Diagonal neighbors (4 blocks)
            ring2_offsets = [(-5, -5), (-5, 5), (5, -5), (5, 5)]

            # Ring 3: Extended neighbors (8 blocks)
            ring3_offsets = [
                (-10, 0), (10, 0), (0, -10), (0, 10),
                (-10, -5), (-10, 5), (10, -5), (10, 5)
            ]

            # Process rings in order of preference
            for ring_offsets in [ring1_offsets, ring2_offsets, ring3_offsets]:
                for lat_offset, lng_offset in ring_offsets:
                    new_lat = lat_base + lat_offset
                    new_lng = lng_base + lng_offset
                    new_id = f"{new_lat:05d}-{new_lng:06d}"

                    # Convert back to decimal coordinates
                    lat_decimal = new_lat / 1000
                    lng_decimal = new_lng / 1000

                    nearby_blocks.append((new_id, lat_decimal, lng_decimal))

            return nearby_blocks

        except Exception as e:
            print(f"      Error generating nearby blocks for {current_id}: {e}")
            return []

    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two coordinates using Haversine formula"""
        # Convert to radians
        lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])

        # Haversine formula
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
        c = 2 * math.asin(math.sqrt(a))
        r = 6371  # Earth's radius in kilometers

        return r * c

    def process_happy_block_poi_analysis(self, happy_block_data: Dict) -> Dict:
        """
        Process POI analysis for a single Happy Block

        Args:
            happy_block_data: Dictionary with Happy Block information

        Returns:
            Enhanced Happy Block data with POI information
        """
        happy_block_id = happy_block_data['happy_block']
        lat_hb = happy_block_data['lat_hb']
        lng_hb = happy_block_data['long_hb']

        # Find POI for this Happy Block
        poi_result = self.find_poi_for_happy_block(happy_block_id, lat_hb, lng_hb)

        # Enhance Happy Block data with POI information
        enhanced_data = {
            **happy_block_data,
            'poi_name': poi_result.get('poi_name', ''),
            'poi_address': poi_result.get('poi_address', ''),
            'poi_place_id': poi_result.get('poi_place_id', ''),
            'poi_confidence': poi_result.get('confidence_level', 'NONE'),
            'poi_remark': poi_result.get('poi_remark', ''),
            'poi_distance_km': poi_result.get('distance_from_hb', 0),
            'search_status': poi_result.get('search_status', 'not_found'),
            'last_updated': time.strftime("%Y-%m-%d %H:%M:%S")
        }

        return enhanced_data

# Test function
if __name__ == "__main__":
    # Test Enhanced POI Agent
    agent = EnhancedPOIAgent()

    # Test Happy Block from L2 database
    test_happy_block = {
        'happy_block': '09320-099700',
        'lat_hb': 9.3175,
        'long_hb': 99.7025,
        'village_names': 'ชลคราม',
        'total_available_ports': 15
    }

    print("Testing Enhanced POI Agent")
    print(f"Happy Block: {test_happy_block['happy_block']}")
    print(f"Coordinates: {test_happy_block['lat_hb']}, {test_happy_block['long_hb']}")

    # Process POI analysis
    result = agent.process_happy_block_poi_analysis(test_happy_block)

    print(f"\nResults:")
    print(f"POI Found: {result['poi_name']}")
    print(f"Address: {result['poi_address']}")
    print(f"Confidence: {result['poi_confidence']}")
    print(f"Remark: {result['poi_remark']}")
    print(f"Distance: {result['poi_distance_km']:.2f}km")