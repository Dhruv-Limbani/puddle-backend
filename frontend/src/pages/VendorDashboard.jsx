import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import VendorProfile from '../components/vendorProfile';
import Marketplace from '../components/Marketplace';
import {
  ProfileIcon,
  MarketplaceIcon,
  DataCatalogIcon,
  AgentIcon,
  PuddleLogoIcon,
  LogoutIcon,
  SidebarToggleIcon
} from '../components/icons';
import './VendorDashboard.css';

export default function VendorDashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [activeTab, setActiveTab] = useState('profile');
  const [isMinimized, setIsMinimized] = useState(false);

  useEffect(() => {
    // Remove the path checking since we're handling tabs internally
    // You can keep this if you want URL persistence, but for now let's simplify
  }, [location]);

  const navigationItems = [
    { id: 'profile', label: 'Profile', desc:'Manage your vendor presence on Puddle', icon: ProfileIcon },
    { id: 'marketplace', label: 'Marketplace', desc:'Search Datasets and Vendors', icon: MarketplaceIcon },
    { id: 'data-catalog', label: 'Data Catalog', desc:'Manage your vendor presence on Puddle', icon: DataCatalogIcon },
    { id: 'agents', label: 'AI Agents', desc:'Manage your vendor presence on Puddle', icon: AgentIcon },
  ];

  const handleNavigation = (item) => {
    setActiveTab(item.id);
    // Don't navigate to a different route, just change the tab state
    // This keeps everything within the /vendor-dashboard route
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'profile':
        return <VendorProfile />;
      case 'marketplace':
        return <Marketplace />;
      case 'data-catalog':
        return <div className="page-placeholder">Data Catalog - Coming Soon</div>;
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
          <p>{navigationItems.find(item => item.id === activeTab)?.desc || 'Vendor Dashboard'}</p>
        </div>
        
        <div className="main-content">
          {renderContent()}
        </div>
      </main>
    </div>
  );
}