# /design-actions - AI-Assisted Development Action Design

Design concrete, calendar-ready development activities for a specific objective using the Action Designer agent persona. The agent reads SE workload context, generates 3-5 development actions with effort estimates and success criteria, assesses workload feasibility, and saves confirmed actions to the SE's profile.

## What This Does

1. Loads the Action Designer agent persona
2. Resolves SE name (fuzzy matching)
3. Loads SE workload context: profile, existing actions, feedback history
4. Calculates current workload level (HIGH/MODERATE/LOW)
5. Generates 3-5 development actions with types, effort, success criteria, timelines
6. Assesses workload feasibility (ACHIEVABLE/REQUIRES_ADJUSTMENT/OVERLOADED)
7. Allows modification of actions before saving
8. Appends confirmed actions to profile.md Development Actions section

## Usage

```
/design-actions sarah-chen "Build executive presence in strategic accounts"
/design-actions sarah "Improve discovery skills for enterprise deals"
```

## Arguments

- `se-name`: The SE's name (supports fuzzy matching)
- `objective`: A development objective in quotes describing what to develop

## Agents Used

- `_agents/action-designer-persona.md` - Practical Development Coach persona

## Implementation

When this command is run, follow these steps exactly:

### Step 1: Load Action Designer Agent Persona

**1.1 Read the persona file:**
Read `{project-root}/.claude/commands/_agents/action-designer-persona.md` completely.

**1.2 Activate persona:**
Adopt the persona's tone, behaviors, and constraints for this entire session:
- **Tone:** Practical, time-conscious, encouraging but realistic about effort
- **Key behaviors:** Reference workload, estimate effort, define success criteria, balance action types
- **Constraints:** Never skip effort estimation, always assess feasibility, confirm before saving

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🛠️ Action Designer Agent Activated
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
I'm the Action Designer - I help turn development objectives into
concrete, calendar-ready actions. Every action comes with effort
estimates, timelines, and clear success criteria.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Step 2: Parse Arguments and Resolve SE Name

**2.1 Parse arguments from:** $ARGUMENTS

Expected format: `{se-name} "{objective statement}"`

Extract:
- `se_name_input`: First argument (SE name)
- `objective_statement`: Second argument (text in quotes)

**2.2 Handle missing arguments:**

If no arguments or only one provided:
```
Please provide both SE name and objective.

Usage: /design-actions {se-name} "{objective}"

Example:
  /design-actions sarah-chen "Build executive presence in strategic accounts"
```
Exit.

**2.3 Normalize SE name:**
- Convert to lowercase
- Replace spaces with hyphens
- Remove special characters

**2.4 List SE folders in \****`team/`***\* (exclude \****`_template/`***\*, \****`_archived/`**\*\*)**

**2.5 Fuzzy Match (Levenshtein Distance):**
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
Exit.

**2.6 Get SE display name from profile.md**

Store: `se_name`, `se_display_name`

### Step 3: Load SE Workload Context (AC: 3)

**3.1 Read profile.md:**
Read `team/{se-name}/profile.md` completely.

**3.2 Extract current role:**
Look for:
- `## Current Role` section → `**Title:**` field
- Default to "Solution Engineer" if not found

Store as `current_role`

**3.3 Extract existing Development Actions:**
Look for `### Development Actions` section or create mental note if not present.

For each development action found:
- Parse checkbox status: `[ ]` (pending) or `[x]` (completed)
- Parse effort from `Effort:` line
- Count pending actions and sum their weekly/ongoing effort

Store as:
```
existing_actions = {
  count: int,
  pending_count: int,
  weekly_hours: float (estimated total from pending actions),
  items: [{description, type, effort, status}]
}
```

**3.4 Extract Career Aspirations and Growth Objectives:**
Look for `## Career Aspirations` section and `### Growth Objectives` subsection.

Store relevant context for grounding action recommendations.

### Step 4: Calculate Workload Level from Feedback (AC: 3)

**4.1 Read feedback-log.md:**
Read `team/{se-name}/feedback-log.md` completely.

**4.2 Handle missing feedback file:**
If file doesn't exist or is empty:
```
Note: No feedback history found for {SE Display Name}.
Assuming LOW deal load. Actions will be designed with standard capacity.
```
Set `deal_load = "LOW"` and `feedback_count = 0`.

**4.3 Count feedback entries from last 90 days:**
Each entry starts with `## YYYY-MM-DD | {Customer} | {Call Type}`

