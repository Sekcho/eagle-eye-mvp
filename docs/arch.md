# Architecture (MVP)
- Agent 1: Geocoder (only for rows missing lat/lng)
- Agent 2: Indicator POI discovery (nearby search)
- Agent 3: Golden Time via BestTime (add venue -> populartimes -> compute peak window)
- Nightly refresh (optional): revalidate cached venue_id, recompute if TTL expired
