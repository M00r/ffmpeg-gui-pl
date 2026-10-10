# FFmpeg GUI PL 💻

Nakładka GUI do programu FFmpeg, ułatwiająca obsługę popularnych operacji wideo i audio.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/release/python-3100/)
[![PyQt5 Version](https://img.shields.io/badge/PyQt5->=5.15-blue.svg)]()
[![Download .exe Version](https://drive.google.com/file/d/1M5WcGSA0SUaSZJVdNy2eOJf8dW5MywMq/view?usp=sharing)]()
## Opis 📝

FFmpeg GUI PL to przyjazna dla użytkownika nakładka graficzna na potężne narzędzie FFmpeg. Została stworzona z myślą o polskich użytkownikach, oferując intuicyjny interfejs do wykonywania złożonych operacji na plikach multimedialnych bez konieczności pisania skomplikowanych poleceń w konsoli.

Aplikacja umożliwia między innymi:

*   Konwersję formatów wideo i audio.
*   Wyodrębnianie klatek wideo (I, P, B, według interwału, zakresu czasu).
*   Wizualizację parametrów kodowania (wektory ruchu, QP).
*   Przetwarzanie wsadowe wielu plików jednocześnie.
*   Zarządzanie kolejką zadań z możliwością pauzy i stopu.
*   Edycję własnych poleceń FFmpeg.
*   Automatyczną aktualizację z weryfikacją sum kontrolnych.
*   Obsługę motywów (jasny/ciemny) i profili konfiguracyjnych.

## Spis Treści 🧭

*   [Opis](#opis)
*   [Kluczowe Funkcje](#kluczowe-funkcje--)
*   [Wymagania](#wymagania--)
*   [Instalacja](#instalacja--)
*   [Uruchomienie](#uruchomienie-▶️)
*   [Konfiguracja](#konfiguracja--)
*   [Interfejs Użytkownika](#interfejs-uzytkownika-🎨)
*   [Przykładowe Scenariusze Użycia](#przykładowe-scenariusze-użycia-💡)
*   [Rozwiązywanie Problemów](#rozwiązywanie-problemów--)
*   [Skróty Klawiszowe](#skróty-klawiszowe-⌨️)
*   [Struktura Projektu](#struktura-projektu-📁)
*   [Informacje o Danych](#informacje-o-danych-💾)
*   [Najlepsze Praktyki](#najlepsze-praktyki--)

## Kluczowe Funkcje 🚀

*   **Konwersja Formatów:** Obsługa wielu popularnych kontenerów i kodeków wideo/audio z możliwością wyboru jakości i parametrów kompresji.
*   **Ekstrakcja Klatek:** Precyzyjne wyodrębnianie klatek według typu (I, P, B), interwału czasowego lub liczby klatek, a także pojedynczych klatek.
*   **Analiza Wideo:** Wizualizacja wektorów ruchu oraz wartości QP (Quality Parameter) dla lepszego zrozumienia procesu kodowania.
*   **Edytor Poleceń:** Swobodne tworzenie i wykonywanie własnych poleceń FFmpeg z pomocą wbudowanych szablonów i podpowiedzi.
*   **Przetwarzanie Wsadowe:** Możliwość wykonania tej samej operacji na wielu plikach jednocześnie, z zarządzaniem w kolejce zadań.
*   **Kolejka Zadań:** Zaawansowane zarządzanie zadaniami z opcjami startu, pauzy, wznowienia i stopu, umożliwiające sekwencyjne przetwarzanie.
*   **Automatyczne Aktualizacje:** Funkcja sprawdzania i pobierania nowych wersji bezpośrednio z repozytorium GitHub, z weryfikacją sum kontrolnych SHA-256.
*   **Profile Ustawień:** Zapisywanie i wczytywanie konfiguracji programu (ścieżki, motyw, kanał aktualizacji) dla łatwego przełączania między różnymi środowiskami pracy.
*   **Wtyczki i Presety:** Możliwość dodawania własnych, niestandardowych operacji do drzewka funkcji programu.
*   **Motywy:** Dostępne dwa motywy interfejsu: jasny i ciemny, dla komfortu pracy w różnych warunkach oświetleniowych.

## Wymagania ⚙️

*   **Python:** Wersja 3.10 lub nowsza.
*   **FFmpeg:** Program FFmpeg musi być zainstalowany osobno i dostępny w systemowej zmiennej PATH lub skonfigurowany w ustawieniach programu.
*   **PyQt5:** Biblioteka interfejsu graficznego dla Pythona.

## Instalacja 📦

1.  **Sklonuj repozytorium:**
    ```bash
    git clone https://github.com/M00r/ffmpeg-gui-pl.git
    cd ffmpeg-gui-pl
    ```

2.  **Zainstaluj zależności Pythona:**
    ```bash
    pip install -r requirements.txt
    ```
    lub
    ```bash
    pip install PyQt5>=5.15 pyinstaller>=6.0
    ```

3.  **Zainstaluj FFmpeg:**
    *   **Windows:** Pobierz wersję „release full” z [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) (np. do `C:\ffmpeg\`). Dodaj `C:\ffmpeg\bin` do zmiennej środowiskowej PATH.
    *   **Linux:** Użyj menedżera pakietów, np. `sudo apt update && sudo apt install ffmpeg`.
    *   **macOS:** Użyj Homebrew: `brew install ffmpeg`.

4.  **Sprawdź instalację FFmpeg:**
    Uruchom w terminalu:
    ```bash
    ffmpeg -version
    ffprobe -version
    ffplay -version
    ```
    Każde polecenie powinno zwrócić informacje o wersji narzędzia.

## Uruchomienie ▶️

W katalogu głównym projektu uruchom skrypt `main.py`:

```bash
python main.py
```

## Konfiguracja ⚙️

Po pierwszym uruchomieniu programu, jego konfiguracja jest zapisywana w katalogu `~/.ffmpeg_gui_pl/`.

### Ustawienia Narzędzi FFmpeg 🛠️

Przejdź do `Plik -> Ustawienia` (skrót `Ctrl+,`), aby skonfigurować ścieżki do wykonywalnych plików FFmpeg, ffprobe i ffplay, jeśli nie znajdują się one w systemowej zmiennej PATH.

*   **Ścieżka do ffmpeg:** Np. `C:\ffmpeg\bin\ffmpeg.exe` lub `/usr/bin/ffmpeg`.
*   **Ścieżka do ffprobe:** Np. `C:\ffmpeg\bin\ffprobe.exe` lub `/usr/bin/ffprobe`.
*   **Ścieżka do ffplay:** Np. `C:\ffmpeg\bin\ffplay.exe` lub `/usr/bin/ffplay`.

### Motyw Interfejsu 🎨

Można przełączyć się między jasnym a ciemnym motywem poprzez menu `Widok -> Motyw jasny` lub `Widok -> Motyw ciemny`.

### Kanał Aktualizacji ⬆️

W ustawieniach można wybrać kanał aktualizacji: `stable` (stabilny) lub `beta` (wersje testowe).

### Profile Ustawień 👤

Program pozwala na zapisywanie i wczytywanie zestawów ustawień (ścieżki, motyw, kanał aktualizacji) za pomocą menu `Profile`.

## Interfejs Użytkownika 🎨

Po uruchomieniu programu, interfejs składa się z następujących głównych elementów:

*   **Menu Górne:** Zawiera opcje `Plik`, `Narzędzia`, `Widok`, `Profile`, `Pomoc`.
*   **Pasek Informacyjny:** Wyświetla ścieżki do wykrytych narzędzi FFmpeg, wersję aplikacji i lokalizację konfiguracji.
*   **Panel Główny (Splitter):** Dzieli okno na dwie sekcje:
    *   **Drzewko Funkcji (lewa strona):** Hierarchiczna lista dostępnych operacji FFmpeg, podzielona na kategorie (Konwersja, Wyodrębnianie Klatek, Analiza, Narzędzia Dodatkowe, Wtyczki).
    *   **Zakładki (prawa strona):**
        *   **Log:** Wyświetla szczegółowe informacje o wykonywanych poleceniach FFmpeg, komunikatach i błędach.
        *   **Podgląd klatek:** Prezentuje miniatury wygenerowanych obrazów, umożliwiając szybki przegląd.
        *   **Kolejka zadań:** Zarządza zadaniami do przetworzenia wsadowego lub sekwencyjnego.
*   **Pasek Postępu:** Wyświetla bieżący postęp wykonywanej operacji.
*   **Pasek Statusu:** Informuje o aktualnym stanie aplikacji (np. „Gotowe”, „Przetwarzanie…”).

## Jak Używać ❓

1.  **Wybierz operację:** W drzewku funkcji po lewej stronie, znajdź interesującą Cię operację i kliknij ją dwukrotnie.
2.  **Skonfiguruj parametry:** W otwartym oknie dialogowym ustaw wymagane parametry (pliki wejściowe, wyjściowe, kodeki, jakość, rozdzielczość itp.).
3.  **Uruchom:** Kliknij przycisk „Uruchom” lub „Akceptuj”. Program wygeneruje odpowiednie polecenie FFmpeg i wykona je w tle.
4.  **Monitoruj postęp:** Obserwuj pasek postępu oraz zakładkę `Log` i `Kolejka zadań`.

## Przykładowe Scenariusze Użycia 💡

### Scenariusz 1: Konwersja filmu do mniejszego pliku 📉

1.  W drzewku funkcji wybierz `1. Konwersja formatów (kontenery) -> Konwertuj do .mp4`.
2.  W oknie dialogowym dodaj plik wideo.
3.  W sekcji "Jakość obrazu" wybierz `Niska (CRF 28)` oraz `1280x720` dla rozdzielczości.
4.  Wskaż katalog docelowy i kliknij „Uruchom”.

### Scenariusz 2: Wyodrębnienie klatek do analizy 🖼️

1.  W drzewku funkcji wybierz `2. Wyodrębnianie i analiza klatek -> 2.1 Według typu klatki -> Wyodrębnij wszystkie klatki I`.
2.  Jako format obrazu wybierz `PNG` (bezstratny).
3.  Wskaż katalog docelowy i kliknij „Uruchom”.
4.  Po zakończeniu, zakładka `Podgląd klatek` pokaże miniatury wyodrębnionych obrazów.

### Scenariusz 3: Wizualizacja ruchu w kodowanym wideo ➡️⬆️⬇️

1.  W drzewku funkcji wybierz `3. Analiza wektorów ruchu -> Wektory ruchu (codecview)`.
2.  Zaznacz opcje `P-klatki: predykcja w przód (pf)`, `B-klatki: predykcja w przód (bf)` oraz `B-klatki: predykcja w tył (bb)`.
3.  Wskaż plik wyjściowy (np. `analiza.mp4`) i kliknij „Uruchom”.
4.  Otwórz wygenerowany plik w odtwarzaczu, aby zobaczyć wizualizację wektorów ruchu.

### Scenariusz 4: Wiele plików - ta sama operacja 🗂️

1.  Wybierz `Narzędzia -> Przetwarzanie wsadowe`.
2.  Dodaj wiele plików do listy.
3.  Wybierz operację (np. `Konwertuj do .mp4`).
4.  Wskaż katalog docelowy i kliknij „Uruchom”.
5.  Postęp operacji będzie widoczny w zakładce `Kolejka zadań`.

### Scenariusz 5: Weryfikacja integralności nagrania 🔒

1.  Aby wygenerować sumy kontrolne dla katalogu, wybierz `Narzędzia -> Oblicz SHA-256 dla katalogu…`.
2.  Wskaż katalog z plikami.
3.  Wyślij wygenerowany plik `checksums.sha256` wraz z plikami.
4.  Odbiorca może zweryfikować integralność plików za pomocą `Narzędzia -> Zweryfikuj checksums.sha256…`.

## Tech Stack 🛠️

*   **Język:** Python
*   **GUI Framework:** PyQt5
*   **Narzędzie główne:** FFmpeg
*   **Dodatkowe narzędzia:** ffprobe, ffplay

## Struktura Projektu 📁

```
ffmpeg-gui-pl/
├── dialogs/             # Okna dialogowe dla różnych operacji
│   ├── __init__.py
│   ├── base.py          # Bazowa klasa okna dialogowego
│   ├── batch.py         # Przetwarzanie wsadowe
│   ├── command_editor.py # Edytor poleceń FFmpeg
│   ├── convert.py       # Konwersja formatów
│   ├── debug_vis.py     # Wizualizacje debugowe (QP, wektory ruchu)
│   ├── frame_extract.py # Wyodrębnianie klatek
│   ├── play_dialog.py   # Odtwarzacz FFplay
│   ├── plugins_dialog.py # Zarządzanie wtyczkami
│   └── update_dialog.py # Okno aktualizacji
├── installer/
│   └── ffmpeg_gui.iss   # Skrypt instalatora (Inno Setup)
├── plugins/
│   ├── __init__.py
│   ├── builtin/         # Wbudowane presety wtyczek
│   │   ├── batch_rename.py
│   │   └── youtube_preset.py
│   └── loader.py        # Ładowanie wtyczek
├── __pycache__/
├── widgets/
│   ├── __init__.py
│   ├── frame_preview.py # Podgląd klatek
│   ├── job_queue_widget.py # Widżet kolejki zadań
│   └── progress_bar.py  # Pasek postępu
├── config.py            # Zarządzanie konfiguracją aplikacji
├── checksum.py          # Obliczanie i weryfikacja sum SHA-256
├── ffmpeg_gui.iss       # Skrypt instalatora Inno Setup (duplikat?)
├── ffmpeg_runner.py     # Uruchamianie FFmpeg w osobnym wątku
├── ffplay_runner.py     # Uruchamianie FFplay w osobnym wątku
├── job_queue.py         # Logika kolejki zadań
├── main.py              # Główny punkt wejścia aplikacji
├── presets.py           # Definicje presetów jakości, kodeków itp.
├── requirements.txt     # Zależności projektu
├── settings_dialog.py   # Okno ustawień programu
├── struktura.txt        # (pusty plik tekstowy)
├── theme.py             # Obsługa motywów interfejsu (QSS)
├── updater.py           # Mechanizm autoaktualizacji
└── version.py           # Informacje o wersji aplikacji
```

## Rozwiązywanie Problemów ❓

| Objaw                                | Przyczyna                                       | Rozwiązanie                                     |
| :----------------------------------- | :---------------------------------------------- | :---------------------------------------------- |
| "Nie znaleziono ffmpeg"            | FFmpeg nie jest w systemowej zmiennej PATH     | Ustaw ścieżkę w `Plik -> Ustawienia`            |
| Program nie startuje                 | Brak zainstalowanej biblioteki PyQt5           | `pip install PyQt5`                             |
| Brak podglądu klatek                 | Nie wskazano katalogu z klatkami                | Ustaw katalog w zakładce `Podgląd klatek`       |
| Wizualizacja QP nie działa           | Używana jest standardowa wersja FFmpeg          | Pobierz wersję `nightly` z czerwca 2025.         |
| Wizualizacja makrobloków nie działa  | Funkcja usunięta z nowszych wersji FFmpeg       | Użyj `Wektory ruchu (codecview)`                |
| Błąd SHA-256 przy aktualizacji       | Plik aktualizacji uszkodzony lub podmieniony    | Pobierz ręcznie ze strony wydania GitHub       |
| Kolejka zadań stoi w miejscu         | Aktywna pauza między zadaniami                   | Kliknij przycisk `Wznów`                        |

## Skróty Klawiszowe ⌨️

*   `Ctrl+O`: Otwórz plik (ffprobe)
*   `Ctrl+,`: Ustawienia programu
*   `Ctrl+E`: Edytor poleceń FFmpeg
*   `Ctrl+P`: Odtwarzacz FFplay
*   `Ctrl+Q`: Zakończ program

## Informacje o Danych 💾

Wszystkie dane konfiguracyjne, profile użytkownika i wtyczki są przechowywane w katalogu domowym użytkownika:

*   **Windows:** `C:\Users\<NazwaUżytkownika>\.ffmpeg_gui_pl\`
*   **Linux/macOS:** `~/.ffmpeg_gui_pl/`

Katalog ten zawiera:

*   `config.json`: Ustawienia programu.
*   `profiles/`: Zapisane profile użytkownika.
*   `plugins/`: Niestandardowe wtyczki dodane przez użytkownika.

Kopiowanie tego katalogu na inny komputer pozwala przenieść ustawienia i wtyczki (ale nie samego FFmpeg).

## Najlepsze Praktyki ✨

*   **Testuj na krótkich fragmentach:** Przed wykonaniem operacji na długich plikach, zawsze testuj ustawienia na krótkim wycinku.
*   **Unikaj `-c copy` do zmiany kodeka:** Opcja `-c copy` kopiuje strumienie bez rekompresji, zmieniając jedynie kontener. Nie służy do zmiany kodeka.
*   **Zrozum CRF:** CRF (Constant Rate Factor) to parametr jakości, a nie bitrate. Niższa wartość oznacza lepszą jakość (i większy plik), wyższa – gorszą jakość (i mniejszy plik). Zakres 18-23 jest zazwyczaj dobrym kompromisem.
*   **Wykorzystaj tryb szybki:** Przy wyodrębnianiu klatek I, używaj trybu szybkiego (`-skip_frame nokey`), aby znacząco przyspieszyć proces.
*   **Archiwizacja w PNG:** Do celów archiwalnych i analizy preferuj format PNG, ponieważ JPG jest formatem stratnym.
*   **Regularne aktualizacje:** FFmpeg jest aktywnie rozwijany. Aktualizuj program i narzędzia FFmpeg, aby korzystać z najnowszych funkcji i poprawek.
*   **Zapisuj profile:** Używaj profili, aby łatwo przenosić konfigurację między różnymi maszynami lub przywracać ustawienia po reinstalacji.

## Przyczyniający się 🧑‍💻

Chcesz pomóc w rozwoju? Zapoznaj się z [CONTRIBUTING.md](CONTRIBUTING.md).

## Licencja 📄

Ten projekt jest licencjonowany na licencji [MIT](LICENSE).

## Ważne Linki 🔗

*   [Strona projektu FFmpeg](https://ffmpeg.org/)
*   [Repozytorium FFmpeg GUI PL](https://github.com/M00r/ffmpeg-gui-pl)

--- 

*Repozytorium: `ffmpeg-gui-pl`*
*Autor: M00r - Iwo*
*URL: [https://github.com/M00r/ffmpeg-gui-pl](https://github.com/M00r/ffmpeg-gui-pl)*

Masz pytania? Zostaw [issue](https://github.com/M00r/ffmpeg-gui-pl/issues).

Podoba Ci się projekt? Daj gwiazdkę ⭐, zasubskrybuj 🌟 i rozważ fork 🍴!

---

