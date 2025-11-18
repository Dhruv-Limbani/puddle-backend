import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { buyerService } from '../services/buyerService';
import {
  BriefcaseIcon,
  UsersIcon,
  MailIcon,
  PhoneIcon,
  MapPinIcon,
  AlignLeftIcon
} from './icons';

const EMPTY_BUYER_FORM = {
  name: '',
  organization: '',
  contact_email: '',
  contact_phone: '',
  country: '',
  region: '',
  city: '',
  address: '',
  organization_type: '',
  job_title: '',
  industry: '',
  use_case_focus: '',
};

export default function BuyerProfile() {
  const { user, token } = useAuth();
  const [buyerProfile, setBuyerProfile] = useState(null);
  const [formData, setFormData] = useState(EMPTY_BUYER_FORM);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [showSuccessToast, setShowSuccessToast] = useState(false);
  const [wasCreate, setWasCreate] = useState(false);

  useEffect(() => {
    loadBuyerData();
  }, [token, user?.id]);

  const loadBuyerData = async () => {
    setLoading(true);
    setError('');
    setMessage('');
    try {
      const buyer = await buyerService.getProfile(token);
      setBuyerProfile(buyer);
      if (buyer) {
        setFormData({
          ...EMPTY_BUYER_FORM,
          ...Object.fromEntries(
            Object.entries(buyer).filter(([key]) => key in EMPTY_BUYER_FORM),
          ),
        });
      } else {
        setFormData(EMPTY_BUYER_FORM);
      }
    } catch (err) {
      setError(err.message || 'Failed to load buyer profile');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (event) => {
    const { name, value } = event.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const preparePayload = () => {
    const payload = {};
    Object.entries(formData).forEach(([key, value]) => {
      if (value !== '') {
        payload[key] = value;
      }
    });
    return payload;
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    
    // Show confirmation modal only for updates
    if (buyerProfile) {
      setShowConfirmModal(true);
      return;
    }
    
    // For new profiles, save directly
    await saveProfile();
  };

  const saveProfile = async () => {
    setSaving(true);
    setMessage('');
    setError('');
    setShowConfirmModal(false);
    
    const payload = preparePayload();
    if (!payload.name || !payload.name.trim()) {
      setError('Name is required');
      setSaving(false);
      return;
    }
    
    try {
      if (buyerProfile) {
        await buyerService.updateProfile(token, payload);
        setWasCreate(false);
        setShowSuccessToast(true);
        setTimeout(() => setShowSuccessToast(false), 3000);
      } else {
        await buyerService.createProfile(token, payload);
        setWasCreate(true);
        setShowSuccessToast(true);
        setTimeout(() => setShowSuccessToast(false), 3000);
      }
      await loadBuyerData();
    } catch (err) {
      setError(err.message || 'Failed to save buyer profile');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="loading-state">
        <div className="loading-spinner"></div>
        <p>Loading buyer profile...</p>
      </div>
    );
  }

  return (
    <div className="buyer-profile">
      {/* Success Toast */}
      {showSuccessToast && (
        <div className="success-toast">
          <div className="success-toast-icon">✓</div>
          <div className="success-toast-message">
            {wasCreate ? 'Profile created successfully' : 'Profile updated successfully'}
          </div>
        </div>
      )}

      {/* Confirmation Modal */}
      {showConfirmModal && (
        <div className="modal-overlay" onClick={() => setShowConfirmModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Confirm Update</h3>
              <p>Are you sure you want to update your buyer profile?</p>
            </div>
            <div className="modal-actions">
              <button className="btn btn-secondary" onClick={() => setShowConfirmModal(false)}>
                Cancel
              </button>
              <button className="btn btn-primary" onClick={saveProfile} disabled={saving}>
                {saving ? 'Updating...' : 'Update'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Alerts */}
      {(message || error) && (
        <div className="alerts-container">
          {message && <div className="alert alert-success">{message}</div>}
          {error && <div className="alert alert-error">{error}</div>}
        </div>
      )}

      {/* Profile Form */}
      <form className="buyer-form" onSubmit={handleSubmit}>
        {/* Basic Information Section */}
        <div className="form-section">
          <h3>Basic Information</h3>
          <div className="form-grid">
            <div className="form-group full">
              <label htmlFor="name" className="form-label">
                Full Name <span className="required">*</span>
              </label>
              <div className="input-wrapper">
                <span className="input-icon">
                  <UsersIcon />
                </span>
                <input
                  type="text"
                  id="name"
                  name="name"
                  className="form-input"
                  value={formData.name}
                  onChange={handleInputChange}
                  placeholder="Jane Doe"
                  disabled={saving}
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="organization" className="form-label">
                Organization
              </label>
              <div className="input-wrapper">
                <span className="input-icon">
                  <BriefcaseIcon />
                </span>
                <input
                  type="text"
                  id="organization"
                  name="organization"
                  className="form-input"
                  value={formData.organization}
                  onChange={handleInputChange}
                  placeholder="Research Institute"
                  disabled={saving}
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="job_title" className="form-label">
                Job Title
              </label>
              <div className="input-wrapper">
                <span className="input-icon">
                  <BriefcaseIcon />
                </span>
                <input
                  type="text"
                  id="job_title"
                  name="job_title"
                  className="form-input"
                  value={formData.job_title}
                  onChange={handleInputChange}
                  placeholder="Data Scientist"
                  disabled={saving}
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="industry" className="form-label">
                Industry
              </label>
              <div className="input-wrapper">
                <span className="input-icon">
                  <BriefcaseIcon />
                </span>
                <input
                  type="text"
                  id="industry"
                  name="industry"
                  className="form-input"
                  value={formData.industry}
                  onChange={handleInputChange}
                  placeholder="Healthcare"
                  disabled={saving}
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="organization_type" className="form-label">
                Organization Type
              </label>
              <div className="input-wrapper">
                <span className="input-icon">
                  <BriefcaseIcon />
                </span>
                <input
                  type="text"
                  id="organization_type"
                  name="organization_type"
                  className="form-input"
                  value={formData.organization_type}
                  onChange={handleInputChange}
                  placeholder="Non-profit"
                  disabled={saving}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Contact Information Section */}
        <div className="form-section">
          <h3>Contact Information</h3>
          <div className="form-grid">
            <div className="form-group">
              <label htmlFor="contact_email" className="form-label">
                Contact Email
              </label>
              <div className="input-wrapper">
                <span className="input-icon">
                  <MailIcon />
                </span>
                <input
                  type="email"
                  id="contact_email"
                  name="contact_email"
                  className="form-input"
                  value={formData.contact_email}
                  onChange={handleInputChange}
                  placeholder="you@example.com"
                  disabled={saving}
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="contact_phone" className="form-label">
                Contact Phone
              </label>
              <div className="input-wrapper">
                <span className="input-icon">
                  <PhoneIcon />
                </span>
                <input
                  type="tel"
                  id="contact_phone"
                  name="contact_phone"
                  className="form-input"
                  value={formData.contact_phone}
                  onChange={handleInputChange}
                  placeholder="+1-555-0100"
                  disabled={saving}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Location Section */}
        <div className="form-section">
          <h3>Location</h3>
          <div className="form-grid">
            <div className="form-group">
              <label htmlFor="country" className="form-label">
                Country
              </label>
              <div className="input-wrapper">
                <span className="input-icon">
                  <MapPinIcon />
                </span>
                <input
                  type="text"
                  id="country"
                  name="country"
                  className="form-input"
                  value={formData.country}
                  onChange={handleInputChange}
                  placeholder="United States"
                  disabled={saving}
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="region" className="form-label">
                Region / State
              </label>
              <div className="input-wrapper">
                <span className="input-icon">
                  <MapPinIcon />
                </span>
                <input
                  type="text"
                  id="region"
                  name="region"
                  className="form-input"
                  value={formData.region}
                  onChange={handleInputChange}
                  placeholder="California"
                  disabled={saving}
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="city" className="form-label">
                City
              </label>
              <div className="input-wrapper">
                <span className="input-icon">
                  <MapPinIcon />
                </span>
                <input
                  type="text"
                  id="city"
                  name="city"
                  className="form-input"
                  value={formData.city}
                  onChange={handleInputChange}
                  placeholder="San Francisco"
                  disabled={saving}
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="address" className="form-label">
                Address
              </label>
              <div className="input-wrapper">
                <span className="input-icon">
                  <MapPinIcon />
                </span>
                <input
                  type="text"
                  id="address"
                  name="address"
                  className="form-input"
                  value={formData.address}
                  onChange={handleInputChange}
                  placeholder="123 Market St"
                  disabled={saving}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Use Case Section */}
        <div className="form-section">
          <h3>Use Case Focus</h3>
          <div className="form-grid">
            <div className="form-group full">
              <label htmlFor="use_case_focus" className="form-label">
                Use Case Focus
              </label>
              <div className="input-wrapper">
                <span className="input-icon textarea-icon">
                  <AlignLeftIcon />
                </span>
                <textarea
                  id="use_case_focus"
                  name="use_case_focus"
                  className="form-input"
                  value={formData.use_case_focus}
                  onChange={handleInputChange}
                  placeholder="Describe the key datasets or insights you're looking for..."
                  disabled={saving}
                  rows={4}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Form Actions */}
        <div className="form-actions">
          <button type="submit" className="btn btn-primary" disabled={saving}>
            {saving ? 'Saving...' : buyerProfile ? 'Update Profile' : 'Create Profile'}
          </button>
        </div>
      </form>
    </div>
  );
}
