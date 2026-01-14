import React, { useState, useEffect } from 'react';
import { Upload, FileText, Image, Video, File, MessageSquare, Zap, Shield, ArrowRight, Play, Check } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import image2 from '../assets/image2.png';
const LandingPage = () => {
  const navigate = useNavigate();
  const [isVisible, setIsVisible] = useState({});

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setIsVisible(prev => ({ ...prev, [entry.target.id]: true }));
          }
        });
      },
      { threshold: 0.1 }
    );

    document.querySelectorAll('[data-animate]').forEach((el) => {
      observer.observe(el);
    });

    return () => observer.disconnect();
  }, []);

  const features = [
    {
      icon: <Upload className="w-6 h-6" />,
      title: "Multi-File Upload",
      description: "Drag and drop multiple files at once. Supports images, videos, PDFs, and documents.",
      color: "from-green-400 to-green-600"
    },
    {
      icon: <FileText className="w-6 h-6" />,
      title: "Instant Analysis",
      description: "Get comprehensive summaries and insights from your uploaded files in seconds.",
      color: "from-blue-400 to-green-400"
    },
    {
      icon: <MessageSquare className="w-6 h-6" />,
      title: "Interactive Chat",
      description: "Ask questions about your files and get detailed, contextual responses.",
      color: "from-green-500 to-emerald-500"
    },
    {
      icon: <Shield className="w-6 h-6" />,
      title: "Secure Processing",
      description: "Your files are processed securely with enterprise-grade encryption.",
      color: "from-emerald-400 to-green-600"
    }
  ];

  const supportedFormats = [
    { icon: <Image className="w-5 h-5" />, name: "Images", formats: "JPG, PNG, GIF, SVG" },
    { icon: <Video className="w-5 h-5" />, name: "Videos", formats: "MP4, AVI, MOV, MKV" },
    { icon: <FileText className="w-5 h-5" />, name: "Documents", formats: "PDF, DOC, TXT" },
    { icon: <File className="w-5 h-5" />, name: "Archives", formats: "ZIP" }
  ];

  return (
    <div className="min-h-screen bg-gray-900 text-white overflow-hidden pt-14">
      {/* Animated Background */}
      <div className="fixed inset-0 z-0">
        <div className="absolute inset-0 bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900"></div>
        <div className="absolute inset-0">
          {[...Array(20)].map((_, i) => (
            <div
              key={i}
              className="absolute w-1 h-1 bg-green-400 rounded-full animate-pulse"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 3}s`,
                animationDuration: `${2 + Math.random() * 2}s`
              }}
            ></div>
          ))}
        </div>
      </div>

      {/* Hero Section */}
      <section className="relative z-10 pt-20 pb-32">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div 
              className={`transition-all duration-1000 ${isVisible.hero ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}
              id="hero"
              data-animate
            >
              <h1 className="text-5xl md:text-7xl font-bold mb-6">
                <span className="bg-gradient-to-r from-green-400 to-green-600 bg-clip-text text-transparent">
                  Analyze Files
                </span>
                <br />
                <span className="text-white">with AI Power</span>
              </h1>
              <p className="text-xl md:text-2xl text-gray-300 mb-8 max-w-3xl mx-auto leading-relaxed">
                Upload any file format and get instant, intelligent summaries. Chat with your documents, 
                images, and videos like never before.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
                <button className="group bg-gradient-to-r from-green-500 to-green-600 text-black px-8 py-4 rounded-lg font-bold text-lg hover:from-green-400 hover:to-green-500 transition-all shadow-lg shadow-green-500/20 flex items-center space-x-2" onClick={() => navigate('/chat')}>
                  <span>Start Analyzing</span>
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </button>
                <button className="group border border-green-400 text-green-400 px-8 py-4 rounded-lg font-bold text-lg hover:bg-green-400/10 transition-all flex items-center space-x-2">
                  <Play className="w-5 h-5" />
                  <span>Watch Demo</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="relative z-10 py-5 bg-gray-800/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div 
            className={`text-center mb-16 transition-all duration-1000 ${isVisible.featuresTitle ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}
            id="featuresTitle"
            data-animate
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-6">
              <span className="text-green-400">Powerful</span> Features
            </h2>
            <p className="text-xl text-gray-300 max-w-2xl mx-auto">
              Everything you need to transform your files into actionable insights
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <div
                key={index}
                className={`group bg-gray-800 border border-green-500/20 rounded-xl p-6 hover:border-green-400/40 transition-all duration-500 hover:transform hover:scale-105 hover:shadow-2xl hover:shadow-green-500/10 ${isVisible.features ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}
                style={{ transitionDelay: `${index * 100}ms` }}
                id="features"
                data-animate
              >
                <div className={`w-12 h-12 bg-gradient-to-r ${feature.color} rounded-lg flex items-center justify-center text-black mb-4 group-hover:scale-110 transition-transform`}>
                  {feature.icon}
                </div>
                <h3 className="text-xl font-bold text-white mb-3">{feature.title}</h3>
                <p className="text-gray-400 leading-relaxed">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* About Us Section */}
      <section id="about" className="relative z-10 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left Column - Content */}
            <div 
              className={`transition-all duration-1000 ${isVisible.aboutContent ? 'opacity-100 translate-x-0' : 'opacity-0 -translate-x-10'}`}
              id="aboutContent"
              data-animate
            >
              <h2 className="text-4xl md:text-5xl font-bold mb-6">
                About <span className="text-green-400">Our Mission</span>
              </h2>
              <p className="text-xl text-gray-300 mb-6 leading-relaxed">
                We believe that every file contains valuable insights waiting to be discovered. 
                Our AI-powered platform breaks down the barriers between you and your data, 
                making complex analysis accessible to everyone.
              </p>
              <p className="text-lg text-gray-400 mb-8 leading-relaxed">
                Founded by a team of AI researchers and data scientists, we're passionate about 
                democratizing artificial intelligence and helping individuals and businesses 
                unlock the hidden potential in their documents, images, and multimedia files.
              </p>
              
              {/* Key Values */}
              <div className="space-y-4">
                {[
                  { title: "Innovation First", desc: "Cutting-edge AI technology that evolves with your needs" },
                  { title: "Privacy Focused", desc: "Your data security and privacy are our top priorities" },
                  { title: "User-Centric", desc: "Designed for simplicity without sacrificing powerful features" }
                ].map((value, index) => (
                  <div key={index} className="flex items-start space-x-3">
                    <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                      <Check className="w-4 h-4 text-black" />
                    </div>
                    <div>
                      <h4 className="font-bold text-white mb-1">{value.title}</h4>
                      <p className="text-gray-400 text-sm">{value.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Right Column - Visual Element */}
            <div 
              className={`transition-all duration-1000 delay-300 ${isVisible.aboutVisual ? 'opacity-100 translate-x-0' : 'opacity-0 translate-x-10'}`}
              id="aboutVisual"
              data-animate
            >
              <div className="relative">
                {/* Main Card */}
                <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl p-8 border border-green-500/20 shadow-2xl">
                  <div className="flex items-center space-x-4 mb-6">
                    <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-green-600 rounded-lg flex items-center justify-center">
                      <Zap className="w-6 h-6 text-black" />
                    </div>
                    <div>
                        <img src={image2} alt="" />
                    </div>
                  </div>         
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Supported Formats */}
      <section className="relative z-10 py-20 bg-gray-800/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div 
            className={`text-center mb-16 transition-all duration-1000 ${isVisible.formatsTitle ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}
            id="formatsTitle"
            data-animate
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-6">
              <span className="text-green-400">Universal</span> File Support
            </h2>
            <p className="text-xl text-gray-300">
              Works with all your favorite file formats
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {supportedFormats.map((format, index) => (
              <div
                key={index}
                className={`bg-gray-800 border border-green-500/20 rounded-xl p-6 text-center hover:border-green-400/40 transition-all duration-300 hover:transform hover:scale-105 ${isVisible.formats ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}
                style={{ transitionDelay: `${index * 100}ms` }}
                id="formats"
                data-animate
              >
                <div className="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center text-green-400 mx-auto mb-4">
                  {format.icon}
                </div>
                <h3 className="text-lg font-bold text-white mb-2">{format.name}</h3>
                <p className="text-sm text-gray-400">{format.formats}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="relative z-10 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div 
            className={`text-center mb-16 transition-all duration-1000 ${isVisible.howTitle ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}
            id="howTitle"
            data-animate
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-6">
              How It <span className="text-green-400">Works</span>
            </h2>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              { step: "1", title: "Upload Files", desc: "Drag and drop or select multiple files of any format" },
              { step: "2", title: "AI Analysis", desc: "Our advanced AI processes and understands your content" },
              { step: "3", title: "Get Insights", desc: "Receive summaries, answers, and interactive discussions" }
            ].map((item, index) => (
              <div
                key={index}
                className={`text-center transition-all duration-1000 ${isVisible.howSteps ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}
                style={{ transitionDelay: `${index * 200}ms` }}
                id="howSteps"
                data-animate
              >
                <div className="w-16 h-16 bg-gradient-to-r from-green-500 to-green-600 rounded-full flex items-center justify-center text-black font-bold text-xl mx-auto mb-6">
                  {item.step}
                </div>
                <h3 className="text-xl font-bold text-white mb-4">{item.title}</h3>
                <p className="text-gray-400 leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative z-10 py-20 bg-gray-800/30">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div 
            className={`transition-all duration-1000 ${isVisible.cta ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}
            id="cta"
            data-animate
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-6">
              Ready to <span className="text-green-400">Transform</span> Your Files?
            </h2>
            <p className="text-xl text-gray-300 mb-8">
              Join thousands of users who are already getting insights from their files with AI
            </p>
            <button className="group bg-gradient-to-r from-green-500 to-green-600 text-black px-10 py-4 rounded-lg font-bold text-xl hover:from-green-400 hover:to-green-500 transition-all shadow-lg shadow-green-500/20 flex items-center space-x-2 mx-auto" onClick={() => navigate('/chat')}>
              <span>Get Started Free</span>
              <ArrowRight className="w-6 h-6 group-hover:translate-x-1 transition-transform" />
            </button>
          </div>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;