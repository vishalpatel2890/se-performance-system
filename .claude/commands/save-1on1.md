# /save-1on1 - Save 1:1 Meeting Notes

Save structured notes after a 1:1 meeting with an SE. This command guides you through capturing discussion points, decisions, action items, and links to coaching items and feedback entries.

## What This Does

1. Resolves SE name (fuzzy matching, same as /prep-1on1)
2. Prompts for meeting date (defaults to today)
3. Collects key discussion points (required)
4. Collects decisions made (optional)
5. Collects action items for manager and SE (optional)
6. Shows open coaching items and allows marking as discussed/completed
7. Links to related feedback entries (optional)
8. Formats and previews complete document
9. Saves to team/{se}/1on1-notes/YYYY-MM-DD.md

## Usage

```
/save-1on1 sarah-chen       # Save notes for Sarah Chen
/save-1on1 sarah            # Fuzzy match - will find sarah-chen
```

## Implementation

When this command is run, follow these steps exactly:

### Step 1: Parse Input and Resolve SE Name

**1.1 Get SE name from argument:**
SE name is provided as: $ARGUMENTS

If no argument provided:
```
Please specify an SE name. Usage: /save-1on1 {se-name}

Available SEs:
{List all SE folders in team/ excluding _template/ and _archived/}
```

**1.2 Normalize the input:**
- Convert to lowercase, replace spaces with hyphens, remove special characters

**1.3 List all SE folders in team/ (exclude _template/, _archived/)**

**1.4 Fuzzy Match (Levenshtein Distance):**
- Exact match → Use directly
- Single close match (distance ≤ 2) → Use with confirmation
- Multiple matches → Ask user to clarify
- No matches → Show error with suggestions (ADR-005)

**If no match found:**
```
I couldn't find an SE named "{input}". Did you mean:
  - {suggestion1}
  - {suggestion2}

Or run `/add-se {input}` to create a new profile.
```

**1.5 Get Display Name from profile.md and confirm:**
```
Saving 1:1 notes for {Display Name}...
```

### Step 2: Collect Meeting Date

**2.1 Calculate today's date in ISO 8601 format (YYYY-MM-DD)**

**2.2 Prompt for date:**
```
📅 Meeting date [default: {today}]:
```

**2.3 Handle user input:**
- If user presses enter or says "today" → Use today's date
- If user enters a valid date (YYYY-MM-DD) → Use that date
- If invalid format → Show error and re-prompt:
  ```
  Invalid date format. Please use YYYY-MM-DD format (e.g., 2025-12-25):
  ```

**2.4 Store as `meeting_date`**

### Step 3: Collect Discussion Points (Required)

**3.1 Prompt for discussion points:**
```
💬 Key discussion points (what topics did you cover?):
Enter each point on a new line. Type 'done' when finished.

>
```

**3.2 Collect multi-line input:**
- Each line becomes a discussion point
- Continue until user types 'done' or enters an empty line
- Must have at least one discussion point

**3.3 If no points entered:**
```
At least one discussion point is required. What was the main topic of your 1:1?

>
```

**3.4 Format as markdown list:**
```markdown
- {point1}
- {point2}
...
```

Store as `discussion_points[]`

### Step 4: Collect Decisions Made (Optional)

**4.1 Prompt for decisions:**
```
📋 Any decisions made? (Enter each on new line, 'done' to finish, 'none' to skip):

>
```

**4.2 Handle user input:**
- If user types 'none', 'skip', or 'n' → Skip this section
- Otherwise, collect multi-line input until 'done' or empty line

**4.3 Format as markdown list if any:**
```markdown
- {decision1}
- {decision2}
```

Store as `decisions[]` (can be empty)

### Step 5: Collect Action Items

**5.1 Prompt for manager action items:**
```
✅ Action items for YOU (manager)? (Each on new line, 'done' to finish, 'none' to skip):

>
```

**5.2 Collect manager items:**
- If 'none' or 'skip' → Empty list
- Otherwise collect until 'done' or empty line
- Format as checkboxes: `- [ ] {item}`

Store as `manager_actions[]`

**5.3 Prompt for SE action items:**
```
✅ Action items for {SE Display Name}? (Each on new line, 'done' to finish, 'none' to skip):

>
```

