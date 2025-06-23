# Meta Ads Library Scraper

Questo actor permette di estrarre annunci pubblicitari dalla Meta Ads Library utilizzando l'API ufficiale di Facebook.

## Caratteristiche

- Estrazione di annunci pubblicitari da Facebook/Instagram
- Ricerca per termini specifici
- Filtri per paese, stato dell'annuncio e tipo
- Estrazione di dati dettagliati inclusi spesa, impressioni e contenuti creativi
- Gestione automatica della paginazione
- Rispetto dei rate limits dell'API

## Input

### Parametri Richiesti

- **accessToken** (string): Token di accesso per l'API di Facebook. Richiesto per autenticare le richieste.

### Parametri Opzionali

- **searchTerms** (string): Termini di ricerca per filtrare gli annunci
- **adReachedCountries** (array): Lista dei codici paese (default: ['IT'])
- **adActiveStatus** (string): Stato degli annunci - 'ALL', 'ACTIVE', 'INACTIVE' (default: 'ALL')
- **adType** (string): Tipo di annuncio - 'ALL', 'POLITICAL_AND_ISSUE_ADS', 'HOUSING_ADS', 'EMPLOYMENT_ADS', 'CREDIT_ADS' (default: 'ALL')
- **limit** (number): Numero di annunci per pagina (default: 100, max: 1000)
- **maxPages** (number): Numero massimo di pagine da processare (default: 10)
- **fields** (array): Campi specifici da estrarre (opzionale, usa i default se non specificato)
- **proxyConfiguration** (object): Configurazione proxy per le richieste

## Output

Ogni annuncio estratto contiene:

- **ad_id**: ID univoco dell'annuncio
- **page_name**: Nome della pagina che ha pubblicato l'annuncio
- **page_id**: ID della pagina
- **ad_creation_time**: Data di creazione dell'annuncio
- **ad_delivery_start_time**: Data di inizio pubblicazione
- **ad_delivery_stop_time**: Data di fine pubblicazione
- **ad_snapshot_url**: URL dello screenshot dell'annuncio
- **currency**: Valuta utilizzata per la spesa
- **funding_entity**: Entità che finanzia l'annuncio
- **impressions**: Dati sulle impressioni
- **spend**: Dati sulla spesa pubblicitaria
- **demographic_distribution**: Distribuzione demografica
- **publisher_platforms**: Piattaforme di pubblicazione
- **ad_creative_body**: Testo principale dell'annuncio
- **ad_creative_link_caption**: Didascalia del link
- **ad_creative_link_description**: Descrizione del link
- **ad_creative_link_title**: Titolo del link
- **scraped_at**: Timestamp dell'estrazione

## Come Ottenere un Access Token

### Requisiti Importanti

⚠️ **ATTENZIONE**: Per accedere alla Meta Ads Library API, la tua app Facebook deve avere un **ruolo specifico** assegnato dal proprietario dell'app. Senza questo ruolo, riceverai l'errore "Application does not have permission for this action" (codice 2332004).

### Passaggi per Configurare l'Accesso

1. **Crea o Configura l'App Facebook**:
   - Vai su [Facebook Developers](https://developers.facebook.com/)
   - Crea una nuova app o usa una esistente
   - Aggiungi il prodotto "Marketing API"

2. **Richiedi l'Accesso alla Ads Library**:
   - L'accesso alla Meta Ads Library richiede un processo di approvazione
   - La tua app deve essere verificata da Meta
   - Devi avere un ruolo appropriato nell'app (Developer, Admin, etc.)

3. **Genera il Token di Accesso**:
   - Usa il Graph API Explorer o genera programmaticamente
   - Assicurati che il token abbia i permessi:
     - `ads_read`
     - `pages_read_engagement`

4. **Verifica i Permessi**:
   - Testa il token con una chiamata di prova all'API
   - Verifica che non ricevi errori di autorizzazione

## Esempio di Input

```json
{
  "accessToken": "YOUR_FACEBOOK_ACCESS_TOKEN",
  "searchTerms": "pizza",
  "adReachedCountries": ["IT", "US"],
  "adActiveStatus": "ACTIVE",
  "adType": "ALL",
  "limit": 50,
  "maxPages": 5
}
```

## Note Importanti

- L'access token deve avere i permessi appropriati per accedere alla Meta Ads Library
- L'API ha rate limits che vengono gestiti automaticamente dall'actor
- I dati disponibili dipendono dalle politiche di trasparenza di Meta
- Alcuni campi potrebbero non essere disponibili per tutti gli annunci

## Risoluzione Problemi

### Errore: "Application does not have permission for this action" (Codice 2332004)

Questo errore indica che:
- La tua app Facebook non ha i permessi necessari per accedere alla Ads Library
- Non hai un ruolo appropriato nell'app Facebook
- L'app non è stata approvata da Meta per l'accesso alla Ads Library

**Soluzioni**:
1. Contatta il proprietario dell'app per assegnarti un ruolo (Developer, Admin, etc.)
2. Richiedi l'approvazione dell'app per l'accesso alla Meta Ads Library
3. Verifica che l'app abbia tutti i permessi necessari
4. Usa un token di accesso generato da un account con i permessi appropriati

### Errore: "Invalid Access Token"

- Verifica che il token non sia scaduto
- Assicurati che il token abbia i permessi `ads_read`
- Rigenera il token se necessario

### Nessun Risultato Trovato

- Verifica i parametri di ricerca (termini, paesi, stato)
- Prova con criteri di ricerca più ampi
- Controlla che ci siano annunci attivi per i parametri specificati

## Limitazioni

- L'API di Meta ha limitazioni sui dati storici disponibili
- Alcuni annunci potrebbero non essere accessibili a causa delle impostazioni di privacy
- I rate limits dell'API possono influenzare la velocità di estrazione
- **Accesso limitato**: Solo app approvate possono accedere alla Meta Ads Library

## Supporto

Per problemi o domande:
- Consulta la [documentazione ufficiale dell'API Meta Ads Library](https://developers.facebook.com/docs/marketing-api/reference/ads-archive/)
- Leggi la [guida sui ruoli delle app Facebook](https://developers.facebook.com/docs/development/build-and-test/app-roles)
- Visita il [centro assistenza per sviluppatori Meta](https://developers.facebook.com/support/)