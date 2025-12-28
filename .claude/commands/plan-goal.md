# /plan-goal - Collaborative Career Planning Mode

Orchestrate a collaborative career planning session using both Goal Decomposer and Action Designer agents. This command manages draft state for session recovery, allows agents to cross-reference and challenge each other's outputs, presents conflicts for user resolution, and commits the complete plan to the SE's profile.

## What This Does

1. Checks for existing draft state and offers resume if found
2. Creates initial draft state on session start
3. Runs Goal Decomposer phase (clarifying questions, quarterly objectives)
4. User confirms objectives with opportunity to modify
5. Runs Action Designer phase for each confirmed objective
6. Agents cross-reference each other's outputs and flag issues
7. Presents conflicts between agent recommendations for user resolution
8. Displays complete plan (all objectives + all actions) for final review
9. Commits confirmed plan to profile.md with timestamps
10. Deletes draft file after successful commit

## Usage

```
/plan-goal sarah-chen "Become Principal SE in 18 months"
/plan-goal sarah "Improve discovery skills to lead strategic deals"
```

## Arguments

- `se-name`: The SE's name (supports fuzzy matching)
- `goal`: A career goal statement in quotes

## Agents Used

- `_agents/goal-decomposer-persona.md` - Pragmatic Career Strategist persona
- `_agents/action-designer-persona.md` - Practical Development Coach persona

## Implementation

When this command is run, follow these steps exactly:

### Step 1: Check for Existing Draft State (AC: 2, 3)

**1.1 Parse SE name from arguments first:**

Parse arguments from: $ARGUMENTS

Expected format: `{se-name} "{goal statement}"`

Extract:
- `se_name_input`: First argument (SE name)
- `goal_statement`: Second argument (text in quotes)

**1.2 Handle missing arguments:**

If no arguments or only one provided:
```
Please provide both SE name and goal statement.

Usage: /plan-goal {se-name} "{goal}"

Example:
  /plan-goal sarah-chen "Become Principal SE in 18 months"
```
Exit.

**1.3 Normalize and resolve SE name:**
- Convert to lowercase
- Replace spaces with hyphens
- Remove special characters
- List SE folders in `team/` (exclude `_template/`, `_archived/`)
- Apply fuzzy matching (Levenshtein distance <= 2)

**If no match found:**
```
I couldn't find an SE named "{input}". Did you mean:
  - {suggestion1}
  - {suggestion2}

Or run `/add-se {input}` to create a new profile.
```
Exit.

**1.4 Get SE display name from profile.md**

Store: `se_name`, `se_display_name`

**1.5 Check for draft file:**
Look for `.career-planning-draft.yaml` in `team/{se-name}/` directory.

**1.6 If draft exists:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Found Saved Draft
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

I found a saved career planning draft for {SE Display Name}:

**Goal:** {draft.goal}
**Created:** {draft.created}
**Stage:** {draft.stage}

Resume this planning session? (y/n)
- y = Resume from where you left off
- n = Start fresh (deletes existing draft)
```

**If 'y' or 'yes':**
- Load draft state completely
- Extract: `goal`, `stage`, `clarification_answers`, `proposed_objectives`, `confirmed_objectives`, `proposed_actions`, `conflicts`
- Jump to appropriate stage:
  - CLARIFICATION → Step 4 (display questions with previous answers, allow modification)
  - OBJECTIVES → Step 5 (display objectives for review)
  - ACTIONS → Step 6 (continue action generation from last objective)
  - REVIEW → Step 8 (display complete plan for final review)

**If 'n' or 'no':**
- Delete existing draft file
- Continue to Step 2 for fresh start

**1.7 If no draft exists:**
Continue to Step 2.

### Step 2: Create Initial Draft State (AC: 2)

**2.1 Create draft state structure:**

```yaml
created: "{YYYY-MM-DD HH:MM:SS}"
goal: "{goal_statement}"
se_name: "{se_name}"
stage: "CLARIFICATION"

clarification_answers: []

proposed_objectives: []

