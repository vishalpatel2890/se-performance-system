# /setup - First-Time Setup Wizard

Run this command to configure your SE Performance Management System for first use.

## What This Does

1. Checks if setup has already been completed
2. Prompts for your name and team name
3. Validates all configuration files (YAML syntax, required fields, cross-references)
4. Sets `setup_complete: true` in settings.yaml
5. Provides quick start guidance for next steps

## Usage

```
/setup
```

## Implementation

When this command is run, follow these steps exactly:

### Step 1: Create Required Directories

First, ensure all required directories exist (they are gitignored, so new users won't have them):

```bash
mkdir -p data/transcripts data/calendar data/salesforce
mkdir -p outputs/reports
mkdir -p team
```

Display nothing if successful. Only display an error if directory creation fails.

### Step 2: Read Current State

Read `config/settings.yaml` and check the following fields:
- `setup_complete` - Is setup already done?
- `setup_in_progress` - Is there a partial setup to resume?
- `manager_name` - Current manager name (if any)
- `team_name` - Current team name (if any)

### Step 3: Handle Different States

**If \****`setup_in_progress`**\*\* is true (partial setup detected):**

Display:
```
I noticed setup was interrupted previously.

Would you like to:
1. **Resume** - Continue from where you left off
2. **Restart** - Start fresh from the beginning

Choose (resume/restart):
```

Wait for user response:
- If "resume": Skip prompts that already have values, continue from the next incomplete step
- If "restart": Clear `setup_in_progress` and all partial values, proceed with fresh setup

**If \****`setup_complete`**\*\* is true (setup already done):**

Display:
```
Setup already complete.

Current configuration:
- Manager: {manager_name}
- Team: {team_name}

Would you like to reconfigure? (y/n)
```

Wait for user response:
- If "n" or "no": Display current config summary and exit
- If "y" or "yes": Proceed with setup flow (will overwrite existing values)

**If \****`setup_complete`**\*\* is false (first-time setup):**

Display greeting:
```
Welcome to the SE Performance Management System!

This wizard will help you configure the system for first use. I'll ask for your name and team name, then validate that all configuration files are properly set up.

Let's get started!
```

### Step 4: Collect Manager Name

Set `setup_in_progress: true` in settings.yaml (to enable resume if interrupted).

Prompt:
```
What is your name? (This will be used as the manager name in the system)
```

Wait for user input. After receiving the name:
- Store the value temporarily
- Display confirmation: `Got it! I'll set the manager name to: "{name}"`

### Step 5: Collect Team Name

Prompt:
```
What is your team name? (e.g., "Enterprise SE Team", "West Region SEs")
```

Wait for user input. After receiving the team name:
- Store the value temporarily
- Display confirmation: `Great! Team name will be: "{team_name}"`

### Step 6: Validate Configuration Files

Display:
```
Now I'll validate your configuration files...
```

**Validation Overview:**

There are two types of validation results:
- **ERRORS**: Block setup completion (must be fixed before proceeding)
- **WARNINGS**: Display but allow setup to continue (non-blocking)

---

**6.1 YAML Syntax Validation (ERRORS - blocking):**

For each config file, attempt to parse the YAML. If parsing fails, report with line number:

Files to validate:
- `config/competencies/meeting-competencies.yaml`
- `config/competencies/role-competencies.yaml`
- `config/settings.yaml`

**If YAML syntax is invalid, display:**
```
I couldn't validate {filename}.

Issue: Invalid YAML syntax on line {line_number} - {error_description}
Suggestion: Check for missing colons, incorrect indentation, or unclosed quotes near line {line_number}

Please fix the issue and run /setup again.
```

Stop here - do not proceed until YAML syntax errors are fixed.

---

**6.2 Required Fields Validation (ERRORS - blocking):**

For each competency file, validate the following required structure:

**For meeting-competencies.yaml and role-competencies.yaml:**
- Each competency (e.g., `eli5:`, `technical_credibility:`) must have:
  - `name` (string) - Display name of the competency
  - `level_examples` (object) - Must contain keys 1, 2, 3, and 4
  - Each level_example (1, 2, 3, 4) must have:
    - `stage` (string)
    - `description` (string)
    - `example` (string)

**If required field is missing, display:**
```
I couldn't validate {filename}.

Issue: Competency '{competency_id}' is missing required field: {field_name}
Suggestion: Add the '{field_name}' field to the '{competency_id}' competency definition

Please fix the issue and run /setup again.
```

**If level\_examples is incomplete, display:**
```
I couldn't validate {filename}.

Issue: Competency '{competency_id}' level_examples is missing level {missing_level}
Suggestion: Ensure level_examples contains all four levels (1, 2, 3, 4) for the Four Stages of Competence framework

Please fix the issue and run /setup again.
```

Stop here - do not proceed until required field errors are fixed.

---

**6.3 Type Validation for settings.yaml (ERRORS - blocking):**

Validate that settings.yaml fields have correct types:
- `career_check_threshold_days` must be a number (integer)
- `default_review_period` must be a string
- `setup_complete` must be a boolean (true/false)

**If type mismatch, display:**
```
I couldn't validate settings.yaml.

Issue: Field '{field_name}' has wrong type - expected {expected_type}, got {actual_type} (value: "{actual_value}")
Suggestion: Update '{field_name}' to be a valid {expected_type} (e.g., {example_value})

Please fix the issue and run /setup again.
```

Examples:
- If `career_check_threshold_days: "thirty"` → "expected number, got string (value: 'thirty'). Suggestion: Use a number like 30"
- If `setup_complete: "yes"` → "expected boolean, got string (value: 'yes'). Suggestion: Use true or false"

Stop here - do not proceed until type errors are fixed.

---

**6.4 Cross-Reference Validation (WARNINGS - non-blocking):**

For meeting-competencies.yaml only, check each `maps_to_role` reference:
- Collect all role competency IDs from role-competencies.yaml
- For each meeting competency's `maps_to_role` array, verify each ID exists

Valid role competency IDs (from role-competencies.yaml):
- technical_credibility
- discovery_quality
- demo_excellence
- deal_influence
- commercial_acumen
- cross_functional_impact
- workload_management

**If invalid reference found, display WARNING (but continue):**
```
Warning: Competency '{meeting_competency_id}' maps to unknown role competency '{invalid_reference}'

Valid role competencies are: technical_credibility, discovery_quality, demo_excellence, deal_influence, commercial_acumen, cross_functional_impact, workload_management

This won't block setup, but the mapping won't work correctly until fixed.
```

Collect all warnings and display them together, then CONTINUE with setup (do not stop).

---

**6.5 Validation Success:**

If all ERRORS pass (YAML syntax, required fields, type validation), count competencies and display summary.

**If there were warnings:**
```
Configuration validated with warnings!

{list of warnings}

Proceeding with setup despite warnings. You can fix these later.

- {meeting_count} meeting competencies loaded
- {role_count} role competencies loaded
```

**If no warnings (clean validation):**
```
Configuration validated successfully!
- {meeting_count} meeting competencies loaded
- {role_count} role competencies loaded
```

Note: This follows progressive disclosure - show only summary on success, no verbose output.

### Step 6.6: Optional Integration Setup (Google Calendar)

Check if `integrations.calendar_mcp_offered` in settings.yaml is already `"skipped"`. If so, skip this step entirely.

Display:
```
**Optional: Google Calendar Integration**

The system can integrate with your Google Calendar to:
- Auto-detect your next 1:1 meeting when running /prep-1on1
- Show upcoming 1:1 meetings with SE names resolved

This requires installing the google-calendar-mcp in your Claude Code settings.

Would you like to set this up now?
- **y** = Guide me through setup
- **n** = Skip for now (you can run /setup-calendar later)
- **skip** = Don't ask about this again
```

Wait for user response:
- If "n" or "no": Set `integrations.calendar_mcp_offered: true` in settings, continue to Step 7
- If "skip": Set `integrations.calendar_mcp_offered: "skipped"` in settings, continue to Step 7
- If "y" or "yes": Proceed to calendar setup instructions below

**If user chooses "y" for calendar setup:**

**Step 6.6.1: Create Google Cloud OAuth Credentials**

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
- If "n" or "no": Display "No problem! Complete these steps first, then run /setup-calendar when ready." Continue to Step 7.
- If "y" or "yes": Proceed to Step 6.6.2

**Step 6.6.2: Get Credentials Path**

Display:
```
**Step 2: Provide Credentials Path**

Enter the full path to your gcp-oauth.keys.json file:
(e.g., /Users/yourname/.config/google/gcp-oauth.keys.json)
```

Wait for user to provide the path. Store it as `{credentials_path}`.

**Step 6.6.3: Add MCP to Claude Code**

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
- If "n" or "no": Display "No problem! Run the command when ready, then run /setup-calendar to verify." Continue to Step 7.
- If "y" or "yes": Proceed to verification instructions

**Step 6.6.4: Verification Instructions**

Display:
```
**Step 4: Verify the Setup**

The MCP won't be available in this session - you need to start a new Claude Code session.

To verify it's working:
1. Open a new Claude Code session (or restart this one)
2. Ask: "What's on my calendar next Monday?"

If it works, you'll see your calendar events. If not, check:
- The credentials file path is correct
- You completed the Google OAuth sign-in when prompted
- Run /setup-calendar to troubleshoot

I'll mark calendar integration as pending verification.
```

Set `integrations.calendar_mcp_configured: "pending"`
Set `integrations.calendar_mcp_setup_date: {current ISO date}`

Continue to Step 7.

### Step 7: Confirm and Save

Display what will be saved:
```
Ready to save your configuration:

- Manager Name: {manager_name}
- Team Name: {team_name}
- Setup Complete: true

Save these settings? (y/n)
```

Wait for user response:
- If "n" or "no": Display "Setup cancelled. No changes were made." and exit
- If "y" or "yes": Proceed to save

### Step 8: Update settings.yaml

Update `config/settings.yaml` with:
- `manager_name: "{user's name}"`
- `team_name: "{user's team name}"`
- `setup_complete: true`
- Remove `setup_in_progress` if it exists (clear the partial state flag)

### Step 9: Display Success and Next Steps

Display:
```
Setup complete!

Your SE Performance Management System is ready to use.

**Next Steps:**

1. Run `/add-se {name}` to add your first SE to the team
2. Run `/competencies` to view or customize the competency framework
3. Run `/log-feedback` to start capturing feedback after calls
{if calendar not configured}
4. Run `/setup-calendar` to configure Google Calendar integration
{endif}

Need help? Check the README.md or run any command with --help.
```

Note: Only show step 4 if `integrations.calendar_mcp_configured` is false.

## Error Handling

All error messages should follow ADR-005 Conversational Error Handling:
- Be friendly and avoid technical jargon
- Explain what went wrong clearly
- Suggest how to fix it
- Include line numbers when relevant for YAML errors

Example error format:
```
I couldn't validate meeting-competencies.yaml.

Issue: Missing colon on line 15
Suggestion: Check for a missing ":" after "level_examples"
```

## State Tracking

The wizard tracks partial state using `setup_in_progress` in settings.yaml:
- Set to `true` when wizard starts collecting input
- Cleared (removed) when wizard completes successfully
- If user interrupts (Ctrl+C) mid-wizard, this flag remains `true`
- On next `/setup` run, detect this flag and offer to resume
