import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { vendorService } from '../services/vendorService';
import {
  BriefcaseIcon,
  ChartIcon,
  UsersIcon,
  CalendarIcon,
  MailIcon,
  PhoneIcon,
  LinkIcon,
  ImageIcon,
  MapPinIcon,
  AlignLeftIcon
} from './icons';

const EMPTY_VENDOR_FORM = {
  name: '',
  industry_focus: '',
  description: '',
  contact_email: '',
  contact_phone: '',
  website_url: '',
  logo_url: '',
  country: '',
  region: '',
  city: '',
  address: '',
  organization_type: '',
  founded_year: '',
};

export default function VendorProfile() {
  const { user, token } = useAuth();
  const [vendorProfile, setVendorProfile] = useState(null);
  const [formData, setFormData] = useState(EMPTY_VENDOR_FORM);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [showSuccessToast, setShowSuccessToast] = useState(false);

  useEffect(() => {
    loadVendorData();
  }, [token, user?.id]);

  const loadVendorData = async () => {
    setLoading(true);
    setError('');
    setMessage('');
    try {
      const vendors = await vendorService.list(token);
      const ownVendor = vendors.find((item) => item.user_id === user?.id) || null;
      setVendorProfile(ownVendor);
      if (ownVendor) {
        setFormData({
          ...EMPTY_VENDOR_FORM,
          ...Object.fromEntries(
            Object.entries(ownVendor).filter(([key]) => key in EMPTY_VENDOR_FORM),
          ),
          founded_year: ownVendor.founded_year ? String(ownVendor.founded_year) : '',
        });
      } else {
        setFormData(EMPTY_VENDOR_FORM);
      }
    } catch (err) {
      setError(err.message || 'Failed to load vendor information');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (event) => {
    const { name, value } = event.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'founded_year' ? value.replace(/[^0-9]/g, '') : value,
    }));
  };

  const preparePayload = () => {
    const payload = {};
    Object.entries(formData).forEach(([key, value]) => {
      if (value === '') return;
      if (key === 'founded_year') {
        const year = parseInt(value, 10);
        if (!Number.isNaN(year)) payload[key] = year;
        return;
      }
      payload[key] = value;
    });
    return payload;
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    
    // Show confirmation modal only for updates
    if (vendorProfile) {
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
    if (!payload.name) {
      setError('Vendor name is required');
      setSaving(false);
      return;
    }
    
    try {
      if (vendorProfile) {
        await vendorService.update(token, vendorProfile.id, payload);
        setShowSuccessToast(true);
        setTimeout(() => setShowSuccessToast(false), 3000);
      } else {
        await vendorService.create(token, payload);
        setMessage('Vendor profile created successfully');
      }
      await loadVendorData();
    } catch (err) {
      setError(err.message || 'Failed to save vendor profile');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="loading-state">
        <div className="loading-spinner"></div>
        <p>Loading vendor profile...</p>
      </div>
    );
  }

  return (
    <div className="vendor-profile">
      {/* Success Toast */}
      {showSuccessToast && (
        <div className="success-toast">
          <div className="success-toast-icon">✓</div>
          <div className="success-toast-message">Profile updated successfully!</div>
        </div>
      )}

      {/* Confirmation Modal */}
      {showConfirmModal && (
        <div className="modal-overlay" onClick={() => setShowConfirmModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Confirm Update</h3>
              <p>Are you sure you want to update your vendor profile?</p>
            </div>
            <div className="modal-actions">
              <button 
                className="btn btn-secondary" 
                onClick={() => setShowConfirmModal(false)}
                disabled={saving}
              >
                Cancel
              </button>
              <button 
                className="btn btn-primary" 
                onClick={saveProfile}
                disabled={saving}
              >
                {saving ? 'Updating...' : 'Confirm Update'}
              </button>
            </div>
          </div>
        </div>
      )}

      {(message || error) && (
        <div className="alerts-container">
          {message && <div className="alert alert-success">{message}</div>}
          {error && <div className="alert alert-error">{error}</div>}
        </div>
      )}

      <form className="vendor-form" onSubmit={handleSubmit}>
        <div className="form-section">
          <h3>Basic Information</h3>
          <div className="form-grid">
            {/* Vendor Name */}
            <div className="form-group full">
              <label htmlFor="name" className="form-label">
                Vendor Name <span className="required">*</span>
              </label>
              <div className="input-wrapper">
                <div className="input-group">
                  <span className="input-icon"><BriefcaseIcon /></span>
                  <input
                    id="name"
                    name="name"
                    type="text"
                    required
                    value={formData.name}
                    onChange={handleInputChange}
                    disabled={saving}
                    placeholder="Example Data Corp"
                    className="form-input"
                  />
                </div>
              </div>
            </div>

            {/* Industry Focus */}
            <div className="form-group">
              <label htmlFor="industry_focus" className="form-label">Industry Focus</label>
              <div className="input-wrapper">
                <div className="input-group">
                  <span className="input-icon"><ChartIcon /></span>
                  <input
                    id="industry_focus"
                    name="industry_focus"
                    type="text"
                    value={formData.industry_focus}
                    onChange={handleInputChange}
                    disabled={saving}
                    placeholder="Finance, Healthcare, Retail..."
                    className="form-input"
                  />
                </div>
              </div>
            </div>

            {/* Organization Type */}
            <div className="form-group">
              <label htmlFor="organization_type" className="form-label">Organization Type</label>
              <div className="input-wrapper">
                <div className="input-group">
                  <span className="input-icon"><UsersIcon /></span>
                  <input
                    id="organization_type"
                    name="organization_type"
                    type="text"
                    value={formData.organization_type}
                    onChange={handleInputChange}
                    disabled={saving}
                    placeholder="Private Company, Non-profit..."
                    className="form-input"
                  />
                </div>
              </div>
            </div>

            {/* Founded Year */}
            <div className="form-group">
              <label htmlFor="founded_year" className="form-label">Founded Year</label>
              <div className="input-wrapper">
                <div className="input-group">
                  <span className="input-icon"><CalendarIcon /></span>
                  <input
                    id="founded_year"
                    name="founded_year"
                    type="text"
                    inputMode="numeric"
                    value={formData.founded_year}
                    onChange={handleInputChange}
                    disabled={saving}
                    placeholder="2016"
                    maxLength={4}
                    className="form-input"
                  />
                </div>
              </div>
            </div>

            {/* Description */}
            <div className="form-group full">
              <label htmlFor="description" className="form-label">Description</label>
              <div className="input-wrapper">
                <div className="input-group">
                  <span className="input-icon textarea-icon"><AlignLeftIcon /></span>
                  <textarea
                    id="description"
                    name="description"
                    rows={4}
                    value={formData.description}
                    onChange={handleInputChange}
                    disabled={saving}
                    placeholder="Tell buyers about your datasets, expertise, and what makes your data valuable..."
                    className="form-input"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="form-section">
          <h3>Contact Information</h3>
          <div className="form-grid">
            {/* Contact Email */}
            <div className="form-group">
              <label htmlFor="contact_email" className="form-label">Contact Email</label>
              <div className="input-wrapper">
                <div className="input-group">
                  <span className="input-icon"><MailIcon /></span>
                  <input
                    id="contact_email"
                    name="contact_email"
                    type="email"
                    value={formData.contact_email}
                    onChange={handleInputChange}
                    disabled={saving}
                    placeholder="data@example.com"
                    className="form-input"
                  />
                </div>
              </div>
            </div>

            {/* Contact Phone */}
            <div className="form-group">
              <label htmlFor="contact_phone" className="form-label">Contact Phone</label>
              <div className="input-wrapper">
                <div className="input-group">
                  <span className="input-icon"><PhoneIcon /></span>
                  <input
                    id="contact_phone"
                    name="contact_phone"
                    type="text"
                    value={formData.contact_phone}
                    onChange={handleInputChange}
                    disabled={saving}
                    placeholder="+1-555-0100"
                    className="form-input"
                  />
                </div>
              </div>
            </div>

            {/* Website URL */}
            <div className="form-group">
              <label htmlFor="website_url" className="form-label">Website URL</label>
              <div className="input-wrapper">
                <div className="input-group">
                  <span className="input-icon"><LinkIcon /></span>
                  <input
                    id="website_url"
                    name="website_url"
                    type="url"
                    value={formData.website_url}
                    onChange={handleInputChange}
                    disabled={saving}
                    placeholder="https://example.com"
                    className="form-input"
                  />
                </div>
              </div>
            </div>

            {/* Logo URL */}
            <div className="form-group">
              <label htmlFor="logo_url" className="form-label">Logo URL</label>
              <div className="input-wrapper">
                <div className="input-group">
                  <span className="input-icon"><ImageIcon /></span>
                  <input
                    id="logo_url"
                    name="logo_url"
                    type="url"
                    value={formData.logo_url}
                    onChange={handleInputChange}
                    disabled={saving}
                    placeholder="https://example.com/logo.png"
                    className="form-input"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="form-section">
          <h3>Location</h3>
          <div className="form-grid">
            {/* Country */}
            <div className="form-group">
              <label htmlFor="country" className="form-label">Country</label>
              <div className="input-wrapper">
                <div className="input-group">
                  <span className="input-icon"><MapPinIcon /></span>
                  <input
                    id="country"
                    name="country"
                    type="text"
                    value={formData.country}
                    onChange={handleInputChange}
                    disabled={saving}
                    placeholder="United States"
                    className="form-input"
                  />
                </div>
              </div>
            </div>

            {/* Region */}
            <div className="form-group">
              <label htmlFor="region" className="form-label">Region / State</label>
              <div className="input-wrapper">
                <div className="input-group">
                  <span className="input-icon"><MapPinIcon /></span>
                  <input
                    id="region"
                    name="region"
                    type="text"
                    value={formData.region}
                    onChange={handleInputChange}
                    disabled={saving}
                    placeholder="California"
                    className="form-input"
                  />
                </div>
              </div>
            </div>

            {/* City */}
            <div className="form-group">
              <label htmlFor="city" className="form-label">City</label>
              <div className="input-wrapper">
                <div className="input-group">
                  <span className="input-icon"><MapPinIcon /></span>
                  <input
                    id="city"
                    name="city"
                    type="text"
                    value={formData.city}
                    onChange={handleInputChange}
                    disabled={saving}
                    placeholder="San Francisco"
                    className="form-input"
                  />
                </div>
              </div>
            </div>

            {/* Address */}
            <div className="form-group">
              <label htmlFor="address" className="form-label">Address</label>
              <div className="input-wrapper">
                <div className="input-group">
                  <span className="input-icon"><MapPinIcon /></span>
                  <input
                    id="address"
                    name="address"
                    type="text"
                    value={formData.address}
                    onChange={handleInputChange}
                    disabled={saving}
                    placeholder="123 Market St"
                    className="form-input"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="form-actions">
          <button type="submit" className="btn btn-primary" disabled={saving || loading}>
            {saving ? 'Saving...' : vendorProfile ? 'Update Profile' : 'Create Profile'}
          </button>
        </div>
      </form>
    </div>
  );
}