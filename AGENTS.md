# AGENTS.md

## Overview
Simple GitHub Pages site for "The Delight of Composition" - a music composition sharing platform.

## Deployment
- Hosted on GitHub Pages at `twmcdunn.github.io`
- Custom domain: `delightofcomposition.org` (see `CNAME`)
- Changes to `main` branch deploy automatically

## Tech Stack
- Pure static HTML/CSS/JS (no build tools)
- AWS DynamoDB for data storage (credentials hardcoded in `script.js`)
- AWS Cognito for identity (credentials hardcoded in `script.js:5-8`)
- Google OAuth for user authentication

## No Build/Test Commands
This repo has no `package.json`, tests, linting, or build scripts. Edit files directly.

## Key Files
- `index.html`: Main page with inline CSS and JavaScript
- `script.js`: AWS DynamoDB client and data operations
- `CNAME`: Custom domain configuration
- `music/`: Audio files directory
