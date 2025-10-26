import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Send, Loader, Bot, User } from 'lucide-react';

function VolunteerChat() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hello! 🙏 I\'m here to help you find volunteer opportunities. Tell me about yourself - where are you located, what are your interests, and when are you available to serve?'
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    
    // Add user message
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const response = await axios.post('/api/chat', {
        message: userMessage
      });

      // Add AI response
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: response.data.response
      }]);
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again or contact support.'
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4">
      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-red-600 to-red-700 text-white px-6 py-4">
          <h2 className="text-2xl font-bold flex items-center">
            <Bot className="mr-2 h-6 w-6" />
            CaritasAI Volunteer 
          </h2>
          <p className="text-red-100 text-sm mt-1">
            Let's find the perfect volunteer opportunity for you
          </p>
        </div>

        {/* Messages */}
        <div className="h-96 overflow-y-auto p-6 space-y-4 bg-gray-50">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-md rounded-lg px-4 py-3 ${
                  message.role === 'user'
                    ? 'bg-red-600 text-white ml-auto'
                    : 'bg-white text-gray-800 shadow-sm border border-gray-200'
                }`}
              >
                <div className="flex items-start">
                  {message.role === 'assistant' && (
                    <Bot className="h-5 w-5 mr-2 mt-0.5 text-red-600 flex-shrink-0" />
                  )}
                  {message.role === 'user' && (
                    <User className="h-5 w-5 mr-2 mt-0.5 flex-shrink-0" />
                  )}
                  <div className="whitespace-pre-wrap">{message.content}</div>
                </div>
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-white text-gray-800 rounded-lg px-4 py-3 shadow-sm border border-gray-200">
                <Loader className="h-5 w-5 animate-spin text-red-600" />
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <form onSubmit={sendMessage} className="border-t border-gray-200 p-4 bg-white">
          <div className="flex space-x-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center space-x-2 transition-colors"
            >
              <Send className="h-4 w-4" />
              <span>Send</span>
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            💡 Try: "I want to volunteer " or "Show me food pantry opportunities in Brooklyn"
          </p>
        </form>
      </div>

      {/* Quick Actions */}
      <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-3">
        {[
          'I want to volunteer',
          'Show me weekend pantry opportunities',
          'I can help with tutoring',
          'What opportunities are near Brooklyn?'
        ].map((prompt, index) => (
          <button
            key={index}
            onClick={() => setInput(prompt)}
            className="px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm text-gray-700 hover:border-red-500 hover:text-red-600 transition-colors"
          >
            {prompt}
          </button>
        ))}
      </div>
    </div>
  );
}

export default VolunteerChat;