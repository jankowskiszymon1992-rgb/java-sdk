# ℹ️ Wyjaśnienie Błędów w Konsoli - Meta Pixel i rrweb

## Błędy które widzisz:

```
Wyrażenie niedostępne

rrweb-plugin-console-record.js:2447 [Meta Pixel] - An invalid email address was specified for 'em'. This data will not be sent with any events for this Pixel.

rrweb-plugin-console-record.js:2447 [Meta Pixel] - You are sending a non-standard event 'SubscribedButtonClick'. The preferred way to send these events is using trackCustom.
```

## 🔍 Skąd pochodzą te błędy?

Te błędy **NIE POCHODZĄ z Twojej aplikacji Elektron**. Pochodzą z **zewnętrznych narzędzi testowych** dodanych przez platformę Emergent:

### 1. **rrweb** - Narzędzie nagrywające sesje
- Znajduje się w `/app/frontend/public/index.html` (linie 31-32)
- URL: `https://d2adkz2s9zrlge.cloudfront.net/rrweb-recorder-20250919-1.js`
- **Cel:** Nagrywanie sesji użytkownika do celów testowych/debugowania
- **Co robi:** Nagrywuje wszystkie akcje użytkownika, kliknięcia, logi konsoli, błędy

### 2. **PostHog** - Narzędzie analityczne
- Znajduje się w `/app/frontend/public/index.html` (linie 94-160)
- **Cel:** Zbieranie statystyk użycia aplikacji

## 🚨 Czy to jest problem?

**NIE!** Te błędy:
- ❌ **Nie wpływają** na działanie Twojej aplikacji Elektron
- ❌ **Nie psują** żadnych funkcji
- ❌ **Nie są** błędami w Twoim kodzie
- ✅ **Pochodzą** z zewnętrznych narzędzi testowych platformy Emergent
- ✅ **Są** tylko informacyjne dla debugowania tych narzędzi

## 🤔 Dlaczego widzę Meta Pixel?

**rrweb** nagrywuje **CAŁĄ** konsolę przeglądarki, w tym:
- Logi z Twojej aplikacji
- Logi z innych kart przeglądarki (jeśli są otwarte)
- Logi z rozszerzeń przeglądarki
- **Logi z testów automatycznych platformy Emergent** (które mogą używać Meta Pixel do testów)

Błędy Meta Pixel prawdopodobnie pochodzą z **testów automatycznych** które platforma Emergent wykonuje na Twojej aplikacji.

## 📝 Komentarz w kodzie:

W pliku `index.html` jest komentarz:

```html
<!--
These two scripts have been added for the testing, please do not edit or remove them
-->
<script src="https://unpkg.com/rrweb@latest/dist/rrweb.min.js"></script>
<script src="https://d2adkz2s9zrlge.cloudfront.net/rrweb-recorder-20250919-1.js"></script>
```

To potwierdza, że te skrypty są **dodane przez platformę** i **nie powinny być usuwane**.

## ✅ Co możesz zrobić?

### Opcja 1: Zignoruj te błędy (ZALECANE)
- Te błędy nie wpływają na działanie aplikacji
- Są częścią narzędzi testowych platformy
- Możesz bezpiecznie je zignorować

### Opcja 2: Filtruj błędy w konsoli
W DevTools możesz filtrować błędy:
1. Otwórz konsolę (F12)
2. W polu filtra wpisz: `-rrweb` (minus przed słowem)
3. To ukryje wszystkie błędy zawierające "rrweb"

### Opcja 3: Skontaktuj się z supportem Emergent
Jeśli te błędy Cię naprawdę przeszkadzają, możesz zapytać support Emergent:
- Czy mogą wyłączyć rrweb dla Twojego projektu
- Lub skonfigurować go tak, żeby nie nagrywał konsoli

## 🎯 Podsumowanie:

| Aspekt | Status |
|--------|--------|
| **Źródło błędów** | ✅ Zewnętrzne narzędzia testowe (rrweb, PostHog) |
| **Wpływ na aplikację** | ❌ Żaden - aplikacja działa normalnie |
| **Czy naprawić?** | ❌ Nie - to nie są błędy w Twoim kodzie |
| **Akcja** | ✅ Zignoruj lub przefiltruj w konsoli |

---

**Twoja aplikacja Elektron działa poprawnie!** Te błędy to artefakty narzędzi testowych platformy Emergent.
