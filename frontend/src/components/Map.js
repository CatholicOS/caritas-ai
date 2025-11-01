
import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { MapPin, Calendar, Users, ExternalLink } from 'lucide-react';

// Leaflet  marker icons
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

// Component to update map view
function ChangeView({ center, zoom }) {
  const map = useMap();
  useEffect(() => {
    if (center) {
      console.log('🗺️ Changing map view to:', center, 'zoom:', zoom);
      map.setView(center, zoom);
    }
  }, [center, zoom, map]);
  return null;
}

// Geocoding function (OpenStreetMap Nominatim)
async function geocodeAddress(address, city, state) {
  console.log('📍 Geocoding:', { address, city, state });
  
  try {
    const query = `${address}, ${city}, ${state}`;
    const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=1`;
    
    console.log('🌐 Geocoding URL:', url);
    
    const response = await fetch(url);
    const data = await response.json();
    
    console.log('✅ Geocoding response:', data);
    
    if (data && data.length > 0) {
      const coords = {
        lat: parseFloat(data[0].lat),
        lng: parseFloat(data[0].lon)
      };
      console.log('✅ Got coordinates:', coords);
      return coords;
    }
    
    // Fallback to just city/state
    console.log('⚠️ Full address failed, trying city only');
    const cityQuery = `${city}, ${state}`;
    const cityUrl = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(cityQuery)}&limit=1`;
    
    console.log('🌐 City geocoding URL:', cityUrl);
    
    const cityResponse = await fetch(cityUrl);
    const cityData = await cityResponse.json();
    
    console.log('✅ City geocoding response:', cityData);
    
    if (cityData && cityData.length > 0) {
      const coords = {
        lat: parseFloat(cityData[0].lat),
        lng: parseFloat(cityData[0].lon)
      };
      console.log('✅ Got city coordinates:', coords);
      return coords;
    }
    
    console.error('❌ Geocoding failed for:', query);
    return null;
  } catch (error) {
    console.error('❌ Geocoding error:', error);
    return null;
  }
}

