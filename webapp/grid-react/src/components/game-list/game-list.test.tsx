import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import Gamelist from './game-list';

describe('<Gamelist />', () => {
  test('it should mount', () => {
    render(<Gamelist />);

    const gameList = screen.getByTestId('game-list');

    expect(gameList).toBeInTheDocument();
  });
});