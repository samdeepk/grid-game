'use client';

import { useState, useEffect } from 'react';
import Gamelist from '../src/components/game-list/game-list';
import CreateGameModal from '../src/components/create-game-modal/create-game-modal';
import UserNameModal from '../src/components/user-name-modal/user-name-modal';
import { getUserName, setUserName, getUserId, setUserId } from '../src/utils/userStorage';
import '../src/App.css';

const API_BASE_URL =
  (process.env.NEXT_PUBLIC_API_BASE_URL &&
    process.env.NEXT_PUBLIC_API_BASE_URL.replace(/\/$/, '')) ||
  '/api';

export default function Home() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isUserNameModalOpen, setIsUserNameModalOpen] = useState(false);
  const [userName, setUserNameState] = useState<string | null>(null);
  const [isCreatingUser, setIsCreatingUser] = useState(false);
  const [userId, setUserIdState] = useState<string | null>(null);
  const [mounted, setMounted] = useState(false);
  const [pendingGameCreation, setPendingGameCreation] = useState(false);

  useEffect(() => {
    // Mark component as mounted (client-side only)
    setMounted(true);
    
    // Check if user name exists on mount (only runs on client)
    const storedUserName = getUserName();
    const storedUserId = getUserId();
    if (storedUserName) {
      setUserNameState(storedUserName);
    }
    if (storedUserId) {
      setUserIdState(storedUserId);
    }
    // Don't auto-open user name modal - let game-list handle it when there are no games
  }, []);

  const createGame = () => {
    // Check if user has a name before allowing game creation
    if (mounted && userName) {
      // User has a name, proceed with game creation
      setIsModalOpen(true);
    } else {
      // User doesn't have a name, prompt for it first
      setPendingGameCreation(true);
      setIsUserNameModalOpen(true);
    }
  };

  const handleGameSubmit = (icon: string) => {
    console.log('Creating game:', { icon });
    // TODO: Add API call to create game
  };

  const handleUserNameSubmit = async (name: string) => {
    setIsCreatingUser(true);
    try {
      // Call the create-user API
      const response = await fetch(
        `${API_BASE_URL}/create-user?name=${encodeURIComponent(name)}`
      );
      
      if (!response.ok) {
        throw new Error(`Failed to create user: ${response.statusText}`);
      }
      
      const userData = await response.json();
      
      // Store user data locally
      setUserName(userData.name);
      setUserId(userData.id);
      setUserNameState(userData.name);
      setUserIdState(userData.id);
      setIsUserNameModalOpen(false);
      
      // If user was trying to create a game, open the create game modal now
      if (pendingGameCreation) {
        setPendingGameCreation(false);
        setIsModalOpen(true);
      }
    } catch (error) {
      console.error('Error creating user:', error);
      alert('Failed to create user. Please try again.');
    } finally {
      setIsCreatingUser(false);
    }
  };

  return (
    <>
      <h1>Grid Game</h1>
      {mounted && userName && <p>Welcome back, {userName}!</p>}
      <div className="card">
        <button onClick={createGame}>Create New Game</button>
      </div>
      <div>
        <h2>Games</h2>
        <section>
          <h3>Games you watched, started or played</h3>
          <Gamelist
            onOpenCreateGameModal={createGame}
            onOpenUserNameModal={() => setIsUserNameModalOpen(true)}
          />
        </section>
      </div>
      <CreateGameModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleGameSubmit}
      />
      <UserNameModal 
        isOpen={isUserNameModalOpen} 
        onSubmit={handleUserNameSubmit}
        onClose={() => {
          setIsUserNameModalOpen(false);
          // Reset pending game creation if user closes modal without submitting
          setPendingGameCreation(false);
        }}
      />
    </>
  );
}

