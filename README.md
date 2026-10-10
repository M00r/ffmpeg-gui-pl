Instrukcja obsługi — FFmpeg GUI PL
Poniżej znajdziesz kompletny przewodnik po programie: od instalacji, przez konfigurację, po każdą funkcję z przykładami.

1. Wymagania wstępne

1.1 Python
Program wymaga Pythona 3.10 lub nowszego. Sprawdź wersję:

powershell
python --version

1.2 Zależności Pythona
W katalogu projektu zainstaluj biblioteki:

powershell
pip install PyQt5

1.3 FFmpeg
Program nie zawiera FFmpeg — musi być zainstalowany osobno.

Windows:
Pobierz z gyan.dev wersję „release full".
Rozpakuj np. do C:\ffmpeg\.
Dodaj C:\ffmpeg\bin do zmiennej PATH, albo wskaż ścieżkę w Ustawieniach programu.

Sprawdzenie:

powershell
ffmpeg -version
ffprobe -version
ffplay -version
Każde z tych poleceń powinno wypisać wersję. Jeśli któreś nie działa, program też go nie znajdzie.

2. Uruchomienie programu
W katalogu projektu:

powershell
python main.py
Otworzy się główne okno z:

menu na górze (Plik, Narzędzia, Widok, Profile, Pomoc),

drzewkiem funkcji po lewej,

zakładkami po prawej: Log, Podgląd klatek, Kolejka zadań,

paskiem postępu na dole,

paskiem statusu ze ścieżkami do ffmpeg/ffprobe/ffplay i wersją.


3. Pierwsza konfiguracja
3.1 Plik → Ustawienia
Otwórz Plik → Ustawienia (skrót Ctrl+,) i sprawdź:

Pole	Co wpisać
Ścieżka do ffmpeg	np. C:\ffmpeg\bin\ffmpeg.exe
Ścieżka do ffprobe	np. C:\ffmpeg\bin\ffprobe.exe
Ścieżka do ffplay	np. C:\ffmpeg\bin\ffplay.exe
Motyw	light (jasny) lub dark (ciemny)
Kanał aktualizacji	stable — dla zwykłego użytkowania
Sprawdzaj aktualizacje przy starcie	zaznaczone
Weryfikuj SHA-256 pobranej aktualizacji	zalecane
Generuj sumy SHA-256 po operacji	opcjonalne
Potwierdzaj nadpisanie plików	zalecane
Kliknij OK. Pasek informacyjny u góry pokaże wykryte ścieżki.

3.2 Motyw
Widok → Motyw jasny lub Widok → Motyw ciemny. Zmiana zapisuje się automatycznie.

4. Interfejs — co gdzie jest

┌─────────────────────────────────────────────────────────────┐
│ Plik   Narzędzia   Widok   Profile   Pomoc                  │  ← menu
├─────────────────────────────────────────────────────────────┤
│ FFmpeg: ... | ffprobe: ... | Wersja: 1.0.0 | Konfig: ...    │  ← pasek info
├──────────────────────┬──────────────────────────────────────┤
│                      │  [Log] [Podgląd klatek] [Kolejka]    │
│   Drzewko funkcji    │                                      │
│   (kliknij 2×)       │  Treść zakładki                      │
│                      │                                      │
├──────────────────────┴──────────────────────────────────────┤
│ [████████░░░░░░░░░░] 42.3%                                  │  ← postęp
├─────────────────────────────────────────────────────────────┤
│ Status: Przetwarzanie…                                      │
└─────────────────────────────────────────────────────────────┘
Jak uruchomić operację z drzewka: kliknij dwukrotnie na wybraną pozycję. Otworzy się okno dialogowe.

5. Funkcje — instrukcje krok po kroku

5.1 Konwersja formatów
Cel: zmienić kontener lub kodek pliku.

W drzewku rozwiń 1. Konwersja formatów.

Kliknij dwukrotnie np. Konwertuj do .mp4.

