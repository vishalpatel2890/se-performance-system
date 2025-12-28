# /track-actions - Development Action and Progress Tracking

Handle all development action tracking operations including progress queries, action completion, new action creation, career conversation logging, and objective status updates.

## What This Does

This command handles multiple conversational interactions for tracking SE career development:

1. **Progress Query** - "What's {se-name}'s progress on development actions?"
2. **Action Completion** - "Mark {se-name}'s {action} complete"
3. **Add Action** - "Add development action for {se-name}"
4. **Log Conversation** - "Log career conversation for {se-name}"
5. **Objective Status** - "Mark {se-name}'s {objective} in progress/complete"

## Usage

```
/track-actions progress sarah-chen
/track-actions complete sarah-chen "SKO workshop"
/track-actions add sarah-chen
/track-actions log-conversation sarah-chen
/track-actions objective sarah-chen "Lead demo training" complete
```

## Arguments

- `action`: The operation type (progress | complete | add | log-conversation | objective)
- `se-name`: The SE's name (supports fuzzy matching)
- Additional arguments depend on operation type

## Implementation

When this command is run, follow these steps:

### Step 0: Parse Arguments and Determine Operation

Parse arguments from: $ARGUMENTS

**Valid formats:**
- `progress {se-name}` - Show progress summary
- `complete {se-name} "{action-name}"` - Mark action complete
- `add {se-name}` - Add new action interactively
- `log-conversation {se-name}` - Log career conversation
- `objective {se-name} "{objective-name}" {status}` - Update objective status

**If no arguments or unrecognized format:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Development Action Tracker
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Usage:
  /track-actions progress {se-name}
  /track-actions complete {se-name} "{action-name}"
  /track-actions add {se-name}
  /track-actions log-conversation {se-name}
  /track-actions objective {se-name} "{objective-name}" {in-progress|complete}

Examples:
  /track-actions progress sarah-chen
  /track-actions complete sarah "SKO workshop"
  /track-actions add sarah
  /track-actions log-conversation sarah
  /track-actions objective sarah "Lead demo training" complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Step 1: Resolve SE Name (Common to All Operations)

**1.1 Normalize the input:**
- Convert to lowercase
- Replace spaces with hyphens
- Remove special characters

**1.2 List all SE folders in team/ (exclude \_template/, \_archived/)**

**1.3 Fuzzy Match (Levenshtein Distance <= 2):**
- Exact match → Use directly
- Single close match (distance <= 2) → Use with confirmation
- Multiple matches → Ask user to clarify
- No matches → Show error with suggestions

**If no match found:**
```
I couldn't find an SE named "{input}". Did you mean:
  - {suggestion1}
  - {suggestion2}

Or run `/add-se {input}` to create a new profile.
```

**1.4 Get Display Name from profile.md**

Store: `se_name`, `se_display_name`

### Step 2: Load and Parse Profile

**2.1 Read ****`team/{se-name}/profile.md`**** completely**

**2.2 Parse Development Actions Section:**

Search for `### Development Actions` section.

For each action (starts with `- [ ]` or `- [x]`):
```
action = {
  raw_line: string (full markdown line),
  line_number: int,
  checkbox: "[ ]" | "[x]",
  description: string,
  type: string (from "Type:" line, default "PROJECT"),
  effort: string (from "Effort:" line),
  due: string (from "Due:" line),
  added: string (from "Added:" line),
  completed: string (from "Completed:" line if [x]),
  outcome: string (from "Outcome:" line if [x]),
  related_objective: string (from "Related Objective:" line),
  status: "COMPLETED" | "OVERDUE" | "IN PROGRESS" | "NOT STARTED"
}
```

**Status determination:**
- If checkbox is `[x]` → COMPLETED
- Else if Due exists and Due < today → OVERDUE
- Else if Due exists and is in future → IN PROGRESS
- Else → NOT STARTED

**Overdue calculation:**
- Parse Due date (handle YYYY-MM-DD, "Q1 2025", "Ongoing")
- "Ongoing" is never overdue
- Quarter formats like "Q1 2025" = end of quarter date (2025-03-31)
- Compare to today's date

Store as `development_actions[]`

**2.3 Parse Growth Objectives Section:**

Search for `### Growth Objectives` section.

