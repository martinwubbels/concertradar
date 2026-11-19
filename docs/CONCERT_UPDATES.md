# ConcertRadar: bronnen en veilige dagelijkse controle

## Wat is geautomatiseerd?
GitHub Actions leest iedere ochtend links van een selectie officiële regionale agenda's en schrijft deze naar `data/discovery-candidates.json`. Dit zijn **mogelijke links**, niet automatisch gecontroleerde concerten.

De dagelijkse fotocontrole werkt apart. De website toont echte concerten uitsluitend vanuit `data/concerts.json`, aangevuld met de ingebouwde fallback. Daardoor veroorzaakt een verkeerd geparste bronlink geen vals concert.

## Beperkingen
- Niet iedere website is bereikbaar voor automatische verzoeken.
- Agenda's met JavaScript, paginering of afwijkende URL-structuren worden niet volledig uitgelezen.
- Het script beoordeelt geen evenementdatum, act, kwaliteit, prijs, ticketvoorraad, annulering of festival-line-up.
- De achttien geconfigureerde bronnen zijn **geen volledige 12-maandsaudit** van alle gewenste podia. Festivals en internationale toppers moeten apart worden onderzocht.
- De 87 nieuw opgenomen historische vermeldingen hebben `verification: historical_unverified`: ze zijn afkomstig uit eerdere chats en zijn niet opnieuw bij hun officiële podium bevestigd.
- De dagelijkse ChatGPT-automatisering kan de GitHub JSON niet direct bijwerken. De dagelijkse GitHub-taak is dus geen vervanging van inhoudelijk concertonderzoek.

## Hoe voeg je een gecontroleerd concert toe?
Controleer de officiële concertpagina. Vul of actualiseer `data/concerts.json`, met dezelfde bestaande `id` voor dezelfde show. Verwijder oude toekomstige evenementen nooit alleen omdat een website vandaag niet antwoordt. Een show verdwijnt pas na de speeldatum, bij bevestigde annulering of na bewuste afwijzing.

## GitHub
Handmatig starten: **Actions → ConcertRadar dagelijkse agenda-controle → Run workflow**.
De uitkomsten verschijnen in `data/discovery-candidates.json`. Een lege kandidatenlijst kan ook betekenen dat de bron niets heeft prijsgegeven.

De foto's worden dagelijks afzonderlijk gecontroleerd door **ConcertRadar fotocontrole**.
