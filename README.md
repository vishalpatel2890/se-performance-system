# SE Performance Management System

An AI-native performance management system for Solution Engineering teams. Built by an SE leader, for SE leaders, to replace generic HR tools that don't understand the pre-sales role.

## Quick Start

### Prerequisites

- [Claude Code](https://claude.com/claude-code) CLI or an IDE with Claude Code integration (VS Code, Cursor, etc.)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/se-performance-system.git
   cd se-performance-system
   ```

2. **Create required directories** (gitignored for your data)
   ```bash
   mkdir -p data/transcripts data/calendar data/salesforce
   mkdir -p outputs/reports
   ```

3. **Run the setup wizard**
   ```bash
   claude
   /setup
   ```
   This will prompt you for your name and team name, and configure the system.

4. **Add your first SE**
   ```bash
   /add-se sarah-chen
   ```
   Follow the prompts to create their profile.

### Core Commands

| Command | Description |
|---------|-------------|
| `/setup` | First-time configuration |
| `/add-se <name>` | Add a new SE to your team |
| `/log-feedback <name>` | Log feedback after a call |
| `/prep-1on1 <name>` | Prepare for a 1:1 meeting |
| `/draft-review <name> <period>` | Generate performance review |
| `/analyze-call <path>` | AI-assisted transcript analysis |
| `/career-check <name>` | Career development summary |

## Project Structure

```
se-performance-system/
├── .claude/commands/     # Slash commands (Claude Code)
├── config/
│   ├── competencies/     # Rating frameworks
│   ├── templates/        # Document templates
│   ├── integrations/     # Gong, Calendar configs
│   └── settings.yaml     # Global settings
├── team/
│   ├── _template/        # Template for new SEs
│   └── {se-name}/        # Individual SE folders
├── data/
│   ├── transcripts/      # Call transcripts
│   ├── calendar/         # Calendar exports
│   └── salesforce/       # Deal data
├── outputs/
│   └── reports/          # Generated reports
└── scripts/              # Integration scripts
```

## Competency Framework

### Meeting Competencies (Observable in calls)
- ELI5 (Simplifying complex concepts)
- Checking Understanding
- Dynamic Engagement
- Objection Handling
- Competitive Positioning
- Discovery Depth
- Demo Storytelling

### Role Competencies (Aggregated over time)
- Technical Credibility
- Discovery Quality
- Demo Excellence
- Deal Influence
- Commercial Acumen
- Cross-Functional Impact
- Workload Management

### Rating Scale (Four Stages of Competence)
| Rating | Stage | Description |
|--------|-------|-------------|
| 1 | UI | Unconscious Incompetence |
| 2 | CI | Conscious Incompetence |
| 3 | CC | Conscious Competence |
| 4 | UC | Unconscious Competence |

## Integrations

### Gong (Transcript Sync)
Set environment variables:
```bash
export GONG_ACCESS_TOKEN="your-token"
export GONG_API_KEY="your-key"
```

### Google Calendar
Set environment variables:
```bash
export CALENDAR_ACCESS_TOKEN="your-token"
export CALENDAR_CREDENTIALS_FILE="path/to/credentials.json"
```

### Salesforce
Manual CSV export (API integration not yet implemented).

## Philosophy

1. **Local-first** - Your data stays on your machine
2. **Append-only** - Feedback logs are append-only for auditability
3. **Evidence-based** - Every rating requires specific evidence
4. **Growth-focused** - This is a development tool, not surveillance
5. **AI-native** - Designed for Claude Code from the ground up

## License

MIT (planned open source release)

## Contributing

This project is in active development. Contributions welcome!
