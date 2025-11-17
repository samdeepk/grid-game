'use client';

import { useState, useEffect } from 'react';
import type { FC } from 'react';
import './user-name-modal.scss';

interface UserNameModalProps {
  isOpen: boolean;
  onSubmit: (name: string) => void;
  onClose?: () => void;
}

const UserNameModal: FC<UserNameModalProps> = ({ isOpen, onSubmit, onClose }) => {
  const [userName, setUserName] = useState('');

  useEffect(() => {
    if (isOpen) {
      setUserName('');
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    

    if (userName.trim()) {
      onSubmit(userName.trim());
    }
  };

  const handleClose = () => {
    if (onClose) {
      onClose();
    }
  };

  return (
    <div className="modal-overlay" onClick={handleClose}>
      <div className="modal-container" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">Welcome to Grid Game!</h2>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            <p className="welcome-text">Let's get started. What should we call you?</p>
            <div className="form-group">
              <label className="label" htmlFor="user-name">
                Your Name
              </label>
              <input
                id="user-name"
                className="input"
                type="text"
                value={userName}
                onChange={(e) => setUserName(e.target.value)}
                placeholder="Enter your name"
                required
                autoFocus
                maxLength={50}
              />
            </div>
          </div>
          <div className="modal-footer">
            <button className="button-primary" type="submit" disabled={!userName.trim()}>
              Continue
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default UserNameModal;

