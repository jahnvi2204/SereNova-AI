import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './components/Home'; // Example of another component
import ChatLayout from './components/ChatLayout';
import Login from './components/Login';
import Signup from './components/Signup';

export default function AppRoutes() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />      {/* Home Route */}
        <Route path="/chat" element={<ChatLayout />} /> {/* Chatbot Route */}
        <Route path="/login" element={<Login />} /> {/* Login Route */}
        <Route path="/signup" element={<Signup />} /> {/* Signup Route */}
      </Routes>
    </Router>
  );
}
