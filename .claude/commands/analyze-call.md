# /analyze-call - AI-Assisted Call Transcript Analysis

Analyze a call transcript to identify SE behaviors, suggest competency ratings with evidence, and log feedback automatically.

## What This Does

1. Reads and parses the specified transcript file
2. Identifies the SE from participants (prompts if ambiguous)
3. Analyzes transcript for competency behaviors with line citations
4. Suggests ratings with evidence and extracts notable quotes
5. Generates coaching suggestions from development areas
6. Presents analysis with action options: accept, modify, save draft, or cancel
7. Logs feedback in same format as /log-feedback

## Usage

```
/analyze-call data/transcripts/2024-12/2024-12-15-nordstrom-discovery.md
/analyze-call data/transcripts/2025-01/2025-01-08-target-demo.md
```

## Arguments

- `transcript-path`: Path to the transcript file (required)

## Implementation

When this command is run, follow these steps exactly:

### Step 1: Parse and Validate Transcript Path

**1.1 Extract transcript path from input:**
- The argument is the full path to the transcript file
- Accept absolute paths or project-relative paths

**1.2 Validate file exists:**
- Read the file to confirm it exists and is readable
- If file not found, display error (ADR-005 pattern):

```
Transcript not found at "{path}"

Please check the path and try again. Transcripts should be in:
  data/transcripts/YYYY-MM/YYYY-MM-DD-customer-type.md

Or use `/add-transcript` to create a new transcript from notes.
```

### Step 2: Parse Transcript and Extract Metadata

**2.1 Read complete transcript file content**

**2.2 Parse header section (before \****`---`**\*\* divider):**

Expected format:
```markdown
# {Customer} - {Call Type}

**Date:** YYYY-MM-DD
**Duration:** {duration}
**Participants:**
- {Name} (SE)
- {Name} ({Role})
- ...

**Source:** gong | manual
```

Extract:
- `customer`: From title (before ` - `)
- `call_type`: From title (after ` - `)
- `date`: From Date field
- `participants`: List of all participants with roles

**2.3 Identify SE(s) from participants:**
- SE is marked with "(SE)" suffix in participants list
- List all SE folders in `team/` (exclude `_template/`, `_archived/`)
- Match participant names to SE folder names

**2.4 If multiple SEs found, prompt user:**
```
Multiple SEs found in this call:
  1. Sarah Chen
  2. Marcus Johnson

Which SE should this feedback be logged for? (Enter number):
```

**2.5 If no SE found, show error:**
```
Could not identify the SE from transcript participants.

Participants found:
  - {list}

Please ensure the SE is listed with "(SE)" suffix in the transcript.
```

**2.6 Add line numbers to transcript:**
- Number each line starting from 1
- Store line-numbered version for citation

**2.7 Display analysis confirmation:**
```
🔍 Analyzing {Customer} {Call Type} with {SE Name}. This may take a moment...
```

### Step 3: Perform AI Analysis

**3.1 Load meeting competencies from \****`config/competencies/meeting-competencies.yaml`**\*\*:**
- Read all 7 competencies with their level_examples and evidence_prompts

**3.2 Analyze transcript for each competency:**

For each competency, examine the transcript for evidence of:
- Behaviors matching level_examples (1-4)
- Responses to evidence_prompts

Generate structured analysis:
- Only rate competencies where clear evidence exists in the transcript
- Skip competencies with no observable evidence

**3.3 Generate rating suggestions with line citations:**

For each rated competency, provide:
- Rating (1-4)
- Stage code (UI/CI/CC/UC)
- Evidence summary with specific line numbers
- Example format: "Used retail-specific analogies when explaining identity resolution (lines 145-152)"

**3.4 Extract observations:**
- **Strengths**: Positive behaviors observed in the call
- **Development Areas**: Opportunities for improvement

**3.5 Extract 1-3 notable quotes:**
- Quotes that demonstrate impact or customer reaction
- Include line number and speaker for each
- Example: `"This is exactly what we've been looking for" - VP Marketing (line 287)`

**3.6 Generate coaching suggestions:**
- Based on development areas observed
- Specific, actionable items for 1:1 discussion
- Example: "Practice ROI quantification framework before next executive call"

**3.7 Build structured analysis result:**

