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

## De zes smaakfuncties (november 2026)

1. **Muziek-DNA:** vijf schuiven (stem, teksten, eigenheid, instrumenten, live-uitstraling, van 0 tot 5), instelbaar onder Mijn muzieksmaak. Alleen in de concerttekst aanwezige kenmerken dragen bij. Het zijn geen echte stem- of songtekstanalyses.
2. **Luistertest:** iedere masterlijstkaart heeft een knop Luistertest. Deze opent Spotify-zoekresultaten voor de artiest. Luister zelf naar drie nummers en kies Geweldig, Interessant of Niets voor mij. De app kan de gespeelde nummers niet verifiëren; de beoordeling is jouw eigen signaal. Het oordeel staat los van concertbezoek.
3. **Afwijsreden:** bij Afwijzen kies je via een invoervenster een reden: muziek, afstand, prijs, datum, gezien of anders. Alleen muziek telt als negatief signaal voor de muzikale voorkeur; overige redenen niet. Bestaande afwijzingen zonder reden blijven neutraal.
4. **Verrassingsradar:** een aparte tab met nog niet als bekend gemarkeerde artiesten met voldoende persoonlijke overeenkomst. Bekende favoriete, geboekte en afgewezen concerten worden uitgesloten.
5. **Concerturgentie:** een apart overzicht met persoonlijke match en hoe dichtbij de concertdatum is. Als een concert geen directe optredenlink heeft of uitverkocht lijkt, staat dit duidelijk vermeld. Geen aannames over zaalcapaciteit, exclusiviteit of live ticketvoorraad; deze ontbrekende factoren worden expliciet genoemd. Dit is geen gegarandeerde beschikbaarheidscontrole.
6. **Smaakontwikkeling:** een tab met de werkelijk opgeslagen concertreviews, chronologisch getoond, en gemiddelde cijfers voor stem, teksten, livekwaliteit en totale beleving. Geen verzonnen historische scores.

De vijf DNA-waarden en de luisteroordelen worden in de bestaande persoonlijke instellingen bewaard en bij ingeschakelde privécloud gesynchroniseerd. De relevante wijzigingstijd bepaalt welke volledige set bij een conflict tussen apparaten voorgaat. Bestaande concerten, woordwolk en reviews blijven ongewijzigd. Nieuwe smaakberekeningen zijn heuristieken op beschikbare metadata en gekozen voorkeuren.

## Unieke rollen voor masterlijst en ontdekkingen (november 2026)

De vroegere tab **Smaakmatches** was slechts een filter op dezelfde masterlijst en is daarom verwijderd. De masterlijst blijft de volledige, doorzoekbare bron, met de bestaande sortering op persoonlijke smaakscore. De Verrassingsradar is nu een compacte, maximaal 8 artiesten tellende selectie van nog niet eerder beoordeelde of geboekte acts. Deze selectie vereist een specifieke concertlink, bruikbare muziekmetadata, een persoonlijke score van ten minste 7,6 en minstens één verklaarbaar positief signaal uit handmatige voorkeuren, muziek-DNA, eerder gewaardeerd genre of een expliciete artiestreferentie. De reden staat boven iedere suggestie.

Historisch niet herbevestigde meldingen en automatisch gevonden titels zonder genre worden niet als sterke verrassingssuggestie gepresenteerd. Onzekere vondsten blijven bereikbaar via Beoordelingsinbox en Nieuw gevonden. De Verrassingsradar is een op criteria gefilterde deelverzameling van de masterlijst, geen zelfstandige ontdekkingsbron. Er zijn geen concerten verwijderd en geen bestaande keuzes of beoordelingen gewijzigd.

## Betrouwbaarheid en persoonlijke concertworkflow (19 november 2026)

De bestaande app is uitgebreid, zonder de 110 centrale concerten, statussen, reviews en woordwolk te vervangen.

