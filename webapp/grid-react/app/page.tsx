'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Gamelist from '../src/components/game-list/game-list';
import CreateGameModal from '../src/components/create-game-modal/create-game-modal';
import UserNameModal from '../src/components/user-name-modal/user-name-modal';
import { JoinGameByCode } from '../src/components/join-game-by-code/join-game-by-code';
import { getUserName, setUserName, getUserId, setUserId, setUserIcon } from '../src/utils/userStorage';
import { createSession, createUser, type Session } from '../src/utils/api';
import '../src/App.css';

export default function Home() {
  const router = useRouter();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isUserNameModalOpen, setIsUserNameModalOpen] = useState(false);
  const [userName, setUserNameState] = useState<string | null>(null);
  const [isCreatingUser, setIsCreatingUser] = useState(false);
  const [userId, setUserIdState] = useState<string | null>(null);
  const [mounted, setMounted] = useState(false);
  const [pendingGameCreation, setPendingGameCreation] = useState(false);
  const [createdSession, setCreatedSession] = useState<Session | null>(null);
  const [joinError, setJoinError] = useState<string | null>(null);

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
    } else {
      // If no user ID exists, automatically show user name modal (blocking)
      setIsUserNameModalOpen(true);
    }
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

  const handleGameSubmit = async (icon: string, gameType: string) => {
    if (!userId) {
      setPendingGameCreation(true);
      setIsUserNameModalOpen(true);
      return;
    }

    try {
      setIsCreatingUser(true);
      const session = await createSession({
        hostId: userId,
        hostName: userName || undefined,
        gameIcon: icon,
        gameType: gameType,
      });
      console.log('Created session', session);
      setIsModalOpen(false);
      setCreatedSession(session);
      // Navigate to waiting room after creating session
      router.push(`/waiting/${session.id}`);
    } catch (error) {
      console.error('Error creating session:', error);
      alert('Failed to create session. Please try again.');
    } finally {
      setIsCreatingUser(false);
    }
  };

  const handleUserNameSubmit = async (name: string, icon?: string) => {
    setIsCreatingUser(true);
    try {
      const userData = await createUser(name, icon);
      setUserName(userData.name);
      setUserId(userData.id);
      setUserNameState(userData.name);
      setUserIdState(userData.id);
      if (userData.icon) {
        setUserIcon(userData.icon);
      }
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

  // Don't render main content if user modal is open and user hasn't been set up yet
  if (mounted && !userId && isUserNameModalOpen) {
    return (
      <>
        <UserNameModal
          isOpen={isUserNameModalOpen}
          onSubmit={handleUserNameSubmit}
          isLoading={isCreatingUser}
          onClose={undefined} // Blocking - no close button
          isBlocking={true}
        />
      </>
    );
  }

  return (
    <>
      <h1>Grid Game</h1>
      {mounted && userName && <p>Welcome back, {userName}!</p>}
      
      <div className="home-actions">
        <div className="card">
          <h3>Join Game by Code</h3>
          {joinError && (
            <div className="error-message">
              {joinError}
            </div>
          )}
          <JoinGameByCode
            onError={(message) => {
              setJoinError(message);
              setTimeout(() => setJoinError(null), 5000);
            }}
          />
        </div>

        <div className="card">
          <h3>Create New Game</h3>
          <button onClick={createGame} className="button-primary" style={{ width: '100%', marginTop: '8px' }}>
            Create New Game
          </button>
        </div>
      </div>

      <div className="card">
        <h2>Your Games</h2>
        <p style={{ color: '#6b7280', marginBottom: '16px', fontSize: '0.875rem' }}>
          Games you watched, started or played
        </p>
        <Gamelist
          onOpenCreateGameModal={createGame}
          onOpenUserNameModal={() => setIsUserNameModalOpen(true)}
        />
      </div>

      <CreateGameModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleGameSubmit}
      />
      <UserNameModal
        isOpen={isUserNameModalOpen && !!userId}
        onSubmit={handleUserNameSubmit}
        isLoading={isCreatingUser}
        onClose={() => {
          setIsUserNameModalOpen(false);
          setPendingGameCreation(false);
        }}
      />
    </>
  );
}

