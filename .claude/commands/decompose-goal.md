# /decompose-goal - AI-Assisted Goal Decomposition

Break down a high-level career goal into specific, actionable quarterly objectives using the Goal Decomposer agent persona. The agent asks clarifying questions, generates SMART objectives with competency alignment, assesses timeline feasibility, and saves confirmed objectives to the SE's profile.

## What This Does

1. Loads the Goal Decomposer agent persona
2. Resolves SE name (fuzzy matching)
3. Loads SE context: profile, career aspirations, feedback history
4. Calculates competency gaps to inform questions and objectives
5. Asks 2-4 clarifying questions referencing SE-specific data
6. Generates 3-5 quarterly objectives with success criteria, dependencies, risks
7. Provides timeline feasibility assessment (ACHIEVABLE/AMBITIOUS/UNREALISTIC)
8. Allows modification of objectives before saving
9. Appends confirmed objectives to profile.md Growth Objectives section

## Usage

```
/decompose-goal sarah-chen "Become Principal SE in 18 months"
/decompose-goal sarah "Improve discovery skills to lead strategic deals"
```

## Arguments

- `se-name`: The SE's name (supports fuzzy matching)
- `goal`: A goal statement in quotes describing the career aspiration

## Agents Used

- `_agents/goal-decomposer-persona.md` - Pragmatic Career Strategist persona

## Implementation

When this command is run, follow these steps exactly:

### Step 1: Load Goal Decomposer Agent Persona

**1.1 Read the persona file:**
Read `{project-root}/.claude/commands/_agents/goal-decomposer-persona.md` completely.

**1.2 Activate persona:**
Adopt the persona's tone, behaviors, and constraints for this entire session:
- **Tone:** Direct, data-driven, encouraging but realistic
- **Key behaviors:** Reference data, ask hard questions, ground in context, quantify gaps
- **Constraints:** Never invent data, never skip questions, honest timeline assessments

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 Goal Decomposer Agent Activated
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
I'm the Goal Decomposer - I help transform career aspirations into
structured quarterly objectives. I'll ask hard questions and ground
everything in your actual feedback data.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Step 2: Parse Arguments and Resolve SE Name

**2.1 Parse arguments from:** $ARGUMENTS

Expected format: `{se-name} "{goal statement}"`

Extract:
- `se_name_input`: First argument (SE name)
- `goal_statement`: Second argument (text in quotes)

**2.2 Handle missing arguments:**

If no arguments or only one provided:
```
Please provide both SE name and goal statement.

Usage: /decompose-goal {se-name} "{goal}"

Example:
  /decompose-goal sarah-chen "Become Principal SE in 18 months"
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

### Step 3: Load SE Context (AC: 3)

**3.1 Read profile.md:**
Read `team/{se-name}/profile.md` completely.

**3.2 Extract current role:**
Look for:
- `## Role & Context` section → `**Current Role:**` or `**Role:**` field
- `**Title:**` field
- Default to "Solution Engineer" if not found

Store as `current_role`

**3.3 Extract focus areas:**
Look for:
- `**Technical Focus:**` field
- `**Industry Focus:**` field
- `### Focus Areas` subsection

Store as `focus_areas[]`

**3.4 Extract career aspirations:**
Look for `## Career Aspirations` or `## Career Aspirations (Career Progression Track)` section.

**For new format:**
- Target Role: from `**Target Role:**` line
- Target Timeline: from `**Target Timeline:**` line
- Motivation: from `**Motivation:**` line

**For existing format:**
- Short-Term: from `### Short-Term` subsection
- Medium-Term: from `### Medium-Term` subsection
- Long-Term: from `### Long-Term` subsection

Store as:
```
career_aspirations = {
  target_role: string,
  target_timeline: string,
  motivation: string
}
```

**3.5 If no Career Aspirations section found:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ℹ️ No Career Aspirations Found
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{SE Display Name}'s profile doesn't have a Career Aspirations section yet.

I can still help decompose the goal you've provided:
"{goal_statement}"

However, for better context, consider first running:
  /career-check {se-name}

