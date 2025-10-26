import React from 'react';
import { Link } from 'react-router-dom';
import { Heart, Users, Church, MessageCircle } from 'lucide-react';

function HomePage() {
  return (
    <div className="px-4 py-8">
      {/* Hero Section */}
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Welcome to CaritasAI
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Connecting volunteers with service opportunities and guiding people to Catholic resources
        </p>
      </div>

      {/* Features Grid */}
      <div className="grid md:grid-cols-3 gap-8 mb-12">
        {/* For Volunteers */}
        <Link
          to="/volunteer"
          className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
        >
          <div className="flex justify-center mb-4">
            <Heart className="h-12 w-12 text-red-600" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2 text-center">
            Volunteer
          </h2>
          <p className="text-gray-600 text-center mb-4">
            Find meaningful service opportunities that match your skills and availability
          </p>
          <ul className="space-y-2 text-sm text-gray-600">
            <li className="flex items-start">
              <span className="text-red-600 mr-2">✓</span>
              AI-powered opportunity matching
            </li>
            <li className="flex items-start">
              <span className="text-red-600 mr-2">✓</span>
              Easy registration
            </li>
            <li className="flex items-start">
              <span className="text-red-600 mr-2">✓</span>
              Track your service hours
            </li>
          </ul>
          <div className="mt-4 text-center">
            <span className="text-red-600 font-semibold">Get Started →</span>
          </div>
        </Link>

        {/* For Those in Need */}
        <Link
          to="/find-help"
          className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
        >
          <div className="flex justify-center mb-4">
            <Church className="h-12 w-12 text-blue-600" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2 text-center">
            Find Help
          </h2>
          <p className="text-gray-600 text-center mb-4">
            Connect with nearby Catholic parishes and charities for assistance
          </p>
          <ul className="space-y-2 text-sm text-gray-600">
            <li className="flex items-start">
              <span className="text-blue-600 mr-2">✓</span>
              Food pantries
            </li>
            <li className="flex items-start">
              <span className="text-blue-600 mr-2">✓</span>
              Financial assistance
            </li>
            <li className="flex items-start">
              <span className="text-blue-600 mr-2">✓</span>
              Counseling & support
            </li>
          </ul>
          <div className="mt-4 text-center">
            <span className="text-blue-600 font-semibold">Find Resources →</span>
          </div>
        </Link>

        {/* For Parish Staff */}
        <Link
          to="/admin"
          className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
        >
          <div className="flex justify-center mb-4">
            <Users className="h-12 w-12 text-green-600" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2 text-center">
            Parish Admin
          </h2>
          <p className="text-gray-600 text-center mb-4">
            Manage outreach programs and track volunteer engagement
          </p>
          <ul className="space-y-2 text-sm text-gray-600">
            <li className="flex items-start">
              <span className="text-green-600 mr-2">✓</span>
              Analytics dashboard
            </li>
            <li className="flex items-start">
              <span className="text-green-600 mr-2">✓</span>
              Event management
            </li>
            <li className="flex items-start">
              <span className="text-green-600 mr-2">✓</span>
              Impact tracking
            </li>
          </ul>
          <div className="mt-4 text-center">
            <span className="text-green-600 font-semibold">View Dashboard →</span>
          </div>
        </Link>
      </div>

      {/* Stats Section */}
      <div className="bg-gradient-to-r from-red-600 to-red-700 rounded-lg shadow-lg p-8 text-white">
        <div className="grid md:grid-cols-4 gap-8 text-center">
          <div>
            <div className="text-4xl font-bold mb-2">20+</div>
            <div className="text-red-100">Volunteers</div>
          </div>
          <div>
            <div className="text-4xl font-bold mb-2">15+</div>
            <div className="text-red-100">Parishes</div>
          </div>
          <div>
            <div className="text-4xl font-bold mb-2">2,000+</div>
            <div className="text-red-100">Hours Served</div>
          </div>
          <div>
            <div className="text-4xl font-bold mb-2">300+</div>
            <div className="text-red-100">Families Helped</div>
          </div>
        </div>
      </div>

      {/* Mission Statement */}
      <div className="mt-12 text-center">
        <h3 className="text-2xl font-bold text-gray-900 mb-4">Our Mission</h3>
        <p className="text-lg text-gray-600 max-w-3xl mx-auto">
          CaritasAI leverages artificial intelligence to strengthen the Church's mission of 
          evangelization through service. We connect willing hearts with those in need, 
          making it easier than ever to live out the Works of Mercy.
        </p>
      </div>
    </div>
  );
}

export default HomePage;