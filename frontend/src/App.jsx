import './App.css'
import { Routes, Route } from 'react-router-dom';
import AuthPage from './components/AuthPage'
import Navbar from './components/Navbar';
import ChatComponent from './components/ChatComponent';
import LandingPage from './components/LandingPage';
import Footer from './components/Footer';
import HeyGenAvatar from './components/HeyGenAvatar';
import ProfessionalChat from './components/ProfessionalChat';
function App() {
  return (
    <>
      <Navbar/>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/auth" element={<AuthPage />} />
        <Route path="/chat" element={<ChatComponent />} />
        <Route path="/profchat" element={<ProfessionalChat />} />
      </Routes>
      <Footer />
      {/* <HeyGenAvatar/> */}
    </>
  )
}

export default App