W oknie:

Dodaj pliki… — możesz wybrać wiele plików na raz (tryb wsadowy).

Kodek wideo / audio — zostaw domyślne dla danego formatu albo zmień.

Bitrate audio — np. 192 kbps.

Preset jakości — np. „Wysoka (CRF 18)".

Rozdzielczość — np. 1280x720 albo „Bez zmiany".

Klatki na sekundę — np. 30 albo „Bez zmiany".

Opcje dodatkowe:

„Kopiuj strumienie bez rekompresji" — najszybciej, ale zmienia tylko kontener.

„MP4: szybki start" — dobra dla plików publikowanych w internecie.

„Usuń audio", „Usuń wideo" — np. do wyciągania obrazu.

Wybierz Katalog docelowy.

Kliknij Uruchom.

Wynik: pliki pojawią się w katalogu docelowym z tym samym tytułem, ale nowym rozszerzeniem.

5.2 Wyodrębnianie klatek I / P / B
Cel: zapisać na dysku wszystkie klatki danego typu.

Czym są klatki:

I (kluczowe) — pełny obraz, podstawa GOP.
P (predykcyjne) — zapisują różnice względem poprzednich.
B (dwukierunkowe) — różnice względem przodu i tyłu.

Drzewko → 2. Wyodrębnianie i analiza klatek → 2.1 Według typu klatki.

Kliknij dwukrotnie np. Wyodrębnij wszystkie klatki I.

Wybierz:

Format obrazu — PNG (bezstratny) lub JPG (mniejszy).
Jakość JPG — 1 = najlepsza, 31 = najgorsza.
Tryb szybki (tylko dla I) — pomija dekodowanie klatek niekluczowych, przyspiesza.
Wskaż katalog docelowy. Program utworzy w nim podkatalog o nazwie pliku wejściowego.
Uruchom.

Wynik: pliki nazwa_I_00001.png, nazwa_I_00002.png itd.

5.3 Wyodrębnianie co N-tą klatkę / co N sekund
Drzewko → 2.2 Według interwału → Co N-tą klatkę / co N sekund.

Wybierz tryb:
Co N-tą klatkę — np. N=10 oznacza co 10. klatkę.
Co N sekund — np. N=2 oznacza co 2 sekundy.
Ustaw N, format obrazu, katalog docelowy.
Uruchom.

5.4 Wyodrębnianie klatek z zakresu czasu
Drzewko → 2.2 Według interwału → Z zakresu czasu (od–do).

Ustaw Start i Koniec (HH:mm:ss).
Ustaw Klatek na sekundę (np. 1 — jedna klatka na sekundę).
Wskaż katalog, Uruchom.

5.5 Pojedyncza klatka
Drzewko → Wyodrębnij konkretną klatkę (numer/czas).

Wybierz tryb:
Według czasu — np. 00:00:05.500.
Według numeru klatki — np. 150.
Wskaż plik wyjściowy (PNG/JPG).
Uruchom.

5.6 Wizualizacja wektorów ruchu
Cel: nałożyć na obraz strzałki pokazujące, jak kodowane są makrobloki w kolejnych klatkach.

Drzewko → 3. Analiza makrobloków i wektorów ruchu → Wektory ruchu (codecview).

Zaznacz, co ma się pojawić:
P-klatki: predykcja w przód (pf)
B-klatki: predykcja w przód (bf)
B-klatki: predykcja w tył (bb)
Wskaż plik wyjściowy (np. output.mp4).

Uruchom.

Uwaga: działa tylko dla kodeków, które eksportują wektory ruchu (H.264 zwykle tak, ale nie zawsze).

5.7 Wizualizacja QP (zaawansowane)
Cel: pokolorować makrobloki według wartości QP (parametr jakości).

