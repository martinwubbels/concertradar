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

## Concert overnemen via gekopieerde link

Onder **Concert toevoegen** staat bovenaan **Link naar officiële concertpagina** met de knop **Haal gegevens op uit link**. De app controleert eerst of de URL al exact in ConcertRadar voorkomt. Anders stuurt de publieke URL via HTTPS naar de gratis [Microlink Metadata API](https://microlink.io/metadata), die op de doelpagina gestructureerde JSON-LD/schema.org-gegevens probeert te lezen.

Als de pagina een `Event` of `MusicEvent` bevat met datum, neemt de gebruiker de gevonden gegevens via **Overnemen** over: evenementnaam, datum, aanvang, zaal, plaats en eventueel prijs in EUR. De input wordt **niet** automatisch opgeslagen of gepubliceerd. Als alleen de paginatitel beschikbaar is, wordt uitsluitend die getoond; er worden geen ontbrekende tijden, zalen of prijzen gegokt. Controleer ieder veld vóór opslaan.

**Privacy en beperkingen:** voer alleen een **publieke** evenementenlink in, nooit een persoonlijke boekingsbevestiging of link met toegangscode. Microlink ontvangt de link en kent voor gratis gebruik beperkingen (momenteel circa 25 verzoeken per dag zonder sleutel). Sommige podia blokkeren metadataextractie. Google-zoekresultaten worden niet automatisch uitgelezen; de afzonderlijke zoekfunctie blijft beschikbaar. De externe link en alle eigen concertgegevens blijven vervolgens in de browser opgeslagen. De functie is met gesimuleerde schema.org-gegevens gevalideerd, maar nog niet end-to-end vanaf de gebruikersbrowser getest.

## Concertimport: Metropool met volledige gegevens

De gebruiker meldde dat bij `https://metropool.nl/agenda/steve-n-seagulls` alleen de paginatitel werd gevonden. Metropool toont de datum, locatie, voorverkoopprijs en aanvang in zichtbare tekst die niet altijd als JSON-LD in Microlink beschikbaar is.

De import probeert nu daarnaast `main` en `body` als tekst te lezen via Microlink en heeft een gerichte parser voor Metropool met onderscheid tussen **zaal open**, **voorprogramma** en **aanvang hoofdact**. Het jaar wordt uit een korte datum alleen afgeleid wanneer nodig; de app waarschuwt dan dat het jaartal gecontroleerd moet worden. Bij verschillende prijzen wordt voorverkoop gebruikt.

Een beperkte openbare broncache `data/link-imports.json` bevat reeds afzonderlijk gecontroleerde eventgegevens om deze URL direct betrouwbaar te kunnen invullen. Voor Steve 'n' Seagulls: 3 december 2026, Bud Stage Hengelo, hoofdact 21:30, voorverkoop €28, PK Keränen als support, volgens de op 19 november 2026 geraadpleegde officiële Metropoolpagina. Bij elke wijziging op de bron moet deze cache apart geactualiseerd worden; het is geen live prijs- of aanvanggarantie.

Andere sites zijn afhankelijk van beschikbare openbare metadata en pagina-inhoud. De live werking van de uitgebreidere Microlink-selectors is nog niet in een gebruikersbrowser geverifieerd.

## ConcertRadar uitbreiding november 2026

### Mijn komende concerten
Het nieuwe starttabblad toont alle toekomstige concerten met status **Kaarten gekocht**. Per concert staan datum, aanvang indien bekend, podium, plaats, eigen notitie en een route-link.

### Beoordelingsinbox
Het tabblad **Beoordelingsinbox** toont nieuwe kandidaatconcerten waarvoor je nog geen keuze hebt gemaakt. Met Interessant, Afwijzen of Kaarten gekocht verdwijnt het concert uit de inbox. Deze suggesties zijn niet automatisch bevestigd; de bronlink blijft beschikbaar.

### Concertgeschiedenis
Na de speeldatum kun je voor geboekte of eerder beoordeelde concerten scores geven van 1 t/m 10 voor stem en zang, songteksten, livekwaliteit en totale ervaring, plus een privénotitie. Gegevens worden lokaal opgeslagen en kunnen worden opgenomen in de optionele privésynchronisatie.

### Kaart, exacte locaties en reistijden
`data/venue-locations.json` bevat een kleine set **gecontroleerde podiumadressen** en alleen waar brongegevens beschikbaar waren, coördinaten. Op die posities staan de kaartmarkers bij de zaal; overige concerten blijven met een grijze marker bij het **plaatscentrum**. Gecontroleerde locaties: De Oosterpoort (Groningen), Hedon (Zwolle), Metropool (Hengelo). Andere adressen zonder gecontroleerde coördinaten worden alleen als adres gebruikt voor een routezoekopdracht.

De routeknop biedt Google Maps voor actuele reistijden. Bij een gecontroleerde marker kan **Bereken rijafstand** een route-inschatting opvragen bij de openbare OSRM-demo vanaf **Klazienaveen (centrum)**. Deze demo biedt geen actuele fileinformatie, kan onbereikbaar zijn en is uitsluitend geschikt voor kleinschalig niet-commercieel gebruik. Het sturen van de routeaanvraag deelt de coördinaten en het IP-adres met de provider; er gebeurt geen massale automatische routering.

### Veranderingen bij bestaande concerten
Een aparte dagelijkse GitHub Actions-workflow `ConcertRadar controle van bekende concerten` leest maximaal 65 officiële publieke concertpagina's per run en zoekt naar sterke aanwijzingen voor veranderde datum, plaats, prijs en uitverkochte status. De uitkomsten komen in `data/changes.json` als **onbevestigde wijzigingsvoorstellen**. De catalogus wordt niet automatisch aangepast. Bij veel concerten (vooral homepage-links en dynamische sites) is controle niet mogelijk; geen melding is dus **geen garantie** dat gegevens ongewijzigd zijn. Deze workflow is nog niet in GitHub Actions uitgevoerd.

### Synchronisatie
De app bevat optionele Supabase-cloudsync. Die is nog **niet ingeschakeld**. Voor echte synchronisatie tussen Windows en Android moet de eigenaar éénmaal een privédatabase inrichten; zie [de instructies](docs/SYNCHRONISATIE.md). `data/cloud-config.json` staat standaard uit. Zonder configuratie blijven alle persoonlijke gegevens lokaal. Gegevens worden niet gepubliceerd op GitHub.

### Back-up
De JSON-export onder Updates & beheer bevat nu naast de concerten ook de volledige lijst met persoonlijke aanvullingen, concertstatussen, beoordelingen en instellingen. Voor terugzetten wordt het persoonlijke extra-overzicht overgenomen; oudere exports met `events` blijven geaccepteerd.

## Concertstatussen en persoonlijke muzieksmaak (november 2026)

**Kleuren en labels**: Kaarten gekocht is goud met een dikke rand, banner en aparte knopkleur. Interessant is blauw. Afgewezen is grijs. Deze statussen zijn herkenbaar in masterlijst, dashboard, kaart en kalender. Op de kaart geeft goud aan dat op die locatie minstens één geboekt concert staat. De popup toont welk optreden het betreft. Tekstlabels blijven altijd zichtbaar.

**Mijn muzieksmaak**: het nieuwe tabblad beschrijft de persoonlijke score. De bestaande redactionele kwaliteitsscores worden niet overschreven. Er komt een aparte Mijn smaak-score (1 tot 10), afgeleid van genres van interessante, geboekte en achteraf beoordeelde concerten. Een review telt sterker dan een boeking. Bij reviews wegen stem en zang en songteksten elk 32%, livekwaliteit 13% en totaalbeleving 23%.

De handmatig ingestelde startvoorkeur gaat uit naar Americana, country, roots, folk, soul en blues. Interessant en Kaarten gekocht zijn beperkt positieve signalen. Een afwijzing telt niet negatief: reistijd, geld of een agendaconflict kunnen de reden zijn. Lagere reviews kunnen de genrescore wel afzwakken. Een sorteeroptie toont de persoonlijke match. Ook nieuwe kandidaten krijgen een inschatting.

De score wordt lokaal opnieuw berekend bij iedere keuze en beoordeling. Het is een transparante vuistregel op basis van genre en bestaande smaakmatches, geen Spotify- of audiomodel. Het systeem leest geen songteksten en weet niet waarom je iets afwijst. Bij weinig gegevens is de schatting onzeker. Cloudsync, indien geactiveerd, synchroniseert persoonlijke keuzes en beoordelingen en niet het berekende resultaat.

## Concertlinks corrigeren (19 november 2026)

Bij een audit van de 110 concerten bleken 98 links een algemene website of programma-ingang te zijn. Er zijn 26 links vervangen door specifieke pagina's uit de officiële podiumagenda's, met een passende artiest en datum. De overige 72 algemene links zijn gemarkeerd als `venue_or_generic`.

De website mag een algemene theaterhomepage niet tonen als officiële concertpagina. In plaats daarvan biedt hij **Zoek optreden** aan: een gerichte Google-zoekopdracht met het oorspronkelijke podiumdomein, artiest, datum en plaats. Dit is geen bevestigde ticketlink. Bij het concert staat het label **Geen directe concertlink**.

De 12 reeds specifieke links zijn voorlopig gemarkeerd als `event_page_unverified` en krijgen de tekst **Concertlink (controleren)** totdat ook hun inhoud en exacte optreden onafhankelijk zijn gecontroleerd.

De dagelijkse agendaworkflow bouwt ook `data/link-review.json`. Dit zijn alleen voorstellen waarbij een artiest, datum en hetzelfde officiële domein overeenkomen. Het script past `data/concerts.json` bewust niet automatisch aan. Handmatige controle van de betreffende pagina is nodig.

Als op een apparaat eerder een concertfoto handmatig is ingesteld, blijven die instellingen bewaard, maar neemt de actuele centrale catalogus voor datzelfde concert de voorrang bij de officiële URL. Dit voorkomt terugkeer van oude algemene links via lokale opslag.

## Dagelijkse automatische toevoegingen aan de masterlijst

De bestaande workflow **ConcertRadar gegevens uit kandidaten** voert na de extractie `scripts/promote_verified_concerts.py` uit, test deze eerst en bouwt vervolgens opnieuw het onbevestigde ontdekkingenoverzicht.

Een nieuw optreden wordt uitsluitend automatisch opgenomen wanneer: de bron een toegestane officiële concertpagina is (niet een homepage), de gestructureerde schema-URL exact bij die pagina hoort, datum/naam/zaal/plaats aanwezig zijn, de titel herkenbaar aansluit op de URL en de bron de show uitdrukkelijk als `MusicEvent` classificeert. **Uitzondering:** het muziekspecialistische podium Metropool gebruikt voor concerten `TheaterEvent`, daarom zijn die daar toegelaten. TheaterEvent van gemengde theaters of een algemeen `Event` wordt niet automatisch toegelaten. Expliciete cabaret-, film-, tribute- en andere niet-passende aanduidingen zijn uitgesloten.

De tool controleert bestaande URL's, naam, datum en plaats op dubbelen. Een al bestaand concert wordt nooit door de automatische promotie overschreven. De nieuwe ID volgt het eerder gebruikte `suggestion-YYYY-MM-DD-artiest` formaat zodat bestaande interesse/afwijzingsstatussen van dezelfde vondst behouden blijven. Bij ID-conflict wordt het concert juist niet toegevoegd.

Toegevoegde concerten krijgen **geen verzonnen kwaliteitsscore**: `quality` en `value` blijven null, `genre` wordt 'Muziek / nog niet ingedeeld'. Een eventueel bedrag is een bronvermelding in EUR en **geen live prijscontrole**. De melding `UITVERKOCHT` wordt alleen uit expliciete bronmetadata afgeleid en moet bij het podium worden gecontroleerd. Nieuwe items krijgen `verification: auto_verified_schema` en een broncontroledatum.

De workflow slaat elke dag een audit op in `data/promotion-report.json` met aantal toegevoegde en geweigerde kandidaten en redenen. Twijfelgevallen blijven in `data/new-discoveries.json` of `data/event-review.json`. De masterlijst wordt alleen gewijzigd wanneer er daadwerkelijk nieuwe, voldoende zekere shows gevonden zijn. Een dag zonder toevoegingen is normaal.

De extractie onderzoekt maximaal 100 kandidaatpagina's per run en bereikt niet alle podia, en de pagina's kunnen metadata ontbreken of de bot blokkeren. Daarom is dit geen complete regionale concertagenda. De eerste geplande automatische run moet na publicatie nog plaatsvinden. De automatische codecontrole voert ook de promotietests uit.

## Bewerkbare smaakwoordwolk (november 2026)

Het tabblad **Mijn muzieksmaak** heeft een interactieve woordwolk. Zelf ingevoerde artiesten, muziekstijlen of kenmerken krijgen een gewicht: **heel graag (+2)**, **graag (+1)**, **liever niet (-1)** of **absoluut niet (-2)**. Woorden worden groter bij een sterker gewicht. Groen staat voor positief, oranje voor negatief. Klik op een woord om het gewicht aan te passen of het woord te verwijderen. Gebruik het formulier om zelf woorden toe te voegen; voorgestelde woorden zijn optioneel en worden niet automatisch opgeslagen. Maximaal 60 woorden.

De woordwolk beïnvloedt rechtstreeks de persoonlijke muzieksmaakscore. De bestaande redactionele score, concertgegevens en persoonlijke beoordelingen veranderen niet. De impact van alle handmatig gekozen woorden samen is begrensd om onrealistische scores te voorkomen.

**Cruciaal:** de berekening zoekt letterlijke overeenkomsten in bestaande concertmetadata: artiestnaam en smaakmatch voor artiesten, genre voor muziekstijlen, omschrijving en genre voor kenmerken. Een woord als 'sterke songteksten' heeft pas invloed als het in de omschrijving staat. Dit is geen audio-, lyrics- of Spotify-analyse. Andere onbekende optredens worden niet automatisch van muziekstijl voorzien.

Woorden worden bewaard in de bestaande persoonlijke instellingen en meegenomen in de JSON-back-up. Bij ingeschakelde Supabase-sync worden woordwolkgegevens op basis van de wijzigingstijd samengevoegd; als je tegelijk op twee apparaten wijzigt, wint de laatst bewaarde volledige woordwolk. Maak voor de eerste synchronisatie een JSON-export.

## Vooringevulde muzieksmaak (november 2026)

De interactieve woordwolk wordt eenmalig aangevuld met 24 bekende voorkeuren uit eerdere concertbesprekingen. Uitgesproken favorieten Willow Avalon en Henry Wagons krijgen gewicht +2. Overige als positief beoordeelde bands en geïnteresseerde acts krijgen +1. Voorkeur voor americana, country, roots, bluegrass, folk, soul, blues en alternatieve rock, sterke teksten en onderscheidende stem. Er zijn geen negatieve voorkeuren ingevuld zonder expliciete afkeer.

**Bestaande keuzes worden niet overschreven**: per term en soort krijgt het eerder opgeslagen gewicht altijd voorrang. De versie-indicator `tasteSeedVersion: 1` verhindert dat een bewust verwijderd woord bij iedere herstart automatisch terugkeert. De eigen woorden staan in `settings.tasteWords` binnen de bestaande lokale opslag en worden via de optionele privésync opgeslagen. Bij een eerdere configuratie met 60 termen worden geen extra woorden opgedrongen.

Ook voor deze woorden geldt: ze beïnvloeden de persoonlijke smaakscore alleen als beschikbare artiest-, genre- of beschrijvingsgegevens overeenkomen. De artiesten zijn gewichten voor aanbevelingen, niet automatisch een aankondiging van een toekomstig optreden.