Continue anyway? (y/n)
```
If 'n', exit. If 'y', continue with provided goal.

### Step 4: Calculate Competency Gaps from Feedback (AC: 4)

**4.1 Read feedback-log.md:**
Read `team/{se-name}/feedback-log.md` completely.

**4.2 Handle missing feedback file:**
If file doesn't exist or is empty:
```
Note: No feedback history found for {SE Display Name}.
I'll generate objectives based on the goal, but without specific
competency data, recommendations will be more general.
```
Set `has_feedback_data = false` and skip to Step 5.

**4.3 Parse all feedback entries:**
Each entry starts with `## YYYY-MM-DD | {Customer} | {Call Type}`

For each entry, extract competency ratings from:
- `### Competency Ratings` table (meeting competencies, 1-4 scale)
- `### Dimension Ratings` table (role competencies, X/5 scale - convert to 1-4)

**4.4 Calculate average rating per meeting competency:**
For each unique meeting competency:
- Sum all ratings
- Divide by count
- Store: `{competency_id: {name: string, avg: float, count: int}}`

**4.5 Read competency configuration:**
Read `config/competencies/meeting-competencies.yaml`
Read `config/competencies/role-competencies.yaml`

**4.6 Map meeting competencies to role competencies:**

Using `maps_to_role` from meeting-competencies.yaml:
- For each role competency, find all meeting competencies that map to it
- Average those meeting competency averages
- Store derived role competency rating

**4.7 Define target ratings based on goal:**

Parse the goal_statement to identify target role:
- Contains "Principal" → target = 3.5-4.0
- Contains "Senior" → target = 3.0-3.5
- Contains "Lead" or "Staff" → target = 4.0
- Default → target = 3.5

**4.8 Calculate gaps:**

For each role competency:
```
gap = target - current_avg
priority =
  "HIGH" if gap > 1.0
  "MEDIUM" if gap > 0.5
  "LOW" otherwise
```

Store as `competency_gaps[]`:
```
{
  competency: string,
  name: string,
  current: float,
  target: float,
  gap: float,
  priority: "HIGH" | "MEDIUM" | "LOW"
}
```

Set `has_feedback_data = true`

### Step 5: Ask Clarifying Questions (AC: 5)

**5.1 Generate 2-4 contextual questions:**

Questions MUST reference SE-specific data when available.

**Question templates with data:**

If `has_feedback_data`:

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

**5.2 Display questions and wait:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Goal: {goal_statement}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Before I create your quarterly objectives, I need to understand a few things:

1. **Competency Focus:** {Question 1}

2. **Timeline Reality:** {Question 2}

3. **Workload Constraints:** {Question 3}

4. **Organizational Factors:** {Question 4 - if applicable}

Please answer these questions so I can create relevant, achievable objectives.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**5.3 Wait for and parse user answers:**

WAIT for user to respond with answers.

Parse and store answers for use in objective generation:
- `answer_competency_gap`
- `answer_timeline`
- `answer_workload`
- `answer_organizational`

### Step 6: Generate Quarterly Objectives (AC: 6, 7, 8, 9)

**6.1 Determine quarters based on timeline:**

Parse timeline from goal_statement and answers:
- Extract number of months/quarters
- Calculate which calendar quarters are covered
- Start from current quarter + 1 (next quarter)

Example: "18 months" starting from Q1 2025 → Q1 2025 through Q2 2026

**6.2 Generate 3-5 objectives:**

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

**6.3 Objective generation guidelines:**

- Earlier quarters: Foundation building, addressing biggest gaps
- Middle quarters: Skill application, visibility opportunities
- Later quarters: Demonstration, proof of readiness
- Each objective should build on previous ones
- Success criteria must be specific: numbers, dates, deliverables
- Dependencies should be realistic: manager approval, peer support, etc.
- Risks should acknowledge real constraints from user answers

**6.4 Display generated objectives:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 Quarterly Objectives for: {goal_statement}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

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
- {risk 2 if present}

**Competency Alignment:**
| Competency | Current | Target | Gap |
|------------|---------|--------|-----|
| {competency} | {current:.1f} | {target:.1f} | {gap:+.1f} |

