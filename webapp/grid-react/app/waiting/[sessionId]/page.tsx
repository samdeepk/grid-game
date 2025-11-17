'use client';

import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { WaitingRoom } from '../../../src/components/waiting-room/waiting-room';

export default function WaitingHostPage({ params }: { params: { sessionId: string } }) {
  const { sessionId } = params;
  const router = useRouter();

  useEffect(() => {
    // nothing special for now
  }, [sessionId]);

  return (
    <div>
      <h1>Waiting</h1>
      <WaitingRoom sessionId={sessionId} />
    </div>
  );
}
