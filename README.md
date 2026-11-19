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