---

{Repeat for all objectives}
```

### Step 7: Timeline Feasibility Assessment (AC: 10, 11)

**7.1 Analyze timeline feasibility:**

Consider:
- Total competency gap to close (sum of all gaps being addressed)
- Number of objectives vs. time available
- Workload constraints from user answers
- Organizational factors from user answers

**7.2 Determine assessment:**

**ACHIEVABLE** when:
- Average gap per objective is < 0.5
- User indicated flexibility on timeline
- Workload can accommodate development time
- No major organizational blockers

**AMBITIOUS** when:
- Some gaps > 0.5 or total gap > 1.5
- Timeline is tight but possible with focused effort
- Requires some workload adjustment
- Depends on favorable conditions (role opening, reduced deals)

**UNREALISTIC** when:
- Multiple gaps > 1.0 or total gap > 2.5
- Timeline is too short for gap magnitude
- Workload cannot be adjusted
- Major organizational blockers exist

**7.3 Generate tradeoffs (if AMBITIOUS or UNREALISTIC):**

Examples:
- "May need to reduce deal load by 15-20% to create development time"
- "Requires explicit manager support for shadowing opportunities"
- "Timeline assumes a Principal SE opening becomes available"
- "Consider extending timeline to 24 months for more realistic pacing"

**7.4 Display assessment:**

```
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
- {tradeoff 3 if applicable}

**Recommendation:**
{Specific recommendation - extend timeline, reduce scope, etc.}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Step 8: Modification Flow (AC: 12)

**8.1 Prompt for modifications:**

```
Would you like to modify any objectives before saving? (y/n/edit)
- y = modify objectives
- n = proceed to save
- edit = make specific changes
```

**8.2 Handle responses:**

**If 'n' or 'no':**
Proceed to Step 9 (Profile Save)

**If 'y' or 'yes' or 'edit':**
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

**8.3 Parse and apply modifications:**

Listen for modification commands:
- "Move {objective/quarter} to {new quarter}"
- "Add {success criterion/dependency/risk} to {objective number}"
- "Remove {objective/criterion/dependency/risk}"
- "Change {field} in {objective} to {new value}"
- "Add new objective: {description}"

Apply changes to objectives list.

**8.4 Re-display updated objectives:**

Show the modified objectives with changes highlighted.

**8.5 Confirm changes:**
```
Changes applied. Would you like to make more modifications? (y/n)
```

If 'y', return to 8.2
If 'n', proceed to Step 9

### Step 9: Save to Profile (AC: 13)

**9.1 Ask for confirmation:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💾 Save Objectives to Profile
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Save these {n} objectives to {SE Display Name}'s profile? (y/n)

This will append to the Growth Objectives section in:
team/{se-name}/profile.md
```

**9.2 Handle response:**

**If 'n' or 'no':**
```
Objectives not saved. You can run /decompose-goal again when ready.
```
Exit.

**If 'y' or 'yes':**
Continue to 9.3

**9.3 Format objectives for profile.md:**

Format each objective as:
```markdown
- [ ] {Objective title} ({quarter})
  Status: NOT STARTED
  Added: {YYYY-MM-DD}
  Goal: {Original goal statement}
  Success Criteria:
    - {criterion 1}
    - {criterion 2}
  Competency Focus: {competency name}
```

**9.4 Update profile.md:**

Read `team/{se-name}/profile.md`

**If Growth Objectives section exists:**
- Find `### Growth Objectives` subsection
- Append new objectives after existing ones

**If Growth Objectives does NOT exist:**
- Find `## Career Aspirations` section
- Add new subsection before the next major section:
```markdown
### Growth Objectives

{formatted objectives}
```

**9.5 Display confirmation:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Objectives Saved
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Added {n} objectives to: team/{se-name}/profile.md

**Goal:** {goal_statement}
**Timeline Assessment:** {ACHIEVABLE | AMBITIOUS | UNREALISTIC}

**Objectives Added:**
{For each:}
- {quarter}: {title}

