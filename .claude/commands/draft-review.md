# /draft-review - Generate Performance Review Draft

Generate a comprehensive performance review draft for an SE covering a specified period. This command aggregates all feedback data, calculates competency trends, and produces an evidence-based review document.

## What This Does

1. Resolves SE name (fuzzy matching)
2. Parses review period to determine date range
3. Aggregates all feedback entries within the period
4. Calculates meeting competency averages
5. Derives role competency ratings via competency mappings
6. Calculates trends by comparing to previous period
7. Generates comprehensive review sections with evidence citations
8. Offers save, edit, regenerate, or cancel options

## Usage

```
/draft-review sarah-chen Q4-2024
/draft-review sarah-chen 2024-Q4
/draft-review sarah-chen "Oct-Dec 2024"
/draft-review sarah-chen "last quarter"
```

## Arguments

- `se-name`: The SE's name in lowercase-hyphen format (supports fuzzy matching)
- `period`: The review period (supports multiple formats)

## Implementation

When this command is run, follow these steps exactly:

### Step 1: Parse Input and Resolve SE Name

**1.1 Parse arguments:**
Arguments are: $ARGUMENTS

Expected format: `{se-name} {period}`
Example: `sarah-chen Q4-2024`

Split arguments to extract:
- SE name (first token or tokens before period pattern)
- Period (remaining tokens matching period patterns)

If arguments are empty or invalid:
```
Please specify an SE name and review period.

Usage: /draft-review {se-name} {period}

Examples:
  /draft-review sarah-chen Q4-2024
  /draft-review sarah-chen "last quarter"
  /draft-review marcus-johnson annual-2024

Available SEs:
{List all SE folders in team/ excluding _template/ and _archived/}
```

**1.2 Normalize the SE name:**
- Convert to lowercase
- Replace spaces with hyphens
- Remove special characters

**1.3 List all SE folders in team/ (exclude _template/, _archived/)**

**1.4 Fuzzy Match (Levenshtein Distance):**
- Exact match → Use directly
- Single close match (distance ≤ 2) → Use with confirmation
- Multiple matches → Ask user to clarify
- No matches → Show error with suggestions

**If no match found:**
```
I couldn't find an SE named "{input}". Did you mean:
  - {suggestion1}
  - {suggestion2}

Or run `/add-se {input}` to create a new profile.
```

**1.5 Get Display Name from profile.md**

### Step 2: Parse Review Period (AC: 4)

**2.1 Supported period formats:**

| Format | Example | Date Range |
|--------|---------|------------|
| Q{N}-{YYYY} | Q4-2024 | Oct 1 - Dec 31, 2024 |
| {YYYY}-Q{N} | 2024-Q4 | Oct 1 - Dec 31, 2024 |
| {Mon}-{Mon} {YYYY} | Oct-Dec 2024 | Oct 1 - Dec 31, 2024 |
| "last quarter" | (dynamic) | Previous calendar quarter |
| annual-{YYYY} | annual-2024 | Jan 1 - Dec 31, 2024 |
| H1-{YYYY} | H1-2024 | Jan 1 - Jun 30, 2024 |
| H2-{YYYY} | H2-2024 | Jul 1 - Dec 31, 2024 |

**2.2 Parse period string:**

For quarterly formats (Q1-Q4):
- Q1: Jan 1 - Mar 31
- Q2: Apr 1 - Jun 30
- Q3: Jul 1 - Sep 30
- Q4: Oct 1 - Dec 31

For "last quarter":
- Calculate based on today's date
- If today is in Q1 → previous Q4 of last year
- If today is in Q2 → Q1 of current year
- If today is in Q3 → Q2 of current year
- If today is in Q4 → Q3 of current year

For month ranges (Oct-Dec, Jan-Mar, etc.):
- Parse start and end months
- Use 1st of start month and last day of end month

**2.3 Validate period and confirm:**
```
Generating {Quarter/Period} {Year} review for {SE Display Name} ({Start Date} - {End Date})
```

Example:
```
Generating Q4 2024 review for Sarah Chen (Oct 1 - Dec 31)
```

**2.4 Determine previous period for trend comparison:**
- For quarterly: previous quarter (Q4 → Q3, Q1 → Q4 of previous year)
- For annual: previous year
- For H1/H2: previous half

### Step 3: Load SE Profile and Feedback (AC: 1)

**3.1 Read `team/{se-name}/profile.md` completely**

Extract:
- Display Name (from header)
- Title (from Current Role section)
- Start Date
- Focus Areas
- Career Aspirations section (target role, timeline, objectives)
- Growth Objectives (if any)
- Development Actions (if any)

**3.2 Read `team/{se-name}/feedback-log.md` completely**

**3.3 Show progress:**
```
Analyzing {N} feedback entries from {Period}...
```

### Step 4: Parse and Filter Feedback Entries (AC: 1, 5)

**4.1 Parse all feedback entries:**

Each entry starts with `## YYYY-MM-DD | {Customer} | {Call Type}`

For each entry, extract:
- Date (from header, format: YYYY-MM-DD)
- Customer name (from header)
- Call type (from header)
- Transcript link (if present: `**Transcript:** [[...]]`)
- Opportunity info (if present: `**Opportunity:** ...`)

**4.2 Parse competency ratings:**

Handle TWO formats that may exist:

**Format 1 - Meeting Competencies (old):**
```
### Competency Ratings
| Competency | Rating |
| ELI5 | 4 (UC) |
| Checking Understanding | 3 (CC) |
```

**Format 2 - Role/Dimension Ratings (new):**
```
### Dimension Ratings
| Dimension | Rating | Notes |
| Technical Credibility | 4/5 | ... |
| Discovery Quality | 5/5 | ... |
```

For Format 1:
- Extract competency name and rating number (1-4)
- These are MEETING competencies

For Format 2:
- Extract dimension name and rating (X/5 format, convert to 1-4 scale: divide by 1.25)
- These are ROLE competencies directly

**4.3 Extract observations:**

Handle both formats:
- `**Strengths:** ...` or `**Went Well:** ...`
- `**Development Areas:** ...`

**4.4 Extract coaching items:**
- Open items: `- [ ] {text} (added YYYY-MM-DD)`
- Completed items: `- [x] {text}`

**4.5 Extract notable quotes:**
- Pattern: `> "{quote}" - {attribution}`

**4.6 Filter entries to review period:**
- Include entries where date >= period_start AND date <= period_end
- Store as `period_entries[]`

**4.7 Filter entries to previous period (for trends):**
- Include entries from the previous period
- Store as `previous_period_entries[]`

### Step 5: Calculate Meeting Competency Averages (AC: 5)

**5.1 Read `config/competencies/meeting-competencies.yaml`**

**5.2 For each meeting competency:**
- Sum all ratings from period_entries where this competency was rated
- Calculate average = sum / count
- Store: `{competency: {avg: X.X, count: N, entries: [...]}}`

**5.3 Build meeting competency table:**

| Competency | Avg Rating | Stage | # Observations |
|------------|------------|-------|----------------|
| ELI5 | 3.5 | CC | 4 |
| Discovery Depth | 4.0 | UC | 3 |

Stage mapping (Four Stages of Competence):
- 1.0-1.4 → UI (Unconscious Incompetence)
- 1.5-2.4 → CI (Conscious Incompetence)
- 2.5-3.4 → CC (Conscious Competence)
- 3.5-4.0 → UC (Unconscious Competence)

### Step 6: Derive Role Competency Ratings (AC: 5)

**6.1 Read `config/competencies/role-competencies.yaml`**

