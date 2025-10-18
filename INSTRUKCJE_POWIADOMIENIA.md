# 🔔 Instrukcje - Jak Włączyć Powiadomienia Push

## ✅ CO ZOSTAŁO NAPRAWIONE

**Główny problem:** Service Worker był wyrejestrowany, przez co powiadomienia w ogóle nie mogły działać.

**Rozwiązanie:** Service Worker został aktywowany - teraz aplikacja może wysyłać powiadomienia push.

---

## 📱 JAK PRZETESTOWAĆ NA TELEFONIE (PWA)

### KROK 1: Sprawdź uprawnienia aplikacji

#### **ANDROID:**
1. Otwórz **Ustawienia** telefonu
2. Wyszukaj **"Elektron"** lub przejdź do **"Aplikacje"**
3. Znajdź aplikację **Elektron** na liście
4. Przejdź do sekcji **"Powiadomienia"**
5. Upewnij się, że **wszystkie powiadomienia są WŁĄCZONE**
6. Sprawdź czy nie ma żadnych ograniczeń (np. "Nie przeszkadzać")

#### **iOS (iPhone/iPad):**
1. Otwórz **Ustawienia**
2. Przewiń w dół i znajdź aplikację **Elektron**
3. Dotknij **"Powiadomienia"**
4. Włącz **"Zezwalaj na powiadomienia"**
5. Włącz wszystkie opcje: Dźwięk, Banery, Odznaki

---

### KROK 2: Odinstaluj i zainstaluj aplikację ponownie (jeśli potrzeba)

Jeśli uprawnienia są włączone ale powiadomienia nadal nie działają:

1. **Usuń aplikację z ekranu głównego**
2. **Otwórz przeglądarkę** (Chrome/Safari)
3. **Wejdź na stronę:** `https://elektron-finance.preview.emergentagent.com`
4. **Zainstaluj ponownie:**
   - Android: Kliknij ikonę "Dodaj do ekranu głównego"
   - iOS: Kliknij "Udostępnij" → "Dodaj do ekranu głównego"
5. **Zaakceptuj uprawnienia** gdy aplikacja o to poprosi

---

### KROK 3: Przetestuj powiadomienia

1. Otwórz aplikację Elektron
2. Przejdź do zakładki **"Przypomnienia"**
3. Kliknij przycisk **"Test powiadomień"** (zielony przycisk z ikoną Send)
4. **Powinieneś zobaczyć powiadomienie push** z tekstem: *"Jeśli widzisz to powiadomienie, system działa poprawnie!"*

---

## 💻 JAK PRZETESTOWAĆ NA KOMPUTERZE (Przeglądarka)

### CHROME/EDGE:
1. Otwórz stronę: `https://elektron-finance.preview.emergentagent.com`
2. **W pasku adresu** zobaczysz ikonę 🔒 lub 🔔
3. **Kliknij ikonę** i znajdź **"Powiadomienia"**
4. Ustaw na **"Zezwól"**
5. **Odśwież stronę** (F5)
6. Przejdź do **"Przypomnienia"** → Kliknij **"Test powiadomień"**

### FIREFOX:
1. Otwórz stronę: `https://elektron-finance.preview.emergentagent.com`
2. W pasku adresu kliknij **ikonę 🛈**
3. Przejdź do **"Uprawnienia"** → **"Powiadomienia"**
4. Zmień na **"Zezwól"**
5. **Odśwież stronę** (F5)
6. Przejdź do **"Przypomnienia"** → Kliknij **"Test powiadomień"**

---

## 🎯 CO TERAZ DZIAŁA

### ✅ Backend:
- Endpoint `GET /api/reminders/check/pending` - sprawdza przypomnienia gotowe do wysłania
- Automatyczne oznaczanie przypomnień jako `sent=true` po wysłaniu
- Filtrowanie przypomnień po dacie i godzinie

### ✅ Frontend:
- Service Worker jest **aktywny i zarejestrowany**
- Przycisk "Test powiadomień" działa
- Przycisk "Sprawdź teraz" wywołuje backend i wysyła powiadomienia
- Automatyczne sprawdzanie co 5 minut

### ✅ System Przypomnień:
- ZUS i Podatki (18-ty dzień miesiąca, godz. 9:00)
- Własne przypomnienia z dowolną datą i godziną
- Powiadomienia push na telefon i komputer

---

## ❓ TROUBLESHOOTING

### Problem: "Powiadomienia są zablokowane"
**Rozwiązanie:** Sprawdź uprawnienia w ustawieniach telefonu/przeglądarki (patrz instrukcje wyżej)

### Problem: "Błąd powiadomienia w PWA"
**Rozwiązanie:**
1. Odinstaluj aplikację
2. Wyczyść cache przeglądarki
3. Zainstaluj aplikację ponownie
4. Zaakceptuj uprawnienia podczas instalacji

### Problem: Powiadomienia nie pojawiają się automatycznie
**Sprawdź:**
1. Czy masz utworzone przypomnienia na dzisiaj?
2. Czy czas przypomnienia już minął?
3. Czy przypomnienie nie jest oznaczone jako "ukończone"?
4. Kliknij "Sprawdź teraz" aby wymusić sprawdzenie

---

## 📞 DODATKOWE INFORMACJE

- **Automatyczne sprawdzanie:** Co 5 minut
- **Testowe przypomnienia:** Użyj przycisku "Test powiadomień"
- **Ręczne sprawdzanie:** Użyj przycisku "Sprawdź teraz"
- **Setup ZUS/Podatki:** Kliknij "Setup ZUS/Podatki" aby utworzyć przypomnienia na cały rok

---

## 🎉 GOTOWE!

Po wykonaniu powyższych kroków, system powiadomień powinien działać zarówno na telefonie jak i komputerze.

Jeśli masz jakiekolwiek problemy, sprawdź najpierw uprawnienia w ustawieniach systemu/przeglądarki.
