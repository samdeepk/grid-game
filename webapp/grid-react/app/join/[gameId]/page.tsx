'use client';

import { useRouter } from 'next/navigation';
import { useCallback, useEffect, useState } from 'react';
import UserNameModal from '../../../src/components/user-name-modal/user-name-modal';
import {
  joinSession as apiJoinSession,
  getSession as apiGetSession,
  createUser as apiCreateUser,
} from '../../../src/utils/api';
import { useUser } from '../../../src/context/UserContext';
import { useToast } from '../../../src/context/ToastContext';

export default function JoinPage({ params }: { params: { gameId: string } }) {
  const { gameId } = params;
  const router = useRouter();
  const { user, isLoading: isUserLoading, login } = useUser();
  const { showToast } = useToast();

  const [isJoining, setIsJoining] = useState(false);
  const [sessionReady, setSessionReady] = useState(false);
  const [hasJoined, setHasJoined] = useState(false);
  const [sessionError, setSessionError] = useState<string | null>(null);
  const [showNameModal, setShowNameModal] = useState(false);

  // Check if session exists
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
  }, [gameId]);

  const attemptJoin = useCallback(async (id: string) => {
    setIsJoining(true);
    try {
      await apiJoinSession(gameId, id);
      setHasJoined(true);
      showToast('Joined game successfully!', 'success');
      router.push(`/waiting/${gameId}`);
    } catch (error: any) {
      console.error('Failed to join session', error);
      showToast(error.message || 'Unable to join session. Please try again.', 'error');
      // If join fails, maybe user is invalid or full, but we stay here.
    } finally {
      setIsJoining(false);
    }
  }, [gameId, router, showToast]);

  // Auto-join if user exists and session is ready
  useEffect(() => {
    if (isUserLoading || !sessionReady || isJoining || hasJoined) return;

    if (user) {
      attemptJoin(user.id);
    } else {
      setShowNameModal(true);
    }
  }, [isUserLoading, sessionReady, user, isJoining, hasJoined, attemptJoin]);

  const onSubmitName = async (name: string, icon?: string) => {
    setIsJoining(true);
    try {
      const newUser = await apiCreateUser(name, icon);
      login(newUser.id, newUser.name, newUser.icon);
      setShowNameModal(false);
      // attemptJoin will be triggered by useEffect when user updates, 
      // BUT user update in context might take a tick. 
      // Safest is to call join directly here or wait for effect.
      // Let's call directly to be sure and show feedback immediately.
      await attemptJoin(newUser.id);
    } catch (error: any) {
      console.error('Failed to create user', error);
      showToast(error.message || 'Unable to create user. Please try again.', 'error');
      setIsJoining(false);
    }
  };

  if (sessionError) {
    return (
      <div style={{ textAlign: 'center', marginTop: '2rem' }}>
        <p style={{ color: 'red', marginBottom: '1rem' }}>{sessionError}</p>
        <button type="button" className="button-primary" onClick={() => router.push('/')}>
          Go home
        </button>
      </div>
    );
  }

  if (showNameModal && !user) {
    return (
      <UserNameModal
        isOpen
        onSubmit={onSubmitName}
        isLoading={isJoining}
        onClose={() => router.push('/')}
      />
    );
  }

  return (
    <div style={{ textAlign: 'center', marginTop: '2rem' }}>
      {isJoining ? 'Joining game...' : 'Loading session...'}
    </div>
  );
}