For each objective (starts with `- [ ]` or `- [x]`):
```
objective = {
  raw_line: string,
  line_number: int,
  checkbox: "[ ]" | "[x]",
  description: string,
  status: string (from "Status:" line or derived),
  added: string (from "Added:" line),
  completed: string (from "Completed:" line if [x]),
  outcome: string (from "Outcome:" line if [x]),
  progress: string (from "Progress:" line),
  blockers: string (from "Blockers:" line)
}
```

Store as `growth_objectives[]`

**2.4 Parse Career Conversation Log:**

Search for `### Career Conversation Log` section and table.

For each table row (skip header and separator):
```
conversation = {
  date: string (YYYY-MM-DD),
  key_themes: string,
  next_steps: string
}
```

Store as `career_conversations[]`

---

## Operation: Progress Query (AC: 1, 2, 3)

**Trigger:** `/track-actions progress {se-name}` or conversational "What's {se-name}'s progress on development actions?"

### Step P1: Count Actions by Status

```
counts = {
  completed: 0,
  overdue: 0,
  in_progress: 0,
  not_started: 0,
  total: 0
}
```

For each action in `development_actions[]`:
- If status == "COMPLETED" → counts.completed++
- If status == "OVERDUE" → counts.overdue++
- If status == "IN PROGRESS" → counts.in_progress++
- If status == "NOT STARTED" → counts.not_started++
- counts.total++

### Step P2: Display Progress Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Development Actions Progress: {SE Display Name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Summary:**
| Status | Count |
|--------|-------|
| ✅ Completed | {counts.completed} |
| ⚠️ Overdue | {counts.overdue} |
| 🔄 In Progress | {counts.in_progress} |
| ⏸️ Not Started | {counts.not_started} |
| **Total** | **{counts.total}** |

{If counts.overdue > 0:}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ OVERDUE ACTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{For each overdue action:}
**⚠️ {action.description}**
  Type: {action.type}
  Due: {action.due} ({days_overdue} days overdue)
  Related Objective: {action.related_objective or "None"}

{End if}

{If counts.in_progress > 0 or counts.not_started > 0:}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 ACTIVE ACTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{For each action with status IN PROGRESS or NOT STARTED:}
**{action.description}**
  Status: {status_emoji} {action.status}
  Type: {action.type}
  Due: {action.due or "Not set"}
  Effort: {action.effort or "Not specified"}
  Related Objective: {action.related_objective or "None"}

{End if}

{If counts.completed > 0:}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ COMPLETED ACTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{For each completed action:}
**{action.description}**
  Completed: {action.completed}
  Outcome: {action.outcome or "Not recorded"}

{End if}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Step P3: If No Actions