**1. Brongegevens controleren.** De bestaande dagelijkse GitHub Action controleert maximaal 35 toekomstige officiële concertpagina's extra en schrijft resultaten naar `data/source-checks.json`. Alleen gestructureerde evenementgegevens met een passende naam en bronpagina mogen een wijzigingssignaal geven. Een daadwerkelijke annulering verschijnt alleen bij expliciet `EventCancelled`. Een ontbrekende pagina of ontbrekende metadata wordt als `unavailable` gemarkeerd, nooit als annulering. De masterlijst wordt door deze controle niet automatisch gewijzigd. Op de concertkaart staat de laatst bekende bronstatus of dat opnieuw controleren niet lukte. Deze controle kan niet garanderen dat ieder optreden dagelijks is herbevestigd.

**2. Artiestprofielen.** Iedere concertkaart krijgt een knop Artiestprofiel. Het profiel combineert bestaande genres en podiumomschrijvingen, maar vermeldt de herkomst en wat niet bekend is. De handmatig op openbare bronnen gecontroleerde profielen voor Willow Avalon, Henry Wagons en Muireann Bradley staan in `data/artist-profiles.json`, inclusief bronverwijzingen. Dat bestand is publiek, maar bevat geen persoonlijke data. Overige artiesten tonen een beknopt profiel op basis van bekende concertmetadata. Geen verzonnen invloeden of songtekstanalyse.

**3. Startscherm.** Het bestaande tabblad met de komende geboekte concerten heet nu Mijn startscherm. Daarboven staan het eerstvolgende geboekte concert, drie nog niet gekozen muziekmatches, nieuwe signalen en agenda-overlap. Het oorspronkelijke overzicht van geboekte concerten blijft volledig intact.

**4. Slimme meldingen.** Geen pushberichten en geen tweede ChatGPT-automatisering. In-app signalen betreffen nieuw automatisch geverifieerde shows vanaf een eerste lokale referentielijst, met een hoge persoonlijke smaakscore of een handmatig gevolgde artiest. Relevante bronwijzigingen bij geboekte shows komen ook in beeld. Bij eerste gebruik worden de bestaande shows als reeds bekend geregistreerd om historische spam te voorkomen. Gelezen signalen blijven via de persoonlijke instellingen opgeslagen, met een begrensde sleutelset om dubbelen te beperken. De meldingen verschijnen wanneer de app wordt geopend en de centrale data beschikbaar is.

**5. Reisgrenzen.** Onder Reisgrenzen stel je normale en uitzonderlijke afstanden in, standaard 90 en 200 km, vanaf het al ingestelde vertrekpunt Klazienaveen (centrum). Afstanden zijn hemelsbreed vanaf een zaalcoördinaat of, als dat ontbreekt, een plaatscentrum. Onbekende coördinaten worden niet gefilterd. Het filter is aanvankelijk uitgeschakeld; pas na aanzetten beïnvloedt het nieuwe, nog niet gekozen masterlijstoptredens. Gekochte kaarten en eerder interessant gemarkeerde concerten blijven zichtbaar. Er wordt geen nauwkeurige rijtijd geclaimd.

**6. Agenda en conflicten.** Het startscherm kan een handmatig ingevoerde bezette datum of een via `.ics` geïmporteerde kalenderdatum vergelijken met gekochte concerten, inclusief meerdere boekingen op dezelfde datum. Alleen datums worden opgeslagen, niet de titels, namen of details van andere afspraken. Dit gebeurt afzonderlijk in de lokale browseropslag, niet in GitHub, niet in de Supabase-gegevens en niet in een online agenda. De bestaande ConcertRadar-ICS-export blijft beschikbaar. Deze eerste conflictcontrole is op datumniveau en geen realtime Google Calendar-koppeling.

**Privacy en herstel.** Persoonlijke reisgrenzen en de gelezen meldingen vallen onder de bestaande instellingen en desgewenst onder Supabase-sync. Geïmporteerde privéagenda-data blijft uitsluitend op dat apparaat. De bestaande JSON-export van ConcertRadar bewaart instellingen en reviews, maar niet de lokaal geïmporteerde agenda-datums. Alle bestaande bronbestanden en event-IDs blijven in stand.

