import {useEffect, useRef, useState} from 'react';
import {AppState} from 'react-native';

/** Poll only visible sessions, without overlapping requests or clearing form input. */
export function useRefresh(refresh: () => Promise<void>, enabled: boolean, paused = false) {
  const latest = useRef(refresh);
  const pause = useRef(paused);
  latest.current = refresh;
  pause.current = paused;
  const [error, setError] = useState('');
  useEffect(() => {
    if (!enabled) { setError(''); return; }
    let stopped = false;
    let loading = false;
    const update = async () => {
      if (stopped || loading || pause.current || (AppState.currentState && AppState.currentState !== 'active')) return;
      loading = true;
      try { await latest.current(); if (!stopped) setError(''); }
      catch { if (!stopped) setError('No pudimos actualizar. Comprueba tu conexión; reintentaremos automáticamente.'); }
      finally { loading = false; }
    };
    const timer = setInterval(() => void update(), 5000);
    const listener = AppState.addEventListener('change', state => {if (state === 'active') void update();});
    return () => {stopped = true; clearInterval(timer); listener.remove();};
  }, [enabled]);
  return error;
}
