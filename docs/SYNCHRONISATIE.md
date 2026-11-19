# Privésynchronisatie tussen Windows en Android

Deze versie ondersteunt een **optionele** Supabase-privécloud. De cloud is **niet actief** voordat de eigenaar zelf een databaseproject heeft ingesteld. De huidige lokale gegevens en status blijven behouden.

## Eenmalig instellen (eigen gratis Supabase-project)

1. Maak een eigen Supabase-project. Controleer actuele gratis limieten op supabase.com.
2. Gebruik de SQL Editor om de volledige inhoud van `supabase/schema.sql` uit te voeren. Daarmee wordt **Row Level Security** ingesteld: elke gebruiker ziet uitsluitend diens eigen gegevens.
3. Onder Authentication: activeer Email OTP / Magic Link en voeg `https://martinwubbels.github.io/concertradar/` toe aan de toegestane redirect URLs.
4. Kopieer bij Project Settings / API de **Project URL** en de **publieke anon/publishable key**. Gebruik **nooit** de service_role/secret key in een openbare GitHub-repository.
5. Bewerk `data/cloud-config.json` met de URL en publieke key. De config is publiek, maar bevat geen persoonlijke gegevens; privacy is afhankelijk van **RLS**.
6. Open ConcertRadar, tab **Synchronisatie**, vul op Windows en Android hetzelfde e-mailadres in en gebruik de aanmeldlink.

## Werking

- De app blijft offline bruikbaar. Je persoonlijke gegevens staan lokaal onder de bestaande `concertradar-v1` key.
- Na aanmelden worden de lokale status, eigen concerten, notities en beoordelingen met de privécloud samengevoegd.
- Beoordelingen en statussen gebruiken hun `updated_at`; de laatst gewijzigde waarde krijgt voorrang. Legacy records zonder tijdstempel worden zo goed mogelijk behouden, maar bij conflicten is de uitkomst niet altijd eenduidig.
- Bij wijzigen wordt een upload op de achtergrond gestart. Bij terugkeren naar het tabblad, en periodiek terwijl de pagina actief is, worden nieuwe wijzigingen opgehaald.
- Verwijderde eigen concerten worden als lokale tombstone opgeslagen zodat ze na synchronisatie niet terugkomen.
- Synchronisatie vereist internet; bij fouten blijven de lokale gegevens bewaard. De exportfunctie is nog steeds de veilige reservekopie.

## Privacy en aandachtspunten

- GitHub Pages blijft **openbaar**. Er komen geen persoonlijke concerten, e-mailadressen, notities of boekingen in deze repository.
- Supabase ontvangt je e-mailadres en versleutelt het dataverkeer met HTTPS. De inhoud van de cloudgegevens is niet end-to-end versleuteld.
- Maak een back-up via **Updates & beheer** voordat je voor het eerst synchroniseert.
- Live cloudsync is nog niet end-to-end getest, omdat er nog geen persoonlijk Supabase-project is gekoppeld.
