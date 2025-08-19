// Code copy functionality for MyConfig documentation
class CodeCopy {
  constructor() {
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
    this.addCopyButtons();
    this.bindEvents();
  }

  addCopyButtons() {
    const codeBlocks = document.querySelectorAll('pre code');
    
    codeBlocks.forEach((codeBlock, index) => {
      const pre = codeBlock.parentElement;
      
      // Skip if button already exists
      if (pre.querySelector('.copy-code-button')) {
        return;
      }
      
      // Create copy button
      const copyButton = document.createElement('button');
      copyButton.className = 'copy-code-button';
      copyButton.textContent = 'Copy';
      copyButton.setAttribute('aria-label', 'Copy code to clipboard');
      copyButton.setAttribute('data-code-index', index);
      
      // Add button to pre element
      pre.style.position = 'relative';
      pre.appendChild(copyButton);
    });
  }

  bindEvents() {
    // Use event delegation for copy buttons
    document.addEventListener('click', (e) => {
      if (e.target.classList.contains('copy-code-button')) {
        this.copyCode(e.target);
      }
    });

    // Re-add buttons when new content is loaded (for SPA navigation)
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
          // Check if new code blocks were added
          const hasNewCodeBlocks = Array.from(mutation.addedNodes).some(node => {
            return node.nodeType === Node.ELEMENT_NODE && 
                   (node.querySelector('pre code') || node.matches('pre code'));
          });
          
          if (hasNewCodeBlocks) {
            setTimeout(() => this.addCopyButtons(), 100);
          }
        }
      });
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true
    });
  }

  async copyCode(button) {
    const pre = button.parentElement;
    const codeBlock = pre.querySelector('code');
    
    if (!codeBlock) return;

    const code = this.getCodeText(codeBlock);
    
    try {
      await this.copyToClipboard(code);
      this.showCopySuccess(button);
    } catch (err) {
      this.showCopyError(button);
      console.error('Failed to copy code:', err);
    }
  }

  getCodeText(codeBlock) {
    // Clone the code block to avoid modifying the original
    const clone = codeBlock.cloneNode(true);
    
    // Remove any copy buttons that might be inside
    const buttons = clone.querySelectorAll('.copy-code-button');
    buttons.forEach(btn => btn.remove());
    
    // Remove line numbers if present
    const lineNumbers = clone.querySelectorAll('.line-number, .lineno');
    lineNumbers.forEach(ln => ln.remove());
    
    // Get text content and clean it up
    let text = clone.textContent || clone.innerText || '';
    
    // Remove extra whitespace and normalize line endings
    text = text.replace(/\r\n/g, '\n').replace(/\r/g, '\n');
    
    // Remove leading/trailing whitespace
    text = text.trim();
    
    return text;
  }

  async copyToClipboard(text) {
    // Try modern clipboard API first
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
      return;
    }
    
    // Fallback for older browsers
    return this.fallbackCopyToClipboard(text);
  }

  fallbackCopyToClipboard(text) {
    return new Promise((resolve, reject) => {
      const textArea = document.createElement('textarea');
      textArea.value = text;
      textArea.style.position = 'fixed';
      textArea.style.left = '-999999px';
      textArea.style.top = '-999999px';
      document.body.appendChild(textArea);
      
      textArea.focus();
      textArea.select();
      
      try {
        const successful = document.execCommand('copy');
        document.body.removeChild(textArea);
        
        if (successful) {
          resolve();
        } else {
          reject(new Error('Copy command failed'));
        }
      } catch (err) {
        document.body.removeChild(textArea);
        reject(err);
      }
    });
  }

  showCopySuccess(button) {
    const originalText = button.textContent;
    button.textContent = 'Copied!';
    button.classList.add('copy-success');
    
    setTimeout(() => {
      button.textContent = originalText;
      button.classList.remove('copy-success');
    }, 2000);
  }

  showCopyError(button) {
    const originalText = button.textContent;
    button.textContent = 'Failed';
    button.classList.add('copy-error');
    
    setTimeout(() => {
      button.textContent = originalText;
      button.classList.remove('copy-error');
    }, 2000);
  }
}

// Initialize code copy functionality when page loads
new CodeCopy();