Drzewko → 2.3 Wizualizacja debugowa → Wizualizacja wartości QP (wymaga FFmpeg nightly).
Wybierz kodek wyjściowy i CRF.
Wskaż plik wyjściowy, Uruchom.
Uwaga: w standardowym FFmpeg 7.1.1 ta funkcja nie zadziała — wymaga kompilacji „nightly" z czerwca 2025 roku. Jeśli nakładka się nie pojawi, to właśnie z tego powodu.

5.8 Sprawdzenie informacji o pliku (ffprobe)
Drzewko → 4. Narzędzia dodatkowe → Pokaż informacje o pliku.

Wybierz plik.
W zakładce Log pojawi się pełny raport: kodeki, bitrate, rozdzielczość, FPS, czas trwania, metadane.
Przydatne przed wyborem operacji — pozwala zobaczyć, co jest w pliku.

5.9 Edytor poleceń FFmpeg
Cel: wpisać własne polecenie FFmpeg, także takie, którego nie ma w drzewku.

Menu Narzędzia → Edytor poleceń FFmpeg (skrót Ctrl+E).
Po lewej masz 15 gotowych szablonów. Kliknij dwukrotnie, aby wstawić do edytora.
Możesz:
Wstaw ścieżkę ffmpeg — dopisze pełną ścieżkę.
Wstaw plik wejściowy… — okno wyboru.
Wstaw plik wyjściowy… — okno zapisu.
Kliknij Uruchom — polecenie wykona się w tle, wynik pojawi się na dole.

Przykładowe szablony:
Konwersja MP4 → MKV (kopiuj)
Wyodrębnij klatki I/P/B
Co 1 sekundę
Wektory ruchu
Zmiana rozdzielczości do 720p
Wyciągnij audio (MP3 / bez rekompresji)
Przytnij fragment
Łączenie plików
GIF z fragmentu

5.10 Odtwarzacz FFplay
Cel: podejrzeć plik lub efekt filtrów bez zapisywania.

Menu Narzędzia → Odtwarzacz FFplay (skrót Ctrl+P).
Wybierz plik.
Opcje:

Pełny ekran — tryb -fs.
Bez ramki okna — tryb -noborder.
Start od (sekundy) — pomiń początek.
Filtr wideo (-vf) — np. scale=1280:720 albo codecview=mv=pf+bf+bb.
-flags2 — np. +export_mvs.
-debug — starsze opcje (zwykle już nie działają).
Kliknij Odtwórz. Zamknięcie okna ffplay kończy odtwarzanie.

5.11 Przetwarzanie wsadowe
Cel: wykonać tę samą operację na wielu plikach jednocześnie.

Menu Narzędzia → Przetwarzanie wsadowe.
Dodaj pliki… — możesz wybrać wiele.
Wybierz Operację:
Konwertuj do .mp4 / .mkv / .webm
Wyodrębnij klatki I / P / B
Wskaż Katalog docelowy.
Uruchom.

Zadania trafią do Kolejki zadań (zakładka po prawej). Możesz je podejrzeć i uruchomić.

5.12 Kolejka zadań
Cel: wykonać wiele operacji jedna po drugiej, z możliwością pauzy.

Zakładka Kolejka zadań po prawej stronie.

Dodawanie zadań:

Z przetwarzania wsadowego (automatycznie).
Z menu Narzędzia → Dodaj do kolejki (bieżący log) — bierze ostatnie polecenie z Loga.
Z wtyczek (patrz punkt 5.14).

Sterowanie:

▲ / ▼ — zmiana kolejności.
Usuń / Wyczyść — usuwanie.
Start — uruchomienie kolejki.
Pauza / Wznów — wstrzymanie między zadaniami.
Stop — zatrzymanie całości.
Kolumny tabeli:
# — numer zadania.
Zadanie — nazwa.
Postęp — pasek procentowy dla aktualnego zadania.
Status — Oczekuje / W toku / OK / Błąd (kod).

5.13 Profile — zapisywanie ulubionych ustawień
Cel: zapamiętać konfigurację (ścieżki, motyw, kanał aktualizacji), aby szybko ją odtworzyć.