confirmed_objectives: []

proposed_actions: []

conflicts: []
```

**2.2 Save draft to `team/{se-name}/.career-planning-draft.yaml`**

**2.3 Display session start:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 Collaborative Career Planning Session
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Starting career planning session for: {SE Display Name}
Goal: "{goal_statement}"

This session will:
1. Break down your goal into quarterly objectives (Goal Decomposer)
2. Design development actions for each objective (Action Designer)
3. Cross-reference and resolve any conflicts between recommendations
4. Save the complete plan to {se_name}'s profile

Your progress is automatically saved. If interrupted, run
/plan-goal {se_name} to resume.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Step 3: Load SE Context and Agent Personas

**3.1 Load Goal Decomposer persona:**
Read `{project-root}/.claude/commands/_agents/goal-decomposer-persona.md` completely.

**3.2 Load Action Designer persona:**
Read `{project-root}/.claude/commands/_agents/action-designer-persona.md` completely.

**3.3 Read SE profile:**
Read `team/{se-name}/profile.md` completely.

Extract:
- `current_role`
- `focus_areas`
- `career_aspirations` (target role, timeline, motivation)
- `existing_objectives` from Growth Objectives section
- `existing_actions` from Development Actions section

**3.4 Read SE feedback log:**
Read `team/{se-name}/feedback-log.md` completely.

Calculate:
- Competency averages per meeting competency
- Role competency gaps (derived from meeting competencies)
- Deal load level (HIGH/MODERATE/LOW based on last 90 days)
- Feedback entry count

**3.5 Read competency configuration:**
Read `config/competencies/meeting-competencies.yaml`
Read `config/competencies/role-competencies.yaml`

Map meeting competencies to role competencies using `maps_to_role` field.

**3.6 Store context for both agents:**
```
context = {
  se_name: string,
  se_display_name: string,
  current_role: string,
  focus_areas: [],
  career_aspirations: {},
  existing_objectives: [],
  existing_actions: [],
  competency_gaps: [],
  deal_load: string,
  feedback_count: int
}
```

### Step 4: Goal Decomposer Phase - Clarifying Questions (AC: 4)

**4.1 Activate Goal Decomposer persona:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 [Goal Decomposer] Phase 1: Understanding Your Goal
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

I'm the Goal Decomposer. Before I create quarterly objectives, I need
to understand your specific situation. My questions will reference your
actual feedback data and career context.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**4.2 Generate 2-4 contextual questions:**

Questions MUST reference SE-specific data when available.

**Question templates with data:**

If competency gaps exist:

Question 1 - Competency Gap (required):
- Find highest priority gap
- Ask: "Looking at your feedback, your {competency_name} is at {current:.1f} while {target_role} expectations are {target:.1f}. What's been holding you back in this area?"

Question 2 - Strength Leverage:
- Find highest rated competency
- Ask: "Your {competency_name} is your strongest area at {current:.1f}. How might we leverage that strength in your development plan?"

Question 3 - Timeline (required):
- Extract timeline from goal_statement or use "your timeline"
- Ask: "You mentioned {timeline}. Is that driven by a specific event (promotion cycle, role opening) or is it aspirational? Is there flexibility?"

Question 4 - Workload/Constraints:
- Count feedback entries in last quarter as proxy for deal activity
- Ask: "Based on your recent activity, you've been busy with {n} deals. Can you realistically reduce deal load to focus on development, or is that fixed?"

**If no feedback data:**

Question 1 (required):
- Ask: "Without detailed feedback data, I'd like to understand: What do you see as your biggest competency gap right now for reaching {target_role}?"

Question 2 (required):
- Ask: "Is your timeline of {timeline} driven by a specific event or aspirational? Is there flexibility?"

Question 3:
- Ask: "Are there organizational factors we should consider - upcoming reorgs, role openings, or promotion cycles?"

Question 4:
- Ask: "What's your current workload like? Can you carve out time for development activities?"

**4.3 Display questions and wait:**

```
📋 Goal: {goal_statement}

