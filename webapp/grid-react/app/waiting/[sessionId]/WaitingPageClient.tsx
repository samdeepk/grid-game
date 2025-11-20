'use client';

import { WaitingRoom } from '../../../src/components/waiting-room/waiting-room';

type Props = {
  sessionId: string;
};

export default function WaitingPageClient({ sessionId }: Props) {
  return (
    <div>
      <h1>Waiting</h1>
      <WaitingRoom sessionId={sessionId} />
    </div>
  );
}