Menu Profile → Zapisz bieżące jako profil….
Podaj nazwę, np. Domowe PC.
Aby wczytać: Profile → Wczytaj profil… i wybierz nazwę.
Aby usunąć: Profile → Usuń profil….
Profile zapisują się w ~/.ffmpeg_gui_pl/profiles/.

5.14 Wtyczki — własne presety
Cel: dodać własne operacje do drzewka (np. preset pod YouTube).

Menu Narzędzia → Wtyczki i presety….

Okno pokazuje:
Zainstalowane wtyczki (wbudowane + użytkownika).
Dostępne presety — lista gotowych operacji.
Przyciski:

Otwórz katalog wtyczek — otwiera ~/.ffmpeg_gui_pl/plugins/.
Dodaj wtyczkę (.py)… — kopiuje plik z wtyczką.
Wbudowane presety:
YouTube 1080p
Twitter/X 720p
Instagram Reels (9:16)
Audio MP3 320 kbps
Audio FLAC (bezstratny)
Wideo H.265 bardzo mały plik

Jak uruchomić preset: w drzewku rozwiń 5. Wtyczki — własne presety i kliknij dwukrotnie na wybrany preset. Program zapyta o plik wejściowy i katalog docelowy, po czym doda zadanie do kolejki.

5.15 Sumy kontrolne SHA-256
Cel: zweryfikować integralność plików po operacji.

Automatycznie: po każdej operacji, jeśli w Ustawieniach zaznaczono „Generuj sumy SHA-256 po operacji", program tworzy plik checksums.sha256 w katalogu wyjściowym. Format zgodny z sha256sum -c.
Ręcznie — generowanie:
Menu Narzędzia → Oblicz SHA-256 dla katalogu….
Wskaż katalog.

W Locie pojawi się liczba przetworzonych plików i ścieżka do checksums.sha256.
Ręcznie — weryfikacja:
Menu Narzędzia → Zweryfikuj checksums.sha256….
Wskaż plik checksums.sha256.
Program policzy sumy wszystkich plików i pokaże raport: ile OK, ile błędnych.

Ręcznie z terminala:

