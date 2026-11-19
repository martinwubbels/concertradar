# ConcertRadar voor GitHub Pages

## Publiceren (gratis)
1. Maak op GitHub een nieuwe **public** repository `concertradar`.
2. Kies **Add file > Upload files** en upload `index.html`, `manifest.webmanifest`, `sw.js`, `icon-192.png`, `icon-512.png` en `.nojekyll` (het laatste bestand is optioneel).
3. Kies **Commit changes**.
4. Ga naar **Settings > Pages**. Kies **Deploy from a branch**, branch `main`, folder `/ (root)`, klik **Save**.
5. Open `https://JOUW-GEBRUIKERSNAAM.github.io/concertradar/` na publicatie.
6. Op Android: open in Chrome > menu > **App installeren** of **Toevoegen aan startscherm**.

## Belangrijk
- De concertlijst is een momentopname, geen live ticketcontrole.
- Favorieten en boekingen blijven **per browser/apparaat** opgeslagen, zonder synchronisatie.
- De opslag van de eerdere lokale HTML wordt **niet automatisch** meegenomen naar GitHub Pages. Exporteer in de oude versie een JSON en importeer via Updates & beheer in de nieuwe website.
- Wikipedia-foto's worden online opgezocht. Officiële concertfoto's worden **nog niet** automatisch opgehaald.
- GitHub Pages is publiek. Zet geen persoonlijke gegevens, tokens of privébestanden in de repository.
- De PWA heeft een offline cache van de appbestanden; nieuwe concerten en foto's vereisen verbinding.
- Automatische dagelijkse data-updates zijn nog niet ingericht.

## Nieuwe architectuur (voorstel in pull request)

- `data/concerts.json` is de gedeelde masterlijst met stabiele concert-ID's.
- `data/photos.json` bevat afbeeldingslinks en bronverwijzingen die uit officiële concertpagina's worden gelezen.
- De website haalt beide bestanden bij openen op. De oorspronkelijke ingebouwde lijst blijft beschikbaar wanneer het netwerk wegvalt.
- Favorieten, handmatige wijzigingen en boekingen blijven alleen lokaal op het apparaat staan. Maak een JSON-export als back-up.
- `.github/workflows/refresh-photos.yml` controleert dagelijks de reeds bekende officiële concertpagina's. Dit gebruikt Python zonder externe pakketten.
- De updater leest openbare `og:image` / `twitter:image` metadata en kopieert **geen** auteursrechtelijk beschermde afbeeldingsbestanden naar de repository. De uitgever van de foto kan hotlinking blokkeren of de afbeelding vervangen.
- In de website heeft een handmatig ingestelde afbeelding voorrang, daarna de concertpagina, daarna Wikipedia.
- De workflow controleert **geen kaartprijzen, voorraad of nieuwe concerten**. Daarvoor zijn afzonderlijke betrouwbare bronnen of een gecontroleerde invoerstroom nodig. Veranderde concertgegevens worden pas zichtbaar na aanpassing van `data/concerts.json`.
- De eerste masterlijst bevat 23 eerder besproken optredens en is een momentopname. Controleer altijd de officiële bronnen.

### Foto's handmatig actualiseren

Open in GitHub **Actions → ConcertRadar fotocontrole → Run workflow**. De resultaten verschijnen vervolgens in `data/photos.json`. De workflow start ook elke dag volgens de ingestelde cron, zolang GitHub Actions is ingeschakeld. De eerste geplande run kan door GitHub vertraging oplopen.

### Concert toevoegen

Voeg in `data/concerts.json` onder `events` een item toe met uniek `id`, `name`, `date` (`YYYY-MM-DD`), `venue`, `city`, `genre`, `price` (getal of null), `quality`, `value`, `priority`, `match`, `reason` en een officiële HTTPS-`url`. Bestaande ID's niet veranderen, anders gaan de lokaal opgeslagen favorieten/boekingen van dat concert verloren.

## Centrale masterlijst en dagelijkse broncontrole

De masterlijst is uitgebreid van 23 tot 110 vermeldingen uit eerdere concertrapporten. De 87 nieuw opgenomen historische vermeldingen zijn gemarkeerd als **niet opnieuw bevestigd**. De website toont dit op iedere betreffende concertkaart. Het overzicht is geen live bevestiging van kaarten of prijzen.

De workflow `ConcertRadar dagelijkse agenda-controle` controleert iedere ochtend enkele officiële regionale agenda's. De output staat in `data/discovery-candidates.json` en bestaat uit **onbevestigde potentiële links**. Deze gegevens worden niet automatisch aan de masterlijst toegevoegd. Eerst moeten datum, act, zaal, ticketprijs en officiële eventpagina worden gecontroleerd.

Meer informatie: [Concertupdates en beperkingen](docs/CONCERT_UPDATES.md).

## Nieuw: concertkaart en automatische ontdekkingen

- **Kaart**: Open het tabblad `Kaart`. Filter op 7, 30 of 90 dagen, 12 maanden of alle toekomstige concerten. De markers tonen per plaats de concertdatums en officiële concertlinks. Vanuit de popup kun je het zaaladres opzoeken.
- **Nauwkeurigheid**: Markeringen tonen bewust het **plaatscentrum**, niet een onbevestigd exact zaaladres. De kaart gebruikt Leaflet en OpenStreetMap via internet; de concertlijst zelf blijft ook zonder kaart zichtbaar.
- **Nieuw gevonden**: Het tabblad toont automatisch geëxtraheerde mogelijke concerten uit `data/new-discoveries.json`. Deze zijn **onbevestigd** en staan niet in de officiële masterlijst. De tab geeft geen kwaliteits- of waardescore en claimt geen live beschikbaarheid.
- **Dagelijkse workflow**: Na `extract_event_details.py` bouwt de workflow via `build_discoveries.py` de ontdekkingenfeed. Duplicaten op naam/datum en bekende officiële eventlinks worden uitgefilterd; overbodige cabaret- en tributevormen worden zo veel mogelijk geweerd. Niet alle bronpagina's bieden bruikbare gegevens. De controle vindt geen gegarandeerde 12-maandsdekking.
- **Bronnen**: OpenStreetMap-tegels en Leaflet worden gratis geladen vanaf openbare providers. Deze providers ontvangen je IP-adres bij het tonen van de kaart.

