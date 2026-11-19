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