## ConcertRadar v2: datakwaliteit, mobiele bediening en luisterprofiel (19 november 2026)

**Concertcontrole.** De bestaande dagelijkse GitHub-workflow controleert tot 50 toekomstige specifieke officiële concertpagina's per run. De selectie roteert op de oudste controledatum in plaats van steeds dezelfde eerste 35 shows. In `data/source-checks.json` blijven zowel de laatste controlepoging als de laatste daadwerkelijk bevestigde datum staan. Ontbrekende metadata of onbereikbaarheid betekent nooit annulering. Expliciete datumwijzigingen en annuleringen in passende gestructureerde broninformatie leveren signalen op. Bestaande catalogusrecords worden niet automatisch aangepast. Bij ieder optreden toont de app een bronstatus en een instelbare grens van 7, 14 (standaard) of 30 dagen. “Check nu bij podium” opent de eigen concertpagina of een gerichte zoekopdracht. Prijzen hebben de aanduiding **Bronprijs (niet live)**, en een vermoeden van uitverkocht wordt nooit als bevestigde actuele ticketvoorraad beschouwd.

**Smaakscore.** De details zijn bij de concertkaart open te klappen. Startpunt, redactionele schatting, genrevoorkeuren, eerdere keuzes, woordwolk, muziek-DNA, luistertest/afwijzing en luistergeschiedenis worden als afzonderlijke bijdragen getoond. Dit is een uitlegbare heuristiek op bestaande metadata, geen audioanalyse.

**Mobiel en compact.** Onder 780 px vervangt een selectiemenu de lange tabnavigatie. De masterlijst heeft een compacte kaartstand die je kunt uitzetten. De bestaande live zoekfunctie en statusknoppen blijven bruikbaar. Er worden geen nieuwe persoonlijke concert-ID's aangemaakt en de oude lokale sleutel `concertradar-v1` is behouden.

**Agenda.** Bij masterlijstconcerten en geboekte concerten staan rechtstreekse Google Calendar- en Outlook-links. Zolang de starttijd niet officieel bevestigd is, wordt een hele-dagafspraak klaargezet. Gebruikers controleren de afspraak zelf voordat zij die opslaan. De bestaande ICS-export en agenda-import blijven bestaan.

**Luistergeschiedenis.** Onder Mijn muzieksmaak is een optionele koppeling met Last.fm via de *eigen* API-sleutel van de gebruiker. Er wordt alleen de lijst met topartiesten van de laatste drie maanden opgevraagd. De sleutel blijft in een aparte lokale browseropslag en gaat niet mee in de JSON-export of optionele cloudsynchronisatie. Spotify kan worden verwerkt via handmatig geïmporteerde JSON-bestanden met standaard of uitgebreide streaminggeschiedenis. Er is **geen directe Spotify-OAuth-koppeling** en er worden geen credentials of persoonlijke luisterdata in de publieke GitHub-repository opgenomen. De afgeleide artiesttellingen staan in de bestaande privéinstellingen. Luistergedrag kan per herkende artiest maximaal +0,65 punt bijdragen aan de persoonlijke smaakscore. De gebruiker kan de gegevens verwijderen. Spotify-export en Last.fm zijn optioneel; alle andere functies blijven zonder koppeling werken.

**Grenzen.** De broncontrole beslaat niet alle officiële concertpagina's iedere dag. Last.fm kan API-toegang vanuit een browser blokkeren. Een Spotify-export is niet automatisch actueel. Er is geen realtime Google Calendar- of Outlook-synchronisatie, alleen handmatige toevoegen-links. Geen externe ticketprijzen of beschikbaarheid worden als live bevestigd zonder specifieke bron.

## Concerten direct zoeken (november 2026)

Boven de overzichten staan twee gescheiden acties. **Zoek nu** start meteen een externe Google-zoekopdracht met het ingevulde genre of de artiest, gericht op bestaande officiële podia en het huidige/volgende jaar. De uitkomsten zijn niet geverifieerd en verschijnen niet automatisch in de masterlijst. Je kunt een gevonden concert daarna controleren of handmatig toevoegen.

