# /profile - View, Update, Archive, Export, and Search SE Profile

Comprehensive SE profile management including view, update, archive, export, and feedback search.

## What This Does

1. Views an SE's profile with a formatted summary
2. Updates individual profile fields with confirmation gates
3. Archives SEs who leave (moves to `team/_archived/`)
4. Exports SE data in markdown or JSON format
5. Searches feedback entries by keyword, date range, or customer
6. **Views feedback history summary** with total entries, date range, and open coaching items
7. **Shows specific feedback entries** by date with full details
8. Uses fuzzy matching to find SE profiles from partial names
9. Preserves all other profile data when making updates

## Usage

```
/profile sarah-chen                    # View Sarah's profile
/profile sarah view                    # Same - view profile
/profile sarah-chen update title       # Update Sarah's title
/profile sara                          # Fuzzy match - will suggest sarah-chen

# Archive operations
/profile sarah-chen archive            # Archive Sarah (moves to team/_archived/)
Archive sarah-chen                     # Natural language archive

# Export operations
/profile sarah-chen export             # Export Sarah's data (prompts for format)
/profile sarah-chen export markdown    # Export as markdown
/profile sarah-chen export json        # Export as JSON
Export Sarah's data                    # Natural language export
Export Sarah's data as JSON            # Natural language export with format

# Search operations
/profile sarah-chen search ROI         # Search Sarah's feedback for "ROI"
Search Sarah's feedback for ROI        # Natural language keyword search
Show Sarah's feedback from Q4          # Date range filter
Show Sarah's feedback from Q4 2024     # Date range with year
Show Sarah's feedback from last 30 days # Relative date range
Show feedback for Nordstrom            # Search by customer name

# Feedback history operations
/profile sarah-chen history            # View feedback history summary
Show Sarah's feedback history          # Natural language history view

# Specific entry view
Show me December 15th                  # View full entry for specific date
Show 2025-12-15                        # View entry using ISO date format
```

## Arguments

- `se-name`: The SE's name (can be partial - fuzzy matching will find closest match)
- `action`: Optional - "view" (default), "update", "archive", "export", "search", "history"
- `field`: For update - which field to change
- `format`: For export - "markdown" or "json"
- `query`: For search - keyword, date range, or customer name
- `date`: For detail view - specific date to show entry for (e.g., "December 15th", "2025-12-15")

## Implementation

When this command is run, follow these steps exactly:

### Step 1: Parse Input and Resolve SE Name

**1.1 Normalize the input:**
- Convert to lowercase
- Replace spaces with hyphens
- Remove special characters except hyphens
- Collapse multiple hyphens

**1.2 List all SE folders:**
```
List all subdirectories in team/ directory
Exclude: _template/, _archived/, any files (only directories)
```

**1.3 Fuzzy Match Algorithm (Levenshtein Distance):**

For each SE folder name, calculate the Levenshtein distance from the normalized input. A match is considered "good" if:
- Exact match (distance = 0)
- Very close match (distance ≤ 2 AND length difference ≤ 2)
- The input is a substring of the folder name
- The folder name starts with the input

**Matching Rules:**
1. **Exact match found** → Use that SE directly
2. **Single good match found** → Use that SE (with brief confirmation in output)
3. **Multiple matches found** → List all suggestions and ask user to clarify
4. **No matches found** → Display conversational error with suggestions

**If no SEs exist in the team folder:**
```
There are no SE profiles yet.

Run `/add-se {name}` to create your first SE profile.
```

**If no match found but some SEs exist:**
```
I couldn't find an SE named "{input}".

Did you mean one of these?
  - sarah-chen
  - marcus-johnson
  - alex-rivera

Or run `/add-se {input}` to create a new profile.
```

### Step 2: Determine Action

Parse the action from arguments or the user's natural language request:

**View indicators:** "view", "show", "display", "get", "what is", "see", "profile" (no other action specified)
**Update indicators:** "update", "change", "set", "modify", "edit", "make"
**Archive indicators:** "archive", "deactivate", "offboard", "remove" (followed by SE name)
**Export indicators:** "export", "download", "backup", "export data", "get data"
**Search indicators:** "search", "find", "look for", "feedback for", "feedback from", "show feedback"

**History indicators:** "feedback history", "history" (when used with SE name, without specific search criteria)
**Detail View indicators:** "show me {date}", "show {date}" (requesting specific date entry)

