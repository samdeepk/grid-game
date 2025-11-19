'use client';

import { useRouter } from 'next/navigation';
import { useCallback, useEffect, useState } from 'react';
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
  const [sessionReady, setSessionReady] = useState(false);
  const [storedUser, setStoredUser] = useState<{ id: string; name: string } | null>(null);
  const [hasJoined, setHasJoined] = useState(false);
  const [sessionError, setSessionError] = useState<string | null>(null);

  useEffect(() => {
    const storedName = getUserName();
    const storedId = getUserId();

    if (storedName && storedId) {
      setStoredUser({ id: storedId, name: storedName });
      setShowNameModal(false);
    } else {
      setStoredUser(null);
      setShowNameModal(true);
    }
  }, []);

  useEffect(() => {
    setHasJoined(false);
  }, [gameId]);

  useEffect(() => {
    let cancelled = false;

    const checkSession = async () => {
      setSessionReady(false);
      setSessionError(null);
      try {
        await apiGetSession(gameId);
        if (!cancelled) {
          setSessionReady(true);
        }
      } catch (err) {
        if (!cancelled) {
          console.error('Session lookup failed', err);
          setSessionError('Session not found or expired.');
        }
      }
    };

    checkSession();

    return () => {
      cancelled = true;
    };
  }, [gameId, router]);

  const attemptJoin = useCallback(async (id: string) => {
    setIsJoining(true);
    try {
      await apiJoinSession(gameId, id);
      setHasJoined(true);
      router.push(`/waiting/${gameId}`);
    } catch (error) {
      console.error('Failed to join session', error);
      alert('Unable to join session. Please try again.');
      setShowNameModal(true);
      setStoredUser(null);
    } finally {
      setIsJoining(false);
    }
  }, [gameId, router]);

  useEffect(() => {
    if (!sessionReady || !storedUser || showNameModal || isJoining || hasJoined) {
      return;
    }
    attemptJoin(storedUser.id);
  }, [sessionReady, storedUser, showNameModal, isJoining, hasJoined, attemptJoin]);

  const onSubmitName = async (name: string, icon?: string) => {
    setIsJoining(true);
    try {
      const newUser = await apiCreateUser(name, icon);
      setUser(newUser.id, newUser.name, newUser.icon ?? undefined);
      setStoredUser({ id: newUser.id, name: newUser.name });
      setShowNameModal(false);
      await attemptJoin(newUser.id);
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

  if (sessionError) {
    return (
      <div>
        <p>{sessionError}</p>
        <button type="button" onClick={() => router.push('/')}>
          Go home
        </button>
      </div>
    );
  }

  return <div>{isJoining ? 'Joining game...' : 'Loading session...'}</div>;
}
