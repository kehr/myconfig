// Theme toggle functionality for MyConfig documentation
class ThemeToggle {
  constructor() {
    this.currentTheme = this.getStoredTheme() || this.getPreferredTheme();
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
    this.applyTheme(this.currentTheme);
    this.createToggleButton();
    this.bindEvents();
  }

  getPreferredTheme() {
    // Check system preference
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark';
    }
    return 'light';
  }

  getStoredTheme() {
    try {
      return localStorage.getItem('myconfig-theme');
    } catch (e) {
      return null;
    }
  }

  storeTheme(theme) {
    try {
      localStorage.setItem('myconfig-theme', theme);
    } catch (e) {
      // localStorage not available
    }
  }

  applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    this.currentTheme = theme;
    this.storeTheme(theme);
    
    // Update meta theme-color for mobile browsers
    this.updateMetaThemeColor(theme);
  }

  updateMetaThemeColor(theme) {
    let metaThemeColor = document.querySelector('meta[name="theme-color"]');
    if (!metaThemeColor) {
      metaThemeColor = document.createElement('meta');
      metaThemeColor.name = 'theme-color';
      document.head.appendChild(metaThemeColor);
    }
    
    const colors = {
      light: '#ffffff',
      dark: '#0f172a'
    };
    
    metaThemeColor.content = colors[theme] || colors.light;
  }

  createToggleButton() {
    const toggleButton = document.createElement('button');
    toggleButton.className = 'theme-toggle';
    toggleButton.setAttribute('aria-label', 'Toggle theme');
    toggleButton.setAttribute('title', 'Toggle between light and dark theme');
    
    this.updateToggleIcon(toggleButton);
    
    // Insert toggle button
    document.body.appendChild(toggleButton);
    
    this.toggleButton = toggleButton;
  }

  updateToggleIcon(button) {
    const icons = {
      light: '🌙', // Moon for switching to dark
      dark: '☀️'   // Sun for switching to light
    };
    
    button.innerHTML = icons[this.currentTheme] || icons.light;
  }

  bindEvents() {
    if (!this.toggleButton) return;

    this.toggleButton.addEventListener('click', () => {
      this.toggleTheme();
    });

    // Listen for system theme changes
    if (window.matchMedia) {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      mediaQuery.addEventListener('change', (e) => {
        // Only auto-switch if user hasn't manually set a preference
        if (!this.getStoredTheme()) {
          const newTheme = e.matches ? 'dark' : 'light';
          this.applyTheme(newTheme);
          this.updateToggleIcon(this.toggleButton);
        }
      });
    }

    // Keyboard shortcut (Ctrl/Cmd + Shift + T)
    document.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'T') {
        e.preventDefault();
        this.toggleTheme();
      }
    });
  }

  toggleTheme() {
    const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
    this.applyTheme(newTheme);
    this.updateToggleIcon(this.toggleButton);
    
    // Add a subtle animation feedback
    this.toggleButton.style.transform = 'scale(0.9)';
    setTimeout(() => {
      this.toggleButton.style.transform = 'scale(1)';
    }, 150);
  }
}

// Initialize theme toggle when page loads
new ThemeToggle();