**Action Priority (when multiple indicators present):**
1. Archive - if "archive" keyword present
2. Export - if "export" keyword present
3. Detail View - if requesting a specific date (e.g., "show me December 15th", "show 2025-12-15")
4. History - if "feedback history" or "history" present WITHOUT specific search criteria
5. Search - if "search", "feedback for", "feedback from" present WITH search criteria (keyword, date range, customer)
6. Update - if update indicators present with field name
7. View - default

If action unclear, default to **view**.

### Step 3A: VIEW Profile

If action is VIEW:

**3A.1 Read Profile File:**
Read `team/{se-name}/profile.md` completely.

**3A.2 Parse Profile Sections:**
Extract these fields:
- **Header:** Display Name (from H1 title)
- **Metadata:** Created date, Last Updated date
- **Current Role:** Title, Team, Focus Areas, Territory/Segment, Start Date
- **Career Aspirations (Short-Term):** Target Role, Timeline, Motivation
- **Growth Objectives:** Count unchecked `[ ]` items as "active"
- **Development Actions:** Count unchecked `[ ]` items as "in progress" (note: these may not exist yet in profile structure)
- **Skills to Develop:** Count unchecked `[ ]` items

**3A.3 Display Formatted Summary:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 SE Profile: {Display Name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Current Role**
├─ Title: {title}
├─ Team: {team}
├─ Focus Areas: {focus_areas}
├─ Start Date: {start_date}
└─ Territory: {territory}

**Career Aspirations**
├─ Target Role: {target_role}
├─ Timeline: {timeline}
└─ Motivation: {motivation}

**Progress Tracking**
├─ Skills to Develop: {skills_count} identified
├─ Current Quarter Goals: {goals_count} set
└─ Strengths Identified: {strengths_count}

**Metadata**
├─ Created: {created_date}
└─ Last Updated: {last_updated}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Quick Actions:**
- `/profile {se-name} update title` - Change title
- `/profile {se-name} update focus-areas` - Update focus areas
- View full profile: `team/{se-name}/profile.md`
```

### Step 3B: UPDATE Profile

If action is UPDATE:

**3B.1 Identify Field to Update:**

Parse which field the user wants to update. Supported fields:
- `title` → Updates "**Title:**" line in Current Role section
- `focus-areas` → Updates "**Focus Areas:**" line in Current Role section
- `team` → Updates "**Team:**" line in Current Role section
- `territory` → Updates "**Territory/Segment:**" line in Current Role section
- `target-role` → Updates target role in Career Aspirations Short-Term section
- `timeline` → Updates timeline in Career Aspirations Short-Term section
- `motivation` → Updates motivation in Career Aspirations Short-Term section

If field not specified or unclear:
```
What would you like to update for {display_name}?

Available fields:
1. title - Job title (e.g., "Senior Solutions Engineer")
2. focus-areas - Focus areas (e.g., "Retail, CPG, Financial Services")
3. team - Team name
4. territory - Territory or segment
5. target-role - Career goal role
6. timeline - Target timeline for career goal
7. motivation - Motivation for career goal

Enter field name or number:
```

**3B.2 Get New Value:**

If new value not provided in arguments:
```
What should the new {field_name} be for {display_name}?

Current value: {current_value}
```
Wait for user input.

**3B.3 Display Confirmation Gate:**

```
Update {display_name}'s {field_name}?

Current: {current_value}
New:     {new_value}

Confirm update? (y/n)
```

Wait for user response:
- If "y" or "yes": Proceed to Step 3B.4
- If "n" or "no": Display "Update cancelled. No changes were made." and exit
- If unclear: Ask for clarification

**3B.4 Update Profile File:**

1. Read `team/{se-name}/profile.md` completely
2. Find the line containing the field to update:
  - For "**Title:**" → Find line starting with `**Title:**`
  - For "**Focus Areas:**" → Find line starting with `**Focus Areas:**`
  - etc.
3. Replace the value after the colon with the new value
4. Update "**Last Updated:**" to today's date (YYYY-MM-DD format)
5. Write the entire file back, preserving ALL other content and formatting

**3B.5 Display Success Message:**

```
✅ Updated {display_name}'s profile

**Change Made:**
{field_name}: {old_value} → {new_value}

**Last Updated:** {today's date}

View the full profile: `/profile {se-name}`
```

### Step 4: Handle Special Update Cases

**Adding to Focus Areas:**
If the user says "add X to focus areas" instead of "update focus areas":
- Parse the new value to add
- Read current focus areas
- Append new value to existing (comma-separated)
- Follow confirmation gate flow with combined value

**Example:**
```
Current Focus Areas: Retail, CPG
User: "Add Financial Services to Sarah's focus areas"
New Focus Areas: Retail, CPG, Financial Services
```

### Step 3C: ARCHIVE SE

If action is ARCHIVE:

**3C.1 Display Confirmation Warning:**

Archive is a significant operation. Always show a warning first:

```
⚠️ Are you sure you want to archive {display_name}?

This will move their folder to team/_archived/. The data will be preserved
but they will no longer appear in active SE lists.

This action can be reversed by manually moving the folder back.

Confirm archive? (y/n)
```

Wait for user response:
- If "y" or "yes": Proceed to Step 3C.2
- If "n" or "no": Display "Archive cancelled. No changes were made." and exit
- If unclear: Ask for clarification

**3C.2 Create Archive Directory (if needed):**

Check if `team/_archived/` directory exists:
- If not exists: Create `team/_archived/` directory

**3C.3 Move SE Folder:**

1. Move entire `team/{se-name}/` folder to `team/_archived/{se-name}/`
2. This includes: profile.md, feedback-log.md, 1on1-notes/, reviews/

**3C.4 Add Archive Date to Profile:**

1. Read `team/_archived/{se-name}/profile.md`
2. Add `**Archived Date:** YYYY-MM-DD` line after the metadata section (after Last Updated)
3. Write the updated file

**3C.5 Display Success Message:**

```
✅ Archived {display_name}

**Archive Location:** team/_archived/{se-name}/
**Archived Date:** {today's date}

Their data has been preserved and can be accessed at the archive location.
To restore, manually move the folder back to team/{se-name}/
```

### Step 3D: EXPORT SE Data

If action is EXPORT:

**3D.1 Determine Export Format:**

Parse format from arguments or ask user:
- If "markdown", "md", or natural language indicates markdown → Use markdown format
- If "json" or natural language indicates JSON → Use JSON format
- If not specified:

```
What format would you like to export {display_name}'s data?

1. markdown - Human-readable format
2. json - Structured data format

Enter format (markdown/json):
```

Wait for user response.

**3D.2 Create Export Directory (if needed):**

Check if `outputs/exports/` directory exists:
- If not exists: Create `outputs/exports/` directory

**3D.3 Gather All SE Data:**

1. Read `team/{se-name}/profile.md` completely
2. Read `team/{se-name}/feedback-log.md` completely
3. List all files in `team/{se-name}/1on1-notes/` and read each
4. List all files in `team/{se-name}/reviews/` and read each

**3D.4A Export as Markdown:**

If format is markdown:

1. Create file at `outputs/exports/{se-name}-export-YYYY-MM-DD.md`
2. Structure the export:

```markdown
# SE Data Export: {Display Name}

**Exported:** YYYY-MM-DD
**SE:** {se-name}

---

## Profile

{Full contents of profile.md}

---

## Feedback Log

{Full contents of feedback-log.md}

---

## 1:1 Notes

### {date from filename}
{Contents of each 1on1-notes file}

---

## Performance Reviews

### {period from filename}
{Contents of each reviews file}

---

*Export generated by SE Performance System*
```

**3D.4B Export as JSON:**

If format is JSON:

1. Create file at `outputs/exports/{se-name}-export-YYYY-MM-DD.json`
2. Parse profile.md to extract structured fields:
  - display_name (from H1 title)
  - title (from **Title:** line)
  - start_date (from **Start Date:** line)
  - manager (from **Manager:** line if present)
  - focus_areas (from **Focus Areas:** line)
  - career_aspirations (from Career Aspirations section)
3. Parse feedback-log.md entries (between --- separators):
  - Extract: date, customer, call_type, dimension_ratings, observations, coaching_items
4. Parse 1on1-notes files:
  - Extract: date (from filename), content
5. Parse reviews files:
  - Extract: period (from filename), content
6. Structure as JSON:

```json
{
  "se_name": "{se-name}",
  "export_date": "YYYY-MM-DD",
  "profile": {
    "display_name": "...",
    "title": "...",
    "start_date": "...",
    "manager": "...",
    "focus_areas": ["...", "..."],
    "career_aspirations": {
      "target_role": "...",
      "timeline": "...",
      "motivation": "..."
    }
  },
  "feedback_entries": [
    {
      "date": "YYYY-MM-DD",
      "customer": "...",
      "call_type": "...",
      "ratings": { "dimension": score },
      "observations": { "went_well": "...", "development_areas": "..." },
      "coaching_items": ["..."]
    }
  ],
  "one_on_one_notes": [
    { "date": "YYYY-MM-DD", "content": "..." }
  ],
  "reviews": [
    { "period": "...", "content": "..." }
  ]
}
```

**3D.5 Display Success Message:**

```
✅ Exported {display_name}'s data

**Format:** {markdown/JSON}
**File:** outputs/exports/{se-name}-export-YYYY-MM-DD.{md/json}
**Contents:**
├─ Profile data
├─ {X} feedback entries
├─ {Y} 1:1 notes
└─ {Z} performance reviews

You can find the export at: outputs/exports/{filename}
```

### Step 3E: SEARCH Feedback

If action is SEARCH:

**3E.1 Parse Search Type:**

Determine what kind of search from the user's request:

**Keyword Search indicators:** "search for {keyword}", "find {keyword}", "feedback about {keyword}"
**Date Range indicators:** "from Q4", "from Q4 2024", "from last 30 days", "from December", "from this month"
**Customer Search indicators:** "for {customer}", "feedback for {customer}", "with {customer}"

A search can have multiple filters combined (e.g., "Sarah's feedback from Q4 about ROI").

**3E.2 Parse Date Range (if applicable):**

Convert natural language date ranges to date filters:

| Input | Interpretation |
| --- | --- |
| "Q1" or "Q1 {year}" | Jan 1 - Mar 31 |
| "Q2" or "Q2 {year}" | Apr 1 - Jun 30 |
| "Q3" or "Q3 {year}" | Jul 1 - Sep 30 |
| "Q4" or "Q4 {year}" | Oct 1 - Dec 31 |
| "last 30 days" | Today - 30 days |
| "last 7 days" | Today - 7 days |
| "this month" | First of current month - today |
| "December" or "December {year}" | Dec 1 - Dec 31 |
| "{month} {year}" | First to last of that month |

If year not specified, use current year (or previous year if current quarter hasn't started).

**3E.3 Read Feedback Log:**

1. Read `team/{se-name}/feedback-log.md` completely
2. Parse each feedback entry (entries are separated by `---`)
3. For each entry, extract:
  - Date (from `## DATE | CUSTOMER | CALL TYPE` header)
  - Customer name
  - Call type
  - Full content (for keyword search)

**3E.4 Apply Filters:**

For each feedback entry:
1. **Date filter:** If date range specified, check if entry date falls within range
2. **Customer filter:** If customer specified, check if customer name matches (case-insensitive, fuzzy match)
3. **Keyword filter:** If keyword specified, check if keyword appears anywhere in entry content (case-insensitive)

Keep entries that match ALL specified filters.

**3E.5 Format and Display Results:**

If matches found:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 Feedback Search Results for {Display Name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Search:** {describe applied filters}
**Found:** {count} matching entries

---

### {Date} | {Customer} | {Call Type}

{Brief context snippet showing where keyword matched, if keyword search}
{Or first 2-3 lines of observations if no keyword}

**Ratings:** {summary of ratings if present}

---

{Repeat for each matching entry}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Quick Actions:**
- View full feedback log: `team/{se-name}/feedback-log.md`
- Refine search: `/profile {se-name} search {different terms}`
```

If no matches found (follow ADR-005 conversational error handling):

```
I couldn't find any feedback entries matching your search for {display_name}.

**Search criteria:**
{list applied filters}

**Suggestions:**
- Try a different keyword
- Expand the date range
- Check spelling of customer name
- Run "Show {se-name}'s feedback history" to see all entries
```

**3E.6 Handle Cross-SE Customer Search:**

If the search is for a customer without specifying an SE (e.g., "Show feedback for Nordstrom"):

1. List all SE folders in `team/` (excluding _template, _archived)
2. For each SE, read their feedback-log.md
3. Search for customer name across all SEs
4. Aggregate results grouped by SE

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 Feedback Search: Customer "{Customer Name}"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Found:** {total count} entries across {SE count} SEs

---

## {SE Display Name 1}

### {Date} | {Customer} | {Call Type}
{Context snippet}

---

## {SE Display Name 2}

### {Date} | {Customer} | {Call Type}
{Context snippet}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Step 3F: HISTORY - View Feedback History Summary

If action is HISTORY (user says "Show Sarah's feedback history" or similar):

**3F.1 Read and Parse Feedback Log:**

1. Read `team/{se-name}/feedback-log.md` completely
2. Split content by `---` delimiter to identify individual entries
3. For each entry, parse:
  - Date (from `## YYYY-MM-DD | CUSTOMER | CALL TYPE` header)
  - Customer name
  - Call type
  - Ratings count (count rows in the ratings table)
  - Coaching items (identify `- [ ]` unchecked and `- [x]` checked items)

**3F.2 Calculate Summary Statistics:**

- **Total Entries:** Count of feedback entries (exclude header and template comments)
- **Date Range:** Earliest entry date to latest entry date
- **Open Coaching Items:** Count of all `- [ ]` (unchecked) items across all entries
- **Completed Coaching Items:** Count of all `- [x]` (checked) items across all entries

**3F.3 Get Recent Entries:**

Sort entries by date (newest first) and take the last 5 entries (or all if fewer than 5).

For each entry, extract:
- Date
- Customer
- Call type
- Number of competencies rated (count rows in ratings table)

**3F.4 Display Formatted History Summary:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Feedback History: {Display Name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Summary**
├─ Total Entries: {count}
├─ Date Range: {earliest_date} to {latest_date}
└─ Open Coaching Items: {open_count}

**Recent Entries** (Last 5)
┌────────────────────────────────────────────────────────┐
│ {Date} | {Customer} | {Call Type} ({N} competencies)   │
├────────────────────────────────────────────────────────┤
│ {Date} | {Customer} | {Call Type} ({N} competencies)   │
├────────────────────────────────────────────────────────┤
│ {Date} | {Customer} | {Call Type} ({N} competencies)   │
├────────────────────────────────────────────────────────┤
│ {Date} | {Customer} | {Call Type} ({N} competencies)   │
├────────────────────────────────────────────────────────┤
│ {Date} | {Customer} | {Call Type} ({N} competencies)   │
└────────────────────────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Quick Actions:**
- "Show me {date}" - View full entry details for a specific date
- "Search for {keyword}" - Find feedback containing specific terms
- "Show Q4" - Filter entries by date range
- "Show feedback for {customer}" - Filter by customer name
- View full log: `team/{se-name}/feedback-log.md`
```

**3F.5 Handle Empty Feedback Log:**

If no feedback entries exist (only header/template):

```
📊 Feedback History: {Display Name}

No feedback entries yet.

{display_name}'s feedback log is ready for entries. To log your first feedback:

- Run `/log-feedback {se-name}` to add a feedback entry
- Or manually add entries to `team/{se-name}/feedback-log.md`
```

### Step 3G: DETAIL VIEW - Show Full Entry for Specific Date

If action is DETAIL VIEW (user says "Show me December 15th" or "Show 2025-12-15"):

**3G.1 Parse Target Date:**

Parse the date from the user's request. Handle various formats:

| Input Format | Interpretation |
| --- | --- |
| "December 15th" or "Dec 15" | December 15 of current year |
| "December 15th 2024" | December 15, 2024 |
| "2025-12-15" | Exact ISO date |
| "the 15th" | 15th of current month |
| "yesterday" | Today - 1 day |
| "last Friday" | Most recent Friday |

Convert to ISO format (YYYY-MM-DD) for matching.

**3G.2 Search for Matching Entries:**

1. Read `team/{se-name}/feedback-log.md` completely
2. Parse each entry and extract the date from the `## YYYY-MM-DD | CUSTOMER | CALL TYPE` header
3. Find all entries matching the target date

**3G.3 Handle Results:**

**If exactly one entry matches:**

Display the full entry content:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Feedback Entry: {Display Name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## {Date} | {Customer} | {Call Type}

**Transcript:** {transcript_link}
**Opportunity:** {opportunity}

### Dimension Ratings
| Dimension | Rating | Notes |
|-----------|--------|-------|
| {dimension} | {rating}/5 | {notes} |
| ... | ... | ... |

### Observations
**Went Well:** {went_well}
**Development Areas:** {development_areas}

### Coaching Items
- [ ] {item} (open)
- [x] {item} (completed)

### Notable Quotes
> "{quote}"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Quick Actions:**
- "Show Sarah's feedback history" - Return to summary view
- "Search for {keyword}" - Search across all entries
```

**If multiple entries match the same date:**

```
Found {count} feedback entries for {date}:

1. {Date} | {Customer 1} | {Call Type 1}
2. {Date} | {Customer 2} | {Call Type 2}

Which entry would you like to see? (Enter 1, 2, or customer name)
```

Wait for user selection, then display the selected entry.

**If no entries match (follow ADR-005):**

```
I couldn't find any feedback entries for {target_date}.

{display_name}'s feedback log has entries on these dates:
- {date_1} ({customer_1} - {call_type_1})
- {date_2} ({customer_2} - {call_type_2})
- {date_3} ({customer_3} - {call_type_3})
{show up to 5 nearest dates}

Would you like to see one of these? Or try:
- "Show Sarah's feedback history" for a full summary
- "Show Q4" to see all entries from a quarter
```

## Error Handling

All error messages should follow ADR-005 Conversational Error Handling:

**If team/ directory doesn't exist:**
```
I can't find the team directory. The project may not be set up yet.

Try running `/setup` first, or check that the `team/` directory exists.
```

**If profile.md is missing for an SE folder:**
```
I found the folder for {se-name}, but there's no profile.md file inside.

This might be a corrupted SE record. You can:
1. Run `/add-se {se-name}` to recreate the profile
2. Manually create `team/{se-name}/profile.md`
```

**If profile.md cannot be parsed:**
```
I'm having trouble reading {se-name}'s profile. The file format might have been changed.

You can view the raw file at: team/{se-name}/profile.md
```

**If field update fails:**
```
I couldn't update the {field_name} field.

The profile structure might have been modified. You can manually edit:
team/{se-name}/profile.md
```

**If archive fails (folder move error):**
```
I couldn't archive {se-name}. There was an error moving the folder.

This might happen if:
- The _archived directory couldn't be created
- There's already an archived SE with that name
- File permissions prevent the move

You can try:
1. Check if team/_archived/{se-name} already exists
2. Manually move the folder: team/{se-name}/ → team/_archived/{se-name}/
```

**If export fails:**
```
I couldn't export {se-name}'s data.

This might happen if:
- The outputs/exports/ directory couldn't be created
- Some files are missing from their profile folder
- File permissions prevent writing

You can try:
1. Check that team/{se-name}/ has the expected files
2. Create outputs/exports/ directory manually
3. Try exporting in the other format
```

**If feedback search finds no entries:**
```
I couldn't find any feedback entries matching "{search terms}" for {display_name}.

Try:
- A different keyword
- Checking the date range (maybe try "all time" or a broader quarter)
- "Show {se-name}'s feedback history" to see what entries exist
```

## Example Sessions

### Example 1: View Profile
```
> /profile sarah-chen

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 SE Profile: Sarah Chen
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Current Role**
├─ Title: Solutions Consultant
├─ Team: Not set
├─ Focus Areas: Nothing yet, they are just starting
├─ Start Date: 2026-01-10
└─ Territory: Not specified

**Career Aspirations**
├─ Target Role: Product Manager
├─ Timeline: 2-3 years
└─ Motivation: They like delivering valuable solutions, working with technical folks.

...
```

### Example 2: Fuzzy Match
```
> /profile sara

I found a close match: sarah-chen

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 SE Profile: Sarah Chen
...
```

### Example 3: Update with Confirmation
```
> /profile sarah-chen update title

What should the new title be for Sarah Chen?

Current value: Solutions Consultant
> Principal Solutions Engineer

Update Sarah Chen's title?

Current: Solutions Consultant
New:     Principal Solutions Engineer

Confirm update? (y/n)
> y

✅ Updated Sarah Chen's profile

**Change Made:**
title: Solutions Consultant → Principal Solutions Engineer

**Last Updated:** 2025-12-23

View the full profile: `/profile sarah-chen`
```

### Example 4: No Match Found
```
> /profile john

I couldn't find an SE named "john".

Did you mean one of these?
  - sarah-chen

Or run `/add-se john` to create a new profile.
```

### Example 5: Add to Focus Areas
```
> /profile sarah-chen update focus-areas

What should the new focus-areas be for Sarah Chen?

Current value: Nothing yet, they are just starting
> Retail, CPG, Financial Services

Update Sarah Chen's focus-areas?

Current: Nothing yet, they are just starting
New:     Retail, CPG, Financial Services

Confirm update? (y/n)
> y

✅ Updated Sarah Chen's profile

**Change Made:**
focus-areas: Nothing yet, they are just starting → Retail, CPG, Financial Services

**Last Updated:** 2025-12-23
```

### Example 6: Archive SE
```
> Archive sarah-chen

⚠️ Are you sure you want to archive Sarah Chen?

This will move their folder to team/_archived/. The data will be preserved
but they will no longer appear in active SE lists.

This action can be reversed by manually moving the folder back.

Confirm archive? (y/n)
> y

✅ Archived Sarah Chen

**Archive Location:** team/_archived/sarah-chen/
**Archived Date:** 2025-12-23

Their data has been preserved and can be accessed at the archive location.
To restore, manually move the folder back to team/sarah-chen/
```

### Example 7: Archive Cancelled
```
> Archive test-user

⚠️ Are you sure you want to archive Test User?

This will move their folder to team/_archived/. The data will be preserved
but they will no longer appear in active SE lists.

This action can be reversed by manually moving the folder back.

Confirm archive? (y/n)
> n

Archive cancelled. No changes were made.
```

### Example 8: Export as Markdown
```
> Export Sarah's data

What format would you like to export Sarah Chen's data?

1. markdown - Human-readable format
2. json - Structured data format

Enter format (markdown/json):
> markdown

✅ Exported Sarah Chen's data

**Format:** markdown
**File:** outputs/exports/sarah-chen-export-2025-12-23.md
**Contents:**
├─ Profile data
├─ 5 feedback entries
├─ 3 1:1 notes
└─ 1 performance reviews

You can find the export at: outputs/exports/sarah-chen-export-2025-12-23.md
```

### Example 9: Export as JSON
```
> Export Sarah's data as JSON

✅ Exported Sarah Chen's data

**Format:** JSON
**File:** outputs/exports/sarah-chen-export-2025-12-23.json
**Contents:**
├─ Profile data
├─ 5 feedback entries
├─ 3 1:1 notes
└─ 1 performance reviews

You can find the export at: outputs/exports/sarah-chen-export-2025-12-23.json
```

### Example 10: Search Feedback by Keyword
```
> Search Sarah's feedback for ROI

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 Feedback Search Results for Sarah Chen
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Search:** keyword "ROI"
**Found:** 2 matching entries

---

### 2025-12-15 | Nordstrom | Discovery Call

"...she effectively quantified the **ROI** potential by referencing
industry benchmarks and similar customer outcomes..."

**Ratings:** Technical: 4/5, Discovery: 5/5

---

### 2025-11-28 | Target | POC Kickoff

"...discussion around **ROI** metrics for the proof of concept..."

**Ratings:** Technical: 4/5, Demo: 4/5

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Quick Actions:**
- View full feedback log: `team/sarah-chen/feedback-log.md`
- Refine search: `/profile sarah-chen search {different terms}`
```

### Example 11: Search by Date Range
```
> Show Sarah's feedback from Q4

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 Feedback Search Results for Sarah Chen
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Search:** Q4 2025 (Oct 1 - Dec 31)
**Found:** 3 matching entries

---

### 2025-12-15 | Nordstrom | Discovery Call

Great discovery session focusing on CDP implementation...

**Ratings:** Technical: 4/5, Discovery: 5/5

---

### 2025-11-28 | Target | POC Kickoff

Strong POC kickoff presentation...

**Ratings:** Technical: 4/5, Demo: 4/5

---

### 2025-10-10 | Macy's | Technical Deep Dive

Excellent technical depth...

**Ratings:** Technical: 5/5

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Example 12: Search by Customer (Cross-SE)
```
> Show feedback for Nordstrom

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 Feedback Search: Customer "Nordstrom"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Found:** 4 entries across 2 SEs

---

## Sarah Chen

### 2025-12-15 | Nordstrom | Discovery Call
Great discovery session focusing on CDP implementation...

### 2025-10-05 | Nordstrom | Demo
Strong product demo covering key use cases...

---

## Marcus Johnson

### 2025-11-20 | Nordstrom | Technical Review
Addressed all technical questions thoroughly...

### 2025-09-15 | Nordstrom | Initial Meeting
Good first impression with stakeholders...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Example 13: Search with No Results
```
> Search Sarah's feedback for blockchain

I couldn't find any feedback entries matching "blockchain" for Sarah Chen.

**Search criteria:**
- Keyword: "blockchain"

**Suggestions:**
- Try a different keyword
- Expand the date range
- Check spelling of customer name
- Run "Show Sarah's feedback history" to see all entries
```

### Example 14: View Feedback History Summary
```
> Show Sarah's feedback history

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Feedback History: Sarah Chen
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Summary**
├─ Total Entries: 3
├─ Date Range: 2025-10-10 to 2025-12-15
└─ Open Coaching Items: 3

**Recent Entries** (Last 5)
┌────────────────────────────────────────────────────────┐
│ 2025-12-15 | Nordstrom | Discovery Call (4 competencies)│
├────────────────────────────────────────────────────────┤
│ 2025-11-28 | Target | POC Kickoff (3 competencies)      │
├────────────────────────────────────────────────────────┤
│ 2025-10-10 | Macy's | Technical Deep Dive (2 competencies)│
└────────────────────────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Quick Actions:**
- "Show me December 15th" - View full entry details
- "Search for ROI" - Find feedback containing specific terms
- "Show Q4" - Filter entries by date range
- "Show feedback for Nordstrom" - Filter by customer name
- View full log: `team/sarah-chen/feedback-log.md`
```

### Example 15: View Specific Date Entry
```
> Show me December 15th

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Feedback Entry: Sarah Chen
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 2025-12-15 | Nordstrom | Discovery Call

**Transcript:** [[data/transcripts/2025-12/2025-12-15-nordstrom-discovery.md]]
**Opportunity:** Nordstrom CDP Implementation - $450,000

### Dimension Ratings
| Dimension | Rating | Notes |
|-----------|--------|-------|
| Technical Credibility | 4/5 | Strong understanding of CDP architecture |
| Discovery Quality | 5/5 | Excellent pain point identification |
| Demo Excellence | 4/5 | Tailored demo to retail use cases |
| Commercial Acumen | 4/5 | Good ROI discussion |

### Observations
**Went Well:** Sarah effectively quantified the ROI potential by referencing industry benchmarks and similar customer outcomes. Her discovery questions uncovered a critical pain point around customer identity resolution that the prospect hadn't fully articulated.

**Development Areas:** Could have pushed harder on timeline and decision process. Consider asking about competing initiatives earlier in the conversation.

### Coaching Items
- [ ] Practice timeline pressure questions
- [ ] Develop stronger competitive positioning for retail CDP space

### Notable Quotes
> "The way you connected our identity resolution to their loyalty program challenges really resonated with the VP of Marketing." - AE feedback

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Quick Actions:**
- "Show Sarah's feedback history" - Return to summary view
- "Search for ROI" - Search across all entries
```

### Example 16: Date Not Found (ADR-005 Pattern)
```
> Show me December 20th

I couldn't find any feedback entries for December 20th.

Sarah Chen's feedback log has entries on these dates:
- 2025-12-15 (Nordstrom - Discovery Call)
- 2025-11-28 (Target - POC Kickoff)
- 2025-10-10 (Macy's - Technical Deep Dive)

Would you like to see one of these? Or try:
- "Show Sarah's feedback history" for a full summary
- "Show Q4" to see all entries from a quarter
```

### Example 17: Empty Feedback History
```
> Show new-se's feedback history

📊 Feedback History: New SE

No feedback entries yet.

New SE's feedback log is ready for entries. To log your first feedback:

- Run `/log-feedback new-se` to add a feedback entry
- Or manually add entries to `team/new-se/feedback-log.md`
```

## Natural Language Support

This command also responds to natural language requests outside of the slash command format:

**View Triggers:**
- "Show Sarah's profile"
- "What is Sarah's title?"
- "Display profile for sarah-chen"
- "Show me information about Sarah"

**Update Triggers:**
- "Update Sarah's title to Principal SE"
- "Change Sarah's focus areas to Retail, CPG"
- "Set Sarah's target role to SE Manager"
- "Add Financial Services to Sarah's focus areas"

**Archive Triggers:**
- "Archive sarah-chen"
- "Archive Sarah"
- "Offboard Sarah Chen"

**Export Triggers:**
- "Export Sarah's data"
- "Export Sarah's data as markdown"
- "Export Sarah's data as JSON"
- "Download Sarah's profile"
- "Backup Sarah's data"

**Search Triggers:**
- "Search Sarah's feedback for ROI"
- "Show Sarah's feedback from Q4"
- "Show Sarah's feedback from Q4 2024"
- "Show Sarah's feedback from last 30 days"
- "Show feedback for Nordstrom" (searches across all SEs)
- "Find feedback about discovery for Sarah"

**History Triggers:**
- "Show Sarah's feedback history"
- "Sarah's feedback history"
- "What feedback do we have for Sarah?"
- "Show all feedback for Sarah"
- "Sarah's history"

**Detail View Triggers:**
- "Show me December 15th" (after viewing history or with SE context)
- "Show 2025-12-15"
- "What happened on December 15th?"
- "Show the Nordstrom call from December 15th"
- "Show yesterday's feedback" (relative date)

When Claude receives these natural language requests, it should follow the same implementation steps above.