**6.2 For each role competency:**

From meeting-competencies.yaml, find all meeting competencies with `maps_to_role` that includes this role competency.

For example, for `technical_credibility`:
- Meeting competencies that map to it: eli5, demo_storytelling, competitive_positioning

**6.3 Calculate weighted average:**
- Average the meeting competency ratings that map to this role competency
- Weight by observation count

**6.4 Also check for direct role ratings:**

If feedback entries contain direct role/dimension ratings (Format 2), include those in the average.

**6.5 Build role competency table:**

| Role Competency | Derived Rating | Supporting Meeting Competencies |
|-----------------|----------------|--------------------------------|
| Technical Credibility | 3.8 | ELI5 (4.0), Demo Storytelling (3.5) |
| Discovery Quality | 3.5 | Discovery Depth (3.5), Checking Understanding (3.5) |

### Step 7: Calculate Trends with Evidence (AC: 1, 2, 3, 4, 6, 7)

**7.1 For previous period entries:**
- Calculate same meeting competency averages as current period
- Store individual ratings with their associated entries (date, customer, observation notes)

**7.2 Compare current vs previous:**

For each competency:
- delta = current_avg - previous_avg
- If delta >= 0.3 → "↑" (improving)
- If delta > -0.3 AND delta < 0.3 → "→" (stable)
- If delta <= -0.3 → "↓" (declining)

**7.3 Handle no previous period data:**
- If no entries in previous period for ANY competency, set `first_review_period = true`
- Display message: "First review period - trends will be available next quarter"
- Trend column shows "—" for all competencies (no arrows)
- Still show current period averages without trend comparisons

**7.4 Extract trend evidence (NEW - Story 5.2):**

For each competency with a trend (↑ or ↓):
- Store `previous_period_name` (e.g., "Q3", "H1", "2023")
- Store `previous_avg` for display: "(was X.X in {previous_period})"

**For improving competencies (↑):**
- Find the HIGHEST rated observation from current period (best example of improvement)
- Find the LOWEST rated observation from previous period (baseline to show growth)
- Store as `improvement_evidence`:
  ```
  {
    current_best: {date, customer, rating, observation},
    previous_baseline: {date, customer, rating, observation}
  }
  ```

**For declining competencies (↓):**
- Find the LOWEST rated observation from current period (worst example)
- Find the HIGHEST rated observation from previous period (previous strength)
- Store as `decline_evidence`:
  ```
  {
    current_low: {date, customer, rating, observation},
    previous_high: {date, customer, rating, observation}
  }
  ```

**7.5 Flag declining competencies (NEW - Story 5.2):**

For competencies with ↓ trend:
- Add ⚠️ warning indicator: "{competency}: {avg} ↓ (was {prev_avg} in {prev_period}) ⚠️ Needs attention"
- Search coaching items for keywords matching the declining competency name
- If matching coaching items found → link them
- If NO matching coaching items → suggest: "Consider adding a coaching item for {competency}"

**7.6 Store trend data for display:**

For each competency, store:
```
{
  name: string,
  current_avg: number,
  previous_avg: number | null,
  trend: "↑" | "→" | "↓" | "—",
  previous_period_name: string | null,
  evidence: improvement_evidence | decline_evidence | null,
  needs_attention: boolean,
  related_coaching_items: string[]
}
```

### Step 8: Generate Executive Summary (AC: 2) - Story 5.3 Enhanced

**8.1 Synthesize performance characterization:**

Based on overall ratings, use descriptive language mapped to performance levels:
- Average >= 3.5 (UC): "Exceptional performer who consistently demonstrates mastery..."
- Average 3.0-3.5 (CC): "Strong contributor who reliably meets and often exceeds expectations..."
- Average 2.5-3.0 (developing): "Developing professional showing promise with clear growth trajectory..."
- Average < 2.5 (early stage): "Earlier-stage performer with significant opportunity for development..."

**8.2 Include in summary with SPECIFIC evidence (NO generic phrases):**

For each point, MUST cite actual feedback data:

**Top 2-3 strengths with evidence snippets:**
- Extract the highest-rated competencies (avg >= 3.5)
- Include ONE specific example per strength with customer name and date
- Example: "...particularly excelling in discovery depth, as demonstrated in the Nordstrom call (Dec 15) where she uncovered a $5M savings opportunity"

**1-2 development areas with constructive framing:**
- Use language: "opportunity to strengthen", "area for continued growth", "focus area"
- Frame with trajectory: "While improving in..." or "Building momentum in..."
- If declining trend exists, acknowledge: "Recent observations suggest renewed attention to..."

**Notable trends with context:**
- For improving competencies: "Showing measurable improvement in {competency}, up from {prev_avg} to {current_avg}"
- For declining competencies: "Recent {competency} observations warrant focused attention"

**Career progression mention (if notable):**
- If Growth Objectives show progress: "On track toward {target_role} objective..."
- If career conversation is overdue, omit from summary (flag in Career section instead)

**8.3 Format as 1-2 cohesive paragraphs:**

The summary MUST read as natural prose, NOT bullet points. Connect ideas with transition phrases:
- "Additionally...", "Of note...", "Building on this..."
- "While excelling in..., there remains opportunity to..."
- "Looking ahead..."

**8.4 Avoid these generic phrases WITHOUT supporting evidence:**
- ❌ "demonstrates strong skills" → ✅ "demonstrated strong discovery skills in the Nordstrom call"
- ❌ "has potential" → ✅ "showed potential through measurable improvement from 3.2 to 3.7 in discovery"
- ❌ "is a team player" → ✅ cite specific collaboration evidence if available
- ❌ "works hard" → ✅ cite specific workload or productivity evidence if available

Every characterization MUST be traceable to feedback-log.md entries.

### Step 9: Generate Competency Assessment Tables (AC: 1, 2, 5, 6, 7)

**9.1 Format Meeting Competencies Table:**

```markdown
### Meeting-Level Competencies

| Competency | Avg Rating | Trend | Stage | # Obs |
|------------|------------|-------|-------|-------|
| {name} | {avg:.1f} | {trend_with_comparison} | {stage} | {count} |
```

**Format for trend_with_comparison:**
- If improving: `↑ (was {prev_avg} in {prev_period})`
- If stable: `→ (was {prev_avg} in {prev_period})`
- If declining: `↓ (was {prev_avg} in {prev_period}) ⚠️`
- If no previous data: `— (first period)`

Sort by rating (highest first).

**9.2 Format Role Competencies Table:**

```markdown
### Role-Level Competencies

| Competency | Rating | Trend | Stage | Evidence Sources |
|------------|--------|-------|-------|------------------|
| {name} | {rating:.1f} | {trend_with_comparison} | {stage} | {meeting_competencies} |
```

**9.3 Display trend evidence section (if any improving or declining competencies):**

After the tables, if `first_review_period` is false and there are trends to highlight:

```markdown
### Trend Details

#### Improving Competencies ↑

**{Competency Name}**: {current_avg} ↑ (was {previous_avg} in {previous_period})

*Evidence of improvement:*
- **Current period ({date} - {customer})**: {observation excerpt from current_best}
  > Rating: {rating}/4
- **Previous period ({date} - {customer})**: {observation excerpt from previous_baseline}
  > Rating: {rating}/4

#### Declining Competencies ↓ ⚠️

**{Competency Name}**: {current_avg} ↓ (was {previous_avg} in {previous_period}) ⚠️ Needs attention

*Evidence of decline:*
- **Current period ({date} - {customer})**: {observation excerpt from current_low}
  > Rating: {rating}/4
- **Previous period ({date} - {customer})**: {observation excerpt from previous_high}
  > Rating: {rating}/4

**Related Coaching Items:**
{list of related coaching items if any, or "Consider adding a coaching item for this area"}
```

