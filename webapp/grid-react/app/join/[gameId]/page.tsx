'use client';

import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import UserNameModal from '../../../src/components/user-name-modal/user-name-modal';
import { getUserName, setUser, getUserId } from '../../../src/utils/userStorage';
import { joinSession as apiJoinSession, getSession as apiGetSession } from '../../../src/utils/api';
// Use browser crypto uuid when available
function genId() {
  return typeof crypto !== 'undefined' && (crypto as any).randomUUID
    ? (crypto as any).randomUUID()
    : Math.random().toString(36).slice(2, 9);
}

export default function JoinPage({ params }: { params: { gameId: string } }) {
  const { gameId } = params;
  const router = useRouter();
  const [isNameModal, setIsNameModal] = useState(false);

  useEffect(() => {
    const run = async () => {
        const s = await apiGetSession(gameId);
        if (!s) {
        alert('Session not found.');
        router.push('/');
        return;
        }
        const userName = getUserName();
        if (!userName) {
            setIsNameModal(true);
        } else {
            // try to join using existing user
            const id = getUserId() ?? genId();
            setUser(id, userName);
            const me = { id, name: userName, icon: null };
            await apiJoinSession(gameId, id);
            router.push(`/game/${gameId}`);
        }
    }
    run();
  }, [gameId]);

  const onSubmitName = async (name: string, icon?: string) => {
    const id = getUserId() ?? genId();
    setUser(id, name, icon);
    await apiJoinSession(gameId, id);
    router.push(`/game/${gameId}`);
  };

  return isNameModal ? (
    <UserNameModal isOpen onSubmit={onSubmitName} onClose={() => router.push('/')} />
  ) : (
    <div>Joining game...</div>
  );
}