**Volledige podiumscan via GitHub** opent de workflow `.github/workflows/search-now.yml`. Deze workflow bestaat uit ontdekking, linkcontrole, extractie, automatische promotie volgens de bestaande strenge criteria, bronverificatie en opbouw van de nieuwe ontdekkingenfeed. Je moet bij GitHub ingelogd zijn en op **Run workflow** klikken om hem te starten. Een publieke GitHub Pages-site kan een beveiligde GitHub Action niet zonder gebruikersautorisatie dispatchen. Er zijn geen tokens, wachtwoorden of webhookgeheimen toegevoegd. Gebruik daarna **Gegevens verversen** om gepubliceerde data opnieuw te laden. De uitkomst hangt af van GitHub Actions, de toegankelijkheid van podiumsites en de bestaande toelatingsregels. Bestaande persoonlijke data blijft intact.

## Concertkaarten v3: compacte interface (november 2026)

De masterlijst, Verrassingsradar, Interessant, Kaarten gekocht en Afgewezen gebruiken nu één uniforme concertkaart. De standaard compacte versie toont naast de datum de artiestenfoto, artiestnaam, podium, plaats en persoonlijke score. Onder deze gegevens staan uitsluitend de drie primaire statusacties: **Interessant**, **Kaarten gekocht** en **Afwijzen**. Statuswijzigingen blijven via de bestaande `data-action`-handlers in het privéprofiel opgeslagen. Een tweede klik maakt de keuze ongedaan, zoals voorheen.

De **Details**-sectie is standaard dicht. Via openklappen blijven de songbeschrijving, vergelijkbare artiesten, broncontrole, prijs, reisafstand, urgentie en de bestaande persoonlijke score-uitleg beschikbaar. Ook de functies Artiestprofiel, Luistertest, Spotify, concertlink, Google Agenda, Outlook en Foto wijzigen zijn behouden. Details hoeven geen nieuwe pagina te openen. Foto's blijven ook in de compacte stand zichtbaar.

Bij smalle schermen worden datum, foto en artiestinformatie op de eerste rij getoond. De matchscore volgt eronder en de drie statusknoppen schalen en breken af waar nodig. Bij uitgebreid geopende Details mag het tekstvlak de volledige kaartbreedte gebruiken. De standaardverzameling van concerten en de persoonlijke instellingen zijn niet gewijzigd.

## Nieuwe suggesties op Mijn startscherm (november 2026)

Op het persoonlijke startscherm staat nu, direct na het eerstvolgende geboekte concert, een sectie **Nieuwe suggesties om te shortlisten**. Er staan maximaal zes nog niet beoordeelde toekomstige concerten, met artiest, datum, podium, plaats, indicatieve persoonlijke matchscore, herkomst en een directe knop **+ Interessant**. Afwijzen en de oorspronkelijke concertpagina zijn ook direct beschikbaar.

De selectie kiest eerst concerten met bruikbare genres en directe links, geeft ruimte aan automatisch gevonden podiumconcerten en daarna aan overige nog onbeoordeelde kandidaten. Bestaande keuzes, reviews, afgelaste concerten of duidelijk uitverkochte evenementen worden niet aanbevolen. Dubbele artiesten worden binnen de selectie vermeden. Ook oudere, nog niet herbevestigde concerten kunnen als opvulling verschijnen, maar zijn expliciet gemarkeerd. **Een suggestie is geen claim dat het concert nieuw is aangekondigd of dat er nog kaarten zijn.**

Na **Interessant** verschijnt het concert op de bestaande shortlist. Na **Afwijzen** verdwijnt het uit de suggesties. Dit gebeurt via dezelfde statusknoppen en gegevensopslag als in de masterlijst. Als je een nog niet centraal opgenomen podiumkandidaat beoordeelt, wordt deze uitsluitend in je persoonlijke lijst toegevoegd met de markering **candidate_unverified**, zodat Interessant, Gekocht en Afgewezen blijven werken. De publieke masterlijst wordt daardoor niet gewijzigd.