powershell
Get-FileHash plik.mp4 -Algorithm SHA256
5.16 Aktualizacje
Automatyczne: przy starcie program sprawdza GitHub Releases (jeśli w Ustawieniach włączone „Sprawdzaj aktualizacje przy starcie").

Ręczne:
Menu Pomoc → Sprawdź aktualizacje….
Jeśli jest nowsza wersja, otworzy się okno z:
Numerem nowej wersji,
Oczekiwaną sumą SHA-256,
Opisem zmian.
Kliknij Pobierz i zainstaluj.

Program:
pobierze plik,
zweryfikuje SHA-256 — jeśli się nie zgadza, instalacja zostanie przerwana,
zapyta o potwierdzenie,
podmieni plik i uruchomi się ponownie.

6. Zakładki po prawej
6.1 Log
Pełny zapis wszystkich operacji: polecenia FFmpeg, komunikaty, błędy.
Zatrzymaj — przerwij bieżące zadanie.
Wyczyść log — wyczyść zawartość.
Zapisz log… — zapisz do pliku .txt.

6.2 Podgląd klatek
Miniatury obrazów wygenerowanych w katalogu.
Wybierz katalog… — wskaż katalog z klatkami.
Odśwież — przeładuj listę.
Dwuklik na miniaturę — otwiera plik w systemowej przeglądarce obrazów.

6.3 Kolejka zadań
Patrz punkt 5.12.

7. Typowe scenariusze
Scenariusz 1: Konwersja filmu do mniejszego pliku
Drzewko → Konwertuj do .mp4.

Wybierz plik.
Preset jakości: „Niska (CRF 28)".
Rozdzielczość: 1280x720.
Katalog docelowy, Uruchom.

Scenariusz 2: Wyciągnięcie klatek do analizy
Drzewko → Wyodrębnij wszystkie klatki I.
Format: PNG (bezstratny, do analizy).
Katalog docelowy, Uruchom.
Po zakończeniu zakładka Podgląd klatek pokaże miniatury.

Scenariusz 3: Wizualizacja ruchu w kodowanym wideo
Drzewko → Wektory ruchu (codecview).

Zaznacz wszystkie trzy opcje: pf, bf, bb.
Plik wyjściowy np. analiza.mp4, Uruchom.
Otwórz wynik w odtwarzaczu — zobaczysz strzałki ruchu.

Scenariusz 4: Wiele plików — ta sama operacja
Menu Narzędzia → Przetwarzanie wsadowe.

Dodaj 10 plików.

Operacja: Konwertuj do .mp4.
Katalog docelowy, Uruchom.
W zakładce Kolejka zadań obserwuj postęp.
Scenariusz 5: Weryfikacja integralności nagrania
Menu Narzędzia → Oblicz SHA-256 dla katalogu….
Wybierz katalog z archiwum.
Wyślij plik checksums.sha256 odbiorcy razem z plikami.
Odbiorca: Narzędzia → Zweryfikuj checksums.sha256… i dostanie raport.

8. Rozwiązywanie problemów
Objaw	Przyczyna	Rozwiązanie
„Nie znaleziono ffmpeg"	FFmpeg nie w PATH	Ustaw ścieżkę w Plik → Ustawienia
Program nie startuje	Brak PyQt5	pip install PyQt5
Brak podglądu klatek	Nie wskazano katalogu	Ustaw katalog w zakładce Podgląd klatek
Wizualizacja QP nie działa	Standardowy FFmpeg 7.1.1	Pobierz wersję nightly
Wizualizacja typów makrobloków nie działa	Funkcja usunięta z FFmpeg	Nie da się — użyj wektorów ruchu
Błąd SHA-256 przy aktualizacji	Plik uszkodzony lub podmieniony	Pobierz ręcznie ze strony wydania
Kolejka stoi w miejscu	Pauza aktywna	Kliknij „Wznów"

10. Skróty klawiszowe
Skrót	Akcja
Ctrl+O	Otwórz plik (ffprobe)
Ctrl+,	Ustawienia
Ctrl+E	Edytor poleceń FFmpeg
Ctrl+P	Odtwarzacz FFplay
Ctrl+Q	Zakończ
11. Gdzie program trzyma dane
Wszystko w katalogu domowym:

text
~/.ffmpeg_gui_pl/
├── config.json         ← ustawienia
├── profiles/           ← zapisane profile
│   └── *.json
└── plugins/            ← wtyczki użytkownika
    └── *.py
Windows: C:\Users\UserName\.ffmpeg_gui_pl\
Linux/macOS: ~/.ffmpeg_gui_pl/

Kopiując ten katalog na inny komputer, przeniesiesz ustawienia i wtyczki (ale nie samego FFmpeg).

11. Najlepsze praktyki
Zawsze testuj nowe operacje na krótkim pliku — np. 10-sekundowym wycinku, zanim puścisz na cały film.
Nie używaj -c copy do zmiany kodeka — kopiowanie tylko przenosi strumienie, nie konwertuje.
CRF to nie to samo co bitrate — CRF to tryb stałej jakości (0 = bezstratny, 51 = najgorszy). 18–23 to dobry zakres.
Przy wyodrębnianiu klatek I używaj trybu szybkiego — pomija dekodowanie pozostałych klatek i przyspiesza kilkukrotnie.
Do archiwizacji używaj PNG — JPG traci dane przy każdej operacji.
Regularnie sprawdzaj aktualizacje — FFmpeg co kilka miesięcy zmienia opcje.
Zapisuj profile — jeśli używasz programu na kilku komputerach, zapisz config i skopiuj na drugi.
