# 🔍 TEST - Czy masz NOWĄ wersję aplikacji?

## KROK 1: Sprawdź wersję Service Worker

1. Naciśnij F12
2. Kliknij zakładkę **"Console"** (góra)
3. W konsoli wpisz dokładnie:
```javascript
navigator.serviceWorker.getRegistration().then(reg => console.log('Service Worker version:', reg.active?.scriptURL))
```
4. Naciśnij Enter

**POWINNO POKAZAĆ:**
```
Service Worker version: https://pwa-troubleshoot-1.preview.emergentagent.com/service-worker.js
```

---

## KROK 2: Sprawdź nazwę cache

W konsoli wpisz:
```javascript
caches.keys().then(keys => console.log('Cache names:', keys))
```
Naciśnij Enter

**POWINNO POKAZAĆ:**
```
Cache names: Array [ "elektron-v18-debug-history-2025" ]
```

**JEŚLI POKAZUJE STARĄ WERSJĘ** (np. v17, v16, v15):
→ Cache nie został wyczyszczony!
→ Masz STARĄ wersję kodu!

---

## KROK 3: Wymuś CAŁKOWITE wyczyszczenie

### A) Wyrejestruj Service Worker:

W konsoli wpisz:
```javascript
navigator.serviceWorker.getRegistrations().then(regs => regs.forEach(reg => reg.unregister().then(() => console.log('Unregistered!'))))
```

### B) Wyczyść WSZYSTKIE cache:

W konsoli wpisz:
```javascript
caches.keys().then(keys => Promise.all(keys.map(key => caches.delete(key)))).then(() => console.log('All caches deleted!'))
```

### C) Wyczyść Local Storage:

W konsoli wpisz:
```javascript
localStorage.clear(); sessionStorage.clear(); console.log('Storage cleared!')
```

### D) Zamknij Firefox CAŁKOWICIE

### E) Otwórz Firefox i wejdź na aplikację

---

## KROK 4: Test czy masz NOWĄ wersję

Po wejściu na aplikację:

1. F12 → Console
2. Kliknij zakładkę "Asystent AI"
3. Kliknij przycisk "📜 Historia"

**JEŚLI MASZ NOWĄ WERSJĘ, zobaczysz:**
```
🔘 Przycisk Historia kliknięty!
🔍 loadSessions wywołana!
📡 Wysyłam request do: https://...
```

**JEŚLI NADAL NIE MA tych logów:**
→ Masz starą wersję
→ Zrób screenshota wyniku KROK 2 (caches.keys())
→ Prześlij mi

---

## ⚡ NAJSZYBSZA METODA (NUCLEAR OPTION):

### Firefox - Tryb prywatny:
1. Ctrl + Shift + P (tryb prywatny)
2. Wejdź na: https://pwa-troubleshoot-1.preview.emergentagent.com
3. F12 → Console
4. Kliknij "Asystent AI" → "📜 Historia"
5. Zobacz czy są logi z 🔘 🔍 📡

**Jeśli w trybie prywatnym DZIAŁA:**
→ Problem jest z cache w normalnym Firefox
→ Usuń profil Firefox całkowicie

**Jak usunąć profil Firefox:**
```
Windows: 
- Naciśnij Windows + R
- Wpisz: %APPDATA%\Mozilla\Firefox\Profiles
- Usuń folder z profilu
- Uruchom Firefox - utworzy nowy profil
```

---

## 📸 CO MI PRZEŚLIJ:

1. **Wynik KROK 2** (caches.keys()) - screenshot lub skopiuj tekst
2. **Screenshot konsoli** po kliknięciu "📜 Historia"
3. **Czy w trybie prywatnym działa?** (Tak/Nie)

**To pozwoli mi dokładnie zobaczyć co jest nie tak!**
