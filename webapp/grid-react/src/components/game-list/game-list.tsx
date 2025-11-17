'use client';

import type { FC } from 'react';
import { useState, useEffect, useRef } from 'react';
import './game-list.scss';


interface GamelistProps {
  onOpenCreateGameModal?: () => void;
  onOpenUserNameModal?: () => void;
}

const Gamelist: FC<GamelistProps> = ({ onOpenCreateGameModal }) => {
  const [games, setGames] = useState<Array<string> | null>(null);
  const hasTriggeredModal = useRef(false);

  useEffect(() => {
    // TODO: Fetch games from API
    // For now, using empty array
    setGames([]);
  }, []);

  useEffect(() => {
    // Trigger modals when there are no games (only once)
    if (games && games.length === 0 && !hasTriggeredModal.current) {
      // const userName = getUserName();
      // hasTriggeredModal.current = true;
      
      // Small delay to ensure component is fully mounted
      // const timer = setTimeout(() => {
      //   if (!userName && onOpenUserNameModal) {
      //     onOpenUserNameModal();
      //   } else if (userName && onOpenCreateGameModal) {
      //     onOpenCreateGameModal();
      //   }
      // }, 100);

      // return () => clearTimeout(timer);
    }
  }, [games]);

  const gameListItems = games?.map((game, index) => <li key={index}>{game}</li>);
  const hasGames = Boolean(gameListItems && gameListItems.length > 0);
 
  return (
    <div className="gamelist-wrapper" data-testid="game-list">
      <ul>{hasGames && gameListItems}</ul>
      {!hasGames && (
        <div className="gamelist-empty-state">
          <div>No games yet</div>
          <div>
            <button onClick={() => onOpenCreateGameModal && onOpenCreateGameModal()}>
              Start Playing
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Gamelist;