```yaml
analysis:
  se_name: "{SE Name}"
  se_folder: "{se-name}"
  customer: "{Customer}"
  call_type: "{Call Type}"
  date: "{YYYY-MM-DD}"
  suggested_ratings:
    - competency_id: "eli5"
      competency_name: "ELI5"
      rating: 3
      stage_code: "CC"
      evidence: "Used retail-specific analogies (lines 145-152)"
    - competency_id: "discovery_depth"
      rating: 4
      stage_code: "UC"
      evidence: "Uncovered attribution pain, quantified at $2M (lines 78-95, 112)"
  observations:
    strengths: "Deep discovery, strong rapport with technical stakeholders"
    development_areas: "Could quantify ROI more explicitly for executives"
  notable_quotes:
    - text: "This is the first time someone's actually understood our attribution challenge."
      line: 287
      speaker: "Customer"
  coaching_suggestions:
    - "Practice ROI quantification framework before next exec call"
    - "Prepare executive summary template for discovery insights"
```

### Step 4: Present Analysis Results

**4.1 Display suggested ratings with evidence:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 SUGGESTED COMPETENCY RATINGS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ELI5: 3 (CC) - Conscious Competence
  Evidence: Used retail-specific analogies when explaining identity resolution (lines 145-152)

Discovery Depth: 4 (UC) - Unconscious Competence
  Evidence: Uncovered attribution pain, quantified at $2M revenue impact (lines 78-95, 112)

Checking Understanding: 3 (CC) - Conscious Competence
  Evidence: Asked "Does that make sense for your use case?" after key explanations (lines 67, 134)
```

**4.2 Display observations:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 OBSERVATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Strengths:
  Deep discovery, strong rapport with technical stakeholders. Effectively used customer-specific examples.

Development Areas:
  Could quantify ROI more explicitly for executives. Timeline discussion was brief.
```

**4.3 Display notable quotes:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💬 NOTABLE QUOTES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. "This is the first time someone's actually understood our attribution challenge."
   - Customer (line 287)

2. "The way you connected identity resolution to our loyalty program was really clear."
   - VP Marketing (line 312)
```

**4.4 Display coaching suggestions:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 COACHING SUGGESTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• Practice ROI quantification framework before next exec call
• Prepare executive summary template for discovery insights
```

**4.5 Display action options:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 ACTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[a] Accept - Save these suggestions to feedback log
[m] Modify - Adjust ratings or observations before saving
[s] Save Draft - Save analysis for later review
[c] Cancel - Exit without saving

Your choice:
```

### Step 5: Handle User Selection

**On [a] Accept:**
- Go to Step 6 (Save to Feedback Log)

**On [m] Modify:**
- Go to Step 7 (Modify Flow)

**On [s] Save Draft:**
- Go to Step 8 (Save Draft Flow)

**On [c] Cancel:**
- Go to Step 9 (Cancel Flow)

### Step 6: Accept Flow - Save to Feedback Log

**6.1 Generate feedback entry using same format as /log-feedback:**

```markdown
---
## {YYYY-MM-DD} | {Customer} | {Call Type}
**Transcript:** [[{transcript-path}]]

### Competency Ratings
| Competency | Rating |
|------------|--------|
| {competency_name} | {rating} ({stage_code}) |

### Observations
**Strengths:** {strengths}
**Development Areas:** {development_areas}

### Coaching Items
- [ ] {coaching_item} (added {today})

### Notable Quotes
> "{quote_text}" - {speaker} (line {line_number})

*AI-assisted analysis*
---
```

**6.2 Append entry to \****`team/{se-name}/feedback-log.md`**

**6.3 Display success confirmation:**

```
✅ Feedback saved for {SE Display Name}
   {date} | {customer} | {call_type} | {N} competencies rated
   Transcript linked: {transcript-path}

   📝 This entry was marked as AI-assisted analysis
```

### Step 7: Modify Flow

**7.1 Display current ratings for modification:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✏️ MODIFY RATINGS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Current ratings (Enter new value 1-4, or press Enter to keep):
Rating scale: 1=UI (unaware) | 2=CI (struggling) | 3=CC (deliberate) | 4=UC (natural)

ELI5 [current: 3]:
Discovery Depth [current: 4]:
Checking Understanding [current: 3]:
```

**7.2 Prompt for observation changes:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✏️ MODIFY OBSERVATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Strengths [Enter to keep current]:
{current value shown}
New value:

