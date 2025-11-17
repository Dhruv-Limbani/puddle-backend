import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import VendorProfile from '../components/VendorProfile';
import Marketplace from '../components/Marketplace';
import DataCatalogTab from '../components/DataCatalog'; // <-- IMPORT THE NEW COMPONENT
import {
  ProfileIcon,
  MarketplaceIcon,
  DataCatalogIcon,
  AgentIcon,
  PuddleLogoIcon,
  LogoutIcon,
  SidebarToggleIcon
} from '../components/icons'; // Make sure Icons.jsx is updated
import './VendorDashboard.css';
import '../components/DataCatalog.css'; // <-- IMPORT THE NEW CSS

export default function VendorDashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [activeTab, setActiveTab] = useState('profile');
  const [isMinimized, setIsMinimized] = useState(false);

  useEffect(() => {
    // This logic is fine, it will set the tab based on the URL
    const path = location.pathname;
    if (path.includes('marketplace')) setActiveTab('marketplace');
    else if (path.includes('data-catalog')) setActiveTab('data-catalog');
    else if (path.includes('agents')) setActiveTab('agents');
    else setActiveTab('profile');
  }, [location]);

  const navigationItems = [
    { id: 'profile', label: 'Profile', desc:'Manage your vendor presence on Puddle', icon: ProfileIcon },
    { id: 'marketplace', label: 'Marketplace', desc:'Search Datasets and Vendors', icon: MarketplaceIcon },
    { id: 'data-catalog', label: 'Data Catalog', desc:'Manage your datasets and columns', icon: DataCatalogIcon }, // <-- UPDATED DESCRIPTION
    { id: 'agents', label: 'AI Agents', desc:'Configure your AI agents', icon: AgentIcon },
  ];

  // This function can be simplified if you don't use routing for tabs
  const handleNavigation = (item) => {
    setActiveTab(item.id);
    // You can choose to navigate or not.
    // navigate(item.path); // Uncomment if you want URL-based navigation
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'profile':
        return <VendorProfile />;
      case 'marketplace':
        return <Marketplace />;
      case 'data-catalog':
        return <DataCatalogTab />; // <-- USE THE NEW COMPONENT
      case 'agents':
        return <div className="page-placeholder">AI Agents - Coming Soon</div>;
      default:
        return <VendorProfile />;
    }
  };

  return (
    <div className={`vendor-dashboard-layout ${isMinimized ? 'sidebar-minimized' : ''}`}>
      {/* Sidebar Navigation */}
      <nav className={`vendor-sidebar ${isMinimized ? 'minimized' : ''}`}>
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
            <span className="user-role">Vendor</span>
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
      <main className={`vendor-main ${isMinimized ? 'sidebar-minimized' : ''}`}>
        <div className="main-header">
          <h1>
            {navigationItems.find(item => item.id === activeTab)?.label || 'Vendor Dashboard'}
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