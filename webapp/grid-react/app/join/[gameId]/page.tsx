'use client';

import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import UserNameModal from '../../../src/components/user-name-modal/user-name-modal';
import { getUserName, getUserId, setUser } from '../../../src/utils/userStorage';
import {
  joinSession as apiJoinSession,
  getSession as apiGetSession,
  createUser as apiCreateUser,
} from '../../../src/utils/api';

export default function JoinPage({ params }: { params: { gameId: string } }) {
  const { gameId } = params;
  const router = useRouter();
  const [showNameModal, setShowNameModal] = useState(false);
  const [isJoining, setIsJoining] = useState(false);

  useEffect(() => {
    const run = async () => {
      try {
        await apiGetSession(gameId);
      } catch (err) {
        alert('Session not found.');
        router.push('/');
        return;
      }

      const storedName = getUserName();
      const storedId = getUserId();

      if (!storedName || !storedId) {
        setShowNameModal(true);
        return;
      }

      await attemptJoin(storedId, storedName);
    };
    run();
  }, [gameId]);

  const attemptJoin = async (id: string, name: string) => {
    setIsJoining(true);
    try {
      await apiJoinSession(gameId, id);
      router.push(`/waiting/${gameId}`);
    } catch (error) {
      console.error('Failed to join session', error);
      alert('Unable to join session. Please try again.');
      setShowNameModal(true);
    } finally {
      setIsJoining(false);
    }
  };

  const onSubmitName = async (name: string, icon?: string) => {
    setIsJoining(true);
    try {
      const newUser = await apiCreateUser(name, icon);
      setUser(newUser.id, newUser.name, newUser.icon ?? undefined);
      await apiJoinSession(gameId, newUser.id);
      router.push(`/waiting/${gameId}`);
    } catch (error) {
      console.error('Failed to create user / join session', error);
      alert('Unable to join session. Please try again.');
    } finally {
      setIsJoining(false);
    }
  };

  if (showNameModal) {
    return (
      <UserNameModal
        isOpen
        onSubmit={onSubmitName}
        isLoading={isJoining}
        onClose={() => router.push('/')}
      />
    );
  }

  return <div>{isJoining ? 'Joining game...' : 'Loading session...'}</div>;
}