De sectie heeft knoppen naar Masterlijst, Beoordelingsinbox en Verrassingsradar. Ze gebruikt geen nieuwe automatische taken, externe gebruikersgegevens of aparte opslag.

## Bronstatus en scoreuitleg bij startschermtips (21 november 2026)

Bij de maximaal zes tips onder **Nieuwe suggesties om te shortlisten** zie je nu direct de bronstatus en een uitklapbare uitleg **Waarom X/10?**. Die uitleg gebruikt dezelfde bestaande persoonlijke scoreberekening als de hoofdkaart en toont de afzonderlijke bijdragen. Dit is een inschatting uit beschrijvingen en opgeslagen voorkeuren, geen automatische analyse van stemmen of songteksten.

Kandidaten uit **Nieuw gevonden** zijn expliciet gemarkeerd als **nog niet bevestigd**. Bij bekende catalogusconcerten toont het startscherm de laatst beschikbare broncontrole, inclusief de melding als gegevens niet recent zijn gecontroleerd. De app controleert de ticketvoorraad niet live en doet geen nieuwe netwerkverzoeken voor het tonen van deze uitleg. Bestaande concerten, concert-ID's en persoonlijke keuzes blijven ongewijzigd.

## Nieuw gevonden concerten en festivals (27 november 2026)

Het tabblad **Nieuw & festivals** staat direct na Mijn startscherm, ook op mobiel. Op het startscherm staat een apart blok met een voorproefje van de laatste onbeoordeelde concertvondsten en aankomende festivals. De volledige pagina toont:

- **Nieuwe concertvondsten** uit de automatische kandidatenfeed en automatisch opgenomen masterlijstconcerten. Bronstatus wordt expliciet vermeld. Dit zijn niet per definitie recente aankondigingen van het podium.
- **Aankomende festivals** uit diezelfde feed en reeds bekende festivals uit de masterlijst. Een bestaand festival wordt niet ten onrechte als nieuwe ontdekking beschreven.
- Filters op alles/concerten/festivals, alle keuzes/nog te beoordelen, en sortering op datum van opname of concertdatum.
- Per kaart datum, podium, locatie voor zover bekend, laatste bronprijs indien beschikbaar, bronstatus en de bestaande Interessant, Afwijzen en Kaarten gekocht-acties. Dubbele vermeldingen en verlopen evenementen worden uit deze pagina gefilterd.

De maker van de automatische kandidatenfeed bewaart voortaan `first_seen_at` en `last_seen_at`, en onderscheidt `event_kind=festival` of `concert`. Bestaande kandidaten zonder die datum gebruiken bij de eerstvolgende verwerking als overgangswaarde de eerdere verwerkingsdatum. De datum betekent **opgenomen in de radar**, niet dat het evenement toen is aangekondigd. De eerdere invoer blijft met dezelfde event-ID's behouden. Herhaalde scans maken geen nieuwe melding van een bestaand concert.

De brongegevens zijn geen live ticketcontrole. In de huidige automatische dataset ontbreken sommige steden en podia. Festivalprogramma's worden niet automatisch gecontroleerd. De app claimt daarom geen volledige dekking en laat onbekende gegevens leeg. De bestaande automatische workflows blijven ongewijzigd; er is geen nieuwe geplande taak toegevoegd.

## Afzonderlijke shortlist bij nieuwe concerten en festivals (27 november 2026)

**Shortlist** is nu een aparte persoonlijke status naast **Interessant**, **Afwijzen** en **Kaarten gekocht**. Shortlist betekent alleen: bewaren om later te beoordelen. Interessant blijft een positief muzieksignaal; Shortlist telt niet mee als positieve smaakbeoordeling.