**5.4 Collect SE items:**
- If 'none' or 'skip' → Empty list
- Otherwise collect until 'done' or empty line
- Format as checkboxes: `- [ ] {item}`

Store as `se_actions[]`

### Step 6: Coaching Items Addressed

**6.1 Read SE's feedback-log.md:**
- Path: `team/{se-name}/feedback-log.md`
- If file doesn't exist, skip to Step 7

**6.2 Extract open coaching items:**
- Search for pattern: `- [ ]` (unchecked checkbox)
- For each item found, extract:
  - Item text (everything after `- [ ]` up to parenthesis or end)
  - Added date from "(added YYYY-MM-DD)"
  - Parent entry context (from `## YYYY-MM-DD | Customer | Type` header)
- Ignore completed items: `- [x]`

**6.3 If no open coaching items:**
```
No open coaching items for {SE Display Name}.

Continuing to feedback linking...
```
Skip to Step 7.

**6.4 Display numbered list:**
```
📚 Open coaching items for {SE Display Name}:

1. {item_text}
   Context: {Customer} {Call Type} - added {date}

2. {item_text}
   Context: {Customer} {Call Type} - added {date}

...

Enter numbers to address (comma-separated, e.g., "1,3"), or 'skip':
```

**6.5 Handle user selection:**
- If 'skip', 'none', or empty → No coaching items addressed
- Parse comma-separated numbers to get selected items
- Validate numbers are in range

**6.6 For each selected item, ask about completion:**
```
🎯 "{item_text}"
   Mark as complete? (y/n):
```

**6.7 Handle completion response:**
- If 'y' or 'yes':
  - Update feedback-log.md: Change `- [ ] {item}` to `- [x] {item} (completed {meeting_date})`
  - Note: Preserve the "(added YYYY-MM-DD)" and add ", completed YYYY-MM-DD)"
  - Record status as "completed" for the note
- If 'n' or 'no':
  - Record status as "discussed" for the note
  - Do NOT modify feedback-log.md

**6.8 Format for note:**
```markdown
- {item_text}
  Status: {discussed|completed}
```

Store as `coaching_items_addressed[]` with their statuses

### Step 7: Link Feedback Entries

**7.1 Read feedback-log.md to get available entries:**
- Extract all entry headers: `## YYYY-MM-DD | {Customer} | {Call Type}`
- Store most recent 10 entries for selection

**7.2 Prompt for linking:**
```
🔗 Link to any feedback entries?

Recent feedback entries:
1. {date} - {Customer} {Call Type}
2. {date} - {Customer} {Call Type}
...

Enter numbers (comma-separated), date/customer to search, or 'skip':
```

**7.3 Handle user input:**
- If 'skip', 'none', or empty → No links
- If numbers → Link those entries
- If text (date or customer name) → Search for matching entries and link

**7.4 Format each link as wiki-style:**
```markdown
- [[./feedback-log.md#YYYY-MM-DD]] - {Customer} {Call Type}
```

Store as `feedback_links[]`

### Step 8: Optional Duration

**8.1 Prompt for duration:**
```
⏱️ Meeting duration (e.g., "30 min", "1 hour") or skip:
```

**8.2 Handle input:**
- If 'skip' or empty → Omit duration field
- Otherwise store the duration text

Store as `duration` (optional)

### Step 9: Optional Free-form Notes

**9.1 Prompt for additional notes:**
```
📝 Any additional notes? (Multi-line, 'done' to finish, 'skip' to omit):

>
```

**9.2 Collect multi-line input:**
- If 'skip' or empty → Omit notes section content
- Otherwise collect until 'done'

Store as `free_notes` (optional)

### Step 10: Format and Preview Document

**10.1 Build the document using this exact structure:**