function Map({ events = [], location = null, onEventClick }) {
  const [mapCenter, setMapCenter] = useState([39.8283, -98.5795]); // Center of USA
  const [mapZoom, setMapZoom] = useState(4);
  const [markers, setMarkers] = useState([]);
  const [loading, setLoading] = useState(false);

  console.log('🗺️ Map component received:', { 
    eventsCount: events.length, 
    location,
    events 
  });

  // Geocode events when they change
  useEffect(() => {
    const geocodeEvents = async () => {
      console.log('🔄 Starting geocoding for', events.length, 'events');
      
      if (!events || events.length === 0) {
        console.log('⚠️ No events to geocode');
        setMarkers([]);
        return;
      }
      
      setLoading(true);
      const geocodedMarkers = [];
      
      for (const event of events) {
        console.log('📌 Processing event:', event.id, event.title);
        
        // Check if we have parish location data
        const city = event.parish_city || event.city;
        const state = event.parish_state || event.state;
        const address = event.parish_address || event.address || '';
        
        console.log('📍 Event location data:', { city, state, address });
        
        if (!city || !state) {
          console.warn('⚠️ Event missing location:', event.id);
          continue;
        }
        
        // Try to geocode
        const coords = await geocodeAddress(address, city, state);
        
        if (coords) {
          console.log('✅ Got coordinates for event', event.id, ':', coords);
          
          // Determine event type for icon color
          const skills = event.skills_needed || [];
          let eventType = 'default';
          
          for (const skill of skills) {
            const lowerSkill = skill.toLowerCase();
            if (lowerSkill.includes('food') || lowerSkill.includes('pantry')) {
              eventType = 'food pantry';
              break;
            } else if (lowerSkill.includes('tutor') || lowerSkill.includes('teach')) {
              eventType = 'tutoring';
              break;
            } else if (lowerSkill.includes('community')) {
              eventType = 'community service';
              break;
            }
          }
          
          geocodedMarkers.push({
            ...event,
            coordinates: coords,
            eventType
          });
        } else {
          console.error('❌ Failed to geocode event:', event.id);
        }
        
        // Rate limiting - wait 1 second between requests
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
      
      console.log('✅ Geocoding complete! Markers:', geocodedMarkers.length);
      setMarkers(geocodedMarkers);
      setLoading(false);
      
      // Auto-zoom to show all markers
      if (geocodedMarkers.length > 0) {
        const lats = geocodedMarkers.map(m => m.coordinates.lat);
        const lngs = geocodedMarkers.map(m => m.coordinates.lng);
        
        const centerLat = (Math.min(...lats) + Math.max(...lats)) / 2;
        const centerLng = (Math.min(...lngs) + Math.max(...lngs)) / 2;
        
        console.log('🎯 Setting map center to:', [centerLat, centerLng]);
        setMapCenter([centerLat, centerLng]);
        setMapZoom(geocodedMarkers.length === 1 ? 12 : 10);
      }
    };
    
    geocodeEvents();
  }, [events]);

  // Update map when location changes from chat
  useEffect(() => {
    const updateMapLocation = async () => {
      if (location && location.city) {
        console.log('🎯 Updating map location to:', location);
        const coords = await geocodeAddress('', location.city, location.state || '');
        if (coords) {
          console.log('✅ Setting map center to location:', coords);
          setMapCenter([coords.lat, coords.lng]);
          setMapZoom(11);
        }
      }
    };
    
    updateMapLocation();
  }, [location]);

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      weekday: 'long', 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  };

  console.log('📊 Map state:', {
    markersCount: markers.length,
    mapCenter,
    mapZoom,
    loading
  });

  return (
    <div className="h-full w-full relative">
      {loading && (
        <div className="absolute top-4 right-4 z-[1000] bg-white px-4 py-2 rounded-lg shadow-lg">
          <p className="text-sm text-gray-600">📍 Loading map markers...</p>
        </div>
      )}
      
      <MapContainer
        center={mapCenter}
        zoom={mapZoom}
        style={{ height: '100%', width: '100%' }}
        className="rounded-lg"
      >
        <ChangeView center={mapCenter} zoom={mapZoom} />
        
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        {markers.map((event, index) => {
          console.log('🎨 Rendering marker for event:', event.id, 'at', event.coordinates);
          return (
            <Marker
              key={event.id || index}
              position={[event.coordinates.lat, event.coordinates.lng]}
            >
              <Popup maxWidth={300}>
                <div className="p-2">
                  <h3 className="font-bold text-lg text-gray-900 mb-2">
                    {event.title}
                  </h3>
                  
                  <div className="space-y-2 text-sm">
                    <div className="flex items-start">
                      <MapPin className="h-4 w-4 mr-2 mt-0.5 text-red-600 flex-shrink-0" />
                      <div>
                        <p className="font-semibold">{event.parish_name}</p>
                        <p className="text-gray-600">
                          {event.parish_city}, {event.parish_state}
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex items-center">
                      <Calendar className="h-4 w-4 mr-2 text-red-600" />
                      <span>{formatDate(event.event_date)}</span>
                    </div>
                    
                    {event.skills_needed && event.skills_needed.length > 0 && (
                      <div className="flex items-start">
                        <ExternalLink className="h-4 w-4 mr-2 mt-0.5 text-red-600 flex-shrink-0" />
                        <span className="text-gray-600">
                          {event.skills_needed.join(', ')}
                        </span>
                      </div>
                    )}
                    
                    {event.max_volunteers && (
                      <div className="flex items-center">
                        <Users className="h-4 w-4 mr-2 text-red-600" />
                        <span>
                          {event.max_volunteers - (event.registered_volunteers || 0)} spots available
                        </span>
                      </div>
                    )}
                  </div>
                  
                  <button
                    onClick={() => onEventClick && onEventClick(event)}
                    className="mt-3 w-full px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors text-sm font-medium"
                  >
                    Register for Event
                  </button>
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>
      
      {/* Debug Info */}
      <div className="absolute top-4 left-4 z-[1000] bg-white p-2 rounded-lg shadow-lg text-xs">
        <p>🗺️ Markers: {markers.length}</p>
        <p>📍 Center: [{mapCenter[0].toFixed(2)}, {mapCenter[1].toFixed(2)}]</p>
        <p>🔍 Zoom: {mapZoom}</p>
      </div>
      
      {/* Legend */}
      <div className="absolute bottom-4 left-4 z-[1000] bg-white p-3 rounded-lg shadow-lg">
        <p className="font-semibold text-sm mb-2">Event Types</p>
        <div className="space-y-1 text-xs">
          <div className="flex items-center">
            <div className="w-3 h-3 rounded-full bg-red-600 mr-2"></div>
            <span>Food Pantry</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 rounded-full bg-blue-600 mr-2"></div>
            <span>Education</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 rounded-full bg-green-600 mr-2"></div>
            <span>Community Service</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Map;