Before I create your quarterly objectives, I need to understand a few things:

1. **Competency Focus:** {Question 1}

2. **Timeline Reality:** {Question 2}

3. **Workload Constraints:** {Question 3}

4. **Organizational Factors:** {Question 4 - if applicable}

Please answer these questions so I can create relevant, achievable objectives.
```

**4.4 Wait for and parse user answers:**

WAIT for user to respond with answers.

Parse and store answers:
- `answer_competency_gap`
- `answer_timeline`
- `answer_workload`
- `answer_organizational`

**4.5 Update draft state:**

```yaml
clarification_answers:
  - question: "{question 1}"
    answer: "{user answer 1}"
  - question: "{question 2}"
    answer: "{user answer 2}"
  ...
stage: "OBJECTIVES"
```

Save updated draft.

### Step 5: Goal Decomposer Phase - Generate Objectives (AC: 4, 5)

**5.1 Generate 3-5 quarterly objectives:**

Based on:
- Goal statement
- Competency gaps (prioritize HIGH, then MEDIUM)
- User answers to clarifying questions
- Target role requirements

**For each objective, generate:**

```
objective = {
  quarter: "QX YYYY",
  title: string (concise, action-oriented),
  description: string (1-2 sentences),
  success_criteria: [
    string (specific, measurable outcome),
    string,
    string (optional)
  ],
  dependencies: [
    string (prerequisite, approval, or resource)
  ],
  risks: [
    string (potential blocker or constraint)
  ],
  competency_alignment: {
    competency: string (role competency name),
    current: float,
    target: float,
    gap: float
  }
}
```

**5.2 Assess timeline feasibility:**

**ACHIEVABLE** when:
- Average gap per objective is < 0.5
- User indicated flexibility on timeline
- Workload can accommodate development time
- No major organizational blockers

**AMBITIOUS** when:
- Some gaps > 0.5 or total gap > 1.5
- Timeline is tight but possible with focused effort
- Requires some workload adjustment
- Depends on favorable conditions

**UNREALISTIC** when:
- Multiple gaps > 1.0 or total gap > 2.5
- Timeline is too short for gap magnitude
- Workload cannot be adjusted
- Major organizational blockers exist

**5.3 Display objectives:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 [Goal Decomposer] Phase 2: Quarterly Objectives
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Based on your goal and our discussion, here are your quarterly objectives:

{For each objective:}

**{quarter}: {title}**

{description}

**Success Criteria:**
- [ ] {criterion 1}
- [ ] {criterion 2}
- [ ] {criterion 3 if present}

**Dependencies:**
- {dependency 1}
- {dependency 2 if present}

**Risk Factors:**
- {risk 1}

**Competency Alignment:**
| Competency | Current | Target | Gap |
|------------|---------|--------|-----|
| {competency} | {current:.1f} | {target:.1f} | {gap:+.1f} |

---

{Repeat for all objectives}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Timeline Feasibility Assessment
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Assessment:** {ACHIEVABLE | AMBITIOUS | UNREALISTIC}

**Reasoning:**
{Specific reasoning based on gaps, timeline, and constraints}

{If AMBITIOUS or UNREALISTIC:}
**Tradeoffs to Consider:**
- {tradeoff 1}
- {tradeoff 2}

**Recommendation:**
{Specific recommendation}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**5.4 Update draft with proposed objectives:**

```yaml
proposed_objectives:
  - quarter: "Q1 2025"
    title: "..."
    # ... full objective structure
```

Save updated draft.

**5.5 User confirms objectives (AC: 5, 12):**

```
Would you like to modify any objectives before proceeding to action planning?
(c = confirm and continue, m = modify, q = quit and save draft)
```

**If 'm' or 'modify':**
```
What changes would you like to make?

Examples:
- "Move the Q2 objective to Q1"
- "Add a success criterion to objective 3"
- "Remove the risk factor about workload"
- "Change the timeline assessment"
- "Add a new objective about mentoring"

