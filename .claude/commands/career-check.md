# /career-check - Career Development Summary

Generate a comprehensive career progression summary for an SE. This command aggregates career aspirations, objectives, development actions, competency gaps, and career conversation history into a structured career document.

## What This Does

1. Resolves SE name (fuzzy matching)
2. Loads SE profile and extracts Career Aspirations section
3. Parses Growth Objectives with status tracking
4. Parses Development Actions with type and progress
5. Calculates competency gaps from feedback history
6. Displays Career Conversation Log
7. Checks career check-in threshold for warning
8. Generates actionable recommendations
9. Offers to log a career conversation

## Usage

```
/career-check sarah-chen
/career-check sarah
```

## Arguments

- `se-name`: The SE's name in lowercase-hyphen format (supports fuzzy matching)

## Implementation

When this command is run, follow these steps exactly:

### Step 1: Parse Input and Resolve SE Name

**1.1 Get SE name from argument:**
SE name is provided as: $ARGUMENTS

If no argument provided:
```
Please specify an SE name. Usage: /career-check {se-name}

Available SEs:
{List all SE folders in team/ excluding _template/ and _archived/}
```

**1.2 Normalize the input:**
- Convert to lowercase
- Replace spaces with hyphens
- Remove special characters

**1.3 List all SE folders in team/ (exclude \_template/, \_archived/)**

**1.4 Fuzzy Match (Levenshtein Distance):**
- Exact match → Use directly
- Single close match (distance ≤ 2) → Use with confirmation
- Multiple matches → Ask user to clarify
- No matches → Show error with suggestions

**If no match found (ADR-005 conversational error handling):**
```
I couldn't find an SE named "{input}". Did you mean:
  - {suggestion1}
  - {suggestion2}

Or run `/add-se {input}` to create a new profile.
```

**1.5 Get Display Name from profile.md and confirm:**
```
Generating career summary for {Display Name}...
```

### Step 2: Load Profile and Extract Career Aspirations (AC: 2, 11)

**2.1 Read \****`team/{se-name}/profile.md`**\*\* completely**

**2.2 Check for Career Aspirations section:**

Search for either format:
- `## Career Aspirations (Career Progression Track)` (new format from tech spec)
- `## Career Aspirations` (existing format)

**2.3 If Career Aspirations section NOT found (AC: 11):**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ℹ️ No Career Aspirations Found
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{Display Name}'s profile doesn't have a Career Aspirations section yet.

Career aspirations help:
- Track progress toward target roles
- Set meaningful growth objectives
- Plan development actions
- Guide career conversations

Would you like to set up career goals now using /plan-goal {se-name}?

Alternatively, you can manually add a Career Aspirations section to their profile.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
Stop processing and exit.

**2.4 Extract Career Aspirations fields (AC: 2):**

