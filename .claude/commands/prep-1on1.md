# /prep-1on1 - Generate 1:1 Preparation Document

Generate a comprehensive 1:1 preparation document for an upcoming meeting with an SE. This command aggregates profile context, recent feedback, open coaching items, and recognition opportunities into a structured prep document.

## What This Does

0. **[NEW]** Auto-detects next 1:1 from calendar (if configured)
1. Resolves SE name (fuzzy matching)
2. Loads SE profile context (role, focus areas, career aspirations)
3. Aggregates recent feedback (last 30 days)
4. Extracts open coaching items with context
5. Identifies recognition opportunities (ratings of 4, positive quotes)
6. Generates 2-3 suggested discussion topics
7. Checks career conversation threshold for warning
8. Formats and displays prep document
9. Offers to save to team/{se}/1on1-notes/{date}-prep.md

## Usage

```
/prep-1on1 sarah-chen       # Generate prep for Sarah Chen
/prep-1on1 sarah            # Fuzzy match - will find sarah-chen
/prep-1on1                  # [NEW] Auto-detect next 1:1 from calendar
```

## Implementation

When this command is run, follow these steps exactly:

### Step 0: Calendar Auto-Detection (when no SE name provided)

**0.1 Check if SE name argument was provided:**
SE name argument is: $ARGUMENTS

If an argument IS provided, skip to Step 1.

**0.2 Check if Google Calendar MCP is available:**
- Check if the `google-calendar-mcp` tools are available (list-events, search-events)
- If MCP is NOT available, skip calendar detection and show the standard "Please specify an SE name" message in Step 1

**0.3 Query calendar for upcoming 1:1 meetings using MCP:**
Use the Google Calendar MCP `list-events` tool with:
- `timeMin`: now (current date/time)
- `timeMax`: 7 days from now
- `maxResults`: 20

**0.4 Identify 1:1 meetings from results:**
Filter events to find 1:1 meetings by checking:
- Title contains "1:1", "1on1", "check-in", or "one on one" (case-insensitive)
- OR event has exactly 2 attendees
- AND title does NOT contain "team meeting", "all hands", "standup", "sprint"

**0.5 Match SE from attendees:**
For each 1:1 meeting found:
- Get attendee names/emails (excluding the manager/organizer)
- List all SE folders in `team/` (exclude `_template/`, `_archived/`)
- Fuzzy match attendee name to SE folder name:
  - Normalize: lowercase, replace spaces with hyphens
  - Check if normalized name matches or is contained in folder name
  - Use Levenshtein distance ≤ 2 for close matches

**0.6 If a next 1:1 is found:**
Display:
```
📅 Your next 1:1 is with {SE Display Name} {relative_time}
   Meeting: {title}
   Time: {formatted_datetime}

Prepare for this 1:1? (y/n)
```

**0.7 Handle user response:**
- If 'y' or 'yes': Use matched SE name and continue to Step 1
- If 'n' or 'no': Display available SEs and ask which one to prepare for
- If user types a different SE name: Use that name and continue to Step 1

**0.8 If no upcoming 1:1 found:**
```
📅 No upcoming 1:1 meetings found on your calendar.

Available SEs:
{List all SE folders in team/ excluding _template/ and _archived/}

Which SE would you like to prepare for?
```
Wait for user input, then continue to Step 1.

**0.9 If calendar query fails or MCP unavailable:**
Fall back gracefully to Step 1 with standard SE name prompt.

---

### Step 1: Parse Input and Resolve SE Name

**1.1 Get SE name from argument:**
SE name is provided as: $ARGUMENTS (or from Step 0 calendar detection)

If no argument provided AND Step 0 was skipped (no calendar):
```
Please specify an SE name. Usage: /prep-1on1 {se-name}

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
Preparing 1:1 document for {Display Name}...
```

### Step 2: Load Profile Context

**2.1 Read `team/{se-name}/profile.md` completely**

**2.2 Extract Current Role section:**
- Title (from **Title:** line)
- Start Date (from **Start Date:** line)
- Focus Areas (from **Focus Areas:** line)
- Territory/Segment (from **Territory/Segment:** line)

