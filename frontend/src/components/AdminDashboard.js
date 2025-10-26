import React, { useState, useEffect } from 'react';
import { Users, Calendar, TrendingUp, Heart, Clock, MapPin } from 'lucide-react';

function AdminDashboard() {
  const [parishName, setParishName] = useState('');
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(false);

  // Mock data for demonstration
  const mockAnalytics = {
    parish_name: 'St. Mary\'s Parish',
    total_events: 45,
    upcoming_events: 12,
    this_month: {
      events: 8,
      registrations: 67
    },
    total_volunteers: 156,
    total_hours: 1240,
    recent_events: [
      {
        id: 1,
        title: 'Food Pantry Service',
        date: '2025-10-28',
        volunteers: 12,
        status: 'open'
      },
      {
        id: 2,
        title: 'Youth Tutoring Program',
        date: '2025-10-30',
        volunteers: 8,
        status: 'open'
      },
      {
        id: 3,
        title: 'Community Meal',
        date: '2025-11-02',
        volunteers: 15,
        status: 'open'
      }
    ]
  };

  const loadAnalytics = () => {
    setLoading(true);
    // Simulate API call
    setTimeout(() => {
      setAnalytics(mockAnalytics);
      setLoading(false);
    }, 500);
  };

  useEffect(() => {
    loadAnalytics();
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Parish Dashboard
        </h1>
        <p className="text-gray-600">
          Monitor your parish's outreach impact and volunteer engagement
        </p>
      </div>

      {/* Parish Selector */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Select Parish
        </label>
        <div className="flex gap-4">
          <select
            value={parishName}
            onChange={(e) => setParishName(e.target.value)}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <option value="">Select a parish...</option>
            <option value="St. Mary's Parish">St. Mary's Parish</option>
            <option value="St. Joseph's Church">St. Joseph's Church</option>
            <option value="Holy Family Parish">Holy Family Parish</option>
          </select>
          <button
            onClick={loadAnalytics}
            className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            Load Data
          </button>
        </div>
      </div>

      {analytics && (
        <>
          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-medium text-gray-600">Total Volunteers</h3>
                <Users className="h-5 w-5 text-green-600" />
              </div>
              <p className="text-3xl font-bold text-gray-900">{analytics.total_volunteers}</p>
              <p className="text-sm text-gray-500 mt-1">Active this year</p>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-medium text-gray-600">Upcoming Events</h3>
                <Calendar className="h-5 w-5 text-blue-600" />
              </div>
              <p className="text-3xl font-bold text-gray-900">{analytics.upcoming_events}</p>
              <p className="text-sm text-gray-500 mt-1">Scheduled</p>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-medium text-gray-600">Service Hours</h3>
                <Clock className="h-5 w-5 text-purple-600" />
              </div>
              <p className="text-3xl font-bold text-gray-900">{analytics.total_hours}</p>
              <p className="text-sm text-gray-500 mt-1">Total contributed</p>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-medium text-gray-600">This Month</h3>
                <TrendingUp className="h-5 w-5 text-red-600" />
              </div>
              <p className="text-3xl font-bold text-gray-900">{analytics.this_month.registrations}</p>
              <p className="text-sm text-gray-500 mt-1">New registrations</p>
            </div>
          </div>

          {/* Recent Events */}
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
              <Calendar className="h-5 w-5 mr-2 text-green-600" />
              Upcoming Events
            </h2>
            <div className="space-y-4">
              {analytics.recent_events.map((event) => (
                <div
                  key={event.id}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900">{event.title}</h3>
                    <p className="text-sm text-gray-600 flex items-center mt-1">
                      <Calendar className="h-4 w-4 mr-1" />
                      {new Date(event.date).toLocaleDateString('en-US', {
                        weekday: 'long',
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric'
                      })}
                    </p>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="text-center">
                      <p className="text-2xl font-bold text-gray-900">{event.volunteers}</p>
                      <p className="text-xs text-gray-500">Volunteers</p>
                    </div>
                    <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
                      {event.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Monthly Summary */}
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">
                This Month's Impact
              </h2>
              <div className="space-y-4">
                <div className="flex justify-between items-center pb-3 border-b">
                  <span className="text-gray-600">Events Hosted</span>
                  <span className="text-2xl font-bold text-gray-900">
                    {analytics.this_month.events}
                  </span>
                </div>
                <div className="flex justify-between items-center pb-3 border-b">
                  <span className="text-gray-600">New Registrations</span>
                  <span className="text-2xl font-bold text-gray-900">
                    {analytics.this_month.registrations}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Avg. per Event</span>
                  <span className="text-2xl font-bold text-gray-900">
                    {Math.round(analytics.this_month.registrations / analytics.this_month.events)}
                  </span>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-green-600 to-green-700 rounded-lg shadow-md p-6 text-white">
              <h2 className="text-xl font-bold mb-4">Quick Actions</h2>
              <div className="space-y-3">
                <button className="w-full px-4 py-3 bg-white bg-opacity-20 rounded-lg hover:bg-opacity-30 transition-colors text-left">
                  <p className="font-semibold">Create New Event</p>
                  <p className="text-sm text-green-100">Schedule a volunteer opportunity</p>
                </button>
                <button className="w-full px-4 py-3 bg-white bg-opacity-20 rounded-lg hover:bg-opacity-30 transition-colors text-left">
                  <p className="font-semibold">View All Volunteers</p>
                  <p className="text-sm text-green-100">Manage volunteer database</p>
                </button>
                <button className="w-full px-4 py-3 bg-white bg-opacity-20 rounded-lg hover:bg-opacity-30 transition-colors text-left">
                  <p className="font-semibold">Download Report</p>
                  <p className="text-sm text-green-100">Export analytics data</p>
                </button>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default AdminDashboard;