- Op **Nieuw & festivals** staan alle vier de keuzeknoppen bij ieder concert en festival. De keuze wordt op de kaart getoond. Via het filter **Op mijn shortlist** zijn ze terug te vinden.
- Direct op **Mijn startscherm** staan bij nieuwe vondsten de knoppen **Shortlist**, **Interessant** en **Afwijzen**. De aanbevolen muziektips hebben dezelfde opties.
- **Mijn shortlist** is een eigen tabblad op desktop en Android. Geselecteerde kandidaten blijven daarin bestaan als de automatische scan ze later niet meer toont. Datum en bronstatus blijven controlepunten.
- In de **Beoordelingsinbox**, bij **Concert toevoegen** en in het uitklapmenu van de bestaande masterlijstkaarten kun je ook shortlisten.
- Eén status per optreden: veranderen van Shortlist naar Interessant of Afwijzen vervangt de eerdere status. Opnieuw kiezen verwijdert de selectie. Bestaande keuzes, reviews en concert-ID's zijn niet aangepast.
- Alles gebruikt de bestaande persoonlijke opslag, JSON-back-up en optionele synchronisatie. De centrale masterlijst wordt niet gewijzigd door je keuze. Er is geen nieuwe geplande taak aangemaakt.

## Focusnavigatie en dashboard (27 november 2026)

De navigatie heeft vijf direct bereikbare hoofdonderdelen: **Start**, **Nieuw & festivals**, **Mijn shortlist**, **Interessant** en **Kaarten gekocht**. De overige bestaande pagina's zijn niet verwijderd, maar staan gegroepeerd onder **Meer**: Ontdekken, Mijn agenda en Instellingen. Dit werkt op desktop en Android, zonder een tweede lijst van twintig mobiele tabbladen.

Het startscherm bestaat uit vier overzichtsblokken:

1. **Mijn volgende concerten**: de vijf eerstvolgende concerten met status **Kaarten gekocht** of **Shortlist**, met links naar alle boekingen, shortlist en kalender.
2. **Nieuw gevonden concerten en festivals**: een compacte weergave van bestaande kandidaatvondsten, inclusief huidige statuskeuzes en bronvermelding.
3. **Topmatches voor jou**: maximaal drie nog onbeoordeelde concerten met directe bronlink en bruikbare gegevens. De smaakscore blijft een inschatting, geen feitelijke audioanalyse.
4. **Agenda en conflicten**: een samenvatting van bekende drukke datums en eventuele overlap. De bestaande agenda-import en het beheren van bezette datums zijn bereikbaar in een uitklapbaar blok. De vergelijking gebruikt alleen datums, geen tijden.

**Nieuwe signalen** blijven beschikbaar als uitklapbaar vijfde blok. Het grote, dubbele overzicht van geboekte concerten staat voortaan onder **Kaarten gekocht** in plaats van ook volledig op Start. De uitgebreide internetzoekfunctie en de handmatige GitHub-podiumscan staan op **Nieuw & festivals**.

De vier statussen **Shortlist**, **Interessant**, **Afwijzen** en **Kaarten gekocht** zijn op de hoofdkaarten direct zichtbaar. Statuskleuren zijn consistent in de app, maar elke status heeft ook een tekstlabel. Geen concert-ID's, opgeslagen keuzes, bestaande automatische controles of optionele cloudinstellingen zijn gewijzigd. Er zijn geen nieuwe geplande taken ingesteld.

Een centraal goedkeuringsproces van ontdekkingskandidaten is **nog niet** gebouwd. Voor echte opname in de publieke masterlijst blijft gecontroleerde GitHub-verwerking nodig. Automatische e-mailherinneringen en continue cloudsynchronisatie zijn niet toegevoegd: daarvoor is aanvullende configuratie en gebruikersinstemming nodig.

## Brontransparantie en veilige beoordelingswachtrij (27 november 2026)

### Discovery

