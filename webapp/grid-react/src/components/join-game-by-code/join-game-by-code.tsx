'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import type { FC } from 'react';
import { getSession } from '../../utils/api';
import './join-game-by-code.scss';

interface JoinGameByCodeProps {
  onError?: (message: string) => void;
}

export const JoinGameByCode: FC<JoinGameByCodeProps> = ({ onError }) => {
  const [code, setCode] = useState('');
  const [isValidating, setIsValidating] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const trimmedCode = code.trim();
    
    if (!trimmedCode) {
      if (onError) {
        onError('Please enter a game code');
      } else {
        alert('Please enter a game code');
      }
      return;
    }

    setIsValidating(true);
    try {
      // Validate that the session exists
      await getSession(trimmedCode);
      // Navigate to join page
      router.push(`/join?id=${trimmedCode}`);
    } catch (error) {
      setIsValidating(false);
      const errorMessage = error instanceof Error ? error.message : 'Invalid game code. Please check and try again.';
      if (onError) {
        onError(errorMessage);
      } else {
        alert(errorMessage);
      }
    }
  };

  return (
    <div className="join-game-by-code">
      <form onSubmit={handleSubmit} className="join-game-form">
        <div className="form-group">
          <label htmlFor="game-code" className="label">
            Enter Game Code
          </label>
          <div className="input-group">
            <input
              id="game-code"
              type="text"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder="Enter session ID"
              className="input"
              disabled={isValidating}
              autoComplete="off"
            />
            <button
              type="submit"
              className="button-primary"
              disabled={!code.trim() || isValidating}
            >
              {isValidating ? 'Joining...' : 'Join Game'}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
};

