# /setup-calendar - Configure Google Calendar Integration

Configure or verify the Google Calendar MCP integration for calendar-based 1:1 detection.

## What This Does

1. Shows current calendar integration status
2. Guides you through MCP setup (if not configured)
3. Tests if the MCP is properly installed
4. Updates your integration status in settings.yaml

## Usage

```
/setup-calendar
```

## Implementation

When this command is run, follow these steps exactly:

### Step 1: Check Current Status

Read `config/settings.yaml` and check:
- `integrations.calendar_mcp_configured` - Has MCP been configured?
- `integrations.calendar_mcp_setup_date` - When was it configured?

**If already configured (`calendar_mcp_configured: true`):**

Display:
```
**Google Calendar Integration Status**

✓ Previously configured: {calendar_mcp_setup_date}

Let me verify the MCP is still working...
```

Proceed to Step 3 (Test MCP) to verify current status.

**If not configured (`calendar_mcp_configured: false` or missing):**

Display:
```
**Google Calendar Integration Status**

○ Not yet configured

This integration enables:
- Auto-detect next 1:1 in /prep-1on1 (no need to specify SE name)
- Show upcoming 1:1 meetings with SE names resolved
- Calendar-aware meeting preparation

Would you like to set this up now? (y/n)
```

Wait for user response:
- If "n" or "no": Display "No changes made. Run /setup-calendar when you're ready." and exit
- If "y" or "yes": Proceed to Step 2

### Step 2: Create Google Cloud OAuth Credentials

Display:
```
**Step 1: Create Google Cloud OAuth Credentials**

You'll need to create a "Desktop App" OAuth credential in Google Cloud Console.

1. Go to https://console.cloud.google.com

2. Create a new project (or select existing):
   - Click the project dropdown at the top
   - Click "New Project"
   - Name it something like "Calendar MCP" and create

3. Enable the Google Calendar API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Calendar API"
   - Click on it and click "Enable"

4. Create OAuth Credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - **IMPORTANT: Select "Desktop app" as application type**
   - Name it (e.g., "Calendar MCP Desktop")
   - Click "Create"

5. Download the credentials:
   - Click the download icon next to your new credential
   - Save the file as `gcp-oauth.keys.json`
   - Move it to a safe location (e.g., ~/.config/google/)

Have you completed these steps and downloaded the credentials file? (y/n)
```

Wait for user response:
- If "n" or "no":
  ```
  No problem! Complete the steps above to create your Google Cloud credentials.

  Run /setup-calendar again when you have the credentials file ready.
  ```
  Exit without making changes.

- If "y" or "yes": Proceed to Step 2.2

### Step 2.2: Get Credentials Path

Display:
```
**Step 2: Provide Credentials Path**

Enter the full path to your gcp-oauth.keys.json file:
(e.g., /Users/yourname/.config/google/gcp-oauth.keys.json)
```

Wait for user to provide the path. Store it as `{credentials_path}`.

### Step 2.3: Add MCP to Claude Code

Display:
```
**Step 3: Add the MCP to Claude Code**

Run this command in your terminal to add the Google Calendar MCP:

claude mcp add -s user google-calendar -e GOOGLE_OAUTH_CREDENTIALS={credentials_path} -- npx @cocal/google-calendar-mcp

This command:
- Adds the MCP to your user-level Claude Code configuration
- Sets the path to your OAuth credentials
- Uses the @cocal/google-calendar-mcp package

After running the command, restart Claude Code to load the MCP.

On first use, it will open your browser to complete Google OAuth sign-in.

Have you run the command? (y/n)
```

Wait for user response:
- If "n" or "no":
  ```
  No problem! Run the command above when ready, then run /setup-calendar again to verify.
  ```
  Exit without making changes.

- If "y" or "yes": Proceed to Step 3

### Step 3: Verification Instructions

Display:
```
**Step 4: Verify the Setup**

The MCP won't be available in this session - you need to start a new Claude Code session.

To verify it's working:
1. Open a new Claude Code session (or restart this one)
2. Ask: "What's on my calendar next Monday?"

If it works, you'll see your calendar events!

If it doesn't work, check:
- The credentials file path is correct in the command you ran
- You completed the Google OAuth sign-in when prompted in browser
- The MCP command output showed no errors

I'll mark calendar integration as pending verification.
```

Update settings.yaml:
- Set `integrations.calendar_mcp_configured: "pending"`
- Set `integrations.calendar_mcp_setup_date: {current ISO date}`

### Step 4: Exit

Display:
```
**Next Steps:**

1. Start a new Claude Code session
2. Test with: "What's on my calendar next Monday?"
3. Once verified, try:
   - "Show my upcoming 1:1s" to see detected 1:1 meetings
   - `/prep-1on1` without an SE name to auto-detect from calendar

View calendar config: config/integrations/calendar.yaml
```

## Error Handling

All error messages should follow ADR-005 Conversational Error Handling:
- Be friendly and avoid technical jargon where possible
- Explain what went wrong clearly
- Suggest specific actions to fix the issue
- Include links to documentation when helpful

## Configuration Reference

The calendar integration uses settings from `config/integrations/calendar.yaml`:

```yaml
# Keywords to identify 1:1 meetings
one_on_one_keywords:
  - "1:1"
  - "1on1"
  - "check-in"

# Patterns to exclude from 1:1 detection
exclude_patterns:
  - "team meeting"
  - "all hands"
  - "standup"

# Query settings
query:
  lookahead_days: 7
  max_results: 50
```

You can edit this file to customize how 1:1 meetings are detected.