Development Areas [Enter to keep current]:
{current value shown}
New value:
```

**7.3 Update analysis with modifications**

**7.4 Display updated preview:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ UPDATED PREVIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{show updated entry preview}
```

**7.5 Return to action options:**

```
[a] Accept - Save these changes to feedback log
[m] Modify - Make more changes
[s] Save Draft - Save for later review
[c] Cancel - Exit without saving

Your choice:
```

### Step 8: Save Draft Flow

**8.1 Create \****`outputs/drafts/`**\*\* directory if it doesn't exist**

**8.2 Generate filename:** `{se-name}-{YYYY-MM-DD}.md`

**8.3 Write draft file with full analysis:**

```markdown
# Draft Analysis: {Customer} {Call Type} with {SE Name}

**Date:** {date}
**Transcript:** {transcript-path}
**Status:** Draft - Pending Review

## Suggested Competency Ratings

| Competency | Rating | Evidence |
|------------|--------|----------|
| {name} | {rating} ({stage_code}) | {evidence with lines} |

## Observations

**Strengths:** {strengths}

**Development Areas:** {development_areas}

## Notable Quotes

{quotes with line numbers}

## Coaching Suggestions

{coaching items}

---
*Generated by /analyze-call on {today}*
```

**8.4 Display confirmation:**

```
💾 Draft saved to: outputs/drafts/{se-name}-{date}.md

To resume later, review the draft and run:
  /log-feedback {se-name}

Or re-analyze the transcript:
  /analyze-call {transcript-path}
```

### Step 9: Cancel Flow

**9.1 Display cancellation message:**

```
❌ Analysis cancelled. No changes were made.
```

**9.2 Exit without any file modifications**

## Stage Code Reference

| Rating | Code | Stage | Description |
| --- | --- | --- | --- |
| 1 | UI | Unconscious Incompetence | Unaware of gap |
| 2 | CI | Conscious Incompetence | Aware but struggling |
| 3 | CC | Conscious Competence | Deliberate effort works |
| 4 | UC | Unconscious Competence | Natural and effortless |

## Error Handling (ADR-005)

**Transcript not found:**
```
Transcript not found at "{path}"

Please check the path and try again. Transcripts should be in:
  data/transcripts/YYYY-MM/YYYY-MM-DD-customer-type.md
```

**No SE identified:**
```
Could not identify the SE from transcript participants.

Participants found: {list}

Please ensure the SE is listed with "(SE)" suffix in the transcript,
or specify the SE: /log-feedback {se-name}
```

**SE not in system:**
```
SE "{name}" found in transcript but not in team profiles.

Run `/add-se {name}` to create their profile first.
```

**Competencies file missing:**
```
Couldn't load competencies from config/competencies/meeting-competencies.yaml

Run `/setup` to initialize the system configuration.
```

## Example Session

```
> /analyze-call data/transcripts/2024-12/2024-12-15-nordstrom-discovery.md

🔍 Analyzing Nordstrom Discovery with Sarah Chen. This may take a moment...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 SUGGESTED COMPETENCY RATINGS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ELI5: 3 (CC) - Conscious Competence
  Evidence: Used retail-specific analogies when explaining identity resolution (lines 145-152)

Discovery Depth: 4 (UC) - Unconscious Competence
  Evidence: Uncovered attribution pain, quantified at $2M revenue impact (lines 78-95, 112)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 OBSERVATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Strengths:
  Deep discovery, strong rapport with technical stakeholders. Effectively used customer-specific examples.

Development Areas:
  Could quantify ROI more explicitly for executives.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💬 NOTABLE QUOTES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. "This is the first time someone's actually understood our attribution challenge."
   - VP Marketing (line 287)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 COACHING SUGGESTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• Practice ROI quantification framework before next exec call

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 ACTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[a] Accept - Save these suggestions to feedback log
[m] Modify - Adjust ratings or observations before saving
[s] Save Draft - Save analysis for later review
[c] Cancel - Exit without saving

Your choice: a

✅ Feedback saved for Sarah Chen
   2024-12-15 | Nordstrom | Discovery | 2 competencies rated
   Transcript linked: data/transcripts/2024-12/2024-12-15-nordstrom-discovery.md

   📝 This entry was marked as AI-assisted analysis
```

## Natural Language Support

Triggers: "Analyze the call transcript at...", "Review call transcript", "AI analyze transcript"