Describe your changes:
```

Apply modifications, re-display, and ask again.

**If 'q' or 'quit':**
```
Draft saved. Run /plan-goal {se-name} to resume later.
```
Exit (draft preserved - AC: 15).

**If 'c' or 'confirm' or 'continue':**

**5.6 Store confirmed objectives:**

```yaml
confirmed_objectives:
  - quarter: "Q1 2025"
    title: "..."
    # ... confirmed objective structure
stage: "ACTIONS"
```

Save updated draft.

### Step 6: Action Designer Phase (AC: 6)

**6.1 Activate Action Designer persona:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🛠️ [Action Designer] Phase 3: Development Actions
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

I'm the Action Designer. Now I'll create concrete, calendar-ready development
actions for each of your {n} confirmed objectives.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**6.2 For each confirmed objective, generate 3-5 actions:**

For each objective in `confirmed_objectives`:

Display:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 Actions for Objective {n}/{total}: {objective.title}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**1. {Action Title}**
   Type: {SHADOWING | STRETCH | TRAINING | PROJECT | MENTORING}
   Effort: {effort estimate}
   Due: {timeline}

   {description}

   How you know it worked: {success_criteria}

---

{Repeat for 3-5 actions}
```

**6.3 User can modify actions for each objective:**

```
Accept these actions for "{objective.title}"? (y = accept, m = modify)
```

**If 'm':**
Allow modifications, re-display, ask again.

**If 'y':**
Store actions and continue to next objective.

**6.4 Store all proposed actions:**

```yaml
proposed_actions:
  - objective: "{objective.title}"
    actions:
      - action: "{action description}"
        type: "{type}"
        effort: "{effort}"
        timeline: "{timeline}"
        success_criteria: "{criteria}"
```

Save updated draft after each objective's actions are confirmed.

### Step 7: Cross-Reference Phase (AC: 7, 8)

**7.1 Action Designer reviews objectives:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔄 [Action Designer] Cross-Reference Analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Let me review the objectives now that I've designed actions for all of them...
```

Check for:
- Multiple objectives requiring same resources (time, people, access)
- Timeline conflicts between objectives and action due dates
- Workload overload when all actions are combined (calculate total hours/week)
- Unrealistic effort distribution

**If issues found:**
```
[Action Designer]: Looking at {objective 1} and {objective 2}...

⚠️ **Resource Conflict Detected:**
Both objectives require {resource} during {timeframe}. This may create contention.

