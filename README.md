# NHK Hack - Universal Web Scraper

A powerful and flexible web scraper built on the Apify platform. NHK Hack can scrape single pages or crawl entire websites, extracting comprehensive data including text content, links, images, and metadata.

## Features

- **Single Page Scraping**: Extract data from individual web pages
- **Website Crawling**: Follow links and scrape multiple pages with configurable depth
- **Comprehensive Data Extraction**:
  - Page title and clean text content
  - All links with anchor text
  - All images with alt text
  - Meta tags and structured data (JSON-LD)
  - Full HTML content (optional)
- **Smart Link Following**: Configurable domain restrictions and crawl depth
- **Robust Error Handling**: Handles HTTP errors, timeouts, and malformed content
- **Async Processing**: High-performance asynchronous scraping

## Input Configuration

### Required Parameters

- **Start URLs** (`startUrls`): Array of URLs to begin scraping from

### Optional Parameters

- **Max Pages** (`maxPages`): Maximum number of pages to scrape (default: 10)
- **Max Depth** (`maxDepth`): Maximum crawling depth (default: 1 for single page)
- **Allowed Domains** (`allowedDomains`): Restrict crawling to specific domains
- **Include Images** (`includeImages`): Extract image URLs (default: true)
- **Include Links** (`includeLinks`): Extract page links (default: true)
- **Include Metadata** (`includeMetadata`): Extract meta tags and structured data (default: true)
- **Include HTML** (`includeHtml`): Include full HTML content (default: false)

## Usage Examples

### Single Page Scraping

```json
{
  "startUrls": [
    {"url": "https://example.com"}
  ],
  "maxPages": 1,
  "maxDepth": 1
}
```

### Website Crawling

```json
{
  "startUrls": [
    {"url": "https://example.com"}
  ],
  "maxPages": 50,
  "maxDepth": 3,
  "allowedDomains": ["example.com"]
}
```

### News Site Scraping

```json
{
  "startUrls": [
    {"url": "https://news-site.com/articles"}
  ],
  "maxPages": 100,
  "maxDepth": 2,
  "allowedDomains": ["news-site.com"],
  "includeHtml": false,
  "includeImages": true
}
```

## Output Format

Each scraped page returns a structured object:

```json
{
  "url": "https://example.com/page",
  "title": "Page Title",
  "text": "Clean text content of the page...",
  "html": "<html>...</html>",
  "links": [
    {
      "url": "https://example.com/link",
      "text": "Link text",
      "title": "Link title"
    }
  ],
  "images": [
    {
      "url": "https://example.com/image.jpg",
      "alt": "Image description",
      "title": "Image title"
    }
  ],
  "metadata": {
    "description": "Page meta description",
    "keywords": "page, keywords",
    "structured_data": [...]
  }
}
```

## Technical Details

### Dependencies

- **apify**: Apify SDK for actor development
- **httpx**: Async HTTP client for web requests
- **beautifulsoup4**: HTML parsing and data extraction
- **lxml**: Fast XML and HTML parser
- **parsel**: Advanced CSS and XPath selectors
- **w3lib**: Web scraping utilities

### Architecture

The scraper is built using modern Python async/await patterns for high performance:

- **NHKHackScraper Class**: Main scraper logic with async context management
- **Modular Extraction**: Separate methods for different data types
- **Smart Crawling**: Intelligent link following with depth and domain controls
- **Error Recovery**: Robust error handling for production use

### Performance

- Async HTTP requests for concurrent processing
- Memory-efficient streaming for large sites
- Configurable limits to prevent resource exhaustion
- Smart duplicate URL detection

## Use Cases

- **Content Research**: Extract articles, blog posts, and documentation
- **Competitive Analysis**: Monitor competitor websites and content
- **Data Mining**: Collect structured data from web sources
- **SEO Analysis**: Extract meta tags, structured data, and page content
- **Link Building**: Discover and analyze link opportunities
- **Market Research**: Gather product information and pricing data

## Best Practices

1. **Start Small**: Begin with low `maxPages` and `maxDepth` values
2. **Use Domain Restrictions**: Set `allowedDomains` to avoid crawling the entire web
3. **Monitor Resources**: Large crawls can consume significant compute time
4. **Respect Robots.txt**: Be mindful of website scraping policies
5. **Rate Limiting**: The scraper includes built-in delays to be respectful

## Error Handling

The scraper handles various error conditions gracefully:

- HTTP errors (404, 500, etc.)
- Network timeouts and connection issues
- Malformed HTML and encoding problems
- JavaScript-heavy sites (extracts available static content)

## Support

For issues, feature requests, or questions about NHK Hack, please refer to the Apify platform documentation or contact the actor maintainer.

---

**NHK Hack** - Powerful web scraping made simple.