**For new format (## Career Aspirations (Career Progression Track)):**
- Target Role: from `**Target Role:**` line
- Target Timeline: from `**Target Timeline:**` line
- Motivation: from `**Motivation:**` line

**For existing format (## Career Aspirations):**
- Short-Term (6-12 months): from `### Short-Term` subsection
- Medium-Term (1-2 years): from `### Medium-Term` subsection
- Long-Term (3-5 years): from `### Long-Term` subsection
- Skills to Develop: from `### Skills to Develop` list

If using existing format, derive:
- Target Role = First role mentioned in Short-Term
- Target Timeline = "6-12 months" (from Short-Term header)
- Motivation = Text from Short-Term section

Store as:
```
career_aspirations = {
  target_role: string,
  target_timeline: string,
  motivation: string,
  short_term: string,
  medium_term: string,
  long_term: string,
  skills_to_develop: string[]
}
```

### Step 3: Parse Growth Objectives (AC: 3)

**3.1 Find Growth Objectives subsection:**
Search for `### Growth Objectives` within Career Aspirations section

**3.2 Parse each objective:**

**Format 1 - New format with metadata:**
```
- [ ] {Objective description}
  Status: {IN PROGRESS | NOT STARTED}
  Added: {YYYY-MM-DD}
  Progress: {optional notes}
  Blockers: {optional blockers}
- [x] {Completed objective}
  Completed: {YYYY-MM-DD}
  Outcome: "{outcome description}"
```

**Format 2 - Simple checklist format:**
```
- [ ] {Objective description}
- [x] {Completed objective}
```

**3.3 For each objective, extract:**
- checkbox_state: `[ ]` (open) or `[x]` (completed)
- description: objective text
- status: "COMPLETED" if [x], otherwise look for "Status:" line
  - If Status: line exists, use that value
  - If no Status: line and checkbox is [ ], default to "NOT STARTED"
- added_date: from "Added:" line (if present)
- progress_notes: from "Progress:" line (if present)
- blockers: from "Blockers:" line (if present)
- completed_date: from "Completed:" line (if [x])
- outcome: from "Outcome:" line (if [x])

**3.4 Determine display status:**
- If [x] → "COMPLETED"
- If Status: IN PROGRESS → "IN PROGRESS"
- Otherwise → "NOT STARTED"

Store as `growth_objectives[]`

### Step 4: Parse Development Actions (AC: 4)

**4.1 Find Development Actions subsection:**
Search for `### Development Actions` within Career Aspirations section

**4.2 Parse each action:**

**Format 1 - New format with metadata:**
```
- [ ] {Action description}
  Type: {SHADOWING | STRETCH | TRAINING | PROJECT | MENTORING}
  Effort: {estimate}
  Due: {YYYY-MM-DD or "Q1 2025"}
  Added: {YYYY-MM-DD}
  Related Objective: {optional}
- [x] {Completed action}
  Completed: {YYYY-MM-DD}
  Outcome: "{outcome text}"
```

**Format 2 - Simple checklist format:**
```
- [ ] {Action description}
- [x] {Completed action}
```

**4.3 For each action, extract:**
- checkbox_state: `[ ]` (open) or `[x]` (completed)
- description: action text
- type: from "Type:" line (default to "PROJECT" if not specified)
- effort: from "Effort:" line (if present)
- due_date: from "Due:" line (if present)
- added_date: from "Added:" line (if present)
- related_objective: from "Related Objective:" line (if present)
- completed_date: from "Completed:" line (if [x])
- outcome: from "Outcome:" line (if [x])

**4.4 Calculate status:**
- If [x] → "COMPLETED"
- If due_date exists and is past today and not completed → "OVERDUE"
- If due_date exists and is in the future → "IN PROGRESS"
- Otherwise → "NOT STARTED"

Store as `development_actions[]`

### Step 5: Calculate Competency Gaps (AC: 5)

**5.1 Read \****`team/{se-name}/feedback-log.md`**\*\* completely**

**5.2 Parse all feedback entries:**

Each entry starts with `## YYYY-MM-DD | {Customer} | {Call Type}`

For each entry, extract competency ratings from:
- `### Competency Ratings` table (meeting competencies, 1-4 scale)
- `### Dimension Ratings` table (role competencies, X/5 scale)

**5.3 Calculate average rating per meeting competency:**

For each unique meeting competency found:
- Sum all ratings
- Divide by count
- Store: `{competency: {avg: X.X, count: N}}`

**5.4 Read \****`config/competencies/meeting-competencies.yaml`**

**5.5 Read \****`config/competencies/role-competencies.yaml`**

**5.6 Map meeting competencies to role competencies:**

For each role competency:
- Find all meeting competencies with `maps_to_role` that includes this role competency
- Average those meeting competency averages
- Store derived role competency rating

Example mapping from meeting-competencies.yaml:
- eli5 maps_to_role: [technical_credibility, demo_excellence]
- discovery_depth maps_to_role: [discovery_quality, commercial_acumen]
- checking_understanding maps_to_role: [discovery_quality, demo_excellence]

**5.7 Define target ratings:**

Based on target role from career aspirations:
- Principal SE / Senior roles: target = 3.5 (UC threshold)
- Staff/Lead roles: target = 4.0 (full UC)
- Default: target = 3.5

**5.8 Calculate gaps:**

For each role competency with derived rating:
- gap = target - current
- If gap > 1.0 → priority = "HIGH"
- If gap > 0.5 → priority = "MEDIUM"
- Otherwise → priority = "LOW"

Store as `competency_gaps[]`:
```
{
  competency: string,
  current: number,
  target: number,
  gap: number,
  priority: "HIGH" | "MEDIUM" | "LOW",
  contributing_meeting_competencies: string[]
}
```

### Step 6: Parse Career Conversation Log (AC: 6)

**6.1 Find Career Conversation Log:**

Search for `### Career Conversation Log` in profile

**6.2 Parse table rows:**

Expected format:
```
| Date | Key Themes | Next Steps |
|------|------------|------------|
| YYYY-MM-DD | {themes} | {steps} |
```

For each data row (skip header and separator):
- date: first column (YYYY-MM-DD)
- key_themes: second column
- next_steps: third column

**6.3 Sort by date (most recent first)**

Store as `career_conversations[]`

**6.4 If no Career Conversation Log found:**
- Set `career_conversations = []`
- Set `last_conversation_date = null`

**6.5 Get most recent conversation date:**
- `last_conversation_date = career_conversations[0].date` (if any exist)

### Step 7: Career Check-in Warning (AC: 7)

**7.1 Read career\_check\_threshold\_days from config/settings.yaml:**
- Look for `career_check_threshold_days:` setting
- Default to 30 if not found

**7.2 Calculate days since last conversation:**
- If `last_conversation_date` exists:
  - `days_since = today - last_conversation_date`
- If no career conversations:
  - `days_since = "never"`

**7.3 Determine if warning needed:**
- If `days_since == "never"` → show warning
- If `days_since > career_check_threshold_days` → show warning
- Otherwise → no warning

Store as:
```
career_warning = {
  show: boolean,
  days_since: number | "never",
  threshold: number,
  days_overdue: number (if applicable)
}
```

### Step 8: Generate Recommendations (AC: 8)

**8.1 Initialize recommendations list:**

```
recommendations = []
```

**8.2 Check for overdue career check-in:**

If `career_warning.show == true`:
```
recommendations.push({
  priority: "HIGH",
  text: "Schedule a career conversation - {days} since last check-in (threshold: {threshold} days)",
  action: "Use this /career-check output as a discussion guide"
})
```

**8.3 Check for HIGH priority competency gaps:**

For each gap with priority == "HIGH":
```
recommendations.push({
  priority: "HIGH",
  text: "Focus on {competency} development - gap of {gap} from target",
  action: "Consider {specific action based on competency type}"
})
```

Action suggestions by competency type:
- technical_credibility: "Technical deep-dive shadowing or certification"
- discovery_quality: "Discovery framework practice and role-play"
- demo_excellence: "Demo coaching sessions with senior SE"
- deal_influence: "Strategic account reviews and deal strategy sessions"
- commercial_acumen: "Business case workshops or finance collaboration"
- cross_functional_impact: "Lead a team enablement session"
- workload_management: "Capacity planning and prioritization coaching"

**8.4 Check for overdue development actions:**

For each action with status == "OVERDUE":
```
recommendations.push({
  priority: "MEDIUM",
  text: "Complete overdue action: {action_description}",
  action: "Due date was {due_date} - discuss blockers or adjust timeline"
})
```

**8.5 Check for stalled objectives:**

For each objective where:
- status == "IN PROGRESS" AND
- progress_notes is empty or null AND
- added_date is > 30 days ago

```
recommendations.push({
  priority: "LOW",
  text: "Update progress on: {objective_description}",
  action: "No progress notes recorded - add status update"
})
```

**8.6 Sort recommendations by priority:**
- HIGH first, then MEDIUM, then LOW

Store as `recommendations[]`

### Step 9: Display Career Summary (AC: 1-8)

**9.1 Build and display the career summary document:**

```markdown
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Career Summary: {SE Display Name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Generated:** {Today's date YYYY-MM-DD}
**Profile Last Updated:** {profile_last_updated}

---

## Career Aspirations

**Target Role:** {target_role}
**Timeline:** {target_timeline}
**Motivation:** {motivation}

{If skills_to_develop exists and not empty:}
**Skills to Develop:**
{For each skill:}
- {skill}

---

## Growth Objectives

{If growth_objectives is not empty:}
| Status | Objective | Added | Progress |
|--------|-----------|-------|----------|
{For each objective:}
| {status_emoji} {status} | {description} | {added_date or "-"} | {progress_notes or "-"} |

Status Legend: ✅ COMPLETED | 🔄 IN PROGRESS | ⏸️ NOT STARTED

{If any objectives have blockers:}
**Blockers Identified:**
{For each objective with blockers:}
- {objective}: {blockers}

{If growth_objectives is empty:}
*No growth objectives defined yet. Consider adding objectives aligned with career aspirations.*

---

## Development Actions

{If development_actions is not empty:}

### In Progress / Upcoming
| Action | Type | Due | Effort |
|--------|------|-----|--------|
{For each action where status != COMPLETED and status != OVERDUE:}
| {description} | {type} | {due_date or "-"} | {effort or "-"} |

### Overdue ⚠️
{If any actions have status == OVERDUE:}
| Action | Type | Due | Days Overdue |
|--------|------|-----|--------------|
{For each overdue action:}
| {description} | {type} | {due_date} | {days_overdue} |

{If no overdue actions:}
*No overdue actions. Great progress!*

### Completed ✅
{If any actions have status == COMPLETED:}
| Action | Completed | Outcome |
|--------|-----------|---------|
{For each completed action:}
| {description} | {completed_date} | {outcome or "-"} |

{If no completed actions:}
*No actions completed yet.*

{If development_actions is empty:}
*No development actions defined yet. Consider adding concrete actions to achieve growth objectives.*

---

## Competency Gap Analysis

{If competency_gaps is not empty:}

**Target Role:** {target_role} (Target Rating: {target}/4)

| Role Competency | Current | Target | Gap | Priority |
|-----------------|---------|--------|-----|----------|
{For each gap, sorted by gap descending:}
| {competency_name} | {current:.1f} | {target:.1f} | {gap:+.1f} | {priority_indicator} |

Priority Legend: 🔴 HIGH (gap > 1.0) | 🟡 MEDIUM (gap > 0.5) | 🟢 LOW

**Gap Details:**
{For each HIGH priority gap:}
- **{competency_name}** ({current:.1f} → {target:.1f}): Based on {contributing_meeting_competencies}

{If competency_gaps is empty:}
*No feedback data available to calculate competency gaps. Log feedback using /log-feedback or /analyze-call.*

---

## Career Conversation Log

{If career_warning.show:}
⚠️ **Career Check-in Overdue** ({career_warning.days_since} days since last conversation, threshold: {career_warning.threshold} days)

{If career_conversations is not empty:}
**Last Conversation:** {last_conversation_date} ({days_ago} days ago)

| Date | Key Themes | Next Steps |
|------|------------|------------|
{For each conversation (limit to 5 most recent):}
| {date} | {key_themes} | {next_steps} |

{If career_conversations is empty:}
*No career conversations logged yet.*

---

## Recommendations

{If recommendations is not empty:}
{For each recommendation, numbered:}
{priority_emoji} **{index}. {text}**
   → {action}

{If recommendations is empty:}
*No urgent recommendations. Career development is on track!*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Step 10: Offer Conversation Logging (AC: 9, 10)

**10.1 After displaying summary, prompt user:**

```
Would you like to log a career conversation? (y/n)
```

**10.2 Handle response:**

**If 'n' or 'no':**
```
Career summary complete. Run /career-check {se-name} anytime to view updated summary.
```
Exit.

**If 'y' or 'yes':**

**10.3 Prompt for conversation details:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 Log Career Conversation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

What were the key themes discussed?
(e.g., "Discussed path to Principal, agreed on SKO workshop lead role")

Enter key themes:
```

Wait for user input → store as `key_themes`

```
What are the agreed next steps?
(e.g., "Schedule exec shadowing by Jan 15, review PM certification options")

Enter next steps:
```

Wait for user input → store as `next_steps`

**10.4 Preview the new entry:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
New Career Conversation Entry:

| Date | Key Themes | Next Steps |
|------|------------|------------|
| {today's date} | {key_themes} | {next_steps} |

Add this to {SE Display Name}'s Career Conversation Log? (y/n)
```

**10.5 Handle confirmation:**

**If 'n' or 'no':**
```
Conversation not logged. You can log it later using /career-check.
```
Exit.

**If 'y' or 'yes':**

**10.6 Update profile.md:**

Read `team/{se-name}/profile.md`

**If Career Conversation Log table exists:**
- Find the table
- Insert new row after header row (most recent first)

**If Career Conversation Log does NOT exist:**
- Find the Career Aspirations section
- Add new subsection at the end:

```markdown
### Career Conversation Log
| Date | Key Themes | Next Steps |
|------|------------|------------|
| {today's date} | {key_themes} | {next_steps} |
```

**10.7 Display confirmation:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Career Conversation Logged

Added to: team/{se-name}/profile.md

Updated Career Conversation Log:
| Date | Key Themes | Next Steps |
|------|------------|------------|
| {today's date} | {key_themes} | {next_steps} |
{previous entries...}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Edge Case Handling

**No SEs exist:**
```
There are no SE profiles yet. Run `/add-se {name}` to create one.
```

**SE not found:**
```
I couldn't find an SE named "{input}". Did you mean:
  - {suggestion1}
  - {suggestion2}

Or run `/add-se {input}` to create a new profile.
```

**No feedback data for gap analysis:**
- Show message: "No feedback data available for competency gap analysis."
- Continue with other sections
- Recommend: "Log feedback using /log-feedback or /analyze-call to enable gap analysis."

**Partial career data:**
- If Growth Objectives missing: Show message suggesting to add objectives
- If Development Actions missing: Show message suggesting to add actions
- If Career Conversation Log missing: Create it when logging first conversation

**Settings file missing:**
If `config/settings.yaml` doesn't exist, use defaults:
- career_check_threshold_days: 30

## Example Session

```
> /career-check sarah

Generating career summary for Sarah Chen...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Career Summary: Sarah Chen
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Generated:** 2025-12-26
**Profile Last Updated:** 2025-12-23

---

## Career Aspirations

**Target Role:** Product Manager
**Timeline:** 2-3 years
**Motivation:** They like delivering valuable solutions, working with technical folks.

**Skills to Develop:**
- To be identified

---

## Growth Objectives

*No growth objectives defined yet. Consider adding objectives aligned with career aspirations.*

---

## Development Actions

*No development actions defined yet. Consider adding concrete actions to achieve growth objectives.*

---

## Competency Gap Analysis

**Target Role:** Product Manager (Target Rating: 3.5/4)

| Role Competency | Current | Target | Gap | Priority |
|-----------------|---------|--------|-----|----------|
| Technical Credibility | 3.8 | 3.5 | +0.3 | 🟢 LOW |
| Discovery Quality | 3.4 | 3.5 | -0.1 | 🟢 LOW |
| Demo Excellence | 2.8 | 3.5 | -0.7 | 🟡 MEDIUM |
| Commercial Acumen | 3.2 | 3.5 | -0.3 | 🟢 LOW |

Priority Legend: 🔴 HIGH (gap > 1.0) | 🟡 MEDIUM (gap > 0.5) | 🟢 LOW

**Gap Details:**
- **Demo Excellence** (2.8 → 3.5): Based on Demo Storytelling, ELI5, Checking Understanding

---

## Career Conversation Log

⚠️ **Career Check-in Overdue** (never recorded, threshold: 30 days)

*No career conversations logged yet.*

---

## Recommendations

🔴 **1. Schedule a career conversation - never recorded (threshold: 30 days)**
   → Use this /career-check output as a discussion guide

🟡 **2. Focus on Demo Excellence development - gap of 0.7 from target**
   → Consider demo coaching sessions with senior SE

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Would you like to log a career conversation? (y/n) y

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 Log Career Conversation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

What were the key themes discussed?
(e.g., "Discussed path to Principal, agreed on SKO workshop lead role")

Enter key themes: Discussed PM career path, demo skills development, Q1 focus areas

What are the agreed next steps?
(e.g., "Schedule exec shadowing by Jan 15, review PM certification options")

Enter next steps: Shadow senior SE demos, start product feedback log, review PM job postings

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
New Career Conversation Entry:

| Date | Key Themes | Next Steps |
|------|------------|------------|
| 2025-12-26 | Discussed PM career path, demo skills development, Q1 focus areas | Shadow senior SE demos, start product feedback log, review PM job postings |

Add this to Sarah Chen's Career Conversation Log? (y/n) y

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Career Conversation Logged

Added to: team/sarah-chen/profile.md

Updated Career Conversation Log:
| Date | Key Themes | Next Steps |
|------|------------|------------|
| 2025-12-26 | Discussed PM career path, demo skills development, Q1 focus areas | Shadow senior SE demos, start product feedback log, review PM job postings |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Performance Target

Career summary generation should complete in < 10 seconds per NFR requirements.
Competency gap calculation should complete in < 2 seconds.

## Related Commands

- `/plan-goal {se-name}` - Set up career goals with AI-assisted planning
- `/prep-1on1 {se-name}` - Generate 1:1 preparation (includes career check-in)
- `/draft-review {se-name} {period}` - Generate performance review (includes career section)
- `/profile {se-name}` - View/edit SE profile
- `/log-feedback {se-name}` - Log feedback for competency tracking
