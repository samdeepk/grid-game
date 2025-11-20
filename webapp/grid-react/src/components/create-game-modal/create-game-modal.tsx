'use client';

import { useState } from 'react';
import type { FC } from 'react';
import './create-game-modal.scss';

interface CreateGameModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (icon: string, gameType: string) => void;
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
  const [selectedGameType, setSelectedGameType] = useState<'tic_tac_toe' | 'connect_four'>('tic_tac_toe');

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedIcon) {
      onSubmit(selectedIcon, selectedGameType);
      setSelectedIcon(iconOptions[0]);
      setSelectedGameType('tic_tac_toe');
      onClose();
    }
  };

  const handleClose = () => {
    setSelectedIcon(iconOptions[0]);
    setSelectedGameType('tic_tac_toe');
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
              <label className="label">Select Game Type</label>
              <div className="game-type-selector">
                <button
                  type="button"
                  className={`game-type-option ${selectedGameType === 'tic_tac_toe' ? 'selected' : ''}`}
                  onClick={() => setSelectedGameType('tic_tac_toe')}
                >
                  <span className="game-type-icon">⭕</span>
                  <span className="game-type-label">Tic-Tac-Toe</span>
                </button>
                <button
                  type="button"
                  className={`game-type-option ${selectedGameType === 'connect_four' ? 'selected' : ''}`}
                  onClick={() => setSelectedGameType('connect_four')}
                >
                  <span className="game-type-icon">🔴</span>
                  <span className="game-type-label">Connect 4</span>
                </button>
              </div>
            </div>
            <div className="form-group">
              <label className="label">Select Icon</label>
              <div className="icon-grid">
                {iconOptions.map((icon) => (
                  <button
                    key={icon}
                    className={`icon-option ${selectedIcon === icon ? 'selected' : ''}`}
                    onClick={() => setSelectedIcon(icon)}
                    type="button"
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

