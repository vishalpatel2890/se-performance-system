# /add-se - Add New SE Profile

Add a new Solution Engineer to your team with their profile and empty feedback log.

## What This Does

1. Creates a new folder in `team/{se-name}/`
2. Creates profile.md with collected information
3. Creates empty feedback-log.md from template
4. Creates empty subdirectories for 1:1 notes and reviews
5. Optionally captures career aspirations

## Usage

```
/add-se sarah-chen
/add-se "Sarah Chen"
```

## Arguments

- `se-name`: The SE's name in any format - will be normalized to lowercase-hyphen (e.g., "Sarah Chen" becomes "sarah-chen")

## Implementation

When this command is run, follow these steps exactly:

### Step 1: Parse and Normalize SE Name

Take the argument provided and normalize it to lowercase-hyphen format:

**Normalization Rules:**
1. Convert to lowercase
2. Replace spaces with hyphens
3. Remove any special characters except hyphens
4. Collapse multiple hyphens to single hyphen
5. Trim leading/trailing hyphens

**Examples:**
- `"Sarah Chen"` → `sarah-chen`
- `"sarah chen"` → `sarah-chen`
- `"SARAH-CHEN"` → `sarah-chen`
- `"Sarah  Chen"` → `sarah-chen`
- `"Sarah_Chen"` → `sarah-chen`

After normalization, display:
```
Creating profile for: {normalized_se_name}
```

### Step 2: Check for Existing SE

Check if directory `team/{se-name}/` already exists.

**If directory exists:**

Display:
```
An SE profile already exists for {se-name}.

Would you like to:
1. **View** - Display the current profile
2. **Edit** - Update profile information

Choose (view/edit) or 'cancel' to exit:
```

Wait for user response:
- If "view": Read and display `team/{se-name}/profile.md` formatted nicely, then exit
- If "edit": Display "Edit functionality coming in Story 2.2. For now, you can manually edit team/{se-name}/profile.md" and exit
- If "cancel": Display "Cancelled. No changes made." and exit
- If unclear: Ask for clarification

**If directory does NOT exist:**

Proceed to Step 3.

### Step 3: Collect SE Information (Required Fields)

Read `config/settings.yaml` to get the `manager_name` value for default.

**3.1 Prompt for Full Name:**
```
What is the SE's full name? (for display purposes)
```
Wait for input. Store as `{display_name}`.

**3.2 Prompt for Title:**
```
What is their job title? (e.g., "Solutions Engineer", "Senior SE", "Principal SE")
```
Wait for input. Store as `{title}`.

**3.3 Prompt for Start Date:**
```
When did they start? (YYYY-MM-DD format, e.g., 2023-06-15)
```
Wait for input. Validate format:
- If valid YYYY-MM-DD format: Store as `{start_date}`
- If invalid: Display "Please enter date in YYYY-MM-DD format (e.g., 2023-06-15)" and re-prompt

**3.4 Prompt for Manager:**
```
Who is their manager? (press Enter to use default: {manager_name from settings.yaml, or "not set" if empty})
```
Wait for input:
- If user presses Enter (empty input): Use `manager_name` from settings.yaml (or leave as "Not set" if empty)
- If user enters a name: Use that name
Store as `{manager}`.

**3.5 Prompt for Focus Areas:**
```
What are their focus areas? (e.g., "Retail, CPG, Financial Services" - comma-separated)
```
Wait for input. Store as `{focus_areas}`.

### Step 4: Collect Career Aspirations (Optional)

Display:
```
Now let's capture career aspirations (optional - press Enter to skip any question):
```

**4.1 Prompt for Target Role:**
```
What role are they working toward? (e.g., "Principal SE", "SE Manager")
```
Wait for input. Store as `{target_role}` or "Not yet defined" if skipped.

**4.2 Prompt for Timeline:**
```
What's their target timeline? (e.g., "12-18 months", "2-3 years")
```
Wait for input. Store as `{timeline}` or "Not yet defined" if skipped.

**4.3 Prompt for Motivation:**
```
What motivates this career goal? (brief description)
```
Wait for input. Store as `{motivation}` or "Not yet discussed" if skipped.

### Step 5: Display Summary and Confirm

