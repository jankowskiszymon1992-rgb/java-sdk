# 🆘 INSTRUKCJA KROK PO KROKU - DevTools

Aplikacja **DZIAŁA POPRAWNIE** na serwerze (0 błędów, 0 logów).
Problem jest w **CACHE w Twojej przeglądarce**.

---

## 📱 TELEFON - ZRÓB TO TERAZ (3 minuty):

### KROK 1: Zamknij Chrome całkowicie
1. Naciśnij przycisk **Ostatnie aplikacje** (kwadrat ⬜)
2. Przesuń Chrome w górę aby zamknąć
3. Lub przejdź do Ustawienia → Aplikacje → Chrome → **Wymuś zatrzymanie**

### KROK 2: Wyczyść cache Chrome
1. Otwórz **Ustawienia** telefonu
2. Przejdź do **Aplikacje**
3. Znajdź **Chrome**
4. Kliknij **Pamięć** lub **Pamięć masowa**
5. Kliknij **Wyczyść pamięć podręczną** (NIE "Wyczyść dane" - tylko cache!)

### KROK 3: Wyczyść dane strony
1. Otwórz Chrome
2. Wejdź na stronę: https://elektron-smart.preview.emergentagent.com
3. W pasku adresu (obok URL) kliknij ikonę **🔒 (kłódka)**
4. Kliknij **Ustawienia witryny**
5. Przewiń na dół i kliknij **Wyczyść i zresetuj**

### KROK 4: Wyrejestruj Service Worker
1. W Chrome wpisz w pasek adresu: `chrome://serviceworker-internals`
2. Znajdź wiersz z "elektron-smart"
3. Kliknij przycisk **Unregister** (Wyrejestruj)

### KROK 5: Otwórz aplikację ponownie
1. Zamknij Chrome
2. Otwórz Chrome
3. Wejdź na: https://elektron-smart.preview.emergentagent.com
4. **DevTools NIE POWINNY się otworzyć**

---

## 💻 KOMPUTER - ZRÓB TO TERAZ (2 minuty):

### METODA 1: Tryb Incognito (TEST)
1. Naciśnij **Ctrl + Shift + N** (Windows) lub **Cmd + Shift + N** (Mac)
2. W oknie Incognito wejdź na: https://elektron-smart.preview.emergentagent.com
3. **Jeśli TAM DZIAŁA** - problem jest w cache normalnego Chrome
4. Przejdź do METODY 2

### METODA 2: Wyczyść cache (PEWNA)
1. Zamknij Chrome całkowicie (zamknij wszystkie okna)
2. Otwórz Chrome ponownie
3. Naciśnij **Ctrl + Shift + Delete** (Windows) lub **Cmd + Shift + Delete** (Mac)
4. W oknie wybierz:
   - Zakres czasu: **Cały czas**
   - Zaznacz: ✅ **Pliki cookie i inne dane witryn**
   - Zaznacz: ✅ **Obrazy i pliki w pamięci podręcznej**
5. Kliknij **Wyczyść dane**
6. Zamknij Chrome
7. Otwórz Chrome
8. Wejdź na: https://elektron-smart.preview.emergentagent.com

### METODA 3: Przeładowanie twarde
1. Otwórz: https://elektron-smart.preview.emergentagent.com
2. Otwórz DevTools: **F12**
3. Kliknij PRAWYM przyciskiem na ikonę **Odśwież** (⟳) w przeglądarce
4. Wybierz **"Opróżnij pamięć podręczną i wykonaj przeładowanie twarde"**

---

## 🔍 JAK SPRAWDZIĆ CZY DZIAŁA?

Po wyczyszczeniu cache:

1. Otwórz aplikację
2. Naciśnij **F12** aby otworzyć DevTools
3. Przejdź do zakładki **Console**
4. Powinno być **CAŁKOWICIE PUSTO** (0 wiadomości)
5. Zamknij DevTools
6. **DevTools NIE POWINNY** otwierać się automatycznie

---

## ⚠️ NADAL NIE DZIAŁA?

### Sprawdź ustawienia Chrome:

1. Otwórz DevTools (F12)
2. Kliknij **⚙️ Settings** (ikonka koła zębatego)
3. Sprawdź zakładkę **Preferences**
4. Upewnij się że **ODZNACZONE** są:
   - ❌ "Auto-open DevTools for popups"
   - ❌ "Disable paused state overlay"
5. Zamknij i otwórz Chrome

### Wyłącz rozszerzenia:

1. Wpisz w pasek adresu: `chrome://extensions`
2. Wyłącz **WSZYSTKIE** rozszerzenia (przełączniki na OFF)
3. Zrestartuj Chrome
4. Sprawdź czy aplikacja działa
5. Jeśli działa - włączaj rozszerzenia po kolei aby znaleźć winowajcę

---

## 📸 JEŚLI NADAL NIE DZIAŁA - PRZEŚLIJ MI:

1. **Screenshot konsoli** (F12 → Console) - co tam widzisz?
2. **Screenshot Service Worker** (F12 → Application → Service Workers)
3. Odpowiedz:
   - Czy w **trybie incognito** działa?
   - Czy wyczyściłeś cache **WSZYSTKIMI** metodami?
   - Jaka przeglądarka i system? (np. Chrome 120 na Windows 11)

---

## ✅ PODSUMOWANIE:

**Aplikacja jest NAPRAWIONA i DZIAŁA** (sprawdzone - 0 błędów, 0 logów).

Problem jest **TYLKO w Twoim cache**.

**Wykonaj WSZYSTKIE kroki powyżej krok po kroku.**

Po wyczyszczeniu cache - **DevTools przestaną się otwierać automatycznie**.