**Next Steps:**
1. Review objectives with {SE Display Name} in your next 1:1
2. Use `/career-check {se-name}` to see full career summary
3. Track progress by checking off success criteria as completed
4. Run `/plan-goal {se-name}` for detailed action planning

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Step 10: Session Complete

**10.1 Offer follow-up options:**

```
Would you like to:
- `/career-check {se-name}` - See full career summary with new objectives
- `/plan-goal {se-name}` - Create detailed action plans for objectives
- Decompose another goal for this SE

Or ask me any questions about the objectives we created.
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
- Note that competency alignment is estimated

**Empty goal statement:**
```
Please provide a goal statement in quotes.

Example:
  /decompose-goal sarah "Become Principal SE in 18 months"
```

**User cancels at any confirmation point:**
- Acknowledge and exit gracefully
- Suggest running command again when ready

**Config files missing:**
- Use sensible defaults for competency mappings
- Note the limitation in output

## Example Session

```
> /decompose-goal sarah-chen "Become Principal SE in 18 months"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 Goal Decomposer Agent Activated
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
I'm the Goal Decomposer - I help transform career aspirations into
structured quarterly objectives. I'll ask hard questions and ground
everything in your actual feedback data.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Loading context for Sarah Chen...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Goal: Become Principal SE in 18 months
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Before I create your quarterly objectives, I need to understand a few things:

1. **Competency Focus:** Looking at Sarah's feedback, Cross-functional Impact
   is at 2.5 while Principal SE expectations are 3.5-4.0. What's been making
   it difficult to focus on team contributions?

2. **Timeline Reality:** Is the 18-month timeline driven by a specific event
   (promotion cycle, upcoming role opening) or is it aspirational? Is there
   flexibility?

3. **Workload Constraints:** Sarah's feedback shows 6 deals in the last
   quarter. Can deal load be reduced to create development bandwidth?

4. **Organizational Factors:** Are there current Principal SE openings, or
   would this require creating a new role?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

> 1. Sarah has been focused on closing deals and hasn't had time for team stuff
> 2. There's a promotion cycle in July 2026, so 18 months is hard deadline
> 3. We could reduce to 4-5 deals per quarter
> 4. There's one opening expected in Q3 2026

Thanks for that context. Let me generate objectives...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 Quarterly Objectives for: Become Principal SE in 18 months
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Q1 2025: Establish Team Enablement Foundation**

Build credibility as a team contributor by creating and delivering
a high-impact enablement session.

**Success Criteria:**
- [ ] Identify top 3 topics where team needs enablement (survey by Jan 15)
- [ ] Create comprehensive enablement session (60-min, slides + demo)
- [ ] Deliver to SE team with 4.0+ feedback rating

**Dependencies:**
- Manager approval for reduced deal load (4-5 deals/quarter)
- 4 hours/week allocated for development activities

**Risk Factors:**
- Q1 often has pipeline pressure - may need to shift if critical deals emerge

**Competency Alignment:**
| Competency | Current | Target | Gap |
|------------|---------|--------|-----|
| Cross-functional Impact | 2.5 | 3.5 | +1.0 |

---

**Q2 2025: Deepen Strategic Deal Influence**

Lead technical strategy on 2-3 complex enterprise deals, demonstrating
Principal-level deal influence.

**Success Criteria:**
- [ ] Lead technical strategy on 2+ deals >$500K
- [ ] Create reusable discovery framework used by 3+ team members
- [ ] Receive 3.5+ average rating on Deal Influence in feedback

**Dependencies:**
- AE alignment on strategic deal selection
- Access to enterprise opportunities

**Risk Factors:**
- Enterprise deal cycles may slip - backup plan for smaller strategic deals

**Competency Alignment:**
| Competency | Current | Target | Gap |
|------------|---------|--------|-----|
| Deal Influence | 3.0 | 3.5 | +0.5 |

---

**Q3 2025: Mentor Junior SE**

Take on formal mentorship responsibility to demonstrate leadership
and team investment.

**Success Criteria:**
- [ ] Assigned as mentor to new SE hire
- [ ] Complete 8+ 1:1 mentoring sessions
- [ ] Mentee achieves first solo customer win

