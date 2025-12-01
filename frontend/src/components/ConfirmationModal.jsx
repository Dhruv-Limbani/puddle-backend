import React from 'react';
import './ConfirmationModal.css';

export default function ConfirmationModal({ isOpen, onClose, onConfirm, title, message, confirmText = "OK", cancelText = "Cancel" }) {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <h3 className="modal-title">{title}</h3>
        <p className="modal-message">{message}</p>
        <div className="modal-actions">
          <button className="btn-modal-cancel" onClick={onClose}>
            {cancelText}
          </button>
          <button className="btn-modal-confirm" onClick={onConfirm}>
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  );
}
