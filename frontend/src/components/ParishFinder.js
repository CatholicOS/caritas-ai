import React, { useState } from 'react';
import axios from 'axios';
import { Search, MapPin, Phone, Mail, Clock, Church } from 'lucide-react';

function ParishFinder() {
  const [location, setLocation] = useState('');
  const [serviceType, setServiceType] = useState('');
  const [parishes, setParishes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const searchParishes = async (e) => {
    e.preventDefault();
    if (!location.trim()) return;

    setLoading(true);
    setSearched(true);

    try {
      // For now, using mock data. Replace with actual API call
      const response = await axios.post('/api/chat', {
        message: `Find parishes in ${location}${serviceType ? ` with ${serviceType}` : ''}`
      });

      // Mock data - replace with actual parsing of AI response
      setParishes([
        {
          id: 1,
          name: 'St. Mary\'s Parish',
          address: '123 Main St',
          city: location,
          phone: '(555) 123-4567',
          email: 'contact@stmarys.org',
          services: ['food pantry', 'financial assistance', 'counseling'],
          hours: 'Mon-Fri 9AM-5PM'
        },
        {
          id: 2,
          name: 'Catholic Charities Office',
          address: '456 Church Ave',
          city: location,
          phone: '(555) 987-6543',
          email: 'help@catholiccharities.org',
          services: ['housing assistance', 'job training', 'healthcare navigation'],
          hours: 'Mon-Sat 8AM-6PM'
        }
      ]);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Find Catholic Resources
        </h1>
        <p className="text-gray-600">
          Connect with nearby parishes and Catholic charities for assistance
        </p>
      </div>

      {/* Search Form */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <form onSubmit={searchParishes} className="space-y-4">
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Your Location
              </label>
              <div className="relative">
                <MapPin className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  placeholder="City or ZIP code"
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Service Needed (Optional)
              </label>
              <select
                value={serviceType}
                onChange={(e) => setServiceType(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Services</option>
                <option value="food pantry">Food Pantry</option>
                <option value="financial assistance">Financial Assistance</option>
                <option value="housing">Housing Assistance</option>
                <option value="counseling">Counseling</option>
                <option value="healthcare">Healthcare</option>
                <option value="job training">Job Training</option>
              </select>
            </div>
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full md:w-auto px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 flex items-center justify-center space-x-2 transition-colors"
          >
            <Search className="h-5 w-5" />
            <span>{loading ? 'Searching...' : 'Find Resources'}</span>
          </button>
        </form>
      </div>

      {/* Results */}
      {searched && (
        <div className="space-y-4">
          {parishes.length === 0 && !loading && (
            <div className="text-center py-12 bg-white rounded-lg shadow">
              <Church className="h-16 w-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-600">No parishes found. Try a different location.</p>
            </div>
          )}

          {parishes.map((parish) => (
            <div key={parish.id} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
              <div className="flex flex-col md:flex-row md:items-start md:justify-between">
                <div className="flex-1">
                  <h3 className="text-xl font-bold text-gray-900 mb-2 flex items-center">
                    <Church className="h-5 w-5 text-blue-600 mr-2" />
                    {parish.name}
                  </h3>
                  
                  <div className="space-y-2 mb-4">
                    <p className="text-gray-600 flex items-center">
                      <MapPin className="h-4 w-4 mr-2 text-gray-400" />
                      {parish.address}, {parish.city}
                    </p>
                    <p className="text-gray-600 flex items-center">
                      <Phone className="h-4 w-4 mr-2 text-gray-400" />
                      {parish.phone}
                    </p>
                    <p className="text-gray-600 flex items-center">
                      <Mail className="h-4 w-4 mr-2 text-gray-400" />
                      {parish.email}
                    </p>
                    <p className="text-gray-600 flex items-center">
                      <Clock className="h-4 w-4 mr-2 text-gray-400" />
                      {parish.hours}
                    </p>
                  </div>

                  <div>
                    <p className="text-sm font-medium text-gray-700 mb-2">Services Available:</p>
                    <div className="flex flex-wrap gap-2">
                      {parish.services.map((service, index) => (
                        <span
                          key={index}
                          className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
                        >
                          {service}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="mt-4 md:mt-0 md:ml-6">
                  <button className="w-full md:w-auto px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                    Contact
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Info Box */}
      <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="font-semibold text-blue-900 mb-2">Need Immediate Help?</h3>
        <p className="text-blue-800 mb-4">
          All services are confidential and available regardless of faith background. 
          If you're experiencing an emergency, please call 911.
        </p>
        <p className="text-sm text-blue-700">
          📞 National Catholic Services Hotline: 1-800-XXX-XXXX (24/7)
        </p>
      </div>
    </div>
  );
}

export default ParishFinder;