'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Gamelist from '../src/components/game-list/game-list';
import CreateGameModal from '../src/components/create-game-modal/create-game-modal';
import UserNameModal from '../src/components/user-name-modal/user-name-modal';
import { getUserName, setUserName, getUserId, setUserId } from '../src/utils/userStorage';
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

  const handleGameSubmit = async (icon: string) => {
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
      });
      console.log('Created session', session);
      setIsModalOpen(false);
      setCreatedSession(session);
    } catch (error) {
      console.error('Error creating session:', error);
      alert('Failed to create session. Please try again.');
    } finally {
      setIsCreatingUser(false);
    }
  };

  const handleUserNameSubmit = async (name: string) => {
    setIsCreatingUser(true);
    try {
      const userData = await createUser(name);
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
      {createdSession && (
        <div className="card share-card">
          <h3>Invite a friend</h3>
          <p>Share this link so they can join your session:</p>
          <div className="share-link">
            <code>
              {typeof window !== 'undefined'
                ? `${window.location.origin}/join/${createdSession.id}`
                : `/join/${createdSession.id}`}
            </code>
            <button
              type="button"
              onClick={() => {
                const shareUrl =
                  typeof window !== 'undefined'
                    ? `${window.location.origin}/join/${createdSession.id}`
                    : `${createdSession.id}`;
                navigator.clipboard
                  .writeText(shareUrl)
                  .then(() => alert('Link copied to clipboard'))
                  .catch(() => alert('Unable to copy link, please copy manually.'));
              }}
            >
              Copy link
            </button>
          </div>
          <button
            className="button-primary"
            type="button"
            onClick={() => router.push(`/waiting/${createdSession.id}`)}
          >
            Continue to waiting room
          </button>
        </div>
      )}
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

