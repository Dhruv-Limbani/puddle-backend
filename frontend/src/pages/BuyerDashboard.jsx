import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import BuyerProfile from '../components/BuyerProfile';
import Marketplace from '../components/Marketplace';
import AcidAI from '../components/AcidAI';
import {
  ProfileIcon,
  MarketplaceIcon,
  AgentIcon,
  PuddleLogoIcon,
  LogoutIcon,
  SidebarToggleIcon
} from '../components/Icons';
import './BuyerDashboard.css';
import './VendorDashboard.css'; // Import shared form styles

export default function BuyerDashboard() {
  const { user, logout, token } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [activeTab, setActiveTab] = useState('profile');
  const [isMinimized, setIsMinimized] = useState(false);

  useEffect(() => {
    // Check query params for tab state (better for history navigation)
    const searchParams = new URLSearchParams(location.search);
    const tab = searchParams.get('tab');
    
    if (tab) {
      setActiveTab(tab);
    } else {
      // Fallback to path check or default
      const path = location.pathname;
      if (path.includes('marketplace')) setActiveTab('marketplace');
      else if (path.includes('acid-ai')) setActiveTab('acid-ai');
      else setActiveTab('profile');
    }
  }, [location]);

  const navigationItems = [
    { id: 'profile', label: 'Profile', desc: 'Manage your buyer profile', icon: ProfileIcon },
    { id: 'marketplace', label: 'Marketplace', desc: 'Search Datasets and Vendors', icon: MarketplaceIcon },
    { id: 'acid-ai', label: 'ACID AI', desc: 'AI Assistant for Dataset Discovery', icon: AgentIcon },
  ];

  const handleNavigation = (item) => {
    // Update URL with query param to support back button navigation
    navigate(`?tab=${item.id}`);
    setActiveTab(item.id);
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'profile':
        return <BuyerProfile />;
      case 'marketplace':
        return <Marketplace />;
      case 'acid-ai':
        return <AcidAI token={token} />;
      default:
        return <BuyerProfile />;
    }
  };

  return (
    <div className={`buyer-dashboard-layout ${isMinimized ? 'sidebar-minimized' : ''}`}>
      {/* Sidebar Navigation */}
      <nav className={`buyer-sidebar ${isMinimized ? 'minimized' : ''}`}>
        <div className="sidebar-header">
          <div className="puddle-logo">
            <PuddleLogoIcon />
            <h2>Puddle</h2>
          </div>
          
          <button 
            className="sidebar-toggle" 
            onClick={() => setIsMinimized(!isMinimized)}
            title={isMinimized ? 'Expand Sidebar' : 'Collapse Sidebar'}
          >
            <SidebarToggleIcon />
          </button>
          
          <div className="user-info">
            <span className="user-name">{user?.email}</span>
            <span className="user-role">Buyer</span>
          </div>
        </div>

        <div className="sidebar-nav">
          {navigationItems.map((item) => {
            const IconComponent = item.icon;
            return (
              <button
                key={item.id}
                title={isMinimized ? item.label : ''}
                className={`nav-item ${activeTab === item.id ? 'active' : ''}`}
                onClick={() => handleNavigation(item)}
              >
                <IconComponent />
                <span>{item.label}</span>
              </button>
            );
          })}
        </div>

        <div className="sidebar-footer">
          <button 
            className="logout-btn" 
            onClick={logout}
            title={isMinimized ? 'Sign Out' : ''}
          >
            <LogoutIcon />
            <span>Sign Out</span>
          </button>
        </div>
      </nav>

      {/* Main Content */}
      <main className={`buyer-main ${isMinimized ? 'sidebar-minimized' : ''}`}>
        <div className="main-header">
          <h1>
            {navigationItems.find(item => item.id === activeTab)?.label || 'Buyer Dashboard'}
          </h1>
          <p>{navigationItems.find(item => item.id === activeTab)?.desc || 'Manage your Puddle account'}</p>
        </div>
        
        <div className="main-content">
          {renderContent()}
        </div>
      </main>
    </div>
  );
}