**9.4 Handle first review period:**

If `first_review_period` is true, add note after tables:

```markdown
> 📊 **First review period** - trends will be available next quarter when historical data exists for comparison.
```

### Step 10: Generate Strengths Section (AC: 7) - Story 5.3 Enhanced

**10.1 Identify strengths:**
- Competencies with average >= 3.5
- Sort by rating (highest first)
- Cap at 4 strengths maximum

**10.2 For each strength, extract RICH evidence (up to 4 strengths):**

**10.2.1 Find 2-3 highest-rated specific examples:**
- Query `period_entries[]` for entries with this competency rating >= 3.5
- Sort by rating (highest first), then by date (most recent first)
- Extract top 2-3 entries

**10.2.2 Format each example with full context:**
- Date: From entry header (YYYY-MM-DD format, display as "Mon DD")
- Customer name: From entry header
- Observation excerpt: Extract from `**Strengths:**` or `**Went Well:**` section
- Keep excerpt to 1-2 sentences that capture the specific behavior observed

**10.2.3 Search for notable quotes:**
- Pattern: `> "{quote text}" - {attribution}` OR `> "{quote text}"`
- Quotes are typically in `### Notable Quotes` section of feedback entry
- If quote exists for this entry, include with attribution
- Format: `> "{exact quote}" - {Customer Name or "Customer"}`

**10.2.4 Connect to business impact (if opportunity data exists):**
- Check if entry has `**Opportunity:** {Customer} - ${Amount}` or similar
- If found, incorporate: "...contributing to the ${Amount} {Customer} opportunity"
- If deal won, mention: "...instrumental in closing the ${Amount} deal"

**10.2.5 CRITICAL - Avoid generic phrases:**
- ❌ "Demonstrates strong skills in this area"
- ❌ "Consistently performs well"
- ❌ "Shows competence"
- ✅ Always cite specific behavior: "Asked 5 probing questions that uncovered..."
- ✅ Always cite specific outcome: "...resulting in customer saying 'I never thought of it that way'"

**10.3 Format with enhanced evidence structure:**

```markdown
## Strengths

### {Competency Name} (Avg: {rating:.1f}/4 - {stage_label})

{One sentence describing what excellence looks like for this competency, derived from competency definition}

**Evidence from {Period}:**

1. **{Mon DD} - {Customer}** ({Call Type})
   {Specific observation excerpt from Strengths/Went Well section - actual language from feedback}
   {If opportunity data exists}: *Contributing to ${Amount} opportunity*
   {If notable quote exists}:
   > "{Exact quote from customer or stakeholder}" - {Attribution}

2. **{Mon DD} - {Customer}** ({Call Type})
   {Specific observation excerpt}
   {Quote if available}

3. **{Mon DD} - {Customer}** ({Call Type}) *{optional 3rd example if rich data}*
   {Observation excerpt}
```

**10.4 Handle sparse data gracefully:**
- If only 1 example exists: Include it with note "Additional observations will strengthen this assessment"
- If no examples with direct Strengths text: Use the rating + any available observation context
- Never invent evidence - only cite what exists in feedback-log.md

### Step 11: Generate Development Areas Section (AC: 8) - Story 5.3 Enhanced

**11.1 Identify development areas:**
- Competencies with average < 3.0
- Sort by rating (lowest first - most critical gaps first)
- Cap at 3 development areas maximum
- Check if any have declining trend (↓) from Step 7

**11.2 For each area, use CONSTRUCTIVE framing (up to 3 areas):**

**11.2.1 Frame the competency gap constructively:**

Use this language mapping:
- ❌ "Failed to..." → ✅ "Opportunity to strengthen..."
- ❌ "Weak in..." → ✅ "Area for continued development in..."
- ❌ "Lacks..." → ✅ "Building capability in..."
- ❌ "Poor performance" → ✅ "Growth trajectory in..."
- ❌ "Needs to improve" → ✅ "Focus area for the coming quarter"

**11.2.2 Extract specific examples from feedback:**
- Query `period_entries[]` for entries with this competency rating < 3
- Include date and customer for each example
- Extract from `**Development Areas:**` section of feedback entry
- Use EXACT language from feedback, do not rephrase harshly

**11.2.3 If declining trend exists (from Step 7.5), incorporate trend evidence:**
- Reference the decline: "Recent observations show a shift from {prev_avg} to {current_avg}"
- Pull `decline_evidence.current_low` and `decline_evidence.previous_high` for contrast
- Frame constructively: "While previously demonstrating strength (Q3 example), recent calls suggest opportunity to refocus"

**11.2.4 Link related coaching items:**
- Scan all `period_entries[]` for coaching items (pattern: `- [ ] ...` or `- [x] ...`)
- Match coaching items to competency by keyword search (competency name, related terms)
- List open items `[ ]` as actionable
- List completed items `[x]` as progress made

**11.2.5 Generate concrete improvement suggestions:**

Based on gap type, suggest specific actions:

For Discovery competencies:
- "Practice the MEDDPICC framework in upcoming calls"
- "Prepare 3 probing questions before each discovery session"

For Technical competencies:
- "Shadow senior SE on technical deep dives"
- "Create cheat sheet of common technical objections and responses"

For Communication competencies:
- "Build in 2-minute pauses for understanding checks"
- "Use 'tell me more about that' follow-up technique"

For Objection Handling:
- "Role-play competitive objection scenarios with peer"
- "Document objection patterns and prepare counter-narratives"

**11.3 Format with enhanced constructive structure:**

```markdown
## Development Areas

### {Competency Name} (Avg: {rating:.1f}/4 - {stage_label})

{Constructive framing sentence}: "{SE Name} has opportunity to strengthen {competency description} to move from {current_stage} to {next_stage}."

{If declining trend}: ⚠️ *Recent trend: {current_avg} ↓ (was {prev_avg} in {prev_period}) - warrants focused attention*

**Observations from {Period}:**

1. **{Mon DD} - {Customer}** ({Call Type})
   {Development area observation - exact language from feedback, constructively framed}

2. **{Mon DD} - {Customer}** ({Call Type})
   {Observation excerpt}

{If decline trend evidence available}:
**Trend Context:**
- *Previous strength* ({prev_period}): {previous_high observation excerpt}
- *Recent observation* ({current_period}): {current_low observation excerpt}

**Related Coaching Items:**
- [ ] {Open coaching item} *(added {date})*
- [x] {Completed item} *(completed)*

{If no matching coaching items}: *Consider adding a coaching item for this area in next 1:1*

**Suggested Actions for {Next Period}:**
1. {Specific, actionable improvement suggestion tied to the gap}
2. {Second suggestion if appropriate}
```

**11.4 Handle edge cases:**
- If no Development Areas entries exist but rating is low: Use observation context + rating
- If no coaching items exist: Suggest creating one
- If all competencies >= 3.0: Display "No significant development areas identified - continue current trajectory"
- Never invent negative evidence - only cite what exists in feedback

### Step 12: Generate Coaching Items Status (AC: 2)

**12.1 Collect all coaching items from period:**
- Scan all period entries for coaching items
- Categorize as completed `[x]` or open `[ ]`

**12.2 Format:**

```markdown
## Coaching Items Status

### Completed This Period
{List all [x] items with dates}

### Open Items (Carry Forward)
{List all [ ] items with context}
```

