# Package.json Documentation

This file explains every aspect of our Excel AI Agent add-in's package.json configuration.

## Basic Information
- **name**: `excel-ai-agent-addin` - Identifies this Office add-in project
- **version**: `0.0.1` - Follows semantic versioning (major.minor.patch.build)
- **license**: `MIT` - Allows free use, modification, and distribution

## Configuration
- **config.app_to_debug**: `excel` - Specifies Excel as the target Office application
- **config.app_type_to_debug**: `desktop` - Desktop Excel vs web Excel Online
- **config.dev_server_port**: `3000` - Port for webpack dev server (must match manifest.xml)

## Scripts (Development Commands)
- **build**: `webpack --mode production` - Creates optimized production bundle
- **build:dev**: `webpack --mode development` - Creates development bundle with source maps
- **dev-server**: `webpack serve --mode development` - Starts dev server with hot reloading
- **lint**: `office-addin-lint check` - Runs ESLint with Office add-in rules
- **lint:fix**: `office-addin-lint fix` - Auto-fixes linting issues
- **prettier**: `office-addin-lint prettier` - Formats code with Office standards
- **signin**: `office-addin-dev-settings m365-account login` - Signs into Microsoft 365
- **signout**: `office-addin-dev-settings m365-account logout` - Signs out of M365
- **start**: `office-addin-debugging start manifest.xml` - Starts Excel with add-in loaded
- **stop**: `office-addin-debugging stop manifest.xml` - Stops debugging session
- **validate**: `office-addin-manifest validate manifest.xml` - Validates manifest file
- **watch**: `webpack --mode development --watch` - Builds and watches for changes

## Runtime Dependencies
- **@fluentui/react-components**: Microsoft's Fluent UI components for Office-style UI
- **@fluentui/react-icons**: Icons from Fluent UI system for consistent iconography
- **core-js**: Polyfills for modern JavaScript features in older browsers/Excel versions
- **es6-promise**: Promise polyfill for older browsers (Office.js uses promises extensively)
- **react**: Core React library for building our user interface
- **react-dom**: React DOM library for rendering components to the task pane
- **regenerator-runtime**: Runtime for async/await in older JavaScript engines

## Development Dependencies

### TypeScript & Babel
- **@babel/core**: JavaScript transpiler core - converts modern JS/TS to older versions
- **@babel/preset-env**: Environment-specific transpilation for Excel compatibility
- **@babel/preset-typescript**: TypeScript compilation preset
- **typescript**: TypeScript compiler for static type checking

### Type Definitions
- **@types/office-js**: TypeScript definitions for Office.js APIs (Excel.run(), etc.)
- **@types/office-runtime**: TypeScript definitions for Office runtime
- **@types/react**: TypeScript definitions for React
- **@types/react-dom**: TypeScript definitions for ReactDOM
- **@types/webpack**: TypeScript definitions for webpack config

### Webpack & Build Tools
- **webpack**: Module bundler for packaging our code and assets
- **webpack-cli**: Command line interface for webpack
- **webpack-dev-server**: Development server with HTTPS and hot reloading
- **babel-loader**: Integrates Babel with webpack build process
- **ts-loader**: TypeScript loader for webpack
- **html-webpack-plugin**: Generates HTML files with script/CSS references
- **copy-webpack-plugin**: Copies static files (manifest, images) to build output
- **source-map-loader**: Extracts source maps for better debugging

### Linting & Code Quality
- **eslint-plugin-office-addins**: ESLint rules for Office add-ins best practices
- **eslint-plugin-react**: ESLint rules for React development
- **office-addin-lint**: Microsoft's linting tools for Office add-ins
- **office-addin-prettier-config**: Prettier configuration for Office add-ins

### Office Add-in Specific Tools
- **office-addin-cli**: CLI tools for Office add-in development
- **office-addin-debugging**: Tools for debugging Office add-ins in Excel
- **office-addin-dev-certs**: HTTPS certificate generation for local development
- **office-addin-manifest**: Tools for validating and working with manifest files

### File Processing
- **file-loader**: Handles file imports (images, fonts, etc.)
- **html-loader**: Processes HTML files and extracts dependencies
- **less**: CSS preprocessor for maintainable styles
- **less-loader**: Integrates LESS compilation into webpack

### Browser Compatibility
- **os-browserify**: Browser polyfill for Node.js 'os' module
- **process**: Browser polyfill for Node.js 'process' global
- **acorn**: JavaScript parser for code analysis and optimization

## Browser Support
- **browserslist**: Defines target browsers for Babel and other tools
  - `last 2 versions`: Support recent versions of major browsers
  - `ie 11`: Support Internet Explorer 11 (still used by some Excel versions)

This configuration ensures our Excel AI Assistant works across all supported Excel environments while providing a modern development experience.