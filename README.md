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

1. Vai su [Facebook Developers](https://developers.facebook.com/)
2. Crea una nuova app o usa una esistente
3. Aggiungi il prodotto "Marketing API"
4. Genera un token di accesso con i permessi necessari:
   - `ads_read`
   - `pages_read_engagement`

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

## Limitazioni

- L'API di Meta ha limitazioni sui dati storici disponibili
- Alcuni annunci potrebbero non essere accessibili a causa delle impostazioni di privacy
- I rate limits dell'API possono influenzare la velocità di estrazione

## Supporto

Per problemi o domande, consulta la [documentazione ufficiale dell'API Meta Ads Library](https://developers.facebook.com/docs/marketing-api/reference/ads-archive/).