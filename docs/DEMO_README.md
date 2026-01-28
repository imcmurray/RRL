# RRL Demo Site

This is a **static demo** of the Rinse Repeat Labs AI Orchestrator, designed to be hosted on GitHub Pages.

## Live Demo

Visit the live demo at: **https://imcmurray.github.io/RRL/**

## What's Included

The demo showcases the RRL web dashboard with:

- **Dashboard** - Overview of ideas, projects, clients, and financials
- **Ideas Management** - Track app ideas through the pipeline
- **Projects** - View active development projects
- **Clients** - Client relationship management
- **Testers** - Beta testing program management
- **Finances** - Financial dashboard with sample data
- **Agent Portals** - Meet all 12 AI agents
- **Agent Chat** - Interactive chat with simulated AI responses
- **Group Meetings** - Multi-agent discussion simulator

## Demo Mode Features

### What Works
- Full navigation and UI exploration
- Dark/light theme toggle (persisted in localStorage)
- Interactive chat with mock AI responses
- Group meeting simulations
- Filter and view sample data

### What's Simulated
- **AI responses** - Pre-written contextual responses instead of live Claude API calls
- **Data persistence** - Changes are not saved (session only via localStorage)
- **Form submissions** - Show confirmation but don't persist

### Sample Data
All data in the demo is fictional, including:
- Company names, contacts, and emails
- Financial figures and invoices
- Project details and timelines
- Tester information

## Deploying the Demo

### GitHub Pages

1. Enable GitHub Pages in your repository settings
2. Set source to "Deploy from a branch"
3. Select the `main` branch and `/docs` folder
4. The demo will be available at `https://<username>.github.io/RRL/`

### Local Testing

```bash
# From the repo root
cd docs
python -m http.server 8000
# Open http://localhost:8000
```

### Alternative: Any Static Host

The `/docs` folder can be deployed to any static hosting service:
- Netlify
- Vercel
- Cloudflare Pages
- AWS S3 + CloudFront

## File Structure

```
docs/
├── index.html          # Dashboard (main page)
├── agents.html         # All agents overview
├── agent.html          # Individual agent portal + chat
├── meeting.html        # Group meeting simulator
├── ideas.html          # Ideas list
├── projects.html       # Projects list
├── clients.html        # Clients list
├── testers.html        # Testers list
├── finances.html       # Financial dashboard
├── css/
│   └── style.css       # All styles including dark mode
├── js/
│   ├── app.js          # Theme toggle, utilities, chat functions
│   └── demo-data.js    # Sample data and mock AI responses
└── *.md               # Documentation files (existing)
```

## Customizing the Demo

### Change Sample Data
Edit `docs/js/demo-data.js` to customize:
- `DemoData.ideas` - App ideas
- `DemoData.testers` - Beta testers
- `DemoData.clients` - Client companies
- `DemoData.projects` - Development projects
- `DemoData.finances` - Financial data
- `DemoData.agents` - Agent information

### Customize Mock AI Responses
Edit the `MockResponses` object in `demo-data.js` to change what agents say:

```javascript
const MockResponses = {
    ceo: [
        "Your custom CEO response here...",
        "Another response option...",
    ],
    // ... other agents
};
```

### Styling
Edit `docs/css/style.css` for visual customizations. The demo uses:
- Bootstrap 5.3
- Bootstrap Icons
- CSS custom properties for theming

## Security Notes

This demo is safe to share publicly because:
1. No real API keys are used or exposed
2. All data is fictional sample data
3. No backend or server-side processing
4. No sensitive business information

## Differences from Full App

| Feature | Demo | Full App |
|---------|------|----------|
| AI Responses | Pre-written mock | Live Claude API |
| Data Persistence | Session only | JSON files (permanent) |
| Authentication | None | None (local app) |
| Backend | Static files | Flask server |
| CLI Support | No | Yes |
| Real-time Updates | No | HTMX polling |
