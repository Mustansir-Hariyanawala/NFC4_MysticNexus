import { useEffect, useState } from 'react';

const ProfessionalChat = () => {
  const [selectedAvatar, setSelectedAvatar] = useState(null);
  const [isFullScreen, setIsFullScreen] = useState(false);

  // Avatar options with descriptions - using your actual HeyGen avatars
  const avatars = [
    {
      id: 1,
      name: "Dr. Smith",
      image: "https://files2.heygen.ai/avatar/v3/f83fffc45faa4368b6db9597e6b323ca_45590/preview_talk_3.webp",
      logo: "🩺",
      description: "Medical expertise and health consultation with professional AI-powered diagnosis support.",
      heygenUrl: "https://labs.heygen.com/guest/streaming-embed?share=eyJxdWFsaXR5IjoiaGlnaCIsImF2YXRhck5hbWUiOiJEZXh0ZXJfRG9jdG9yX1NpdHRpbmcyX3B1YmxpYyIsInByZXZpZXdJbWciOiJodHRwczovL2ZpbGVzMi5oZXlnZW4uYWkvYXZhdGFyL3YzL2Y4M2ZmZmM0NWZhYTQzNjhiNmRiOTU5N2U2YjMyM2NhXzQ1NTkwL3ByZXZpZXdfdGFsa18zLndlYnAiLCJuZWVkUmVtb3ZlQmFja2dyb3VuZCI6ZmFsc2UsImtub3dsZWRnZUJhc2VJZCI6Ijk0MzIzOTA4YzgzNDQ5Mjg5YWY4N2MyODlhZTJmZDMwIiwidXNlcm5hbWUiOiI0MmE3OTNhZTJjMjk0OWNlYTE1YmI5MjhjMGZlMmFkMSJ9&inIFrame=1"
    },
    {
      id: 2,
      name: "Dr. Johnson",
      image: "https://files2.heygen.ai/avatar/v3/33c9ac4aead44dfc8bc0082a35062a70_45580/preview_talk_3.webp",
      logo: "💻",
      description: "Research scientist and tech expert specializing in data analysis and IT solutions.",
      heygenUrl: "https://labs.heygen.com/guest/streaming-embed?share=eyJxdWFsaXR5IjoiaGlnaCIsImF2YXRhck5hbWUiOiJCcnlhbl9JVF9TaXR0aW5nX3B1YmxpYyIsInByZXZpZXdJbWciOiJodHRwczovL2ZpbGVzMi5oZXlnZW4uYWkvYXZhdGFyL3YzLzMzYzlhYzRhZWFkNDRkZmM4YmMwMDgyYTM1MDYyYTcwXzQ1NTgwL3ByZXZpZXdfdGFsa18zLndlYnAiLCJuZWVkUmVtb3ZlQmFja2dyb3VuZCI6ZmFsc2UsImtub3dsZWRnZUJhc2VJZCI6ImRlbW8tMSIsInVzZXJuYW1lIjoiNDJhNzkzYWUyYzI5NDljZWExNWJiOTI4YzBmZTJhZDEifQ%3D%3D&inIFrame=1"
    },
    {
      id: 3,
      name: "Attorney Williams",
      image: "https://files2.heygen.ai/avatar/v3/a7c86cb77b3144948bf8020f6e734bbf_45640/preview_talk_1.webp",
      logo: "⚖️",
      description: "Professional legal counsel providing comprehensive legal advice and document review services.",
      heygenUrl: "https://labs.heygen.com/guest/streaming-embed?share=eyJxdWFsaXR5IjoiaGlnaCIsImF2YXRhck5hbWUiOiJKdWR5X0xhd3llcl9TaXR0aW5nMl9wdWJsaWMiLCJwcmV2aWV3SW1nIjoiaHR0cHM6Ly9maWxlczIuaGV5Z2VuLmFpL2F2YXRhci92My9hN2M4NmNiNzdiMzE0NDk0OGJmODAyMGY2ZTczNGJiZl80NTY0MC9wcmV2aWV3X3RhbGtfMS53ZWJwIiwibmVlZFJlbW92ZUJhY2tncm91bmQiOmZhbHNlLCJrbm93bGVkZ2VCYXNlSWQiOiJkZW1vLTEiLCJ1c2VybmFtZSI6IjQyYTc5M2FlMmMyOTQ5Y2VhMTViYjkyOGMwZmUyYWQxIn0%3D&inIFrame=1"
    }
  ];

  useEffect(() => {
    if (!selectedAvatar) return;

    const host = "https://labs.heygen.com";
    const url = selectedAvatar.heygenUrl;
    isFullScreen;
    const wrapDiv = document.createElement("div");
    wrapDiv.id = "heygen-streaming-embed";
    
    const container = document.createElement("div");
    container.id = "heygen-streaming-container";
    
    const stylesheet = document.createElement("style");
    stylesheet.innerHTML = `
      #heygen-streaming-embed {
        z-index: 9999;
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: linear-gradient(135deg, #111827, #1f2937);
        border: none;
        transition: all linear 0.3s;
        overflow: hidden;
        opacity: 0;
        visibility: hidden;
      }
      #heygen-streaming-embed.show {
        opacity: 1;
        visibility: visible;
      }
      #heygen-streaming-container {
        width: 100%;
        height: 100%;
        position: relative;
      }
      #heygen-streaming-container iframe {
        width: 100%;
        height: 100%;
        border: 0;
      }
      .close-button {
        position: absolute;
        top: 20px;
        right: 20px;
        background: linear-gradient(to right, #10b981, #16a085);
        border: none;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        font-size: 24px;
        cursor: pointer;
        z-index: 10000;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s;
        color: black;
        font-weight: bold;
      }
      .close-button:hover {
        background: linear-gradient(to right, #059669, #047857);
        transform: scale(1.1);
      }
    `;
    
    const iframe = document.createElement("iframe");
    iframe.allowFullscreen = false;
    iframe.title = "Streaming Embed";
    iframe.role = "dialog";
    iframe.allow = "microphone";
    iframe.src = url;
    
    const closeButton = document.createElement("button");
    closeButton.className = "close-button";
    closeButton.innerHTML = "×";
    closeButton.onclick = () => {
      setSelectedAvatar(null);
      setIsFullScreen(false);
    };
    
    let visible = false;
    let initial = false;
    
    const messageHandler = (e) => {
      if (e.origin === host && e.data && e.data.type === "streaming-embed") {
        if (e.data.action === "init") {
          initial = true;
          wrapDiv.classList.toggle("show", initial);
        }
      }
    };
    
    window.addEventListener("message", messageHandler);
    container.appendChild(iframe);
    container.appendChild(closeButton);
    wrapDiv.appendChild(stylesheet);
    wrapDiv.appendChild(container);
    document.body.appendChild(wrapDiv);
    
    // Show immediately in full screen
    setTimeout(() => {
      wrapDiv.classList.add("show");
    }, 100);
    
    return () => {
      window.removeEventListener("message", messageHandler);
      if (document.body.contains(wrapDiv)) {
        document.body.removeChild(wrapDiv);
      }
    };
  }, [selectedAvatar]);

  if (selectedAvatar) {
    return null; // The iframe will be rendered via DOM manipulation
  }

  return (
    <div className="min-h-screen bg-gray-900 p-8">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-green-400 to-green-600 bg-clip-text text-transparent mb-4">
            Choose Your AI Avatar
          </h1>
          <p className="text-green-300 text-lg">
            Select an AI assistant to start your personalized interaction
          </p>
        </div>
        
        <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
          {avatars.map((avatar) => (
            <div
              key={avatar.id}
              onClick={() => setSelectedAvatar(avatar)}
              className="bg-gray-800 rounded-2xl shadow-2xl hover:shadow-green-500/20 transition-all duration-300 cursor-pointer transform hover:scale-105 overflow-hidden border border-green-500/20 hover:border-green-400/50"
            >
              {/* Avatar Image Section */}
              <div className="relative h-64 bg-gradient-to-br from-gray-700 to-gray-800">
                <img
                  src={avatar.image}
                  alt={avatar.name}
                  className="w-full h-full object-cover"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/40 to-transparent"></div>
              </div>
              
              {/* Logo and Description Section */}
              <div className="p-6">
                <div className="flex items-center justify-center mb-4 gap-2">
                  <div className="text-4xl bg-white p-3 rounded-full border border-green-500/30">
                    {avatar.logo}
                  </div>
                  <h3 className="text-xl font-semibold text-green-400 text-center mb-2">
                    {avatar.name}
                  </h3>
                </div>
                
                <p className="text-green-300 text-sm leading-relaxed text-center mb-6">
                  {avatar.description}
                </p>
                
                <div className="mt-6">
                  <button className="w-full bg-gradient-to-r from-green-500 to-green-600 text-black py-3 px-6 rounded-lg font-bold hover:from-green-400 hover:to-green-500 transition-all duration-200 transform hover:scale-[1.02] shadow-lg shadow-green-500/20">
                    Start Conversation
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ProfessionalChat;