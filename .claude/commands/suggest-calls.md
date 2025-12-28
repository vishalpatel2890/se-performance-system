# /suggest-calls - Suggest Calls to Review from Calendar

Suggest which customer calls to review based on calendar activity, cross-referencing with feedback logs to show reviewed vs unreviewed calls.

## What This Does

1. Checks Google Calendar MCP availability
2. Retrieves customer calls from calendar (last N days) using MCP
3. Cross-references with feedback logs to identify reviewed/unreviewed
4. Checks Gong transcript availability for unreviewed calls
5. Displays grouped results by SE
6. Allows selection to start pre-populated /log-feedback

## Usage

```
/suggest-calls              # Suggest calls to review from last 7 days
```

**Natural Language Triggers:**
- "What calls should I review?"
- "Which calls need feedback?"
- "Suggest calls to review"
- "Show unreviewed calls"

## Implementation

When this command is run, follow these steps exactly:

### Step 1: Check Calendar Integration (MCP-based)

**1.1 Check if Google Calendar MCP is available:**
- Check if the `google-calendar-mcp` tools are available (list-events, search-events, get-event)
- If MCP tools are NOT available, display setup instructions and exit

**1.2 If MCP not configured, display:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 CALENDAR INTEGRATION NOT CONFIGURED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

To suggest calls for review, Google Calendar MCP is required.

Setup instructions:
1. Install the google-calendar-mcp:

   claude mcp add -s user google-calendar -e GOOGLE_OAUTH_CREDENTIALS=/path/to/gcp-oauth.keys.json -- npx @cocal/google-calendar-mcp

2. Restart Claude Code

3. First use will open browser for Google OAuth sign-in

For detailed setup, see: https://github.com/nspady/google-calendar-mcp
Or run `/setup-calendar` for step-by-step guidance.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
Then **STOP** - do not continue to other steps.

**1.3 Check if config/integrations/calendar.yaml exists:**
- Read the file to get `query.lookback_days` (default: 7)
- Store as `lookback_days`

**1.4 MCP handles authentication automatically:**
- OAuth is handled via browser-based flow by the MCP
- If calendar query fails, MCP will prompt for re-authentication

### Step 2: Retrieve Customer Calls from Calendar (using MCP)

**2.1 Load configuration:**
- Read `config/integrations/calendar.yaml`
- Get `query.lookback_days` (default: 7)
- Get `exclude_patterns` for filtering
- Get `one_on_one_keywords` to identify 1:1s (to exclude from customer calls)

**2.2 Display progress:**
```
Checking calendar for recent customer meetings (last {lookback_days} days)...
```

**2.3 Get list of SE folders:**
- List all directories in `team/` excluding `_template/` and `_archived/`
- Store as `se_folders[]`

**2.4 Query calendar events using MCP:**
Use the Google Calendar MCP `list-events` tool with:
- `timeMin`: {lookback_days} days ago (calculate date)
- `timeMax`: now (today's date/time)
- `maxResults`: 100

Note: We query PAST events (not future) to find calls that need review.

**2.5 Identify customer calls (NOT 1:1s or internal meetings):**
For each calendar event:
- Skip if title matches `exclude_patterns` from config (team meeting, all hands, standup, sprint, planning, retro, sync, internal)
- Skip if title matches `one_on_one_keywords` from config (1:1, 1on1, check-in, one on one)
- Include if has external attendees (non-company email domains)
- Include if title contains customer-related keywords (demo, discovery, technical, POC, executive briefing)

**2.6 Match events to SEs:**
For each customer call event:
- Check attendees list
- Match attendee names/emails to `se_folders[]` using fuzzy matching (Levenshtein distance <= 2)
- Extract: date, SE name, customer (from title or attendee domain), call type (from title)

**2.7 Store as \****`calendar_calls[]`**\*\*:**
```yaml
- date: "2024-12-18"
  se: "sarah-chen"
  customer: "Acme"
  call_type: "Technical Deep-dive"
  event_title: "Acme Technical Call"
```

### Step 3: Cross-Reference with Feedback Logs

**3.1 For each SE in \****`se_folders[]`**\*\*:**
- Read `team/{se-name}/feedback-log.md`
- Parse all feedback entries

**3.2 Parse feedback entries:**
Each entry starts with `## YYYY-MM-DD | {Customer} | {Call Type}`

For each entry, extract:
- Date (from header, format: YYYY-MM-DD)
- Customer name (from header)
- Call type (from header)

Store as `feedback_entries[]`:
```yaml
- se: "sarah-chen"
  date: "2024-12-15"
  customer: "Nordstrom"
  call_type: "Discovery"
```

**3.3 Match calendar events to feedback entries:**
For each `calendar_call`:
- Search `feedback_entries` for matching:
  - Same SE name
  - Same date (exact match)
  - Similar customer name (case-insensitive, fuzzy match)
- If match found: set `reviewed = true`, `feedback_logged = true`
- If no match: set `reviewed = false`

**3.4 Store matching results:**
```yaml
reviewed:
  - date: "2024-12-15"
    se: "sarah-chen"
    customer: "Nordstrom"
    call_type: "Discovery"
    feedback_logged: true

unreviewed:
  - date: "2024-12-18"
    se: "sarah-chen"
    customer: "Acme"
    call_type: "Technical Deep-dive"
    gong_available: false
    event_title: "Acme Technical Call"
```

### Step 4: Check Gong Transcript Availability

**4.1 For each unreviewed call:**
- Construct expected transcript path: `data/transcripts/YYYY-MM/`
- List files in that directory

**4.2 Match by date and customer:**
- Look for files matching pattern: `YYYY-MM-DD-{customer}-*.md`
- Customer matching is case-insensitive, fuzzy (Levenshtein distance <= 2)
- Also check file contents for customer name if filename doesn't match

**4.3 If transcript found:**
- Set `gong_available = true`
- Store `transcript_path` for use in log-feedback

**4.4 If no transcript found or data/transcripts/ doesn't exist:**
- Set `gong_available = false`

### Step 5: Format and Display Results

**5.1 Group calls by SE:**
- Sort SEs alphabetically
- Within each SE, sort calls by date (most recent first)

**5.2 Display header:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📞 CALLS TO REVIEW (last {lookback_days} days)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**5.3 Display reviewed section:**
If any reviewed calls exist:
```
Reviewed:
```
For each reviewed call:
```
✓ {YYYY-MM-DD} {SE Display Name} - {Customer} {Call Type} (feedback logged)
```

If no reviewed calls:
```
Reviewed:
  (none in this period)
```

**5.4 Display unreviewed section:**
If any unreviewed calls exist:
```
Not Yet Reviewed:
```
For each unreviewed call, grouped by SE:
```
○ {YYYY-MM-DD} {SE Display Name} - {Customer} {Call Type} [Gong transcript available]
```
Note: Only show "[Gong transcript available]" if `gong_available = true`

If no unreviewed calls:
```
Not Yet Reviewed:
  (all calls have feedback logged!)
```

**5.5 Display counts:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Reviewed: {X} | Not Yet Reviewed: {Y}
```

**5.6 If no calendar events found at all:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📞 CALLS TO REVIEW (last {lookback_days} days)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

No customer calls found in the last {lookback_days} days.

This could mean:
- No customer meetings on your calendar in this period
- Meetings don't match customer call patterns (check exclude_patterns in config)
- Calendar MCP may need re-authentication

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
Then **STOP** - do not continue to Step 6.

### Step 6: Selection and Handoff to log-feedback

**6.1 Display selection prompt:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Log feedback for any of these? (enter date/customer or 'skip')
```

**6.2 Wait for user input**

**6.3 Handle "skip" or empty input:**
If user enters "skip", "s", "", or nothing:
```
✓ No action taken.
```
Then **STOP**.

**6.4 Parse user selection:**
Accept multiple input formats:
- Date only: "2024-12-18" or "12-18" or "18"
- Customer only: "Acme" or "acme"
- Combined: "sarah 2024-12-18" or "Acme 12-18"
- SE-date-customer: "sarah-chen 2024-12-18 Acme"

**6.5 Find matching unreviewed call:**
- Search unreviewed calls for match
- Use fuzzy matching for customer name (Levenshtein distance <= 2)
- Date matching: exact match required

**6.6 If no match found:**
```
I couldn't find a matching unreviewed call for "{input}".

Available unreviewed calls:
{list unreviewed calls with numbers}

Try again with a date or customer name, or enter 'skip' to exit.
```
Go back to Step 6.1.

**6.7 If match found, confirm selection:**
```
Selected: {date} | {SE Display Name} | {Customer} | {Call Type}
```

**6.8 If Gong transcript available, offer analysis:**
```
Gong transcript available: {transcript_path}
Analyze transcript first? (y/n)
```

If 'y' or 'yes':
- Run `/analyze-call {transcript_path}` first
- Then continue to Step 6.9

If 'n' or 'no':
- Continue directly to Step 6.9

**6.9 Start /log-feedback with pre-populated context:**
```
Starting feedback log...
```

Launch `/log-feedback {se-name}` with context:
- Pre-set date to selected call date
- Pre-set customer to selected customer
- Pre-set call_type to selected call type
- If Gong transcript available, pre-set transcript_path

Display:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 Logging feedback for {SE Display Name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Call context (pre-populated):
  Date: {date}
  Customer: {customer}
  Call Type: {call_type}
  {If transcript: Transcript: {transcript_path}}
```

Then hand off to /log-feedback flow, skipping the call details collection step.

## Example Session

```
> What calls should I review?

Checking calendar for recent customer meetings (last 7 days)...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📞 CALLS TO REVIEW (last 7 days)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Reviewed:
✓ 2024-12-15 Sarah Chen - Nordstrom Discovery (feedback logged)
✓ 2024-12-14 Marcus Johnson - Target Demo (feedback logged)

Not Yet Reviewed:
○ 2024-12-18 Sarah Chen - Acme Technical Deep-dive [Gong transcript available]
○ 2024-12-17 Alex Rivera - BigCorp Executive Briefing
○ 2024-12-16 Marcus Johnson - RetailCo Discovery

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Reviewed: 2 | Not Yet Reviewed: 3
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Log feedback for any of these? (enter date/customer or 'skip') Acme

Selected: 2024-12-18 | Sarah Chen | Acme | Technical Deep-dive

Gong transcript available: data/transcripts/2024-12/2024-12-18-acme-technical.md
Analyze transcript first? (y/n) n

Starting feedback log...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 Logging feedback for Sarah Chen
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Call context (pre-populated):
  Date: 2024-12-18
  Customer: Acme
  Call Type: Technical Deep-dive
  Transcript: data/transcripts/2024-12/2024-12-18-acme-technical.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 COMPETENCY RATINGS (1-4, or Enter to skip)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Rating scale: 1=UI (unaware) | 2=CI (struggling) | 3=CC (deliberate) | 4=UC (natural)

eli5 (simplify complex concepts):
...
```

## Example Session - No Calendar Integration

```
> What calls should I review?

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 CALENDAR INTEGRATION NOT CONFIGURED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

To suggest calls for review, Google Calendar MCP is required.

Setup instructions:
1. Install the google-calendar-mcp:

   claude mcp add -s user google-calendar -e GOOGLE_OAUTH_CREDENTIALS=/path/to/gcp-oauth.keys.json -- npx @cocal/google-calendar-mcp

2. Restart Claude Code

3. First use will open browser for Google OAuth sign-in

For detailed setup, see: https://github.com/nspady/google-calendar-mcp
Or run `/setup-calendar` for step-by-step guidance.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Example Session - Skip Selection

```
> /suggest-calls

Checking calendar for recent customer meetings (last 7 days)...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📞 CALLS TO REVIEW (last 7 days)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Reviewed:
  (none in this period)

Not Yet Reviewed:
○ 2024-12-18 Sarah Chen - Acme Technical Deep-dive

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Reviewed: 0 | Not Yet Reviewed: 1
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Log feedback for any of these? (enter date/customer or 'skip') skip

✓ No action taken.
```

## Error Handling (ADR-005)

**No SEs exist:**
```
There are no SE profiles yet. Run `/add-se {name}` to create one.
```

**Calendar MCP error:**
```
Calendar query failed: {error_message}

The Google Calendar MCP may need re-authentication.
Try running `/setup-calendar` to verify the connection.
```

**MCP not available:**
```
Google Calendar MCP is not configured.
Run `/setup-calendar` for setup instructions.
```

**No team/ directory:**
```
The team/ directory doesn't exist. Run `/setup` to initialize the project.
```

## Configuration

**Date range configuration:**
- Default: 7 days (configurable via `config/integrations/calendar.yaml`)
- Key: `query.lookback_days`

**Customer call detection (from calendar.yaml):**
- `exclude_patterns`: team meeting, all hands, standup, sprint, planning, retro, sync, internal
- `one_on_one_keywords`: 1:1, 1on1, check-in, one on one (excluded from customer calls)
- Include if: has external attendees OR title contains customer-related keywords
- Customer keywords: demo, discovery, technical, POC, executive, briefing

## Performance

Target: Call review suggestion generation should complete in < 5 seconds for calendar + feedback cross-reference.

## Related Commands

- `/log-feedback {se-name}` - Log feedback for an SE (target of handoff)
- `/analyze-call {transcript-path}` - AI-assisted transcript analysis
- `/prep-1on1 {se-name}` - Prepare for 1:1 meeting
- `/setup-calendar` - Configure Google Calendar MCP integration

---

## Google Calendar MCP Tools Reference

This command uses the following tools from `google-calendar-mcp`:

| Tool | Usage in This Command |
| --- | --- |
| `list-events` | Retrieve past calendar events with date filtering (last N days) |
| `search-events` | Find events matching text query (optional, for specific customer lookup) |
| `get-event` | Get full details of a specific event (attendees, description) |

**MCP Setup:** See https://github.com/nspady/google-calendar-mcp for installation and OAuth configuration, or run `/setup-calendar` for guided setup.