If `development_actions[]` is empty:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Development Actions Progress: {SE Display Name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

No development actions found for {SE Display Name}.

To add development actions:
  /track-actions add {se-name}

Or use /plan-goal to create a complete career plan with objectives and actions.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Operation: Action Completion (AC: 4, 5, 6)

**Trigger:** `/track-actions complete {se-name} "{action-name}"` or conversational "Mark {se-name}'s {action} complete"

### Step C1: Find Matching Action

**C1.1 Parse action name from arguments**

Extract the action name from quotes or remaining arguments.

**C1.2 Fuzzy match against action descriptions**

For each incomplete action in `development_actions[]`:
- Calculate Levenshtein distance between input and action.description
- If exact substring match → score = 0
- If distance <= 2 → score = distance
- Otherwise → score = Infinity

Sort by score, take best match.

**C1.3 If no match found:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ Action Not Found
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

I couldn't find an action matching "{input}" for {SE Display Name}.

Did you mean one of these?
{For top 3 incomplete actions:}
  - {action.description}

Or check their profile for available actions:
  /track-actions progress {se-name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
Exit.

**C1.4 If action already completed:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ℹ️ Action Already Complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"{action.description}" is already marked complete.

Completed: {action.completed}
Outcome: {action.outcome or "Not recorded"}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
Exit.

### Step C2: Prompt for Outcome

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Mark Action Complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Action: {action.description}
SE: {SE Display Name}

What was the outcome of this action?
(e.g., "Gained confidence leading discovery sessions, identified 3 qualification questions to add")

Enter outcome:
```

Wait for user input → store as `outcome_text`

### Step C3: Preview and Confirm

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Preview Changes
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Action: {action.description}

Changes:
  - Checkbox: [ ] → [x]
  - Completed: {today's date YYYY-MM-DD}
  - Outcome: "{outcome_text}"

Mark this action complete? (y/n)
```

**If 'n' or 'no':**
```
Action not marked complete. No changes made.
```
Exit.

**If 'y' or 'yes':**
Continue to Step C4.

### Step C4: Update Profile

**C4.1 Find action block in profile.md:**

The action block starts with `- [ ] {action.description}` and includes indented metadata lines.

**C4.2 Transform action block:**

Replace:
```markdown
- [ ] {action.description}
  Type: {type}
  Effort: {effort}
  Due: {due}
  Added: {added}
  Related Objective: {related_objective}
```

With:
```markdown
- [x] {action.description}
  Type: {type}
  Completed: {today's date YYYY-MM-DD}
  Outcome: "{outcome_text}"
  Related Objective: {related_objective}
```

**C4.3 Use Edit tool to update profile.md**

### Step C5: Check Related Objective (AC: 7)

**C5.1 If action has Related Objective:**

Find the related objective name.

Count all actions with the same Related Objective:
- Count completed (including the one just completed)
- Count incomplete

**C5.2 If all actions for objective are complete:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 All Actions Complete for Objective
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

All development actions for "{related_objective}" are now complete!

Related Actions:
{For each action with this objective:}
  ✅ {action.description}

Mark the objective "{related_objective}" as done? (y/n)
```

**If 'y':**
- Prompt for objective outcome
- Update objective in profile.md (see Objective Status section)
- Show confirmation

**If 'n':**
```
Objective left as is. You can mark it complete later with:
  /track-actions objective {se-name} "{objective}" complete
```

### Step C6: Confirmation

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Action Marked Complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Updated: team/{se-name}/profile.md

Action: {action.description}
Completed: {today's date}
Outcome: "{outcome_text}"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Operation: Add Action (AC: 8, 9)

**Trigger:** `/track-actions add {se-name}` or conversational "Add development action for {se-name}"

### Step A1: Prompt for Action Details

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
➕ Add Development Action
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Adding new development action for: {SE Display Name}

**Step 1 of 5: Action Description**
What is the development action?
(e.g., "Shadow senior SE on enterprise discovery calls")

Enter action:
```

Wait for user input → store as `action_description`

### Step A2: Get Action Type

```
**Step 2 of 5: Action Type**
What type of development action is this?

  1. SHADOWING - Observing others to learn techniques
  2. STRETCH - Challenging assignment beyond current skill
  3. TRAINING - Formal learning (course, certification, workshop)
  4. PROJECT - Specific deliverable or initiative
  5. MENTORING - Regular guidance from experienced practitioner

Enter type (1-5 or name):
```

Map input to type:
- 1 or "shadowing" → SHADOWING
- 2 or "stretch" → STRETCH
- 3 or "training" → TRAINING
- 4 or "project" → PROJECT
- 5 or "mentoring" → MENTORING

Store as `action_type`

### Step A3: Get Effort Estimate

```
**Step 3 of 5: Effort Estimate**
How much time will this require?

Examples:
  - "4 hours" (one-time)
  - "2 hours/week" (recurring)
  - "3 sessions" (multiple meetings)

Enter effort estimate:
```

Wait for user input → store as `action_effort`

### Step A4: Get Due Date

```
**Step 4 of 5: Due Date**
When should this be completed?

Enter due date (YYYY-MM-DD, "Q1 2025", or "Ongoing"):
```

Wait for user input → store as `action_due`

Validate format:
- YYYY-MM-DD: Valid date format
- QN YYYY: Valid quarter format
- "Ongoing": Valid for continuous activities
- Invalid: Ask for correction

### Step A5: Get Related Objective (Optional)

**A5.1 If growth\_objectives[] is not empty:**

```
**Step 5 of 5: Related Objective (Optional)**
Which growth objective does this action support?

Available objectives:
{For each objective, numbered:}
  {n}. {objective.description}

Enter number, or press Enter to skip:
```

If user enters number → store as `related_objective` (the objective description)
If user presses Enter → store as empty string

**A5.2 If growth\_objectives[] is empty:**

```
**Step 5 of 5: Related Objective**
No growth objectives found. Skipping.

Tip: Use /plan-goal {se-name} to create objectives first.
```

Store `related_objective = ""`

### Step A6: Preview and Confirm

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 New Development Action
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

- [ ] {action_description}
  Type: {action_type}
  Effort: {action_effort}
  Due: {action_due}
  Added: {today's date YYYY-MM-DD}
  {If related_objective:}Related Objective: {related_objective}

Add this action to {SE Display Name}'s profile? (y/n)
```

**If 'n' or 'no':**
```
Action not added. No changes made.
```
Exit.

**If 'y' or 'yes':**
Continue to Step A7.

### Step A7: Update Profile

**A7.1 Find Development Actions section in profile.md**

**A7.2 Append new action:**

Format new action:
```markdown
- [ ] {action_description}
  Type: {action_type}
  Effort: {action_effort}
  Due: {action_due}
  Added: {today's date}
  {If related_objective:}Related Objective: {related_objective}
```

**A7.3 If Development Actions section doesn't exist:**

Find Career Aspirations section and add:
```markdown
### Development Actions

- [ ] {action_description}
  Type: {action_type}
  Effort: {action_effort}
  Due: {action_due}
  Added: {today's date}
  {If related_objective:}Related Objective: {related_objective}
```

**A7.4 Use Edit tool to update profile.md**

### Step A8: Confirmation

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Development Action Added
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Updated: team/{se-name}/profile.md

New Action:
  {action_description}
  Type: {action_type}
  Due: {action_due}
  {If related_objective:}Related Objective: {related_objective}

View all actions:
  /track-actions progress {se-name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Operation: Log Career Conversation (AC: 10, 11)

**Trigger:** `/track-actions log-conversation {se-name}` or conversational "Log career conversation for {se-name}"

### Step L1: Prompt for Date

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 Log Career Conversation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Logging career conversation for: {SE Display Name}

**Date**
Enter conversation date (YYYY-MM-DD) or press Enter for today:
```

If user presses Enter → use today's date
If user enters date → validate and store

Store as `conversation_date`

### Step L2: Prompt for Key Themes

```
**Key Themes**
What were the main topics discussed?
(e.g., "Discussed path to Principal, agreed on SKO workshop lead role")

Enter key themes:
```

Wait for user input → store as `key_themes`

### Step L3: Prompt for Next Steps

```
**Next Steps**
What are the agreed next steps?
(e.g., "Schedule exec shadowing by Jan 15, review PM certification options")

Enter next steps:
```

Wait for user input → store as `next_steps`

### Step L4: Preview and Confirm

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 New Career Conversation Entry
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Date | Key Themes | Next Steps |
|------|------------|------------|
| {conversation_date} | {key_themes} | {next_steps} |

Add this to {SE Display Name}'s Career Conversation Log? (y/n)
```

**If 'n' or 'no':**
```
Conversation not logged. No changes made.
```
Exit.

**If 'y' or 'yes':**
Continue to Step L5.

### Step L5: Update Profile

**L5.1 Find Career Conversation Log table in profile.md**

**L5.2 If table exists:**

Insert new row after header (most recent first):

Find:
```markdown
| Date | Key Themes | Next Steps |
|------|------------|------------|
```

Insert after:
```markdown
| Date | Key Themes | Next Steps |
|------|------------|------------|
| {conversation_date} | {key_themes} | {next_steps} |
```

**L5.3 If Career Conversation Log section doesn't exist:**

Find Career Aspirations section (or end of file if not found) and add:
```markdown
### Career Conversation Log

| Date | Key Themes | Next Steps |
|------|------------|------------|
| {conversation_date} | {key_themes} | {next_steps} |
```

**L5.4 Use Edit tool to update profile.md**

### Step L6: Confirmation

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Career Conversation Logged
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Updated: team/{se-name}/profile.md

Entry Added:
| Date | Key Themes | Next Steps |
|------|------------|------------|
| {conversation_date} | {key_themes} | {next_steps} |

View full career summary:
  /career-check {se-name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Operation: Objective Status (AC: 12, 13)

**Trigger:** `/track-actions objective {se-name} "{objective-name}" {status}` or conversational "Mark {se-name}'s {objective} in progress/complete"

### Step O1: Parse and Find Objective

**O1.1 Parse objective name and status from arguments**

Extract:
- `objective_input`: Text in quotes or between se-name and status
- `status_input`: "in-progress" or "complete" (or variations)

**O1.2 Fuzzy match objective against growth\_objectives[]**

Similar to action matching:
- Calculate Levenshtein distance
- Take best match with distance <= 3

**O1.3 If no match found:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ Objective Not Found
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

I couldn't find an objective matching "{input}" for {SE Display Name}.

Available objectives:
{For each objective:}
  - {objective.description}

Or run /plan-goal {se-name} to create new objectives.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
Exit.

### Step O2: Handle Status Update

**If status\_input is "in-progress" or "in progress":**

**O2.1 Preview change:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔄 Mark Objective In Progress
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Objective: {objective.description}
SE: {SE Display Name}

Change:
  Status: {current_status} → IN PROGRESS

Mark this objective as in progress? (y/n)
```

**O2.2 If confirmed, update profile.md:**

Transform:
```markdown
- [ ] {objective.description}
  Status: NOT STARTED
  Added: {added}
```

To:
```markdown
- [ ] {objective.description}
  Status: IN PROGRESS
  Added: {added}
```

**If status\_input is "complete" or "done":**

**O2.3 Check if objective already complete:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ℹ️ Objective Already Complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"{objective.description}" is already marked complete.

Completed: {objective.completed}
Outcome: {objective.outcome or "Not recorded"}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
Exit.

**O2.4 Prompt for outcome:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Mark Objective Complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Objective: {objective.description}
SE: {SE Display Name}

What was the outcome of this objective?
(e.g., "Promoted to Principal SE, achieved all success criteria")

Enter outcome:
```

Wait for user input → store as `outcome_text`

**O2.5 Preview and confirm:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Preview Changes
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Objective: {objective.description}

Changes:
  - Checkbox: [ ] → [x]
  - Completed: {today's date YYYY-MM-DD}
  - Outcome: "{outcome_text}"

Mark this objective complete? (y/n)
```

**O2.6 If confirmed, update profile.md:**

Transform:
```markdown
- [ ] {objective.description}
  Status: IN PROGRESS
  Added: {added}
  Goal: {goal}
  Success Criteria:
    - {criterion}
  Competency Focus: {competency}
```

To:
```markdown
- [x] {objective.description}
  Completed: {today's date}
  Outcome: "{outcome_text}"
  Goal: {goal}
  Success Criteria:
    - {criterion}
  Competency Focus: {competency}
```

### Step O3: Confirmation

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Objective Updated
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Updated: team/{se-name}/profile.md

Objective: {objective.description}
{If complete:}Completed: {today's date}
{If complete:}Outcome: "{outcome_text}"
{If in-progress:}Status: IN PROGRESS

View career summary:
  /career-check {se-name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

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

**No Development Actions section:**
- For progress query: Show "No development actions found" message
- For add action: Create section when saving
- For complete action: Show "No actions found" error

**No Growth Objectives section:**
- For add action: Skip related objective step
- For objective status: Show "No objectives found" error

**Escape special characters in outcome text:**
- Escape quotes within user-provided outcome text
- Handle multi-line input gracefully

**Date validation:**
- YYYY-MM-DD must be valid date
- Quarter format (Q1-Q4 YYYY) must be valid
- "Ongoing" is special case - never overdue

**Confirmation gate violations:**
- If user says "n", "no", or "cancel" → IMMEDIATELY stop, do NOT proceed
- Only proceed with 'y' or 'yes' explicit confirmation

## Fuzzy Matching Algorithm

For SE names, action names, and objective names:

**Levenshtein Distance Calculation:**
```
function levenshtein(s1, s2):
  if s1 == s2: return 0
  if len(s1) == 0: return len(s2)
  if len(s2) == 0: return len(s1)

  matrix = create 2D array (len(s1)+1 x len(s2)+1)

  for i in range(len(s1)+1):
    matrix[i][0] = i
  for j in range(len(s2)+1):
    matrix[0][j] = j

  for i in range(1, len(s1)+1):
    for j in range(1, len(s2)+1):
      cost = 0 if s1[i-1] == s2[j-1] else 1
      matrix[i][j] = min(
        matrix[i-1][j] + 1,      # deletion
        matrix[i][j-1] + 1,      # insertion
        matrix[i-1][j-1] + cost  # substitution
      )

  return matrix[len(s1)][len(s2)]
```

**Matching thresholds:**
- SE names: distance <= 2
- Action descriptions: distance <= 2 OR substring match
- Objective descriptions: distance <= 3 OR substring match

## Performance Target

All operations should complete in < 5 seconds per NFR requirements.

## Related Commands

- `/career-check {se-name}` - Full career summary with competency gaps
- `/plan-goal {se-name} "{goal}"` - Create career plan with objectives and actions
- `/profile {se-name}` - View/edit SE profile
- `/prep-1on1 {se-name}` - 1:1 preparation (includes action status)
