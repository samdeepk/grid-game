'use client';

import { useState } from 'react';
import type { FC } from 'react';
import './create-game-modal.scss';

interface CreateGameModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (icon: string) => void;
}

const iconOptions = [
  '🎮',
  '🎯',
  '🎲',
  '🎪',
  '🎨',
  '🎭',
  '🎸',
  '🎺',
  '🎻',
  '🎤',
  '🎧',
  '🎬',
  '🎥',
  '🎞️',
  '🎟️',
  '🎫',
  '🏆',
  '🏅',
  '🥇',
  '🥈',
  '🥉',
  '⚽',
  '🏀',
  '🏈',
  '⚾',
  '🎾',
  '🏐',
  '🏉',
  '🎱',
  '🏓',
];

const CreateGameModal: FC<CreateGameModalProps> = ({ isOpen, onClose, onSubmit }) => {
  const [selectedIcon, setSelectedIcon] = useState(iconOptions[0]);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedIcon) {
      onSubmit(selectedIcon);
      setSelectedIcon(iconOptions[0]);
      onClose();
    }
  };

  const handleClose = () => {
    setSelectedIcon(iconOptions[0]);
    onClose();
  };

  return (
    <div className="modal-overlay" onClick={handleClose}>
      <div className="modal-container" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">Create New Game</h2>
          <button className="close-button" onClick={handleClose} type="button">
            ×
          </button>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            <div className="form-group">
              <label className="label">Select Icon</label>
              <div className="icon-grid">
                {iconOptions.map((icon) => (
                  <button
                    key={icon}
                    className={`icon-option ${selectedIcon === icon ? 'selected' : ''}`}
                    onClick={() => setSelectedIcon(icon)}
                    type="button"
                    aria-label={`Select icon ${icon}`}
                    aria-pressed={selectedIcon === icon}
                  >
                    {icon}
                  </button>
                ))}
              </div>
            </div>
          </div>
          <div className="modal-footer">
            <button className="button" type="button" onClick={handleClose}>
              Cancel
            </button>
            <button className="button-primary" type="submit" disabled={!selectedIcon}>
              Create Game
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateGameModal;