## Persoonlijke concertkeuzes

In iedere concertkaart staan nu **Interessant**, **Afwijzen** en **Kaarten gekocht**. Er kan één status tegelijk actief zijn. Opnieuw aanklikken wist die keuze. De tabbladen **Interessant**, **Kaarten gekocht** en **Afgewezen** tonen de bijbehorende concerten. Afgewezen concerten verdwijnen uit de gewone lijst en kaart, maar blijven herstelbaar in het tabblad Afgewezen. De eerdere favorieten en boekingen worden als bestaande keuze gelezen.

Ook in **Nieuw gevonden** kun je een kandidaat markeren, zonder dat deze automatisch als geverifieerd concert wordt gepubliceerd.

**Let op:** keuzes worden uitsluitend in de huidige browser opgeslagen. Ze synchroniseren **niet** automatisch tussen Android en Windows. Gebruik JSON-export/import als reservekopie en om keuzes over te zetten.

De **Kaart** gebruikt plaatscentra als benaderende positie. Klik voor het echte adres via de zoeklink in de popup. Kaartmateriaal vereist internet.

## Mijn concertplanner

- Tab **Concert toevoegen**: voeg ook een optreden toe dat nog niet in de centrale lijst voorkomt.
- Verplichte velden: artiest, datum, podium en plaats. Optioneel: aanvangstijd, genre, prijs, officiële link en eigen notitie.
- Kies meteen **Kaarten gekocht**, **Interessant**, **Afgewezen** of geen keuze.
- Eigen concerten zijn te wijzigen en te verwijderen. Bij wijzigen blijft de unieke ID behouden, zodat status en eerder opgeslagen gegevens niet verdwijnen.
- Zelf toegevoegde concerten verschijnen in de gewone masterlijst, in de statusfilters en bij een bekende plaats ook in de kaartweergave. Een niet-herkende plaats wordt niet met een verzonnen marker aangegeven.
- Tab **Mijn kalender**: maandweergave van alle concerten met status Interessant of Kaarten gekocht. De knop **Download mijn concertagenda (.ics)** exporteert deze concerten als dagafspraken, zonder verzonnen begintijden.
- De kalender is bewust **niet live gekoppeld aan Google of Outlook**. Een .ics-export maakt een kopie; latere wijzigingen worden niet automatisch gesynchroniseerd.
- Eigen concerten, notities en keuzes zijn **privé in de lokale browseropslag**. Windows en Android synchroniseren nog niet. Maak geregeld een JSON-export in **Updates & beheer** en importeer die desgewenst op een ander apparaat.
- De eerdere handmatige invoer wordt herkend op ID's met `handmatig-`. Deze kan in het nieuwe tabblad worden bewerkt.

### Concertgegevens opzoeken bij zelf toevoegen
Gebruik **Zoek gegevens in ConcertRadar**. De app zoekt overeenkomsten op artiest en eventueel datum in de masterlijst en ontdekkingenfeed. Met **Overnemen** vul je de beschikbare velden in. Dit is geen live verificatie: bestaande concertgegevens en ontdekkingen kunnen onvolledig of verouderd zijn. Met **Zoek op internet** opent een gerichte webzoekopdracht; de gebruiker vult of controleert de resultaten zelf. De app leest vanwege CORS- en privacybeperkingen niet zelfstandig willekeurige concertwebsites of persoonlijke ticketmail.

## Live concertgegevens automatisch opzoeken (november 2026)

Onder **Concert toevoegen** staat **Zoek concert automatisch**. Met minstens drie letters van de artiestnaam raadpleegt de browser:
1. de lokale ConcertRadar-masterlijst en het overzicht met kandidaten;
2. de openbare [Gigora concert-API](https://gigora.live/developers);
3. de openbare [StungEvents zoek-API](https://docs.stungevents.com/debug/default/index).

De browser stuurt de ingevulde artiestnaam (en, waar ondersteund, datum/plaats) naar de externe dienst. De diensten vereisen volgens hun documentatie geen API-sleutel en bieden CORS. De gevonden shows worden alleen als **mogelijke overeenkomsten** getoond met bronvermelding. De gebruiker selecteert een resultaat met **Overnemen**; daarna worden datum, eventuele aanvang, podium, plaats, prijs en een concert/ticketlink in het formulier ingevuld voor zover de bron die aanbiedt. Onbekende velden worden niet verzonnen.

**Beperkingen**: een zoekdienst heeft niet alle kleine podia, kan offline zijn en kan onjuiste of oude informatie leveren. Bij geen resultaten is de knop **Zoek via Google** beschikbaar. De app kan Google-zoekresultaten niet automatisch uitlezen zonder een aparte zoek-API. Controleer de officiële podiumsite vóór opslaan. De live aanvragen zijn alleen getest met voorbeeld-API-antwoorden; bereikbaarheid vanuit de gebruikersbrowser is nog niet bevestigd. Persoonlijke concerten worden nog steeds alleen lokaal opgeslagen.
