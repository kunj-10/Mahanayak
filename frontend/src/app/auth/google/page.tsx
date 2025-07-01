'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import axios from 'axios';

type Step = 'loading' | 'error' | 'askUserType' | 'done';

export default function GoogleCallbackPage() {
  const searchParams = useSearchParams();
  const router = useRouter();

  const [step, setStep] = useState<Step>('loading');
  const [message, setMessage] = useState('Authenticating with Google...');
  const [sessionToken, setSessionToken] = useState<string | null>(null);
  const [userInfo, setUserInfo] = useState<{ name: string; email: string } | null>(null);

  const redirect = searchParams.get('redirect') || '/';

  useEffect(() => {
    const code = searchParams.get('code');
    if (!code) {
      setStep('error');
      setMessage('No code found in callback URL');
      setTimeout(() => router.replace(redirect), 3000);
      return;
    }

    const authenticate = async () => {
      try {
        const res = await axios.post('/bapi/auth/google', { code }, { withCredentials: true });

        const data = res.data;

        if (data.registration_token) {
          setSessionToken(data.registration_token);
          console.log(data.registration_token)
          setUserInfo({ name: data.name, email: data.email });
          setStep('askUserType');
        } else {
          setStep('done');
          setMessage('Authentication successful! Redirecting...');
          setTimeout(() => router.replace(redirect), 1500);
        }
      } catch (err: any) {
        console.error(err);
        setStep('error');
        setMessage(err.response?.data?.detail || 'Authentication failed. Redirecting...');
        setTimeout(() => router.replace(redirect), 3000);
      }
    };

    authenticate();
  }, [searchParams, router]);

  const handleUserTypeSelection = async (userType: 'volunteer' | 'organizer') => {
    if (!sessionToken) return;
    setStep('loading');

    try {
      await axios.post(
        '/bapi/auth/complete_registration',
        {
          token: sessionToken,
          user_type: userType,
        },
        { withCredentials: true }
      );

      setStep('done');
      setMessage('Registration complete! Redirecting...');
      setTimeout(() => router.replace(redirect), 1500);
    } catch (e) {
      setStep('error');
      setMessage('Registration failed. Please try again.');
      setTimeout(() => router.replace(redirect), 3000);
    }
  };

  return (
    <div style={styles.container}>
      {step === 'loading' || step === 'done' ? (
        <>
          <div style={styles.spinner} />
          <p className="mt-4 text-center text-lg">{message}</p>
        </>
      ) : step === 'error' ? (
        <p style={styles.error}>{message}</p>
      ) : (
        <div className="bg-gray-900/50 rounded-xl shadow-lg p-6 max-w-sm w-full text-center">
          <h2 className="text-xl font-semibold mb-4">Hi {userInfo?.name} 👋</h2>
          <p className="mb-6 text-gray-700">How would you like to register?</p>
          <button
            className="w-full cursor-pointer py-2 mb-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium"
            onClick={() => handleUserTypeSelection('volunteer')}
          >
            Register as Volunteer
          </button>
          <button
            className="w-full cursor-pointer py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium"
            onClick={() => handleUserTypeSelection('organizer')}
          >
            Register as Organizer
          </button>
        </div>
      )}
    </div>
  );
}

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    display: 'flex',
    height: '100vh',
    alignItems: 'center',
    justifyContent: 'center',
    flexDirection: 'column',
    padding: '0 1rem',
  },
  spinner: {
    width: '48px',
    height: '48px',
    border: '6px solid #ccc',
    borderTop: '6px solid #0070f3',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
  },
  error: {
    color: '#e00',
    fontSize: '1.2rem',
    textAlign: 'center',
  },
};