**Suggested Resolution:**
- Option A: {shift one objective's timeline}
- Option B: {reduce scope of one objective}
```

**7.2 Goal Decomposer responds:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔄 [Goal Decomposer] Response to Cross-Reference
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Let me review the Action Designer's analysis...
```

Check for:
- Actions that don't fully address objectives
- Missing activities for certain competency gaps
- Suggestions for objective adjustments based on action feasibility

**If issues found:**
```
[Goal Decomposer]: Reviewing the actions for {objective}...

⚠️ **Alignment Concern:**
The proposed actions may not fully address the success criterion "{criterion}".

**Suggested Adjustment:**
- Consider adding {additional action type} focused on {specific area}
- Or adjust the success criterion to be more achievable: "{revised criterion}"
```

**7.3 Store cross-reference notes:**

Add any issues found to draft:
```yaml
conflicts:
  - source: "ACTION_DESIGNER"
    description: "{conflict description}"
    options:
      - "Option A: {description}"
      - "Option B: {description}"
    resolution: "PENDING"
  - source: "GOAL_DECOMPOSER"
    description: "{concern description}"
    options:
      - "Option A: {description}"
      - "Option B: {description}"
    resolution: "PENDING"
```

Save updated draft.

### Step 8: Conflict Resolution Phase (AC: 9, 10)

**8.1 If no conflicts:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ No Conflicts Detected
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Both agents agree that the objectives and actions are well-aligned.
Proceeding to final review.
```

Skip to Step 9.

**8.2 For each conflict, present options:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚖️ Conflict Resolution Required
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Conflict {n}/{total}:** {conflict.description}

**Source:** {conflict.source}

**Options:**
  A: {option_a_description}
  B: {option_b_description}

Which option would you prefer? (a/b/skip)
- a = Choose Option A
- b = Choose Option B
- skip = Leave unresolved (will be noted in plan)
```

**8.3 Store resolution:**

Update conflict in draft:
```yaml
conflicts:
  - source: "{source}"
    description: "{description}"
    resolution: "USER_CHOICE_A" | "USER_CHOICE_B" | "SKIPPED"
```

**8.4 Apply resolution:**

Modify objectives or actions based on user's choice.

Save updated draft.

### Step 9: Final Review Phase (AC: 11, 12)

**9.1 Update draft stage:**

```yaml
stage: "REVIEW"
```

Save updated draft.

**9.2 Display complete plan:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 COMPLETE CAREER PLAN: {goal_statement}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**SE:** {SE Display Name}
**Goal:** {goal_statement}
**Timeline Assessment:** {ACHIEVABLE | AMBITIOUS | UNREALISTIC}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 GROWTH OBJECTIVES ({n} total)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{For each objective:}

**{n}. {quarter}: {title}**
   {description}
   Success Criteria: {criteria summary}
   Competency Focus: {competency} ({current:.1f} → {target:.1f})

{Repeat}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🛠️ DEVELOPMENT ACTIONS ({total_actions} total)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{For each objective with its actions:}

**For: {objective.title}**

{For each action:}
  - [{type}] {action_title} - {effort} - Due: {timeline}

{Repeat}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 WORKLOAD SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Total Actions:** {total_actions}
**Estimated Weekly Commitment:** ~{total_hours} hours/week average
**Feasibility:** {ACHIEVABLE | REQUIRES_ADJUSTMENT | OVERLOADED}

{If conflicts were resolved:}
**Resolved Conflicts:** {n} conflicts addressed during planning

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**9.3 Final modification opportunity:**

```
Would you like to make any final changes before committing this plan?
(y = make changes, n = proceed to commit, q = quit and save draft)
```

**If 'y':**
```
What would you like to change?
- "Remove objective 3"
- "Add an action to objective 2"
- "Change the timeline for action X"

Describe your changes:
```

Apply changes, re-display complete plan, ask again.

**If 'q':**
```
Draft saved. Run /plan-goal {se-name} to resume later.
```
Exit (draft preserved - AC: 15).

**If 'n':**
Continue to Step 10.

### Step 10: Commit Plan to Profile (AC: 13, 14)

**10.1 Ask for final confirmation:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💾 Commit Career Plan
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Commit this plan to {SE Display Name}'s profile? (y/n)

This will:
1. Add {n} objectives to Growth Objectives section
2. Add {m} development actions to Development Actions section
3. Include timestamps for tracking

File: team/{se-name}/profile.md
```

**10.2 Handle response:**

**If 'n' or 'no':**
```
Plan not saved. Draft preserved at:
team/{se-name}/.career-planning-draft.yaml

Run /plan-goal {se-name} to resume later.
```
Exit.

**If 'y' or 'yes':**
Continue to 10.3

**10.3 Format objectives for profile.md:**

Get today's date as `YYYY-MM-DD`.

Format each objective as:
```markdown
- [ ] {Objective title} ({quarter})
  Status: NOT STARTED
  Added: {today's date}
  Goal: {Original goal statement}
  Success Criteria:
    - {criterion 1}
    - {criterion 2}
  Competency Focus: {competency name}
```

**10.4 Format actions for profile.md:**

Format each action as:
```markdown
- [ ] {Action title}: {description}
  Type: {SHADOWING | STRETCH | TRAINING | PROJECT | MENTORING}
  Effort: {effort}
  Due: {timeline}
  Added: {today's date}
  Related Objective: {objective title}
```

**10.5 Update profile.md:**

Read `team/{se-name}/profile.md`

**For Growth Objectives:**
- Find `### Growth Objectives` subsection
- If exists: Append new objectives after existing ones
- If not exists: Create section under `## Career Aspirations`

**For Development Actions:**
- Find `### Development Actions` subsection
- If exists: Append new actions after existing ones
- If not exists: Create section under `## Career Aspirations`

**If Career Aspirations section doesn't exist:**
- Find `## Notes` section or end of file
- Add both Career Aspirations and Development Actions sections

**10.6 Delete draft file (AC: 14):**

Delete `team/{se-name}/.career-planning-draft.yaml`

**10.7 Display confirmation:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Career Plan Committed
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Successfully saved to: team/{se-name}/profile.md

**Goal:** {goal_statement}
**Timeline Assessment:** {ACHIEVABLE | AMBITIOUS | UNREALISTIC}

**Added:**
- {n} Growth Objectives
- {m} Development Actions

**Objectives:**
{For each:}
- {quarter}: {title}

**Actions:**
{For each:}
- [{type}] {title} (Due: {timeline})

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 Next Steps
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Review the plan with {SE Display Name} in your next 1:1
2. Add calendar blocks for scheduled activities
3. Run `/career-check {se-name}` to track progress
4. Update objectives and actions as they're completed

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Step 11: Session Complete

**11.1 Offer follow-up options:**

```
Would you like to:
- `/career-check {se-name}` - See full career summary with new plan
- `/plan-goal {another-se} "{goal}"` - Plan for another SE
- Ask questions about the plan we created

Or is there anything else you'd like help with?
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
- Generate more general objectives
- Use LOW workload assumption
- Note limitations in output

**Empty goal statement:**
```
Please provide a goal statement in quotes.

Example:
  /plan-goal sarah "Become Principal SE in 18 months"
```

**Draft file corrupted:**
```
The saved draft appears to be corrupted. Would you like to:
- Start fresh (delete corrupted draft)
- Exit and manually inspect the file

Choose (start/exit):
```

**User exits at any point (AC: 15):**
- Draft is preserved automatically
- User can resume with `/plan-goal {se-name}`

**Config files missing:**
- Use sensible defaults for competency mappings
- Note the limitation in output

**Profile missing Career Aspirations section:**
- Create the section when saving
- Add both Growth Objectives and Development Actions subsections

## Draft State Schema

```yaml
# team/{se-name}/.career-planning-draft.yaml
created: "YYYY-MM-DD HH:MM:SS"
goal: "{original goal text}"
se_name: "{se-name}"
stage: "CLARIFICATION | OBJECTIVES | ACTIONS | REVIEW"

clarification_answers:
  - question: "{question asked}"
    answer: "{user response}"

proposed_objectives:
  - quarter: "Q1 2025"
    title: "{objective title}"
    description: "{description}"
    success_criteria:
      - "{criterion}"
    dependencies:
      - "{dependency}"
    risks:
      - "{risk}"
    competency_alignment:
      competency: "{name}"
      current: 2.5
      target: 3.5
      gap: 1.0

confirmed_objectives:
  - # Same structure as proposed_objectives

proposed_actions:
  - objective: "{objective title}"
    actions:
      - action: "{action description}"
        type: "SHADOWING"
        effort: "2 hours/session"
        timeline: "Q1 2025"
        success_criteria: "{how you know it worked}"

conflicts:
  - source: "ACTION_DESIGNER | GOAL_DECOMPOSER"
    description: "{conflict description}"
    options:
      - "Option A: {description}"
      - "Option B: {description}"
    resolution: "PENDING | USER_CHOICE_A | USER_CHOICE_B | SKIPPED"
```

## Performance Target

Collaborative planning session should complete in < 5 minutes (interactive).

## Related Commands

- `/decompose-goal {se-name} "{goal}"` - Standalone goal decomposition
- `/design-actions {se-name} "{objective}"` - Standalone action design
- `/career-check {se-name}` - Career summary with competency gaps
- `/profile {se-name}` - View/edit SE profile
- `/add-se {name}` - Create new SE profile

## Implementation Status

**Status:** Complete - Story 6.4
**Implemented:** 2025-12-27