**2.3 Extract Career Aspirations section:**
- Short-Term target (from ### Short-Term subsection)
- Medium-Term goals (from ### Medium-Term subsection)
- Long-Term vision (from ### Long-Term subsection)
- Skills to Develop list

**2.4 Extract Job Performance section:**
- Strengths list
- Development Areas list
- Current Quarter Goals list

**2.5 Parse Career Conversation Log (if exists in profile):**
- Find most recent date mentioned in career-related notes
- If no career conversation log exists, use profile Last Updated date as fallback
- Store as `last_career_conversation_date`

**2.6 Find Last 1:1 date:**
- List all files in `team/{se-name}/1on1-notes/` directory
- Sort by filename (YYYY-MM-DD format)
- Get most recent file date
- If no files exist, set `last_1on1_date = "No previous 1:1 notes"`

### Step 3: Aggregate Recent Feedback (Last 30 Days)

**3.1 Read `team/{se-name}/feedback-log.md` completely**

**3.2 Parse all feedback entries:**
Each entry starts with `## YYYY-MM-DD | {Customer} | {Call Type}`

For each entry, extract:
- Date (from header)
- Customer name (from header)
- Call type (from header)
- Competency ratings (from ### Competency Ratings table)
- Strengths (from **Strengths:** line)
- Development Areas (from **Development Areas:** line)

**3.3 Filter to last 30 days:**
- Calculate date 30 days ago from today
- Include only entries with date >= 30 days ago
- Store as `recent_entries[]`

**3.4 Count total calls in period:**
- `call_count = len(recent_entries)`

**3.5 Calculate average rating per competency:**
- For each competency that appears in recent entries
- Sum all ratings and divide by count
- Store as `competency_averages = {competency: avg_rating}`

**3.6 Identify strengths and development areas:**
- Strengths: competencies with avg >= 3.5
- Development areas: competencies with avg < 3.0
- Neutral: competencies between 3.0 and 3.5

### Step 4: Extract Open Coaching Items

**4.1 Scan feedback-log.md for open coaching items:**
Search for pattern: `- [ ]` (unchecked checkbox)

**4.2 For each open item found:**
- Extract the item text
- Extract the "(added YYYY-MM-DD)" date
- Find the parent feedback entry (## YYYY-MM-DD | Customer | Type)
- Store: {text, added_date, customer, call_type}

**4.3 Ignore completed items:**
- Skip any `- [x]` patterns (completed items)

**4.4 Sort by date (most recent first):**
- Sort by added_date descending

**4.5 Format each item with context:**
```
{item_text} (added YYYY-MM-DD, {Customer} {Call Type})
```

Store as `open_coaching_items[]`

### Step 5: Identify Recognition Opportunities

**5.1 Scan recent feedback entries for ratings of 4 (UC):**
- Look in Competency Ratings tables for "4 (UC)" ratings
- Extract: competency name, date, customer

**5.2 Extract positive observations:**
- From **Strengths:** sections of recent entries
- Look for particularly notable achievements

**5.3 Extract notable quotes:**
- From ### Notable Quotes sections
- These are formatted as `> "{quote}"`
- Include speaker attribution if present

**5.4 Build recognition opportunities list (limit to top 3):**
Prioritize:
1. Ratings of 4 (UC) - indicates mastery
2. Positive quotes from customers
3. Strong strengths observations

**5.5 Format each recognition:**
```
- {Achievement/quote} ({date}, {Customer})
```

Store as `recognition_opportunities[]`

### Step 6: Generate Discussion Topics

**6.1 Analyze open coaching items:**
- Group similar items (e.g., multiple timeline-related items)
- Prioritize items that have appeared multiple times
- Create 1 topic from coaching items if any exist

**6.2 Analyze development areas:**
- From feedback aggregation, identify lowest competency averages
- Create 1 topic addressing skill development needs

**6.3 Check career objectives:**
- From profile, identify active career goals
- If career conversation is overdue, include career check-in topic
- Create 1 topic around career progression

**6.4 Generate 2-3 specific, actionable topics:**
Format each topic as:
```
**{Topic Title}**
Why: {Reasoning based on data}
Context: {Specific observations}
Questions:
- {Specific question to ask}
- {Follow-up question}
```

**6.5 Avoid generic topics:**
- Don't use generic phrases like "check in on progress"
- Reference specific feedback entries, dates, customers
- Make questions contextual to their situation

Store as `discussion_topics[]`

### Step 7: Career Check-in Warning

**7.1 Read career_check_threshold_days from config/settings.yaml:**
- Look for `career_check_threshold_days:` setting
- Default to 30 if not found

**7.2 Calculate days since last career conversation:**
- Use `last_career_conversation_date` from Step 2.5
- If no date found, assume never discussed (show warning)
- `days_since = today - last_career_conversation_date`

**7.3 Generate warning if threshold exceeded:**
If `days_since > career_check_threshold_days`:
```
⚠️ Career Check-in Overdue ({days_since} days since last conversation)
Consider scheduling dedicated career discussion time.
```

**7.4 Include career objectives summary:**
- Target role from Career Aspirations
- Timeline (6-12 months, 1-2 years, etc.)
- Active development actions if any

Store as `career_warning` (string or empty)

### Step 8: Format and Display Prep Document

**8.1 Build document using this structure:**

```markdown
# 1:1 Preparation: {SE Display Name}

**Date:** {Today's date YYYY-MM-DD}
**Last 1:1:** {last_1on1_date}

---

## Quick Context

- **Role:** {title}
- **Focus Areas:** {focus_areas}
- **Current Goals:** {quarter_goals_summary}

---

## Recognition Opportunities

{If recognition_opportunities is not empty:}
{For each recognition:}
- {achievement} ({date}, {Customer})
  {If quote exists:} > "{quote}"

{If empty:}
*No exceptional ratings in recent feedback to highlight.*

---

## Open Coaching Items ({count})

{If open_coaching_items is not empty:}
{For each item, numbered:}
1. {item_text}
   Context: {Customer} {Call Type} - added {date}

{If empty:}
*No open coaching items. Great follow-through!*

---

## Recent Feedback Summary (last 30 days)

- **Calls reviewed:** {call_count}
- **Strengths:** {strengths_list with averages}
- **Development areas:** {development_areas_list with averages}

{If call_count == 0:}
*No feedback entries in the last 30 days. Consider reviewing recent calls.*

---

## Suggested Discussion Topics

{For each topic:}
### {topic_number}. {Topic Title}
**Why:** {reasoning}
**Context:** {specific_observations}
**Questions to ask:**
- {question1}
- {question2}

---

## Career Check-in

**Last career conversation:** {last_career_date} ({days_ago} days ago)
{career_warning if threshold exceeded}
**Target:** {target_role} in {timeline}
**Active objectives:** {objectives_count} | **Development actions:** {actions_count} in progress

---

## Notes Template

### Discussion Notes


### Feedback Delivered


### New Coaching Items


### Action Items
**Theirs:**
- [ ]

**Mine:**
- [ ]

### Topics for Next Time

```

**8.2 Display the complete document**

### Step 9: Save Flow

**9.1 After displaying document, prompt user:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Save this prep to team/{se-name}/1on1-notes/{today}-prep.md? (y/n)
```

**9.2 Create directory if needed:**
- If `team/{se-name}/1on1-notes/` doesn't exist, create it

**9.3 Handle user response:**

If 'y' or 'yes':
- Write the exact displayed content to file
- Display confirmation:
```
✅ Prep saved to team/{se-name}/1on1-notes/{today}-prep.md
```

If 'n' or 'no':
- Display:
```
Prep document not saved. You can copy the content above if needed.
```

## Edge Case Handling

**No feedback entries:**
```
Note: No feedback entries found for {SE Name}.

This 1:1 prep focuses on:
- Profile goals and career aspirations
- Getting to know working style
- Setting up regular feedback cadence

Suggested topic: Establish baseline - understand current projects and challenges.
```

**New SE (no history):**
- Focus on onboarding check-in topics
- Use profile goals as primary discussion framework
- Suggest foundational questions for new relationship

**No profile found:**
Should not happen if SE name resolved, but if profile.md is missing:
```
Warning: Profile not found at team/{se-name}/profile.md
Run `/profile {se-name}` to create or view profile.
```

**Career data incomplete:**
- If Career Aspirations section is empty or placeholder, note:
```
Career Check-in: Career goals not yet documented
Consider using this 1:1 to discuss career aspirations.
```

## Example Session

```
> /prep-1on1 sarah

Preparing 1:1 document for Sarah Chen...

# 1:1 Preparation: Sarah Chen

**Date:** 2025-12-24
**Last 1:1:** No previous 1:1 notes

---

## Quick Context

- **Role:** Principal Solutions Consultant
- **Focus Areas:** Nothing yet, they are just starting
- **Current Goals:** To be set in next 1:1

---

## Recognition Opportunities

- Exceptional discovery depth with retail-specific analogies (2024-12-15, Nordstrom)
  > "This is the first time someone's actually understood our attribution challenge." - Jennifer Walsh, VP Marketing

- Unconscious competence in ELI5 - made identity resolution accessible (2024-12-15, Nordstrom)

---

## Open Coaching Items (4)

1. Explore competitive intel more deeply when customers mention prior vendor evaluations
   Context: Nordstrom Discovery - added 2024-12-24

2. Add timeline/urgency discovery to qualification
   Context: Nordstrom Discovery - added 2024-12-24

3. Practice timeline questions
   Context: Nordstrom Discovery Call - added 2025-12-15

4. Develop stronger competitive positioning for retail CDP space
   Context: Nordstrom Discovery Call - added 2025-12-15

---

## Recent Feedback Summary (last 30 days)

- **Calls reviewed:** 2
- **Strengths:** Discovery Depth (avg 4.0), ELI5 (avg 3.5)
- **Development areas:** Demo Storytelling (avg 2.0), Checking Understanding (avg 2.0)

---

## Suggested Discussion Topics

### 1. Timeline and Competitive Discovery Skills
**Why:** Multiple coaching items around timeline questions and competitive positioning
**Context:** Nordstrom calls flagged both areas; customer mentioned 18-month search
**Questions to ask:**
- "What techniques are you using to uncover decision timelines?"
- "How can we better leverage competitive intel when customers mention prior vendors?"

### 2. Demo Storytelling Development
**Why:** Lowest rated competency across recent feedback (avg 2.0)
**Context:** May need focused practice on narrative structure vs. feature lists
**Questions to ask:**
- "How comfortable are you with our demo storytelling framework?"
- "Would it help to shadow a demo from Marcus who excels here?"

### 3. Career Check-in
**Why:** New SE, career goals being established
**Context:** Target role: Product Manager in 2-3 years
**Questions to ask:**
- "What skills do you want to develop this quarter?"
- "How can I support your path toward product management?"

---

## Career Check-in

**Last career conversation:** Not recorded
⚠️ Career Check-in Overdue - Consider discussing career goals
**Target:** Product Manager in 2-3 years
**Active objectives:** TBD | **Development actions:** TBD

---

## Notes Template

### Discussion Notes


### Feedback Delivered


### New Coaching Items


### Action Items
**Theirs:**
- [ ]

**Mine:**
- [ ]

### Topics for Next Time


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Save this prep to team/sarah-chen/1on1-notes/2025-12-24-prep.md? (y/n) y

✅ Prep saved to team/sarah-chen/1on1-notes/2025-12-24-prep.md
```

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

**Settings file missing:**
If `config/settings.yaml` doesn't exist, use defaults:
- career_check_threshold_days: 30
- feedback.recent_days: 30

## Performance

Target: Prep generation should complete in < 10 seconds.

## Natural Language Support

**Prep-1on1 Triggers:** "Prep for 1:1 with Sarah", "Generate 1:1 prep for sarah-chen", "1:1 preparation for"

**Show Upcoming 1:1s Triggers:** "Show upcoming 1:1s", "What 1:1s do I have", "List my 1:1 meetings", "When is my next 1:1"

---

## Related: Show Upcoming 1:1s

When a user asks to see their upcoming 1:1 meetings (using natural language triggers above), follow this flow:

### Check Calendar Configuration

**1. Check if Google Calendar MCP is available:**
- Check if `google-calendar-mcp` tools are available
- If NOT available, display:
```
Calendar integration requires the google-calendar-mcp to be configured.
See: https://github.com/nspady/google-calendar-mcp for setup instructions.
```

### Query and Display 1:1s

**2. Query calendar using MCP:**
Use the Google Calendar MCP `list-events` tool with:
- `timeMin`: now
- `timeMax`: 7 days from now
- `maxResults`: 50

**3. Filter for 1:1 meetings:**
Apply same filtering as Step 0.4:
- Title contains 1:1 keywords OR 2 attendees
- Exclude team meetings, all hands, standups, sprints

**4. Match SEs from attendees:**
For each 1:1 meeting, fuzzy match attendee names to `team/` folders.

**5. Display formatted output:**
```
📅 Upcoming 1:1 Meetings

{For each 1:1 meeting, display:}
  {date} {time} | {meeting_title}
  SE: {matched_se_name or "Unknown"}

{If no 1:1s found:}
No upcoming 1:1 meetings found in the next 7 days.
```

**6. Offer to prepare:**
```
Would you like to prepare for any of these? Enter SE name or number:
```

If user selects one, proceed to prep generation using that SE.

---

## Google Calendar MCP Tools Reference

This command uses the following tools from `google-calendar-mcp`:

| Tool | Usage |
|------|-------|
| `list-events` | Retrieve upcoming calendar events with date filtering |
| `search-events` | Find events matching text query (e.g., "1:1 with Sarah") |
| `get-event` | Get full details of a specific event |

**MCP Setup:** See https://github.com/nspady/google-calendar-mcp for installation and OAuth configuration.
