import { lazy, Suspense } from 'react';
import type { ComponentProps } from 'react';
import Gamelist from './game-list';

const LazyGamelist = lazy(() => import('./game-list'));

const GamelistLazy = (props: ComponentProps<typeof Gamelist>) => (
  <Suspense fallback={null}>
    <LazyGamelist {...props} />
  </Suspense>
);

export default GamelistLazy;
