'use client';

import { useRouter, useSearchParams } from 'next/navigation';
import { useEffect, Suspense } from 'react';
import { WaitingRoom } from '../../src/components/waiting-room/waiting-room';

function WaitingContent() {
  const searchParams = useSearchParams();
  const sessionId = searchParams.get('id');
  const router = useRouter();

  useEffect(() => {
    if (!sessionId) {
      router.push('/');
    }
  }, [sessionId, router]);

  if (!sessionId) return null;

  return (
    <div>
      <h1>Waiting</h1>
      <WaitingRoom sessionId={sessionId} />
    </div>
  );
}

export default function WaitingHostPage() {
  return (
    <Suspense fallback={<div>Loading waiting room...</div>}>
      <WaitingContent />
    </Suspense>
  );
}