Display summary:
```
Here's the profile I'll create for {display_name}:

**SE Profile Summary**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Name: {display_name}
Folder: team/{se-name}/
Title: {title}
Start Date: {start_date}
Manager: {manager}
Focus Areas: {focus_areas}

**Career Aspirations**
Target Role: {target_role}
Timeline: {timeline}
Motivation: {motivation}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This will create:
- team/{se-name}/profile.md
- team/{se-name}/feedback-log.md
- team/{se-name}/1on1-notes/ (empty directory)
- team/{se-name}/reviews/ (empty directory)

Create profile? (y/n)
```

Wait for user response:
- If "n" or "no": Display "Profile creation cancelled. No files were created." and exit
- If "y" or "yes": Proceed to Step 6

### Step 6: Create Directory Structure

Create the following:
1. Directory: `team/{se-name}/`
2. Directory: `team/{se-name}/1on1-notes/`
3. Directory: `team/{se-name}/reviews/`

### Step 7: Create Profile File

Get today's date in YYYY-MM-DD format for timestamps.

Create `team/{se-name}/profile.md` with the following content (replace all placeholders):

```markdown
# {display_name} - SE Profile

**Created:** {today's date}
**Last Updated:** {today's date}

---

## Current Role

**Title:** {title}
**Team:** {team_name from settings.yaml, or "Not set"}
**Focus Areas:** {focus_areas}
**Territory/Segment:** Not specified
**Start Date:** {start_date}

---

## Job Performance

### Strengths

- To be identified through feedback
-
-

### Development Areas

- To be identified through feedback
-

### Current Quarter Goals

1. To be set in next 1:1
2.
3.

### Key Metrics (Current Quarter)

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| POC Close Rate | TBD | - | - |
| Deal Influence | TBD | - | - |
| Customer Satisfaction | TBD | - | - |

---

## Career Aspirations

### Short-Term (6-12 months)

{target_role} - {timeline}

{motivation}

### Medium-Term (1-2 years)

To be discussed in career conversations.

### Long-Term (3-5 years)

To be discussed in career conversations.

### Skills to Develop

- To be identified
-
-

---

## Working Style

### Communication Preferences

To be discussed in 1:1s.

### Feedback Style

To be discussed in 1:1s.

### Motivators

- To be identified
-

### Stressors

- To be identified
-

---

## Notes

Profile created via /add-se command. Update this section with relevant notes from 1:1s and observations.
```

### Step 8: Create Feedback Log

Read `team/_template/feedback-log.md` and create `team/{se-name}/feedback-log.md` with placeholders replaced:
- Replace `{{se_name}}` with `{display_name}`
- Replace `{{created_date}}` with today's date

### Step 9: Display Success Message

Display:
```
Profile created for {display_name}.

**Files Created:**
- team/{se-name}/profile.md
- team/{se-name}/feedback-log.md
- team/{se-name}/1on1-notes/ (directory)
- team/{se-name}/reviews/ (directory)

**Next Steps:**
Run `/log-feedback {se-name}` to add your first feedback entry.
```

## Error Handling

All error messages should follow ADR-005 Conversational Error Handling:

**If team/ directory doesn't exist:**
```
I can't create the SE profile because the team/ directory doesn't exist.

This usually means the project isn't set up yet. Try running /setup first, or create the team/ directory manually.
```

**If templates are missing:**
```
I couldn't find the feedback log template at team/_template/feedback-log.md.

This file should have been created during project setup. You may need to restore it from the default configuration.
```

**If file write fails:**
```
I couldn't create the profile files.

Issue: {error description}
Suggestion: Check that you have write permissions to the team/ directory.
```

## Example Session

```
> /add-se "Sarah Chen"

Creating profile for: sarah-chen

What is the SE's full name? (for display purposes)
> Sarah Chen

What is their job title?
> Senior Solutions Engineer

When did they start? (YYYY-MM-DD format)
> 2023-06-15

Who is their manager? (press Enter to use default: Vishal)
> [Enter]

What are their focus areas?
> Retail, CPG

Now let's capture career aspirations (optional - press Enter to skip):

What role are they working toward?
> Principal SE

What's their target timeline?
> 12-18 months

What motivates this career goal?
> Lead strategic accounts and mentor junior SEs

[Summary displayed]

Create profile? (y/n)
> y

Profile created for Sarah Chen.

Files Created:
- team/sarah-chen/profile.md
- team/sarah-chen/feedback-log.md
- team/sarah-chen/1on1-notes/ (directory)
- team/sarah-chen/reviews/ (directory)

Next Steps:
Run `/log-feedback sarah-chen` to add your first feedback entry.
```
