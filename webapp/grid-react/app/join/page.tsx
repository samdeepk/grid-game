'use client';

import { useRouter, useSearchParams } from 'next/navigation';
import { useCallback, useEffect, useState, Suspense } from 'react';
import UserNameModal from '../../src/components/user-name-modal/user-name-modal';
import {
  joinSession as apiJoinSession,
  getSession as apiGetSession,
  createUser as apiCreateUser,
} from '../../src/utils/api';
import { useUser } from '../../src/context/UserContext';
import { useToast } from '../../src/context/ToastContext';

function JoinContent() {
  const searchParams = useSearchParams();
  const gameId = searchParams.get('id');
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
    if (!gameId) {
      router.push('/');
      return;
    }

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
    if (!gameId) return;
    setIsJoining(true);
    try {
      await apiJoinSession(gameId, id);
      setHasJoined(true);
      showToast('Joined game successfully!', 'success');
      router.push(`/waiting?id=${gameId}`);
    } catch (error: any) {
      console.error('Failed to join session', error);
      showToast(error.message || 'Unable to join session. Please try again.', 'error');
    } finally {
      setIsJoining(false);
    }
  }, [gameId, router, showToast]);

  // Auto-join if user exists and session is ready
  useEffect(() => {
    if (isUserLoading || !sessionReady || isJoining || hasJoined || !gameId) return;

    if (user) {
      attemptJoin(user.id);
    } else {
      setShowNameModal(true);
    }
  }, [isUserLoading, sessionReady, user, isJoining, hasJoined, attemptJoin, gameId]);

  const onSubmitName = async (name: string, icon?: string) => {
    setIsJoining(true);
    try {
      const newUser = await apiCreateUser(name, icon);
      login(newUser.id, newUser.name, newUser.icon);
      setShowNameModal(false);
      await attemptJoin(newUser.id);
    } catch (error: any) {
      console.error('Failed to create user', error);
      showToast(error.message || 'Unable to create user. Please try again.', 'error');
      setIsJoining(false);
    }
  };

  if (!gameId) return null;

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

export default function JoinPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <JoinContent />
    </Suspense>
  );
}

