import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import VendorProfile from '../components/vendorProfile';
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
    const path = location.pathname;
    if (path.includes('marketplace')) setActiveTab('marketplace');
    else if (path.includes('data-catalog')) setActiveTab('data-catalog');
    else if (path.includes('agents')) setActiveTab('agents');
    else setActiveTab('profile');
  }, [location]);

  const navigationItems = [
    { id: 'profile', label: 'Profile', icon: ProfileIcon, path: '/vendor-dashboard' },
    { id: 'marketplace', label: 'Marketplace', icon: MarketplaceIcon, path: '/marketplace' },
    { id: 'data-catalog', label: 'Data Catalog', icon: DataCatalogIcon, path: '/data-catalog' },
    { id: 'agents', label: 'AI Agents', icon: AgentIcon, path: '/agents' },
  ];

  const handleNavigation = (item) => {
    setActiveTab(item.id);
    navigate(item.path);
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'profile':
        return <VendorProfile />;
      case 'marketplace':
        return <div className="page-placeholder">Marketplace - Coming Soon</div>;
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
          <p>Manage your vendor presence on Puddle</p>
        </div>
        
        <div className="main-content">
          {renderContent()}
        </div>
      </main>
    </div>
  );
}