'use client';

import { useState, useEffect } from 'react';
import Gamelist from '../src/components/game-list/game-list';
import CreateGameModal from '../src/components/create-game-modal/create-game-modal';
import UserNameModal from '../src/components/user-name-modal/user-name-modal';
import { getUserName, setUserName } from '../src/utils/userStorage';
import '../src/App.css';

export default function Home() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isUserNameModalOpen, setIsUserNameModalOpen] = useState(false);
  const [userName, setUserNameState] = useState<string | null>(null);

  useEffect(() => {
    // Check if user name exists on mount
    const storedUserName = getUserName();
    if (storedUserName) {
      setUserNameState(storedUserName);
    }
    // Don't auto-open user name modal - let game-list handle it when there are no games
  }, []);

  const createGame = () => {
    setIsModalOpen(true);
  };

  const handleGameSubmit = (icon: string) => {
    console.log('Creating game:', { icon });
    // TODO: Add API call to create game
  };

  const handleUserNameSubmit = (name: string) => {
    setUserName(name);
    setUserNameState(name);
    setIsUserNameModalOpen(false);
  };

  return (
    <>
      <h1>Grid Game</h1>
      {userName && <p>Welcome back, {userName}!</p>}
      <div className="card">
        <button onClick={createGame}>Create New Game</button>
      </div>
      <div>
        <h2>Games</h2>
        <section>
          <h3>Games you watched, started or played</h3>
          <Gamelist
            onOpenCreateGameModal={() => setIsModalOpen(true)}
            onOpenUserNameModal={() => setIsUserNameModalOpen(true)}
          />
        </section>
      </div>
      <CreateGameModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleGameSubmit}
      />
      <UserNameModal isOpen={isUserNameModalOpen} onSubmit={handleUserNameSubmit} />
    </>
  );
}

