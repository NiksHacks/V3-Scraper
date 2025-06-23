# Meta Ads Library Web Scraper

Un potente scraper per la Meta Ads Library che utilizza web scraping per raccogliere dati pubblicitari pubblici senza necessità di token di accesso o verifiche aziendali.

## Caratteristiche

- **Nessun Token Richiesto**: Funziona senza token di accesso Facebook o verifiche aziendali
- **Web Scraping Avanzato**: Utilizza Playwright per navigazione dinamica e BeautifulSoup per parsing
- **Ricerca Flessibile**: Supporta ricerca per termini, paesi, stato degli annunci e tipo
- **Scroll Automatico**: Carica automaticamente più contenuti scrollando la pagina
- **Gestione Cookie**: Gestisce automaticamente i popup di consenso cookie
- **Dati Strutturati**: Output in formato JSON strutturato e pulito

## Input

### Tutti Opzionali

- **searchTerms** (string): Termini di ricerca per filtrare gli annunci
- **adReachedCountries** (array): Lista dei codici paese (default: ['IT'])
- **adActiveStatus** (string): Stato degli annunci - 'ALL', 'ACTIVE', 'INACTIVE' (default: 'ALL')
- **adType** (string): Tipo di annuncio - 'ALL', 'POLITICAL_AND_ISSUE_ADS', 'HOUSING_ADS', 'EMPLOYMENT_ADS', 'CREDIT_ADS' (default: 'ALL')
- **limit** (number): Numero massimo di annunci da raccogliere (default: 50, max: 500)
- **maxPages** (number): Numero massimo di pagine da scorrere (default: 5, max: 20)
- **proxyConfiguration** (object): Configurazione proxy per le richieste

## Output

Ogni annuncio estratto contiene:

- **ad_id**: ID univoco generato per l'annuncio
- **page_name**: Nome della pagina che ha pubblicato l'annuncio
- **ad_creative_body**: Testo principale dell'annuncio
- **ad_snapshot_url**: URL per visualizzare l'annuncio nella libreria
- **ad_delivery_start_time**: Data di inizio pubblicazione (se disponibile)
- **impressions**: Dati sulle impressioni (se disponibili)
- **spend**: Dati sulla spesa (se disponibili)
- **scraped_at**: Timestamp di quando è stato raccolto il dato
- **source**: Indica che i dati provengono da web scraping

## Vantaggi del Web Scraping

### Nessuna Verifica Richiesta

- **Nessun Token**: Non serve un token di accesso Facebook
- **Nessuna App**: Non è necessario creare o verificare un'app Facebook
- **Nessuna Azienda**: Non serve avere un'azienda registrata per la verifica Meta
- **Accesso Immediato**: Funziona subito senza approvazioni

### Limitazioni

- **Dati Pubblici**: Accede solo ai dati pubblicamente disponibili nella libreria
- **Velocità**: Più lento rispetto all'API ufficiale
- **Stabilità**: Dipende dalla struttura del sito web di Facebook
- **Rate Limiting**: Limitato dalla velocità di caricamento delle pagine

## Esempio di Input

```json
{
  "searchTerms": "pizza",
  "adReachedCountries": ["IT", "US"],
  "adActiveStatus": "ACTIVE",
  "adType": "ALL",
  "limit": 50,
  "maxPages": 5
}
```

## Note Importanti

- **Dati Pubblici**: Accede solo ai dati pubblicamente visibili nella Meta Ads Library
- **Velocità**: Il web scraping è più lento rispetto all'API ufficiale
- **Struttura Sito**: Dipende dalla struttura HTML del sito Facebook (può cambiare)
- **Rate Limiting**: Limitato dalla velocità di caricamento delle pagine
- **Geo-restrizioni**: Alcuni dati potrebbero essere limitati per paese
- **Contenuto Dinamico**: Alcuni elementi potrebbero non essere sempre visibili

## Risoluzione Problemi

### Nessun Annuncio Trovato

**Causa**: I criteri di ricerca sono troppo specifici o la pagina non si è caricata correttamente.

**Soluzione**:
1. Prova termini di ricerca più generici
2. Espandi i paesi target
3. Cambia lo stato degli annunci (es. da ACTIVE a ALL)
4. Aumenta il numero di pagine massime

### Errori di Caricamento Pagina

**Causa**: Problemi di connessione o blocchi temporanei.

**Soluzione**:
1. Riprova dopo qualche minuto
2. Usa una configurazione proxy
3. Riduci la velocità di scraping

### Dati Incompleti

**Causa**: La struttura della pagina è cambiata o alcuni elementi non sono visibili.

**Soluzione**:
1. Verifica che la pagina si carichi correttamente nel browser
2. Prova con criteri di ricerca diversi
3. Controlla i log per errori specifici

## Limitazioni

- I dati storici disponibili dipendono dalle politiche di Meta
- Alcuni annunci potrebbero non essere accessibili a causa delle impostazioni di privacy
- La velocità di scraping può influenzare la quantità di dati raccolti
- **Accesso limitato**: Solo ai dati pubblicamente disponibili

## Supporto

Per problemi o domande:
- [Meta Ads Library](https://www.facebook.com/ads/library/)
- [Documentazione Playwright](https://playwright.dev/)
- [Documentazione BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)