- Twee extra, bij hun eigen website gecontroleerde officiële agenda's: **Simplon Groningen** (`https://simplon.nl/programma/`) en **Theater Meppen** (`https://www.meppen-theater.de/termine/liste/`). Dit zijn extra bronnen, geen garantie dat hun agenda steeds volledig uitleesbaar is.
- De dagscan verdeelt nieuwe links om-en-om over podia. Bij grote agenda's schuift per scan ook het startpunt voor de eerste 100 links op. Een grote agenda kan de maximaal 600 linkkandidaten niet meer als eerste volzetten. Per bron worden status, laatste poging, laatste geslaagde scan en aantal gevonden links bijgehouden in `data/discovery-candidates.json`.
- Bij metadata-extractie rouleren de beginposities per podium in `data/event-review.json` (`cursor_by_venue`). Daardoor blijven optredens onderaan lange agenda's niet elke dag buiten de scan. Een herordende agenda kan de selectie nog steeds beïnvloeden.
- `data/new-discoveries.json` bevat per kandidaat het schema-type, de laatst gelezen metadata en de herkomst van de plaatsnaam. Als een plaats niet op de eventpagina staat, wordt die alleen bij ondubbelzinnige officiële podiumlocaties afgeleid. Dit blijft expliciet als *onbevestigde kandidaat* gemarkeerd.
- In **Nieuw & festivals** laat het uitklapbare blok *Broncontrole* per podium zien wat er is gelukt en wat niet. Het geeft aan of broninformatie uit de laatst gepubliceerde scan komt. Alleen die scanstatus is controleerbaar; prijzen en ticketvoorraad zijn geen livegegevens.

### Beoordelingswachtrij en veilig toelaten

- **Toon alleen wachtrij** beperkt het scherm tot nog onbeoordeelde kandidaten. Shortlist, Interessant en Afwijzen blijven persoonlijke keuzes die nooit de publieke masterlijst wijzigen.
- **Voorstel voor masterlijst** opent een **vooraf ingevuld GitHub-issue**. Je moet op GitHub aangemeld zijn en het issue zelf daadwerkelijk indienen. Dit is geen directe publicatie of bevestiging.
- Het afzonderlijke workflowbestand `.github/workflows/review-candidate.yml` reageert alleen op een nieuw issue van de repository-eigenaar, of op een handmatig gestart `workflow_dispatch` met exact kandidaat-ID. Er is **geen** nieuw dagelijks of terugkerend schema aangemaakt.
- Het script `scripts/review_candidate.py` zoekt de kandidaat in de gepubliceerde vondsten en het vers geëxtraheerde bronbestand (maximaal 48 uur oud), controleert exacte officiële URL, event-schema, artiest, datum, plaats, bestaande optredens en unieke event-ID. Streng bevestigde MusicEvent-vermeldingen en het toegestane Metropool-TheaterEvent kunnen door. **Algemene Events** mogen uitsluitend een expliciet onbevestigd PR-voorstel opleveren als het officiële schema zowel een uitvoerende artiest als een concrete muziekbeschrijving bevat. In zo'n PR staat duidelijk dat verdere menselijke controle nodig is. Dubbelzinnige en niet-onderbouwde optredens worden geweigerd.
- Een geslaagd voorstel maakt na het uitvoeren van de bestaande smoke-tests een **pullrequest** met uitsluitend het nieuwe concert in `data/concerts.json`. Dat PR moet nog door de eigenaar worden bekeken en samengevoegd. Als GitHub Actions geen pullrequests mag openen, is daarvoor in de repository-instellingen toegang nodig; de workflow mag geen onzekere kandidaat direct naar `main` schrijven.
- De testbestanden voor bronspreiding, rolwisseling, valideren van de PR en de UI draaien voortaan ook in de gewone codecontrole.

### Dashboard en menu

- **Meer** is ingedeeld in *Overzicht*, *Persoonlijk* en *Beheer*, zonder functies weg te halen.
- De hoogste actuele topmatch heeft extra zichtbaarheid. In het startscherm staat per topmatch de bestaande uitsplitsing **Waarom X/10?**. Het gaat om metadata- en voorkeursscores, niet om analyse van opgenomen muziek of van songteksten.

De bestaande voorkeurskeuzes, concert-ID's, lokale opslag, vrijwillige synchronisatie en geplande GitHub-scans blijven intact. Automatische publieksgerichte goedkeuring, gegarandeerde ticketvoorraad en realtime volledigheid van podiumagenda's worden niet geclaimd.