```markdown
# 1:1 Notes: {SE Display Name}

**Date:** {meeting_date}
{If duration:}**Duration:** {duration}

---

## Discussion Points

{For each point in discussion_points:}
- {point}

---

## Decisions Made

{If decisions is not empty:}
{For each decision in decisions:}
- {decision}

{If empty:}
*No specific decisions recorded.*

---

## Action Items

### For Manager
{If manager_actions is not empty:}
{For each item in manager_actions:}
- [ ] {item}

{If empty:}
*None*

### For SE
{If se_actions is not empty:}
{For each item in se_actions:}
- [ ] {item}

{If empty:}
*None*

---

## Coaching Items Addressed

{If coaching_items_addressed is not empty:}
{For each item in coaching_items_addressed:}
- {item_text}
  Status: {status}

{If empty:}
*No coaching items discussed.*

---

## Related Feedback

{If feedback_links is not empty:}
{For each link in feedback_links:}
- [[./feedback-log.md#{date}]] - {Customer} {Call Type}

{If empty:}
*No feedback entries linked.*

---

## Notes

{If free_notes is not empty:}
{free_notes}

{If empty:}
*No additional notes.*
```

**10.2 Display the complete document:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 PREVIEW: 1:1 Notes for {SE Display Name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{Full document content}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Step 11: Save Flow

**11.1 Create directory if needed:**
- If `team/{se-name}/1on1-notes/` doesn't exist, create it

**11.2 Prompt for confirmation:**
```
Save to team/{se-name}/1on1-notes/{meeting_date}.md? (y/n)
```

**11.3 Handle user response:**

If 'y' or 'yes':
- Write the document to file
- Display confirmation:
```
✅ 1:1 notes saved to team/{se-name}/1on1-notes/{meeting_date}.md
```
- If any coaching items were marked complete, confirm:
```
📝 Updated feedback-log.md: Marked {count} coaching item(s) as complete
```

If 'n' or 'no':
```
1:1 notes not saved. You can copy the content above if needed.
```
- Note: If user says 'n', do NOT update feedback-log.md even if they said 'y' to marking items complete earlier

---

## Related Commands: Show 1:1 Notes

### Show Last 1:1 Notes

**Triggers:** "Show Sarah's last 1:1 notes", "What did we discuss last 1:1 with sarah-chen", "Show {se-name}'s last 1:1"

**Flow:**
1. Resolve SE name (same fuzzy matching as above)
2. List files in `team/{se-name}/1on1-notes/` directory
3. Filter OUT files ending in `-prep.md` (these are prep documents, not notes)
4. Sort remaining files by date (filename format: YYYY-MM-DD.md)
5. If no note files found:
   ```
   No 1:1 notes found for {SE Display Name}. Use /save-1on1 {se-name} to create one.
   ```
6. Read and display the most recent note file:
   ```
   📄 Last 1:1 notes for {SE Display Name} ({date}):

   {File contents}
   ```

### Show All 1:1s

**Triggers:** "Show all 1:1s with Sarah", "List my 1:1 meetings with sarah-chen", "Show all 1:1s with {se-name}"

**Flow:**
1. Resolve SE name
2. List files in `team/{se-name}/1on1-notes/` directory
3. Filter OUT files ending in `-prep.md`
4. Sort by date (most recent first)
5. If no note files found:
   ```
   No 1:1 notes found for {SE Display Name}. Use /save-1on1 {se-name} to create one.
   ```
6. Display list with dates:
   ```
   📋 1:1 Notes for {SE Display Name}:

   1. {date} - {Optional: first discussion point as topic}
   2. {date} - {Optional: first discussion point as topic}
   ...

   Enter a number to view, or 'cancel':
   ```
7. If user selects a number, read and display that note file

---

## Edge Case Handling

**No profile found:**
```
Warning: Profile not found at team/{se-name}/profile.md
Cannot save 1:1 notes without SE profile. Run `/add-se {se-name}` first.
```

**File already exists for date:**
```
⚠️ A 1:1 note already exists for {date}: team/{se-name}/1on1-notes/{date}.md

Options:
1. Overwrite existing file
2. Add suffix (e.g., {date}-2.md)
3. Cancel

Choose (1/2/3):
```

**Feedback log doesn't exist:**
- Skip coaching items section (Step 6)
- Note in console: "No feedback log found for {SE Display Name}"

**No coaching items to link:**
- Show message and continue
- Coaching Items Addressed section shows "*No coaching items discussed.*"

---

## Example Session

```
> /save-1on1 sarah

Saving 1:1 notes for Sarah Chen...

📅 Meeting date [default: 2025-12-25]:

💬 Key discussion points (what topics did you cover?):
Enter each point on a new line. Type 'done' when finished.

> Discussed timeline discovery skills
> Reviewed Nordstrom call feedback
> Talked about career goals and PM path
> done

📋 Any decisions made? (Enter each on new line, 'done' to finish, 'none' to skip):

> Sarah will shadow Marcus on next discovery call
> Schedule career planning session in January
> done

✅ Action items for YOU (manager)? (Each on new line, 'done' to finish, 'none' to skip):

> Connect Sarah with Marcus for shadowing
> Review PM career path framework
> done

✅ Action items for Sarah Chen? (Each on new line, 'done' to finish, 'none' to skip):

> Prepare 3 timeline discovery questions for next call
> Read competitive positioning guide
> done

📚 Open coaching items for Sarah Chen:

1. Explore competitive intel more deeply when customers mention prior vendor evaluations
   Context: Nordstrom Discovery - added 2024-12-24

2. Add timeline/urgency discovery to qualification
   Context: Nordstrom Discovery - added 2024-12-24

3. Practice timeline pressure questions
   Context: Nordstrom Discovery Call - added 2025-12-15

4. Develop stronger competitive positioning for retail CDP space
   Context: Nordstrom Discovery Call - added 2025-12-15

5. Consider creating a technical deep-dive template for other SEs
   Context: Macy's Technical Deep Dive - added 2025-10-10

Enter numbers to address (comma-separated, e.g., "1,3"), or 'skip': 2,3

🎯 "Add timeline/urgency discovery to qualification"
   Mark as complete? (y/n): n

🎯 "Practice timeline pressure questions"
   Mark as complete? (y/n): y

🔗 Link to any feedback entries?

Recent feedback entries:
1. 2025-12-24 - Nordstrom Discovery
2. 2025-12-15 - Nordstrom Discovery Call
3. 2025-11-28 - Target POC Kickoff
4. 2025-10-10 - Macy's Technical Deep Dive
5. 2024-12-15 - Nordstrom Discovery

Enter numbers (comma-separated), date/customer to search, or 'skip': 2

⏱️ Meeting duration (e.g., "30 min", "1 hour") or skip: 30 min

📝 Any additional notes? (Multi-line, 'done' to finish, 'skip' to omit):

> skip

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 PREVIEW: 1:1 Notes for Sarah Chen
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 1:1 Notes: Sarah Chen

**Date:** 2025-12-25
**Duration:** 30 min

---

## Discussion Points

- Discussed timeline discovery skills
- Reviewed Nordstrom call feedback
- Talked about career goals and PM path

---

## Decisions Made

- Sarah will shadow Marcus on next discovery call
- Schedule career planning session in January

---

## Action Items

### For Manager
- [ ] Connect Sarah with Marcus for shadowing
- [ ] Review PM career path framework

### For SE
- [ ] Prepare 3 timeline discovery questions for next call
- [ ] Read competitive positioning guide

---

## Coaching Items Addressed

- Add timeline/urgency discovery to qualification
  Status: discussed
- Practice timeline pressure questions
  Status: completed

---

## Related Feedback

- [[./feedback-log.md#2025-12-15]] - Nordstrom Discovery Call

---

## Notes

*No additional notes.*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Save to team/sarah-chen/1on1-notes/2025-12-25.md? (y/n) y

✅ 1:1 notes saved to team/sarah-chen/1on1-notes/2025-12-25.md
📝 Updated feedback-log.md: Marked 1 coaching item(s) as complete
```

---

## Error Handling (ADR-005)

**No SEs exist:**
```
There are no SE profiles yet. Run `/add-se {name}` to create one.
```

**SE not found:**
```
I couldn't find an SE named "{input}". Did you mean: {list}?
Or run `/add-se {input}` to create a new profile.
```

**Invalid date format:**
```
Invalid date format. Please use YYYY-MM-DD format (e.g., 2025-12-25):
```

**Missing required field:**
```
At least one discussion point is required. What was the main topic of your 1:1?
```

---

## Performance

Target: Note saving should complete in < 5 seconds (simple file operations, no AI analysis).

---

## Files Modified

- Creates: `team/{se-name}/1on1-notes/YYYY-MM-DD.md`
- May modify: `team/{se-name}/feedback-log.md` (if coaching items marked complete)

## Files Read

- `team/{se-name}/profile.md` - For SE display name
- `team/{se-name}/feedback-log.md` - For coaching items and feedback entries