If no completed items: "No coaching items completed this period."
If no open items: "No open coaching items - great follow-through!"

### Step 13: Generate Career Progression Section (AC: 9)

**13.1 Pull from profile.md Career Aspirations:**
- Target role (Short-Term section)
- Timeline
- Motivation (from description)

**13.2 Extract Growth Objectives (if documented):**
- List objectives
- Calculate progress percentage if tracked

**13.3 Extract Development Actions (if documented):**
- List actions
- Summarize status (in progress, completed, not started)

**13.4 Note last career conversation:**
- From 1on1-notes dates or explicit career conversation log
- Flag if overdue (> 30 days)

**13.5 Format:**

```markdown
## Career Progression

> Note: This section is separate from job performance per the two-track development model.

**Target Role:** {role} ({timeline})
**Motivation:** {motivation from profile}

### Growth Objectives Status
{List objectives with progress}

### Development Actions Progress
{List actions with status}

**Last Career Conversation:** {date} ({N} days ago)
{Warning if overdue}
```

### Step 14: Generate Goals for Next Period (AC: 10)

**14.1 Generate 2-4 goals:**
- 1-2 goals based on development areas (lowest competencies)
- 1 goal aligned with career objectives
- 1 goal for strength amplification (optional)

**14.2 Each goal includes:**
- Clear objective statement
- Success criteria (measurable)
- Timeline (next quarter)
- How it connects to development areas or career path

**14.3 Format:**

```markdown
## Goals for Next Period

### Goal 1: {Goal Title}
**Objective:** {Specific, measurable goal}
**Success Criteria:**
- {Criterion 1}
- {Criterion 2}
**Timeline:** {Next quarter}
**Rationale:** {Why this goal matters - connects to gap or career}

### Goal 2: ...
```

### Step 15: Generate Overall Rating (AC: 2)

**15.1 Calculate weighted average:**
- Average all role competency ratings
- This gives overall score on 1-4 scale

**15.2 Map to rating category:**
- 3.5-4.0: "Exceeds Expectations"
- 3.0-3.5: "Meets Expectations"
- 2.5-3.0: "Partially Meets Expectations"
- < 2.5: "Below Expectations"

**15.3 Add trajectory indicator:**
- If average trend is ↑: "trending toward next level"
- If average trend is →: "stable performance"
- If average trend is ↓: "needs attention to maintain level"

**15.4 Write summary justification (2-3 sentences):**
- Reference overall performance
- Note key differentiators
- Forward-looking statement

**15.5 Format:**

```markdown
## Overall Rating

**Rating:** {Category} ({X.X}/4.0)
**Trajectory:** {trajectory statement}

{2-3 sentence justification}
```

### Step 16: Assemble and Display Review (AC: 2)

**16.1 Assemble complete review:**

```markdown
# Performance Review: {SE Display Name}

**Review Period:** {Period} ({Start Date} - {End Date})
**Review Date:** {Today's Date}
**Manager:** {From config or "Not specified"}

---

## Executive Summary

{executive_summary}

---

## Competency Assessment

### Meeting-Level Competencies

{meeting_competencies_table}

### Role-Level Competencies

{role_competencies_table}

---

## Strengths

{strengths_section}

---

## Development Areas

{development_areas_section}

---

## Coaching Items Status

{coaching_items_section}

---

## Career Progression

{career_section}

---

## Goals for Next Period

{goals_section}

---

## Overall Rating

{overall_rating_section}

---

## Feedback Sources

| Source Type | Count | Date Range |
|-------------|-------|------------|
| Call Reviews | {count} | {date_range} |
| 1:1 Notes | {count} | {date_range} |

---

**Review Status:** Draft
**Generated:** {timestamp}
```

**16.2 Display the complete review**

### Step 17: Show Options Menu (AC: 3, 5) - Story 5.3 Enhanced

**17.1 After displaying review, show options:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Review Options:

[e] Edit sections of this draft
[t] Adjust tone of a section
[m] Add more examples to a section
[s] Save as-is to team/{se-name}/reviews/{period}-review.md
[r] Regenerate with different parameters
[d] Drill-down: See all ratings for a specific competency
[c] Cancel

Or just tell me what you'd like to change (e.g., "make development areas more direct" or "add more examples to strengths")

Enter choice:
```

**17.2 Handle responses:**

**If 'e' (Edit):**
```
Which section would you like to edit?
1. Executive Summary
2. Competency Assessment
3. Strengths
4. Development Areas
5. Coaching Items Status
6. Career Progression
7. Goals for Next Period
8. Overall Rating

Enter section number (or 'done' when finished):
```

→ Go to Step 21 (Section Editing Workflow)

**If 't' (Adjust Tone) - Story 5.3 AC: 4:**
```
Which section would you like to adjust the tone for?
1. Executive Summary
2. Strengths
3. Development Areas

And what tone adjustment?
- "more direct" - More straightforward language, less hedging
- "softer" - More encouraging language, gentler framing
- "more formal" - Professional/HR-appropriate language
- "more conversational" - Manager-to-SE natural language

Enter section number and tone (e.g., "3 more direct"):
```

→ Go to Step 19 (Tone Adjustment)

**If 'm' (Add More Examples) - Story 5.3 AC: 5:**
```
Which section would you like to expand with more examples?
1. Strengths
2. Development Areas

Enter section number (or 'back' to return):
```

→ Go to Step 20 (Add More Examples)

**If natural language request detected (Story 5.3 AC: 4, 5):**

Parse user input for these patterns:

**Tone adjustment patterns:**
- "make {section} more direct" → Tone adjustment for {section} with "direct" modifier
- "make {section} softer" → Tone adjustment for {section} with "softer" modifier
- "be more direct about development areas" → Tone adjustment for Development Areas
- "tone down the strengths" → Tone adjustment for Strengths with "softer" modifier
- "make it more formal" → Tone adjustment for all narrative sections

**Specificity patterns:**
- "add more examples" → Expand examples in Strengths AND Development Areas
- "add more examples to {section}" → Expand examples in specific section
- "give me more detail" → Expand examples in all sections
- "show more evidence" → Expand examples with additional quotes/data
- "can you include more quotes" → Focus on extracting additional notable quotes

**Add section patterns (Story 5.4 AC: 2):**
- "add a section about {topic}" → Go to Step 22 (Add Custom Section)
- "add a section on {topic}" → Go to Step 22
- "include a section about {topic}" → Go to Step 22
- "I want to add something about {topic}" → Go to Step 22

**Rating override patterns (Story 5.4 AC: 3):**
- "change {competency} rating to {value}" → Go to Step 23 (Rating Override)
- "adjust {competency} to {value}" → Go to Step 23
- "override {competency} rating" → Go to Step 23
- "set {competency} to {value}" → Go to Step 23

**Past reviews patterns (Story 5.4 AC: 5):**
- "show {se-name}'s previous reviews" → Go to Step 24 (Past Reviews Listing)
- "list past reviews" → Go to Step 24
- "show review history" → Go to Step 24
- "what reviews exist for {se-name}" → Go to Step 24

**Review comparison patterns (Story 5.4 AC: 6):**
- "compare {se-name}'s {period1} and {period2} reviews" → Go to Step 25 (Review Comparison)
- "compare {period1} to {period2}" → Go to Step 25
- "show changes between {period1} and {period2}" → Go to Step 25
- "how has {se-name} progressed" → Go to Step 25

If pattern detected → Route to appropriate handler (Step 19-25)
If pattern NOT detected → Ask user to clarify

**If 's' (Save):**

→ Go to Step 26 (Save Final Review)

**If 'r' (Regenerate):**
```
Regenerate options:
1. Same period, refresh data
2. Different period
3. Adjust rating thresholds

