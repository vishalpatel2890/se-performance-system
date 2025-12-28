# SE Performance Management System

## Project Overview

An AI-native performance management system for Solution Engineering teams. Built by an SE leader, for SE leaders, to replace generic HR tools that don't understand the pre-sales role.

**License:** MIT

## Architecture

This system uses **Pattern 3: Append-Only Feedback Logs** - a single chronological markdown file per SE that captures all feedback, coaching items, and observations over time. This approach was chosen for:
- Human readability (can review any SE's history in one file)
- Git-friendliness (clean diffs, version controlled)
- Claude-friendliness (single file = full context)
- Low friction (just append to markdown)

## Directory Structure

```
se-performance-system/
├── CLAUDE.md                 # This file - project context
├── PLANNING.md               # Detailed planning and rationale
├── config/                   # Competency models and rubrics
├── data/                     # Transcripts, calendar, Salesforce exports
│   ├── transcripts/          # Gong call transcripts by month
│   ├── calendar/             # Google Calendar exports
│   └── salesforce/           # Deal/opportunity data
├── team/                     # SE profiles and feedback logs
│   ├── _template/            # Templates for new SEs
│   └── {se-name}/            # Individual SE folders
│       ├── profile.md        # SE context and goals
│       ├── feedback-log.md   # Chronological feedback entries
│       ├── 1on1-notes/       # Meeting notes
│       └── reviews/          # Formal review documents
├── outputs/                  # Generated reports and drafts
├── scripts/                  # Integration scripts (Gong, Calendar, SF)
└── .claude/commands/         # Slash commands for workflows
```

## Key Concepts

### SE Competency Dimensions
When rating or discussing SE performance, use these dimensions:
1. **Technical Credibility** - Earning customer trust through expertise
2. **Discovery Quality** - Uncovering pain and quantifying impact  
3. **Demo Excellence** - Showcasing value through tailored demos
4. **Deal Influence** - Impact on deal progression and close rates
5. **Commercial Acumen** - Pricing, packaging, value articulation
6. **Cross-functional Impact** - Enablement, product feedback, mentorship
7. **Workload Management** - Prioritization, balance, avoiding burnout

### Rating Scale
- 5 = Exceptional (role model)
- 4 = Exceeds expectations
- 3 = Meets expectations  
- 2 = Developing
- 1 = Below expectations

### Feedback Log Entry Format
Each entry in an SE's feedback-log.md follows this structure:
```markdown
---
## {DATE} | {CUSTOMER} | {CALL TYPE}
**Transcript:** [[path/to/transcript.md]]
**Opportunity:** {Customer} - ${Amount}
### Dimension Ratings
| Dimension | Rating | Notes |
|-----------|--------|-------|
| Technical Credibility | X/5 | ... |
...
### Observations
**Went Well:** ...
**Development Areas:** ...
### Coaching Items
- [ ] {Item to address in 1:1}
### Notable Quotes
> "..."
---
```

## Slash Commands

### /log-feedback {se-name}
Log structured feedback after reviewing a call. Will:
- Search for matching transcript in data/transcripts/
- Prompt for observations conversationally
- Generate dimension ratings
- Append to SE's feedback-log.md
- Track coaching items

### /prep-1on1 {se-name}
Generate 1:1 preparation. Will:
- Read SE's profile and recent feedback
- List open coaching items
- Suggest talking points
- Identify recognition opportunities

### /draft-review {se-name} {period}
Draft formal performance review. Will:
- Aggregate all feedback for the period
- Calculate dimension trends
- Generate evidence-based assessment
- Suggest goals for next period

### /team-health
Generate team-wide health report. Will:
- Aggregate across all SEs
- Identify patterns and outliers
- Surface systemic issues
- Highlight top performers

### /analyze-call {transcript-path}
AI-assisted call analysis. Will:
- Read transcript
- Identify SE behaviors (positive/developmental)
- Suggest dimension ratings with evidence
- Extract coaching opportunities

## Working with Transcripts

- Transcripts are stored in `data/transcripts/YYYY-MM/`
- Naming convention: `YYYY-MM-DD-customer-call-type.md`
- Reference transcripts in feedback using: `[[../data/transcripts/...]]`
- If no transcript exists, feedback can still be logged from memory

## Integration Notes

### Google Calendar (via MCP)

Calendar integration uses `google-calendar-mcp` for:
- Auto-detecting upcoming 1:1 meetings in `/prep-1on1`
- Showing upcoming 1:1 meetings
- Matching attendees to SE profiles

**Quick Setup:**
1. Create Google Cloud OAuth credentials (Desktop App type) - see `/setup-calendar` for detailed steps
2. Run: `claude mcp add -s user google-calendar -e GOOGLE_OAUTH_CREDENTIALS=/path/to/gcp-oauth.keys.json -- npx @cocal/google-calendar-mcp`
3. Restart Claude Code
4. First use will open browser for Google OAuth sign-in

**Full Setup Guide:** Run `/setup-calendar` for step-by-step instructions including:
- Creating Google Cloud project and enabling Calendar API
- Creating Desktop App OAuth credentials
- Adding the MCP to Claude Code

**MCP Tools Available:**
- `list-events` - Retrieve calendar events
- `search-events` - Search for events by text
- `get-event` - Get event details
- `list-calendars` - List available calendars

See https://github.com/nspady/google-calendar-mcp for additional documentation.

### Other Integrations

**Current State:** Manual data exports
- Gong: Export transcripts manually, save to data/transcripts/
- Salesforce: Export reports, save to data/salesforce/

**Future:** Additional MCP integrations may be added

## Important Behaviors

1. **Always append, never overwrite** - Feedback logs are append-only
2. **Reference evidence** - When discussing performance, cite specific calls/situations
3. **Focus on development** - This is a growth tool, not surveillance
4. **Be specific** - Vague feedback isn't actionable
5. **Track coaching items** - Follow through is critical
6. **CRITICAL: Respect confirmation gates** - When a command shows a y/n confirmation:
  - STOP and wait for the user's response
  - If user says "n", "no", or "cancel" → IMMEDIATELY cancel the operation, do NOT proceed
  - Only proceed with the action if user explicitly says "y" or "yes"
  - This is especially important for destructive operations like archive, delete, or overwrite

## Tone for Generated Content

When generating reviews, feedback, or coaching suggestions:
- Be direct but constructive
- Focus on behaviors, not personality
- Tie feedback to business impact
- Suggest specific actions for improvement
- Recognize strengths before addressing gaps