**Dependencies:**
- New SE hiring in Q2-Q3 timeframe
- Mentorship program approval from SE leadership

**Risk Factors:**
- Hiring timeline may shift - alternative: informal mentorship of existing junior SE

**Competency Alignment:**
| Competency | Current | Target | Gap |
|------------|---------|--------|-----|
| Cross-functional Impact | 2.5 | 3.5 | +1.0 |

---

**Q4 2025: Product Feedback Leadership**

Become the recognized voice between SE team and Product, establishing
strategic influence beyond direct customer work.

**Success Criteria:**
- [ ] Submit 10+ structured product feedback items with customer evidence
- [ ] Lead monthly SE-Product sync meeting
- [ ] Influence 2+ roadmap decisions based on SE feedback

**Dependencies:**
- Product team engagement and meeting access
- Manager endorsement of this initiative

**Risk Factors:**
- Product team may have limited bandwidth for SE feedback loop

**Competency Alignment:**
| Competency | Current | Target | Gap |
|------------|---------|--------|-----|
| Cross-functional Impact | 2.5 | 3.5 | +1.0 |

---

**Q1 2026: Demonstrate Principal Readiness**

Compile evidence portfolio and secure endorsements for July 2026
promotion cycle.

**Success Criteria:**
- [ ] Create promotion portfolio with evidence for all competencies
- [ ] Secure 3+ peer endorsements from senior SEs and cross-functional partners
- [ ] Complete self-assessment with gap-to-Principal analysis

**Dependencies:**
- Continued progress on Q1-Q4 2025 objectives
- Principal SE opening confirmed for Q3 2026

**Risk Factors:**
- Role opening may be delayed or filled externally

**Competency Alignment:**
| Competency | Current | Target | Gap |
|------------|---------|--------|-----|
| Cross-functional Impact | 2.5 | 3.5 | +1.0 |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Timeline Feasibility Assessment
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Assessment:** AMBITIOUS

**Reasoning:**
The 18-month timeline to Principal SE is achievable but aggressive given:
- Cross-functional Impact gap of 1.0 (HIGH priority)
- Fixed July 2026 promotion deadline
- Deal load reduction required (6 → 4-5 deals)

The objectives are structured to close the gap progressively, but require
consistent execution with no major delays.

**Tradeoffs to Consider:**
- Must reduce deal load by ~20% (6→4-5 deals) starting Q1 2025
- Requires manager support for 4 hours/week development time
- Depends on new SE hiring for mentorship objective (Q3 backup plan exists)
- Timeline assumes Principal SE opening materializes in Q3 2026

**Recommendation:**
This plan is achievable with the deal load reduction you mentioned and
manager support. Consider having an explicit backup plan if the Principal
opening is delayed - perhaps target Q4 2026 cycle as contingency.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Would you like to modify any objectives before saving? (y/n/edit) n

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💾 Save Objectives to Profile
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Save these 5 objectives to Sarah Chen's profile? (y/n) y

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Objectives Saved
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Added 5 objectives to: team/sarah-chen/profile.md

**Goal:** Become Principal SE in 18 months
**Timeline Assessment:** AMBITIOUS

**Objectives Added:**
- Q1 2025: Establish Team Enablement Foundation
- Q2 2025: Deepen Strategic Deal Influence
- Q3 2025: Mentor Junior SE
- Q4 2025: Product Feedback Leadership
- Q1 2026: Demonstrate Principal Readiness

**Next Steps:**
1. Review objectives with Sarah in your next 1:1
2. Use `/career-check sarah-chen` to see full career summary
3. Track progress by checking off success criteria as completed
4. Run `/plan-goal sarah-chen` for detailed action planning

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Performance Target

Goal decomposition session should complete in < 5 minutes (interactive).

## Related Commands

- `/career-check {se-name}` - Career summary with competency gaps
- `/plan-goal {se-name}` - Collaborative goal planning (combines Goal Decomposer + Action Designer)
- `/profile {se-name}` - View/edit SE profile
- `/add-se {name}` - Create new SE profile

## Implementation Status

**Status:** Complete - Story 6.2
**Implemented:** 2025-12-26
