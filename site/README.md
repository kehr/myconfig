# MyConfig Website

This directory contains the GitHub Pages website for the MyConfig project, following industry best practices for Jekyll site organization.

## Directory Structure

```
site/
├── _config.yml          # Jekyll configuration
├── index.md             # Homepage
├── about.md             # About page
├── Gemfile              # Ruby dependencies
├── _layouts/            # Jekyll layouts
├── _includes/           # Jekyll includes
├── _sass/               # Sass stylesheets
├── assets/              # Static assets
│   ├── css/             # CSS files
│   │   └── custom.css   # Custom styles
│   └── js/              # JavaScript files
│       ├── copy-code.js # Code copy functionality
│       ├── search.js    # Search functionality
│       └── theme-toggle.js # Dark mode toggle
└── docs/                # Symlink to ../docs (project documentation)
```

## Features

- **Responsive Design**: Mobile-first responsive layout
- **Dark Mode**: Toggle between light and dark themes
- **Search Functionality**: Client-side search across documentation
- **Code Copy**: One-click code block copying
- **SEO Optimized**: Meta tags and structured data
- **Fast Loading**: Optimized assets and minimal dependencies

## Development

### Local Development

```bash
cd site
bundle install
bundle exec jekyll serve
```

The site will be available at `http://localhost:4000`

### Building for Production

```bash
cd site
bundle exec jekyll build
```

The built site will be in the `_site` directory.

## Deployment

The site is automatically deployed to GitHub Pages via GitHub Actions when changes are pushed to the main branch. The workflow is configured in `.github/workflows/pages.yml`.

## Configuration

Key configuration options in `_config.yml`:

- **Site Information**: Title, description, URL
- **Navigation**: Header pages and menu structure
- **Collections**: Documentation organization
- **Plugins**: Jekyll plugins for enhanced functionality
- **Features**: Toggle for search, dark mode, code copy
- **Exclusions**: Files to exclude from build process

## Content Management

- **Pages**: Add new pages as `.md` files in the root
- **Documentation**: Linked via symlink to `../docs`
- **Assets**: Place images, CSS, JS in `assets/` directory
- **Layouts**: Custom layouts in `_layouts/` directory
- **Includes**: Reusable components in `_includes/` directory

## Best Practices

This structure follows Jekyll and GitHub Pages best practices:

1. **Separation of Concerns**: Website files isolated from main codebase
2. **Standard Structure**: Uses conventional Jekyll directory layout
3. **Documentation Integration**: Seamless access to project docs via symlink
4. **CI/CD Ready**: Optimized for automated deployment
5. **Performance**: Minimal dependencies and optimized assets
6. **Maintainability**: Clear organization and configuration