Count entries where date is within last 90 days from today.

Store as `feedback_count_90d`

**4.4 Determine deal load level:**
```
if feedback_count_90d > 6:
  deal_load = "HIGH"
elif feedback_count_90d >= 4:
  deal_load = "MODERATE"
else:
  deal_load = "LOW"
```

**4.5 Calculate existing development commitment:**
Sum hours/week from pending Development Actions in profile.

Store as `existing_dev_hours_weekly`

**4.6 Store workload context:**
```
workload_context = {
  deal_load: "HIGH" | "MODERATE" | "LOW",
  feedback_count: int,
  existing_dev_hours: float,
  existing_action_count: int,
  capacity_available: 6 - existing_dev_hours (typical capacity is 6 hrs/week)
}
```

**4.7 Display workload context:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Workload Context for {SE Display Name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Current Deal Load:** {deal_load} ({feedback_count} activities in last 90 days)
**Existing Development Actions:** {pending_count} pending ({existing_dev_hours} hrs/week)
**Available Capacity:** ~{capacity_available} hrs/week for new actions

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Step 5: Generate Development Actions (AC: 4, 5, 6, 7, 8, 10)

**5.1 Analyze objective:**
Parse the objective_statement to understand:
- What competency/skill is being developed
- What context clues suggest about timeline
- What action types are most relevant

**5.2 Generate 3-5 development actions:**

Based on:
- Objective statement
- SE's current role and context
- Workload context (available capacity)
- Action type balance requirements

**For each action, generate:**

```
action = {
  title: string (concise, action-oriented),
  type: "SHADOWING" | "STRETCH" | "TRAINING" | "PROJECT" | "MENTORING",
  effort: string (X hours/session, X hours/week, or X hours one-time),
  timeline: string (YYYY-MM-DD, QX YYYY, or "Ongoing"),
  description: string (1-2 sentences),
  success_criteria: string (how you know it worked)
}
```

**5.3 Action generation guidelines:**

- **Balance types:** Include at least 1 learning-focused (SHADOWING/TRAINING) and 1 doing-focused (STRETCH/PROJECT/MENTORING)
- **Sequence logically:** Learning actions typically come before application actions
- **Respect capacity:** Total effort should generally fit within available capacity
- **Be specific:** Actions should be calendar-ready with concrete activities
- **Define success:** Each action needs a measurable "how you know it worked" statement

**5.4 Display generated actions:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 Development Actions for: {objective_statement}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**1. {Action Title}**
   Type: {type}
   Effort: {effort}
   Due: {timeline}

   {description}

   How you know it worked: {success_criteria}

---

{Repeat for each action, numbered 1-5}
```

### Step 6: Assess Workload Feasibility (AC: 9)

**6.1 Calculate total new commitment:**

For each action, estimate total hours:
- "X hours/session" × expected sessions = total hours
- "X hours/week" for Y weeks = total hours
- "X hours one-time" = total hours

Sum to get `new_action_hours_total`

Estimate weekly average if actions span multiple weeks.

**6.2 Calculate combined commitment:**

```
combined_weekly = existing_dev_hours + new_weekly_average
```

**6.3 Determine feasibility:**

```
if combined_weekly <= 6:
  feasibility = "ACHIEVABLE"
elif combined_weekly <= 8:
  feasibility = "REQUIRES_ADJUSTMENT"
else:
  feasibility = "OVERLOADED"
```

Also flag REQUIRES_ADJUSTMENT or OVERLOADED if:
- deal_load == "HIGH" AND combined_weekly > 4
- existing_action_count + new_action_count > 5

**6.4 Generate suggestions if not ACHIEVABLE:**

Examples:
- "Consider extending timeline to spread effort over more weeks"
- "May need to reduce deal load to create development time"
- "Consider completing some existing actions before adding more"
- "Prioritize 2-3 highest-impact actions and defer others"

**6.5 Display workload assessment:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Workload Assessment
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Current Deal Load:** {deal_load}
**Existing Development Commitments:** {existing_dev_hours} hrs/week
**New Actions Total:** ~{new_action_hours_total} hours over {timespan}
**Combined Commitment:** ~{combined_weekly} hrs/week

**Feasibility:** {ACHIEVABLE | REQUIRES_ADJUSTMENT | OVERLOADED}

{If not ACHIEVABLE:}
⚠️ **Suggestions:**
- {suggestion 1}
- {suggestion 2}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Step 7: Modification Flow (AC: 11)

**7.1 Prompt for modifications:**

```
Would you like to modify any actions before saving? (y/n/edit)
- y = modify actions
- n = proceed to save
- edit = make specific changes
```

**7.2 Handle responses:**

**If 'n' or 'no':**
Proceed to Step 8 (Profile Save)

**If 'y' or 'yes' or 'edit':**
```
What changes would you like to make?

Examples:
- "Change the shadowing action to 3 sessions instead of 2"
- "Extend the timeline for action 4 to Q2"
- "Remove action 5"
- "Add a training action about discovery"
- "Change the effort estimate for the project to 10 hours"

Describe your changes:
```

**7.3 Parse and apply modifications:**

Listen for modification commands:
- "Change {field} in action {N} to {value}"
- "Remove action {N}"
- "Add {type} action: {description}"
- "Extend timeline for {action} to {new timeline}"
- "Reduce effort on {action} to {new effort}"

Apply changes to actions list.

**7.4 Re-display updated actions and assessment:**

Show the modified actions with updated workload assessment.

**7.5 Confirm changes:**
```
Changes applied. Would you like to make more modifications? (y/n)
```

If 'y', return to 7.2
If 'n', proceed to Step 8

### Step 8: Save to Profile (AC: 12)

**8.1 Ask for confirmation:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💾 Commit Actions to Profile
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Commit these {n} development actions to {SE Display Name}'s profile? (y/n)

This will append to the Development Actions section in:
team/{se-name}/profile.md
```

**8.2 Handle response:**

**If 'n' or 'no':**
```
Actions not saved. You can run /design-actions again when ready.
```
Exit.

**If 'y' or 'yes':**
Continue to 8.3

**8.3 Format actions for profile.md:**

Get today's date as `YYYY-MM-DD`.

Format each action as:
```markdown
- [ ] {Action title}: {description}
  Type: {type}
  Effort: {effort}
  Due: {timeline}
  Added: {today's date}
  Related Objective: {objective_statement}
```

**8.4 Update profile.md:**

Read `team/{se-name}/profile.md`

**If Development Actions section exists:**
- Find `### Development Actions` subsection
- Append new actions after existing ones

**If Development Actions does NOT exist:**
- Find `## Career Aspirations` section
- Add new subsection before the next major section:
```markdown
### Development Actions

{formatted actions}
```

**If Career Aspirations section doesn't exist:**
- Find `## Notes` section or end of file
- Add both Career Aspirations and Development Actions sections:
```markdown
## Career Aspirations

### Development Actions

{formatted actions}

---
```

**8.5 Display confirmation:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Actions Committed
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Added {n} development actions to: team/{se-name}/profile.md

**Objective:** {objective_statement}
**Feasibility:** {ACHIEVABLE | REQUIRES_ADJUSTMENT | OVERLOADED}

**Actions Added:**
{For each:}
- {type}: {title} (Due: {timeline})

**Next Steps:**
1. Review actions with {SE Display Name} in your next 1:1
2. Add calendar blocks for scheduled activities
3. Track progress by checking off actions as completed
4. Use `/career-check {se-name}` to see full career summary

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Step 9: Session Complete

**9.1 Offer follow-up options:**

```
Would you like to:
- `/design-actions {se-name} "{another objective}"` - Design actions for another objective
- `/career-check {se-name}` - See full career summary with new actions
- `/profile {se-name}` - View updated profile

Or ask me any questions about the actions we created.
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

**No feedback data:**
- Acknowledge limitation
- Default to LOW deal load
- Note that workload assessment is estimated

**Empty objective statement:**
```
Please provide an objective in quotes.

Example:
  /design-actions sarah "Build executive presence in strategic accounts"
```

**User cancels at any confirmation point:**
- Acknowledge and exit gracefully
- Suggest running command again when ready

**HIGH workload flagged:**
- Display clear warning
- Suggest reducing scope or extending timeline
- Still allow user to proceed if they choose

**Profile has no Career Aspirations section:**
- Create the section when saving
- Add Development Actions subsection

## Example Session

```
> /design-actions sarah-chen "Build executive presence in strategic accounts"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🛠️ Action Designer Agent Activated
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
I'm the Action Designer - I help turn development objectives into
concrete, calendar-ready actions. Every action comes with effort
estimates, timelines, and clear success criteria.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Loading context for Sarah Chen...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Workload Context for Sarah Chen
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Current Deal Load:** MODERATE (5 activities in last 90 days)
**Existing Development Actions:** 1 pending (2 hrs/week mentoring)
**Available Capacity:** ~4 hrs/week for new actions

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Designing development actions for: Build executive presence in strategic accounts

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 Development Actions for: Build executive presence in strategic accounts
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**1. Shadow Executive Briefings**
   Type: SHADOWING
   Effort: 2 hours/session (3 sessions)
   Due: Q1 2025

   Shadow a senior SE or executive during 3 customer executive briefings.
   Focus on how they establish credibility, frame value, and handle executive questions.

   How you know it worked: Documented 5+ techniques to incorporate into your own executive interactions.

---

**2. Executive Communication Training**
   Type: TRAINING
   Effort: 4 hours one-time
   Due: 2025-02-01

   Complete the Executive Presence module in the enablement library.
   Focus on concise messaging, strategic framing, and presence techniques.

   How you know it worked: Applied 3 techniques from training in your next executive meeting.

---

**3. Lead Strategic Account Executive Session**
   Type: STRETCH
   Effort: 4 hours prep + 1 hour session
   Due: 2025-02-28

   Lead an executive strategy session on your largest strategic account.
   Senior SE provides backup support but you drive the conversation.

   How you know it worked: Received 4+ rating on executive communication in feedback.

---

**4. Create Executive Value Narrative**
   Type: PROJECT
   Effort: 8 hours one-time
   Due: 2025-03-15

   Develop a polished executive value narrative for your primary vertical.
   Include industry context, strategic value drivers, and proof points.

   How you know it worked: Narrative used successfully in 2+ executive conversations.

---

**5. Mentor Peer on Executive Skills**
   Type: MENTORING
   Effort: 1 hour/week for 4 weeks
   Due: 2025-03-31

   Partner with a peer who wants to develop executive presence.
   Share learnings from your shadowing and training, provide feedback on their approach.

   How you know it worked: Peer reports improved confidence in executive conversations.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Workload Assessment
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Current Deal Load:** MODERATE
**Existing Development Commitments:** 2 hrs/week
**New Actions Total:** ~27 hours over 12 weeks (~2.3 hrs/week)
**Combined Commitment:** ~4.3 hrs/week

**Feasibility:** ACHIEVABLE

This commitment level fits within typical development capacity. The actions
are sequenced from learning (shadowing/training) to application (stretch/project)
to reinforcement (mentoring).
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Would you like to modify any actions before saving? (y/n/edit) y

What changes would you like to make? "Change the shadowing action to 3 sessions instead of 2"

The shadowing action is already set for 3 sessions. Did you mean a different change?

Let me know if you'd like to:
- Change the effort on any action
- Adjust timelines
- Remove or add actions

Make another change or type 'n' to proceed: n

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💾 Commit Actions to Profile
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Commit these 5 development actions to Sarah Chen's profile? (y/n) y

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Actions Committed
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Added 5 development actions to: team/sarah-chen/profile.md

**Objective:** Build executive presence in strategic accounts
**Feasibility:** ACHIEVABLE

**Actions Added:**
- SHADOWING: Shadow Executive Briefings (Due: Q1 2025)
- TRAINING: Executive Communication Training (Due: 2025-02-01)
- STRETCH: Lead Strategic Account Executive Session (Due: 2025-02-28)
- PROJECT: Create Executive Value Narrative (Due: 2025-03-15)
- MENTORING: Mentor Peer on Executive Skills (Due: 2025-03-31)

**Next Steps:**
1. Review actions with Sarah Chen in your next 1:1
2. Add calendar blocks for scheduled activities
3. Track progress by checking off actions as completed
4. Use `/career-check sarah-chen` to see full career summary

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Performance Target

Action design session should complete in < 3 minutes (less interactive than goal decomposition).

## Related Commands

- `/decompose-goal {se-name} "{goal}"` - Break down career goals into quarterly objectives
- `/career-check {se-name}` - Career summary with competency gaps
- `/plan-goal {se-name}` - Collaborative goal planning (combines Goal Decomposer + Action Designer)
- `/profile {se-name}` - View/edit SE profile
- `/add-se {name}` - Create new SE profile

## Implementation Status

**Status:** Complete - Story 6.3
**Implemented:** 2025-12-26
