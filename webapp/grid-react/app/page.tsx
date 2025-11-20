'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Gamelist from '../src/components/game-list/game-list';
import CreateGameModal from '../src/components/create-game-modal/create-game-modal';
import UserNameModal from '../src/components/user-name-modal/user-name-modal';
import { JoinGameByCode } from '../src/components/join-game-by-code/join-game-by-code';
import { createSession, createUser } from '../src/utils/api';
import { useUser } from '../src/context/UserContext';
import { useToast } from '../src/context/ToastContext';
import '../src/App.css';

export default function Home() {
  const router = useRouter();
  const { user, isLoading: isUserLoading, login } = useUser();
  const { showToast } = useToast();
  
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isUserNameModalOpen, setIsUserNameModalOpen] = useState(false);
  const [isCreatingUser, setIsCreatingUser] = useState(false);
  const [pendingGameCreation, setPendingGameCreation] = useState(false);
  const [joinError, setJoinError] = useState<string | null>(null);

  useEffect(() => {
    if (!isUserLoading && !user) {
      setIsUserNameModalOpen(true);
    }
  }, [isUserLoading, user]);

  const createGame = () => {
    if (user) {
      setIsModalOpen(true);
    } else {
      setPendingGameCreation(true);
      setIsUserNameModalOpen(true);
    }
  };

  const handleGameSubmit = async (icon: string, gameType: string) => {
    if (!user) {
      setPendingGameCreation(true);
      setIsUserNameModalOpen(true);
      return;
    }

    try {
      // Show loading state if needed, or just rely on async await
      const session = await createSession({
        hostId: user.id,
        hostName: user.name,
        gameIcon: icon,
        gameType: gameType,
      });
      setIsModalOpen(false);
      showToast('Game created successfully!', 'success');
      router.push(`/waiting?id=${session.id}`);
    } catch (error: any) {
      console.error('Error creating session:', error);
      showToast(error.message || 'Failed to create session', 'error');
    }
  };

  const handleUserNameSubmit = async (name: string, icon?: string) => {
    setIsCreatingUser(true);
    try {
      const userData = await createUser(name, icon);
      login(userData.id, userData.name, userData.icon);
      
      setIsUserNameModalOpen(false);
      showToast(`Welcome, ${userData.name}!`, 'success');
      
      if (pendingGameCreation) {
        setPendingGameCreation(false);
        setIsModalOpen(true);
      }
    } catch (error: any) {
      console.error('Error creating user:', error);
      showToast(error.message || 'Failed to create user', 'error');
    } finally {
      setIsCreatingUser(false);
    }
  };

  if (isUserLoading) {
    return <div className="loading-screen">Loading...</div>;
  }

  // Blocking modal if no user
  if (!user && isUserNameModalOpen) {
    return (
      <UserNameModal
        isOpen={isUserNameModalOpen}
        onSubmit={handleUserNameSubmit}
        isLoading={isCreatingUser}
        onClose={undefined}
        isBlocking={true}
      />
    );
  }

  return (
    <div className="home-container">
      <header className="home-header">
        <div>
          <p className="eyebrow">Welcome to</p>
          <h1 className="home-title">Grid Game</h1>
        </div>
        {user && <p className="home-subtitle">Welcome back, {user.name}!</p>}
      </header>

      <div className="home-grid">
        <section className="home-actions">
          <div className="card">
            <div className="card-header">
              <h3>Join Game by Code</h3>
              <p>Jump into an existing match instantly</p>
            </div>
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
            <div className="card-header">
              <h3>Create New Game</h3>
              <p>Start a fresh session and invite a friend</p>
            </div>
            <button onClick={createGame} className="button-primary">
              Create New Game
            </button>
          </div>
        </section>

        <section className="card home-games-card">
          <div className="card-header">
            <h2>Your Games</h2>
            <p>Games you watched, started or played</p>
          </div>
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
      
      {/* Non-blocking modal if user wants to change name later (though UI for opening it isn't explicit here yet) */}
      {user && (
        <UserNameModal
          isOpen={isUserNameModalOpen}
          onSubmit={handleUserNameSubmit}
          isLoading={isCreatingUser}
          onClose={() => {
            setIsUserNameModalOpen(false);
            setPendingGameCreation(false);
          }}
        />
      )}
    </div>
  );
}