Enter choice:
```

Handle accordingly and regenerate.

**If 'd' (Drill-down):**
```
Which competency would you like to explore?

Available competencies with ratings in this period:
1. ELI5 (4 observations)
2. Checking Understanding (3 observations)
3. Discovery Depth (4 observations)
...

Enter competency number or name (or 'back' to return):
```

After user selects competency → Go to Step 18

**If 'c' (Cancel):**
```
Review generation cancelled. No changes saved.
```

### Step 18: Competency Drill-Down (AC: 5)

This step provides detailed view of all ratings for a specific competency.

**18.1 Parse user request:**

User can request drill-down in two ways:
- From menu selection (competency number or name)
- Direct request: "Show me all {competency} ratings for {SE name} in {period}"

Extract:
- `target_competency`: The competency to drill into
- `se_name`: The SE (from current context or parse from request)
- `period`: The review period (from current context or parse from request)

**18.2 Query feedback entries:**

For the specified competency:
- Scan all entries in `period_entries[]` that have a rating for this competency
- Also scan `previous_period_entries[]` if available for comparison

**18.3 Format drill-down output:**

```markdown
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Competency Drill-Down: {Competency Name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**SE:** {SE Display Name}
**Period:** {Period} ({Start Date} - {End Date})
**Average Rating:** {avg}/4 ({stage})
**Trend:** {trend} (was {prev_avg} in {prev_period})

---

### All Observations ({count} entries)

#### {Period Name} (Current Period)

| Date | Customer | Rating | Stage | Notes |
|------|----------|--------|-------|-------|
| {YYYY-MM-DD} | {Customer} | {rating}/4 | {stage} | {observation excerpt - first 100 chars} |
| ... | ... | ... | ... | ... |

**Detailed Observations:**

1. **{Date} - {Customer} ({Call Type})**
   - **Rating:** {rating}/4 ({stage})
   - **Strengths noted:** {excerpt from strengths}
   - **Development areas:** {excerpt from development areas}
   - **Full observation:** {complete observation text}

2. **{Date} - {Customer} ({Call Type})**
   ...

#### {Previous Period Name} (For Comparison)

| Date | Customer | Rating | Stage | Notes |
|------|----------|--------|-------|-------|
| {YYYY-MM-DD} | {Customer} | {rating}/4 | {stage} | {observation excerpt} |

---

**Related Coaching Items:**
{list any coaching items mentioning this competency}

**Competency Definition:**
{description from meeting-competencies.yaml}

**Level Examples:**
- Level 1 (UI): {example}
- Level 2 (CI): {example}
- Level 3 (CC): {example}
- Level 4 (UC): {example}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[back] Return to review options
[another] Drill into another competency
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**18.4 Handle drill-down navigation:**

- If user selects 'back' → Return to Step 17 options menu
- If user selects 'another' → Show competency selection again
- If user asks for another competency by name → Repeat Step 18

### Step 19: Tone Adjustment (Story 5.3 AC: 4)

This step regenerates a section with adjusted tone based on user request.

**19.1 Parse tone adjustment request:**

Extract:
- `target_section`: Executive Summary, Strengths, or Development Areas
- `tone_modifier`: "more direct", "softer", "more formal", "more conversational"

**19.2 Apply tone modifiers:**

**For "more direct" tone:**
- Remove hedging words: "somewhat", "perhaps", "might", "could consider"
- Use active voice: "Sarah excels at..." instead of "Excellence has been demonstrated by..."
- Be specific about gaps: "Checking Understanding needs immediate attention" instead of "There may be opportunity in..."
- Shorten sentences, use declarative statements

**For "softer" tone:**
- Add encouraging framing: "Building on current progress...", "With continued focus..."
- Emphasize growth trajectory: "Moving from CC toward UC..."
- Balance critique with positives: "While {gap} is an area for growth, {strength} shows strong foundation"
- Use "opportunity" instead of "needs", "area for development" instead of "weakness"

**For "more formal" tone:**
- Use third person consistently: "The SE demonstrated..." not "Sarah showed..."
- Remove contractions: "does not" instead of "doesn't"
- Use standard HR language: "Meets Expectations", "Exceeds Expectations"
- Structure with clear section headers

**For "more conversational" tone:**
- Use first/second person where appropriate: "I've observed...", "You've shown..."
- Include natural transitions: "Looking at the calls this quarter..."
- Allow some informality while maintaining professionalism
- Reference specific conversations: "In our last 1:1, we discussed..."

**19.3 Regenerate section:**

- Re-read the source data (period_entries[], profile, etc.) as needed
- Apply the appropriate Step (8, 10, or 11) with tone modifier applied
- Keep all evidence and citations intact - only change phrasing

**19.4 Display regenerated section:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✏️ Regenerated {Section Name} with "{tone_modifier}" tone:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{regenerated_section_content}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[k] Keep this version
[r] Try a different tone
[o] Revert to original
[back] Return to options

Enter choice:
```

**19.5 Handle response:**
- If 'k' (Keep): Update section in review, return to Step 17
- If 'r' (Different tone): Ask for new tone modifier, repeat Step 19
- If 'o' (Revert): Restore original section, return to Step 17
- If 'back': Return to Step 17 without changes

### Step 20: Add More Examples (Story 5.3 AC: 5)

This step expands a section with additional evidence from feedback entries.

**20.1 Parse expansion request:**

Extract:
- `target_section`: Strengths or Development Areas
- `expansion_type`: "more examples", "more quotes", "more detail"

**20.2 Query for additional evidence:**

**For Strengths section expansion:**
- Query `period_entries[]` for entries not yet cited in current Strengths section
- Sort by rating (highest first) for the target competencies
- Look for additional notable quotes in `### Notable Quotes` sections
- Check for opportunity data connections not yet mentioned

**For Development Areas section expansion:**
- Query `period_entries[]` for additional examples at lower ratings
- Look for coaching items not yet linked
- Search for related trend evidence from previous period
- Find any additional context from observation text

**20.3 Format additional examples:**

Following same format as original section (Step 10.3 or Step 11.3):
- Include date, customer, call type
- Extract observation text
- Include quotes if available
- Link opportunity data if exists

**20.4 Display expansion options:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 Additional Examples Found for {Section Name}:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Currently cited:** {current_example_count} examples

**Additional examples available:**

{For each additional example}:
[ ] **{Mon DD} - {Customer}** ({Call Type})
    {Observation excerpt}
    {Quote if available}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[a] Add all additional examples
[s] Select specific examples to add (enter numbers)
[q] Add only entries with quotes
[back] Return without adding

Enter choice:
```

**20.5 Handle response:**
- If 'a' (Add all): Append all additional examples to section
- If 's' (Select): Ask which examples (comma-separated), add selected
- If 'q' (Quotes only): Add only examples that have notable quotes
- If 'back': Return to Step 17 without changes

**20.6 Display updated section:**

After adding examples, show the expanded section with clear delineation:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ {Section Name} Updated - Now includes {new_count} examples
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{updated_section_content}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Return to Step 17 options menu.

**20.7 Handle no additional examples:**

If no additional uncited examples exist:

```
ℹ️ All available examples for {Section Name} are already included.

The current {example_count} examples represent all feedback entries
with relevant observations for this period.

[back] Return to options
```

### Step 21: Section Editing Workflow (Story 5.4 AC: 1)

This step provides a full section editing workflow that shows current content before accepting edits.

**21.1 Parse section selection:**

Map user input to section:
- 1 → Executive Summary
- 2 → Competency Assessment
- 3 → Strengths
- 4 → Development Areas
- 5 → Coaching Items Status
- 6 → Career Progression
- 7 → Goals for Next Period
- 8 → Overall Rating

**21.2 Display current section content:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✏️ Editing: {Section Name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Current Content:**

{Display the FULL current section content exactly as it appears in the review}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
How would you like to modify this section?

Options:
- Type your replacement text directly
- Say "make it shorter" or "make it more detailed"
- Say "regenerate" to regenerate from scratch
- Say "back" to return without changes

Enter your changes:
```

**21.3 Handle edit request:**

**If direct text provided:**
- Replace section content with user's text
- Preserve formatting (headers, bullets, etc.)

**If modification request (shorter/detailed/regenerate):**
- "make it shorter" → Condense while keeping key evidence
- "make it more detailed" → Expand with additional evidence from feedback
- "regenerate" → Re-run the original generation step for this section

**21.4 Display updated section:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ {Section Name} Updated
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{Updated section content}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[k] Keep this version
[e] Edit again
[o] Revert to original
[back] Return to options menu

Enter choice:
```

**21.5 Handle response:**
- If 'k' (Keep): Apply changes, return to Step 17
- If 'e' (Edit again): Repeat Step 21.2 with updated content
- If 'o' (Revert): Restore original, return to Step 17
- If 'back': Return to Step 17 without changes

### Step 22: Add Custom Section (Story 5.4 AC: 2)

This step allows adding new custom sections to the review based on specific topics.

**22.1 Parse topic from request:**

Extract `{topic}` from patterns like:
- "add a section about {topic}"
- "add a section on {topic}"
- "include a section about {topic}"

Example: "add a section about POC leadership" → topic = "POC leadership"

**22.2 Search feedback for topic:**

Search `team/{se-name}/feedback-log.md` for entries containing:
- Topic keywords (e.g., "POC", "leadership")
- Related terms (e.g., for "POC": "proof of concept", "pilot", "evaluation")

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 Adding Section: {Topic}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{If matches found}:
I found {N} feedback entries related to "{topic}":

1. {Date} - {Customer}: {excerpt mentioning topic}
2. {Date} - {Customer}: {excerpt mentioning topic}

Would you like me to:
[g] Generate section from these entries
[a] Add your own details instead
[b] Use both - combine feedback with your input

Enter choice:

{If no matches found}:
I didn't find any feedback entries specifically about "{topic}".

To create this section, please provide:
1. Context: What specifically would you like to highlight?
2. Examples: Any specific instances or observations?
3. Impact: What was the result or significance?

Enter details (or 'back' to cancel):
```

**22.3 Generate section content:**

**If generating from feedback:**
- Extract relevant observations from matching entries
- Format as a new section following review conventions
- Include dates and customer names as evidence

**If user provides details:**
- Structure their input as a professional review section
- Add appropriate framing and context

**If combining both:**
- Merge feedback evidence with user-provided context
- Prioritize user framing, support with evidence

**22.4 Determine insertion location:**

Based on topic, suggest appropriate location:
- Technical topics → After Strengths or Development Areas
- Leadership/soft skills → After Career Progression
- Specific project work → After Coaching Items
- General → Before Goals for Next Period

```
Where should this section be placed?
1. After Executive Summary
2. After Competency Assessment
3. After Strengths
4. After Development Areas
5. After Coaching Items Status
6. After Career Progression
7. Before Goals for Next Period

Suggested: {suggested_location}

Enter location number (or press Enter for suggested):
```

**22.5 Display new section for confirmation:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ New Section Generated: {Topic}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## {Topic Title}

{Generated section content with evidence}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[k] Keep and insert at {location}
[e] Edit before inserting
[c] Cancel
[back] Return to options

Enter choice:
```

**22.6 Handle response:**
- If 'k' (Keep): Insert section at specified location, return to Step 17
- If 'e' (Edit): Go to Step 21 with new section
- If 'c' or 'back': Cancel, return to Step 17

### Step 23: Rating Override (Story 5.4 AC: 3)

This step allows manager override of AI-calculated ratings with audit trail.

**23.1 Parse override request:**

Extract from patterns like:
- "change {competency} rating to {value}"
- "adjust {competency} to {value}"
- "set {competency} to {value}"

Extract:
- `target_competency`: The competency name (fuzzy match against known competencies)
- `new_value`: The new rating value (should be 1.0-4.0)

**23.2 Validate competency name:**

Fuzzy match against:
- Meeting competencies from `config/competencies/meeting-competencies.yaml`
- Role competencies from `config/competencies/role-competencies.yaml`

If no match found:
```
I couldn't identify the competency "{input}".

Available competencies:
Meeting: ELI5, Checking Understanding, Discovery Depth, ...
Role: Technical Credibility, Discovery Quality, Demo Excellence, ...

Please try again with a valid competency name.
```

**23.3 Validate rating value:**

```
{If value < 1.0 or value > 4.0}:
⚠️ Invalid rating value: {value}

Ratings must be between 1.0 and 4.0:
- 1.0-1.4: UI (Unconscious Incompetence)
- 1.5-2.4: CI (Conscious Incompetence)
- 2.5-3.4: CC (Conscious Competence)
- 3.5-4.0: UC (Unconscious Competence)

Please enter a valid rating.
```

**23.4 Confirm override:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ Rating Override Confirmation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Competency:** {Competency Name}
**Current Rating:** {current_value}/4 (AI-calculated from {N} observations)
**New Rating:** {new_value}/4 (manager override)
**Stage Change:** {current_stage} → {new_stage}

This override will:
- Update the rating in the Competency Assessment tables
- Add "(manager-adjusted)" notation for audit trail
- Recalculate Overall Rating if this affects the average
- Preserve the original AI-calculated value in metadata

Proceed with override? (y/n):
```

**23.5 Apply override:**

**If 'y' (Yes):**
- Update rating in Meeting Competencies table (if meeting competency)
- Update rating in Role Competencies table (if role competency or affects derived rating)
- Add "(manager-adjusted)" notation to the rating cell
- Recalculate overall rating average
- Store override in review metadata:
  ```
  **Rating Overrides:**
  - {Competency}: {original_value} → {new_value} (manager-adjusted on {date})
  ```

**If 'n' (No):**
- Cancel override, return to Step 17

**23.6 Display confirmation:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Rating Override Applied
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**{Competency Name}:** {new_value}/4 (manager-adjusted)

Updated tables:
{Show relevant table rows with new values}

Overall Rating: {new_overall} (was {old_overall})

[back] Return to options
```

Return to Step 17.

### Step 24: Past Reviews Listing (Story 5.4 AC: 5)

This step lists all previous reviews for an SE.

**24.1 List reviews directory:**

Check `team/{se-name}/reviews/` directory for files matching pattern `*.md`

**24.2 Handle empty directory:**

```
{If directory doesn't exist or is empty}:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Past Reviews: {SE Display Name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

No previous reviews found for {SE Display Name}.

This will be their first saved review.

[back] Return to options
```

**24.3 Parse each review file:**

For each `.md` file in reviews directory:
- Extract period from filename (e.g., "2024-Q4" from "2024-Q4-review.md")
- Read file and extract:
  - Review Date (from header)
  - Overall Rating (from Overall Rating section)
  - Status (Draft/Final from metadata)

**24.4 Display review list:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Past Reviews: {SE Display Name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Found {N} previous reviews:

| # | Period | Date | Rating | Status |
|---|--------|------|--------|--------|
| 1 | Q4 2024 | Dec 25, 2024 | 3.4/4 (Meets Expectations) | Final |
| 2 | Q3 2024 | Sep 30, 2024 | 3.2/4 (Meets Expectations) | Final |
| 3 | Q2 2024 | Jun 28, 2024 | 3.0/4 (Meets Expectations) | Final |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[v] View a review (enter number)
[c] Compare two reviews
[back] Return to options

Enter choice:
```

**24.5 Handle view request:**

If user enters a number:
- Read the corresponding review file
- Display full content
- Offer option to return to list

**24.6 Handle compare request:**

If user enters 'c':
- Ask which two reviews to compare
- Go to Step 25 (Review Comparison)

Return to Step 17 if 'back'.

### Step 25: Review Comparison (Story 5.4 AC: 6)

This step compares two reviews to show progress over time.

**25.1 Parse comparison request:**

Extract periods from patterns like:
- "compare Q3 and Q4 reviews"
- "compare 2024-Q3 to 2024-Q4"
- Numbers from past reviews list (e.g., "1 and 2")

**25.2 Load both review files:**

- Read `team/{se-name}/reviews/{period1}-review.md`
- Read `team/{se-name}/reviews/{period2}-review.md`

**25.3 Handle missing file:**

```
{If one or both files don't exist}:
⚠️ Cannot compare: {period} review not found.

Available reviews:
{List available reviews}

Please specify valid review periods.
```

**25.4 Extract comparable data:**

From each review, extract:
- **Competency Ratings**: All meeting and role competency ratings
- **Overall Rating**: Final rating and category
- **Coaching Items**: Open and completed items
- **Goals**: Goals listed for next period

**25.5 Calculate deltas:**

For each competency:
- `delta = period2_rating - period1_rating`
- Classify: ↑ (improved >= 0.3), → (stable), ↓ (declined <= -0.3)

For overall rating:
- `overall_delta = period2_overall - period1_overall`

**25.6 Identify coaching item changes:**

- **Resolved**: Items that were open in period1 and completed in period2
- **New**: Items that appear in period2 but not period1
- **Carried Forward**: Items open in both periods

**25.7 Display comparison:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Review Comparison: {SE Display Name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Comparing:** {Period1} → {Period2}

---

### Overall Progress

| Metric | {Period1} | {Period2} | Change |
|--------|-----------|-----------|--------|
| Overall Rating | {rating1}/4 | {rating2}/4 | {delta} {trend_indicator} |
| Category | {category1} | {category2} | {change_note} |

---

### Competency Changes

**Improved ↑**
| Competency | {Period1} | {Period2} | Change |
|------------|-----------|-----------|--------|
| {name} | {rating1} | {rating2} | +{delta} ↑ |

**Declined ↓**
| Competency | {Period1} | {Period2} | Change |
|------------|-----------|-----------|--------|
| {name} | {rating1} | {rating2} | {delta} ↓ |

**Stable →**
| Competency | {Period1} | {Period2} | Change |
|------------|-----------|-----------|--------|
| {name} | {rating1} | {rating2} | {delta} |

---

### Coaching Items

**Resolved Since {Period1}:** {count}
{List resolved items}

**New in {Period2}:** {count}
{List new items}

**Carried Forward:** {count}
{List carried items}

---

### Goal Progress

**{Period1} Goals → Status in {Period2}:**
1. {goal1}: {status - Achieved/In Progress/Not Started}
2. {goal2}: {status}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[d] Drill into a specific competency change
[back] Return to options

Enter choice:
```

**25.8 Handle drill-down:**

If user selects 'd':
- Ask which competency
- Show detailed observations from both periods
- Highlight specific changes in behavior

Return to Step 17 if 'back'.

### Step 26: Save Final Review (Story 5.4 AC: 4)

This step saves the review with proper metadata and Final status.

**26.1 Prepare save location:**

- Directory: `team/{se-name}/reviews/`
- Filename: `{YYYY}-{QN}-review.md` (e.g., `2024-Q4-review.md`)

**26.2 Create directory if needed:**

If `team/{se-name}/reviews/` doesn't exist, create it.

**26.3 Check for existing file:**

```
{If file already exists}:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ Review Already Exists
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

A review for {Period} already exists at:
team/{se-name}/reviews/{filename}

Options:
[o] Overwrite existing review
[n] Save as new version (e.g., 2024-Q4-review-v2.md)
[c] Cancel

Enter choice:
```

**26.4 Prepare review with metadata header:**

Add metadata header to the review content:

```markdown
---
review_status: Final
generated_date: {YYYY-MM-DD}
review_period: {Period}
se_name: {se-name}
se_display_name: {SE Display Name}
manager: {Manager Name from config or "Not specified"}
rating_overrides:
  {If any overrides from Step 23}:
  - competency: {name}
    original: {value}
    adjusted: {new_value}
    date: {override_date}
custom_sections:
  {If any custom sections from Step 22}:
  - title: {section_title}
    added_date: {date}
---

# Performance Review: {SE Display Name}
...
```

**26.5 Update review status in content:**

Change:
```
**Review Status:** Draft
```

To:
```
**Review Status:** Final
```

**26.6 Confirm save:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💾 Save Review
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Ready to save {Period} review for {SE Display Name}:

**File:** team/{se-name}/reviews/{filename}
**Status:** Final
**Rating:** {overall_rating}/4 ({category})
{If overrides}: **Rating Overrides:** {count} adjustments
{If custom sections}: **Custom Sections:** {count} added

Save this review? (y/n):
```

**26.7 Execute save:**

**If 'y' (Yes):**
- Write file to `team/{se-name}/reviews/{filename}`
- Display confirmation:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Review Saved Successfully
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Location:** team/{se-name}/reviews/{filename}
**Status:** Final
**Saved:** {timestamp}

This review is now part of {SE Display Name}'s permanent record.

[v] View saved file
[back] Return to options
[done] Exit review workflow
```

**If 'n' (No):**
- Cancel save, return to Step 17

**26.8 Handle post-save options:**
- If 'v': Display the saved file content
- If 'back': Return to Step 17 (can make more edits)
- If 'done': Exit the draft-review workflow

## Edge Case Handling

**No feedback in period:**
```
⚠️ No feedback entries found for {SE Name} in {Period}.

The review period {Start Date} - {End Date} has no recorded feedback.

Options:
1. Expand the date range
2. Generate a minimal review with profile data only
3. Cancel

Enter choice:
```

**Partial data:**
If some sections can't be generated (e.g., no career data):
- Note in that section: "*No career aspirations documented. Consider discussing in next 1:1.*"
- Continue with available data

**First review (no trends):**
- Trend column shows "—" for all competencies
- Add note: "First review period - no historical data for trend comparison"

**Mixed rating formats:**
- Handle both meeting competency (1-4) and dimension ratings (X/5)
- Convert all to consistent 1-4 scale for calculations

## Example Session

```
> /draft-review sarah-chen Q4-2024

Generating Q4 2024 review for Sarah Chen (Oct 1 - Dec 31)

Analyzing 3 feedback entries from Q4 2024...
Comparing to Q3 2024 for trend analysis...

# Performance Review: Sarah Chen

**Review Period:** Q4 2024 (Oct 1 - Dec 31)
**Review Date:** 2025-12-25
**Manager:** Not specified

---

## Executive Summary

Sarah Chen demonstrated strong performance in Q4 2024, particularly excelling in
discovery depth and technical credibility. Her consultative approach consistently
uncovered quantifiable business value for customers, as evidenced by the Nordstrom
discovery call where she identified a $5M savings opportunity.

Key development areas include timeline urgency discovery and competitive positioning -
both areas have open coaching items that should be prioritized in Q1 2025. Overall,
Sarah is meeting expectations with clear upward trajectory in core SE competencies.

---

## Competency Assessment

### Meeting-Level Competencies

| Competency | Avg Rating | Trend | Stage | # Obs |
|------------|------------|-------|-------|-------|
| Discovery Depth | 3.7 | ↑ (was 3.2 in Q3) | UC | 3 |
| ELI5 | 3.5 | → (was 3.4 in Q3) | UC | 2 |
| Dynamic Engagement | 3.0 | → (was 3.1 in Q3) | CC | 2 |
| Checking Understanding | 2.8 | ↓ (was 3.3 in Q3) ⚠️ | CC | 2 |
| Objection Handling | 3.0 | — (first period) | CC | 2 |

### Trend Details

#### Improving Competencies ↑

**Discovery Depth**: 3.7 ↑ (was 3.2 in Q3)

*Evidence of improvement:*
- **Current period (2024-12-15 - Nordstrom)**: Exceptional discovery uncovering $5M savings opportunity
  > Rating: 4/4
- **Previous period (2024-08-20 - Target)**: Good discovery but missed quantification opportunity
  > Rating: 3/4

#### Declining Competencies ↓ ⚠️

**Checking Understanding**: 2.8 ↓ (was 3.3 in Q3) ⚠️ Needs attention

*Evidence of decline:*
- **Current period (2024-11-10 - Macy's)**: Moved too quickly without confirming comprehension
  > Rating: 2/4
- **Previous period (2024-09-15 - Nordstrom)**: Regular check-ins throughout presentation
  > Rating: 4/4

**Related Coaching Items:**
- [ ] Practice pausing for understanding checks (added 2024-11-10)

...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Review Options:

[e] Edit sections of this draft
[t] Adjust tone of a section
[m] Add more examples to a section
[s] Save as-is to team/sarah-chen/reviews/2024-Q4-review.md
[r] Regenerate with different parameters
[d] Drill-down: See all ratings for a specific competency
[c] Cancel

Or just tell me what you'd like to change (e.g., "make development areas more direct" or "add more examples to strengths")

Enter choice: make development areas more direct

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✏️ Regenerated Development Areas with "more direct" tone:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Development Areas

### Checking Understanding (Avg: 2.8/4 - CC)

Sarah needs to improve her understanding checks during presentations.
Current performance dropped from 3.3 to 2.8 this quarter.

⚠️ *Trend: 2.8 ↓ (was 3.3 in Q3) - requires immediate attention*

**Observations from Q4 2024:**

1. **Nov 10 - Macy's** (Technical Deep Dive)
   Moved too quickly through technical concepts without verifying
   the customer understood before progressing.

**Related Coaching Items:**
- [ ] Practice pausing for understanding checks *(added 2024-11-10)*

**Suggested Actions for Q1 2025:**
1. Build in mandatory 2-minute pauses after each major section
2. Practice the "tell me back what you heard" technique

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[k] Keep this version
[r] Try a different tone
[o] Revert to original
[back] Return to options

Enter choice: k

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Review Options:

[e] Edit sections of this draft
[t] Adjust tone of a section
[m] Add more examples to a section
[s] Save as-is to team/sarah-chen/reviews/2024-Q4-review.md
[r] Regenerate with different parameters
[d] Drill-down: See all ratings for a specific competency
[c] Cancel

Or just tell me what you'd like to change (e.g., "make development areas more direct" or "add more examples to strengths")

Enter choice: add more examples to strengths

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 Additional Examples Found for Strengths:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Currently cited:** 4 examples

**Additional examples available:**

[1] **Oct 22 - Williams-Sonoma** (Discovery)
    Strong value quantification approach
    > "You really understand our business" - VP Marketing

[2] **Nov 5 - Kroger** (Demo)
    Excellent handling of technical objections

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[a] Add all additional examples
[s] Select specific examples to add (enter numbers)
[q] Add only entries with quotes
[back] Return without adding

Enter choice: q

✅ Strengths Updated - Now includes 5 examples

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Review Options:
...

Enter choice: d

Which competency would you like to explore?

Available competencies with ratings in this period:
1. Discovery Depth (3 observations)
2. ELI5 (2 observations)
3. Dynamic Engagement (2 observations)
4. Checking Understanding (2 observations)
5. Objection Handling (2 observations)

Enter competency number or name (or 'back' to return): 1

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Competency Drill-Down: Discovery Depth
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**SE:** Sarah Chen
**Period:** Q4 2024 (Oct 1 - Dec 31)
**Average Rating:** 3.7/4 (UC)
**Trend:** ↑ (was 3.2 in Q3)

---

### All Observations (3 entries)

#### Q4 2024 (Current Period)

| Date | Customer | Rating | Stage | Notes |
|------|----------|--------|-------|-------|
| 2024-12-15 | Nordstrom | 4/4 | UC | Exceptional discovery - $5M savings opportunity |
| 2024-11-28 | Target | 4/4 | UC | Strong POC scoping with clear success criteria |
| 2024-10-10 | Macy's | 3/4 | CC | Good understanding of current state |

**Detailed Observations:**

1. **2024-12-15 - Nordstrom (Discovery)**
   - **Rating:** 4/4 (UC)
   - **Strengths noted:** Natural consultative approach uncovering $5M savings
   - **Full observation:** Customer said "Wow, I never thought about it that way"

2. **2024-11-28 - Target (POC Kickoff)**
   - **Rating:** 4/4 (UC)
   - **Strengths noted:** Clear ROI metrics and success criteria identified

3. **2024-10-10 - Macy's (Technical Deep Dive)**
   - **Rating:** 3/4 (CC)
   - **Strengths noted:** Good understanding of current state challenges

#### Q3 2024 (For Comparison)

| Date | Customer | Rating | Stage | Notes |
|------|----------|--------|-------|-------|
| 2024-08-20 | Target | 3/4 | CC | Good discovery but missed quantification |
| 2024-07-15 | Kroger | 3/4 | CC | Solid follow-up questions |

---

**Competency Definition:**
Going beyond surface-level questions to uncover true business impact

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[back] Return to review options
[another] Drill into another competency
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Enter choice: back

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Review Options:

[e] Edit sections of this draft
[s] Save as-is to team/sarah-chen/reviews/2024-Q4-review.md
[r] Regenerate with different parameters
[d] Drill-down: See all ratings for a specific competency
[c] Cancel

Enter choice: s

✅ Review saved to team/sarah-chen/reviews/2024-Q4-review.md
```

## Error Handling

**No SEs exist:**
```
There are no SE profiles yet. Run `/add-se {name}` to create one.
```

**Invalid period format:**
```
I couldn't parse the period "{input}".

Supported formats:
- Q4-2024 or 2024-Q4 (quarterly)
- Oct-Dec 2024 (month range)
- "last quarter" (dynamic)
- annual-2024 (full year)
- H1-2024 or H2-2024 (half year)

Please try again with a supported format.
```

**SE not found:**
```
I couldn't find an SE named "{input}". Did you mean: {list}?
Or run `/add-se {input}` to create a new profile.
```

## Performance Target

Review generation should complete within 60 seconds per NFR requirements.

## Related Commands

- `/log-feedback {se-name}` - Add feedback entries to SE's log
- `/prep-1on1 {se-name}` - Generate 1:1 preparation document
- `/profile {se-name}` - View/edit SE profile
- `/competencies` - View competency framework definitions
