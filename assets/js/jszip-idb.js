// IndexedDB-based JSZip loader for file:// or environments without Cache API
(function(){
  if (typeof window === 'undefined') return;
  if (typeof JSZip !== 'undefined') {
    window.JSZipLoadedPromise = Promise.resolve();
    return;
  }

  const DB_NAME = 'kean-jszip-db';
  const STORE = 'bundles';
  const KEY = 'jszip-3.10.1';
  const CDN = 'https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js';

  function openDB(){
    return new Promise((resolve, reject) => {
      try{
        const req = indexedDB.open(DB_NAME, 1);
        req.onupgradeneeded = function(e){
          const db = e.target.result;
          if (!db.objectStoreNames.contains(STORE)) db.createObjectStore(STORE);
        };
        req.onsuccess = function(e){ resolve(e.target.result); };
        req.onerror = function(e){ reject(e.target.error); };
      }catch(err){ reject(err); }
    });
  }

  function idbGet(db){
    return new Promise((resolve, reject) => {
      try{
        const tx = db.transaction([STORE], 'readonly');
        const st = tx.objectStore(STORE);
        const r = st.get(KEY);
        r.onsuccess = () => resolve(r.result || null);
        r.onerror = () => reject(r.error);
      }catch(err){ reject(err); }
    });
  }

  function idbSet(db, value){
    return new Promise((resolve, reject) => {
      try{
        const tx = db.transaction([STORE], 'readwrite');
        const st = tx.objectStore(STORE);
        const r = st.put(value, KEY);
        r.onsuccess = () => resolve(true);
        r.onerror = () => reject(r.error);
      }catch(err){ reject(err); }
    });
  }

  async function fetchAndStore(db){
    try{
      const resp = await fetch(CDN, {cache: 'no-store'});
      if (!resp.ok) throw new Error('Network error fetching JSZip');
      const text = await resp.text();
      try{ await idbSet(db, text); }catch(e){ /* ignore idb write errors */ }
      return text;
    }catch(err){ throw err; }
  }

  window.JSZipLoadedPromise = (async function(){
    // Try IDB first
    try{
      const db = await openDB();
      const cached = await idbGet(db);
      if (cached) {
        try{ (0,eval)(cached); }catch(e){ console.warn('Eval cached JSZip failed', e); }
        // refresh in background
        fetchAndStore(db).catch(()=>{});
        return;
      }
      // no cached copy -> fetch and store
      const text = await fetchAndStore(db);
      try{ (0,eval)(text); }catch(e){ console.warn('Eval fetched JSZip failed', e); }
      return;
    }catch(err){
      // Fallback: attempt network fetch directly
      try{
        const resp = await fetch(CDN, {cache: 'no-store'});
        if (!resp.ok) throw new Error('Network fetch failed');
        const text = await resp.text();
        try{ (0,eval)(text); }catch(e){ console.warn('Eval fetched JSZip failed', e); }
        return;
      }catch(err2){
        console.warn('Unable to load JSZip via IDB or network', err2);
        throw err2;
      }
    }
  })();

})();
