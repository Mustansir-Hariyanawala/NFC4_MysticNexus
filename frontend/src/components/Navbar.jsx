import React, { useState } from "react";
import { FileText, Menu, X } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Link } from 'react-router-dom';
import Symbol2 from '../assets/Symbol2.png';

const Navbar = () => {
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);

  const toggleMenu = () => {
    setMenuOpen(!menuOpen);
  };

  return (
    <nav className="fixed top-0 left-0 w-full z-50 bg-gray-900 border-b border-green-500/20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          {/* Logo */}
          <div className="flex items-center">
            <div className="w-20 h-20 rounded-lg flex items-center justify-center">
              <img src={Symbol2} className="w-full"/>
            </div>
            <span className="text-xl font-bold text-green-400" onClick={()=>navigate('/')}>CogniScript</span>
          </div>

          {/* Desktop Menu */}
          <div className="hidden md:flex items-center space-x-8">
            <Link to="/" className="text-gray-300 hover:text-green-400 transition-colors">Home</Link>
            <a href="#features" className="text-gray-300 hover:text-green-400 transition-colors">Features</a>
            <a href="#how-it-works" className="text-gray-300 hover:text-green-400 transition-colors">How it Works</a>
            <button className="bg-gradient-to-r from-green-500 to-green-600 text-black px-6 py-2 rounded-lg font-semibold hover:from-green-400 hover:to-green-500 transition-all shadow-lg shadow-green-500/20" onClick={()=>navigate('/chat')}>
              Get Started
            </button>
            <Link to="/auth" className="text-gray-300 hover:text-green-400 transition-colors">Login</Link>
          </div>

          {sessionStorage.getItem('username') && (
            <div className="relative group">
              <div className="w-8 h-8 rounded-full bg-gradient-to-r from-green-400 to-green-600 text-black font-bold flex items-center justify-center cursor-pointer hover:from-green-500 hover:to-green-700 transition-all duration-300 shadow-lg">
                {sessionStorage.getItem('username')[0].toUpperCase()}
              </div>
              <div className="absolute right-0 mt-2 w-48 bg-gray-800 rounded-lg shadow-2xl opacity-0 group-hover:opacity-100 transition-all duration-300 z-50 border border-green-500/20">
                <div className="px-4 py-3 text-sm text-white border-b border-green-500/20 bg-green-800">
                  Welcome {sessionStorage.getItem('username')}
                </div>
                <button
                  onClick={() => {
                    sessionStorage.clear();
                    navigate('/');
                    window.location.reload();
                  }}
                  className="w-full text-left px-4 py-3 text-sm text-gray-300 hover:text-red-400 hover:bg-gradient-to-r hover:from-red-500/10 hover:to-red-400/10 transition-all duration-300 rounded-b-lg"
                >
                  Logout
                </button>
              </div>
            </div>
          )}


          {/* Mobile Menu Toggle Button */}
          <div className="md:hidden">
            <button onClick={toggleMenu} className="text-green-400 hover:text-green-300 focus:outline-none">
              {menuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Dropdown Menu */}
        {menuOpen && (
          <div className="md:hidden flex flex-col space-y-4 pb-4">
            <a href="#features" className="text-gray-300 hover:text-green-400 transition-colors">Features</a>
            <a href="#how-it-works" className="text-gray-300 hover:text-green-400 transition-colors">How it Works</a>
            <button className="bg-gradient-to-r from-green-500 to-green-600 text-black px-6 py-2 rounded-lg font-semibold hover:from-green-400 hover:to-green-500 transition-all shadow-lg shadow-green-500/20">
              Get Started
            </button>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
