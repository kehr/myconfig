// Simple search functionality for MyConfig documentation
class DocumentSearch {
  constructor() {
    this.searchData = [];
    this.searchInput = null;
    this.searchResults = null;
    this.init();
  }

  init() {
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => this.setup());
    } else {
      this.setup();
    }
  }

  setup() {
    this.createSearchInterface();
    this.buildSearchIndex();
    this.bindEvents();
  }

  createSearchInterface() {
    // Create search container
    const searchContainer = document.createElement('div');
    searchContainer.className = 'search-container';
    searchContainer.innerHTML = `
      <input type="text" class="search-input" placeholder="Search documentation..." />
      <div class="search-results"></div>
    `;

    // Insert search container after hero section or at top of main content
    const heroSection = document.querySelector('.hero-section');
    const mainContent = document.querySelector('main') || document.querySelector('.page-content');
    
    if (heroSection && heroSection.nextElementSibling) {
      heroSection.parentNode.insertBefore(searchContainer, heroSection.nextElementSibling);
    } else if (mainContent) {
      mainContent.insertBefore(searchContainer, mainContent.firstChild);
    }

    this.searchInput = searchContainer.querySelector('.search-input');
    this.searchResults = searchContainer.querySelector('.search-results');
  }

  buildSearchIndex() {
    // Index current page content
    this.indexPageContent();
    
    // Index documentation pages (if we have access to them)
    this.indexDocumentationPages();
  }

  indexPageContent() {
    const content = document.querySelector('main') || document.body;
    const headings = content.querySelectorAll('h1, h2, h3, h4, h5, h6');
    const paragraphs = content.querySelectorAll('p');
    const codeBlocks = content.querySelectorAll('pre code');

    // Index headings
    headings.forEach(heading => {
      if (heading.textContent.trim()) {
        this.searchData.push({
          title: heading.textContent.trim(),
          content: heading.textContent.trim(),
          url: window.location.pathname + '#' + (heading.id || this.generateId(heading.textContent)),
          type: 'heading',
          element: heading
        });
      }
    });

    // Index paragraphs
    paragraphs.forEach(paragraph => {
      if (paragraph.textContent.trim() && paragraph.textContent.length > 20) {
        this.searchData.push({
          title: paragraph.textContent.substring(0, 50) + '...',
          content: paragraph.textContent.trim(),
          url: window.location.pathname,
          type: 'content',
          element: paragraph
        });
      }
    });

    // Index code blocks
    codeBlocks.forEach(code => {
      if (code.textContent.trim()) {
        this.searchData.push({
          title: 'Code: ' + code.textContent.substring(0, 30) + '...',
          content: code.textContent.trim(),
          url: window.location.pathname,
          type: 'code',
          element: code
        });
      }
    });
  }

  indexDocumentationPages() {
    // Static index of documentation pages
    const docPages = [
      { title: 'Installation Guide', url: '/docs/installation', content: 'System requirements, installation methods, and troubleshooting' },
      { title: 'Usage Guide', url: '/docs/usage', content: 'Complete command reference and common scenarios' },
      { title: 'Configuration Reference', url: '/docs/configuration', content: 'TOML configuration, profiles, and environment variables' },
      { title: 'CLI Tools Guide', url: '/docs/cli-tools', content: 'CLI tools detection and backup guide' },
      { title: 'Plugin Development', url: '/docs/plugins', content: 'Plugin system and extension development' },
      { title: 'Template System', url: '/docs/templates', content: 'Customizing output files with templates' },
      { title: 'Security Features', url: '/docs/security', content: 'Security mechanisms and best practices' },
      { title: 'Testing Guide', url: '/docs/testing', content: 'Testing framework and procedures' }
    ];

    docPages.forEach(page => {
      this.searchData.push({
        title: page.title,
        content: page.content,
        url: page.url,
        type: 'page'
      });
    });
  }

  bindEvents() {
    if (!this.searchInput) return;

    let searchTimeout;

    this.searchInput.addEventListener('input', (e) => {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(() => {
        this.performSearch(e.target.value);
      }, 300);
    });

    this.searchInput.addEventListener('focus', () => {
      if (this.searchInput.value.trim()) {
        this.performSearch(this.searchInput.value);
      }
    });

    // Hide results when clicking outside
    document.addEventListener('click', (e) => {
      if (!e.target.closest('.search-container')) {
        this.hideResults();
      }
    });

    // Handle keyboard navigation
    this.searchInput.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        this.hideResults();
        this.searchInput.blur();
      }
    });
  }

  performSearch(query) {
    if (!query || query.length < 2) {
      this.hideResults();
      return;
    }

    const results = this.searchData.filter(item => {
      const searchText = (item.title + ' ' + item.content).toLowerCase();
      return searchText.includes(query.toLowerCase());
    });

    this.displayResults(results.slice(0, 8)); // Limit to 8 results
  }

  displayResults(results) {
    if (!this.searchResults) return;

    if (results.length === 0) {
      this.searchResults.innerHTML = '<div class="search-result-item">No results found</div>';
      this.searchResults.style.display = 'block';
      return;
    }

    const resultsHTML = results.map(result => `
      <div class="search-result-item" data-url="${result.url}" data-type="${result.type}">
        <div class="search-result-title">${this.highlightQuery(result.title)}</div>
        <div class="search-result-content">${this.highlightQuery(result.content.substring(0, 100))}${result.content.length > 100 ? '...' : ''}</div>
        <div class="search-result-type">${result.type}</div>
      </div>
    `).join('');

    this.searchResults.innerHTML = resultsHTML;
    this.searchResults.style.display = 'block';

    // Bind click events to results
    this.searchResults.querySelectorAll('.search-result-item').forEach(item => {
      item.addEventListener('click', () => {
        const url = item.dataset.url;
        const type = item.dataset.type;
        
        if (type === 'heading' && url.includes('#')) {
          // Scroll to heading on same page
          const hash = url.split('#')[1];
          const element = document.getElementById(hash);
          if (element) {
            element.scrollIntoView({ behavior: 'smooth' });
            this.hideResults();
            return;
          }
        }
        
        // Navigate to different page
        if (url !== window.location.pathname) {
          window.location.href = url;
        }
        
        this.hideResults();
      });
    });
  }

  highlightQuery(text) {
    const query = this.searchInput.value.toLowerCase();
    if (!query) return text;

    const regex = new RegExp(`(${query})`, 'gi');
    return text.replace(regex, '<mark>$1</mark>');
  }

  hideResults() {
    if (this.searchResults) {
      this.searchResults.style.display = 'none';
    }
  }

  generateId(text) {
    return text.toLowerCase()
      .replace(/[^\w\s-]/g, '')
      .replace(/\s+/g, '-')
      .trim();
  }
}

// Initialize search when page loads
new DocumentSearch();