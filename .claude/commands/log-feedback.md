# /log-feedback - Log Structured Feedback for SE Performance

Log structured feedback after reviewing a customer call. Quick form-style entry with competency scores and overall notes.

## What This Does

1. Resolves SE name (fuzzy matching)
2. Collects call context: date, customer, call type
3. Displays compact competency rating form (scores 1-4 only)
4. Captures overall notes for the call (not per-competency)
5. Captures coaching items and notable quotes
6. Shows preview and confirmation gate
7. Appends to feedback log

## Usage

```
/log-feedback sarah-chen           # Log feedback for Sarah Chen
/log-feedback sarah                # Fuzzy match - will find sarah-chen
```

## Implementation

When this command is run, follow these steps exactly:

### Step 1: Parse Input and Resolve SE Name

**1.1 Normalize the input:**
- Convert to lowercase, replace spaces with hyphens, remove special characters

**1.2 List all SE folders in team/ (exclude _template/, _archived/)**

**1.3 Fuzzy Match (Levenshtein Distance):**
- Exact match → Use directly
- Single close match (distance ≤ 2) → Use with confirmation
- Multiple matches → Ask user to clarify
- No matches → Show error with suggestions (ADR-005)

**If no match found:**
```
I couldn't find an SE named "{input}". Did you mean: {suggestions}?
Or run `/add-se {input}` to create a new profile.
```

**1.4 Get Display Name from profile.md and show:**
```
📝 Logging feedback for {Display Name}
```

### Step 2: Check for Recent Gong Calls (Optional)

**2.1 Check if Gong integration is configured:**
- Check if GONG_ACCESS_TOKEN environment variable is set
- If not set, skip to Step 3 (manual entry)

**2.2 Look for recent transcripts for this SE:**
- Scan `data/transcripts/` for transcripts from the last 14 days
- Read each transcript file and check the Participants list for the SE name
- Collect matching transcripts with their metadata

**2.3 If recent Gong calls found, offer selection:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📞 RECENT GONG CALLS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Found recent calls for {SE Name}:

  [1] 2025-01-15 | Nordstrom | Discovery | 45 min
      → data/transcripts/2025-01/2025-01-15-nordstrom-discovery.md

  [2] 2025-01-12 | Target | Demo | 60 min
      → data/transcripts/2025-01/2025-01-12-target-demo.md

  [m] Enter call details manually

Select a call or 'm' for manual entry:
```

**2.4 If user selects a Gong call:**
- Extract date, customer, and call type from the transcript
- Set `transcript_path` to link the feedback entry
- Skip to Step 3 (competency ratings) with pre-populated context

**2.5 If user selects 'm' or no Gong calls found:**
- Continue to Step 3 (manual entry)

### Step 3: Collect Call Context (Quick Form)

Display a compact form and collect responses:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 CALL DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Date [Enter=today]:
Customer:
Call type [1-7]: 1.Discovery 2.Demo 3.Technical 4.Exec 5.POC-Kick 6.POC-Review 7.Other
```

Collect each field:
- **Date**: Default to today if empty. Validate YYYY-MM-DD format.
- **Customer**: Required, cannot be empty.
- **Call type**: Accept 1-7 or name. Map to full name.

### Step 4: Competency Ratings (Quick Form)

Display all competencies in a compact rating form. User rates only the competencies they observed:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 COMPETENCY RATINGS (1-4, or Enter to skip)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Rating scale: 1=UI (unaware) | 2=CI (struggling) | 3=CC (deliberate) | 4=UC (natural)

eli5 (simplify complex concepts):
checking_understanding (verify comprehension):
dynamic_engagement (keep all engaged):
objection_handling (address concerns):
competitive_positioning (differentiate):
discovery_depth (uncover business impact):
demo_storytelling (narrative not features):
```

For each competency:
- Accept 1, 2, 3, 4, or empty (skip)
- If invalid → Re-prompt for that competency only
- Store only the rated competencies (skip empty ones)

**Stage code mapping:**
- 1 → UI (Unconscious Incompetence)
- 2 → CI (Conscious Incompetence)
- 3 → CC (Conscious Competence)
- 4 → UC (Unconscious Competence)

### Step 5: Overall Call Notes

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 OBSERVATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

What went well? (required):
Development areas? (optional):
Coaching items? (comma-separated, optional):
Notable quote? (optional):
```

- **Strengths**: Required, cannot be empty
- **Development areas**: Optional
- **Coaching items**: Optional, split by comma, format as `- [ ] {item} (added YYYY-MM-DD)`
- **Quote**: Optional, format with `> ` prefix

### Step 6: Check for First Entry

Read `team/{se-name}/feedback-log.md` and count existing entries (by `## YYYY-MM-DD` pattern).
Set `is_first_entry = true` if count is 0.

### Step 7: Generate Entry and Confirm

**7.1 Build entry:**

```markdown
---
## {YYYY-MM-DD} | {Customer} | {Call Type}
**Transcript:** [[{transcript-path}]]  ← Include only if Gong call was selected

### Competency Ratings
| Competency | Rating |
|------------|--------|
| {name} | {rating} ({stage_code}) |

### Observations
**Strengths:** {strengths}
**Development Areas:** {dev_areas or "None noted"}

### Coaching Items
- [ ] {item} (added YYYY-MM-DD)

### Notable Quotes
> "{quote}"
---
```

- Omit Coaching Items section if none
- Omit Notable Quotes section if none

**7.2 Display preview and confirm:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ PREVIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{entry content}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Save to feedback log? (y/n)
```

- "y" or "yes" → Proceed to save
- "n" or "no" → Cancel: "Feedback entry cancelled."

### Step 8: Save and Confirm

1. Append entry to END of `team/{se-name}/feedback-log.md`
2. Display success:

```
✅ Feedback saved for {Display Name}
   {date} | {customer} | {call_type} | {N} competencies rated
```

3. If first entry, show tips:
```
💡 Tips:
   • Run `/prep-1on1 {se-name}` before your next 1:1
   • Coaching items are tracked until marked complete
```

## Example Session (with Gong Integration)

```
> /log-feedback sarah

📝 Logging feedback for Sarah Chen

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📞 RECENT GONG CALLS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Found recent calls for Sarah Chen:

  [1] 2024-12-15 | Nordstrom | Discovery | 45 min
      → data/transcripts/2024-12/2024-12-15-nordstrom-discovery.md

  [m] Enter call details manually

Select a call or 'm' for manual entry: 1

✓ Using call: Nordstrom - Discovery (2024-12-15)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 COMPETENCY RATINGS (1-4, or Enter to skip)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Rating scale: 1=UI (unaware) | 2=CI (struggling) | 3=CC (deliberate) | 4=UC (natural)

eli5: 3
checking_understanding:
dynamic_engagement:
objection_handling:
competitive_positioning:
discovery_depth: 4
demo_storytelling:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 OBSERVATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

What went well? Strong discovery, identified critical pain point around customer identity. Great rapport with VP Marketing. Used retail-specific analogies.
Development areas? Could push harder on timeline and decision criteria
Coaching items? Practice timeline questions, Competitive positioning for retail CDP
Notable quote? "The way you connected identity resolution to our loyalty challenges really resonated" - VP Marketing

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ PREVIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

---
## 2024-12-15 | Nordstrom | Discovery
**Transcript:** [[data/transcripts/2024-12/2024-12-15-nordstrom-discovery.md]]

### Competency Ratings
| Competency | Rating |
|------------|--------|
| ELI5 | 3 (CC) |
| Discovery Depth | 4 (UC) |

### Observations
**Strengths:** Strong discovery, identified critical pain point around customer identity. Great rapport with VP Marketing. Used retail-specific analogies.
**Development Areas:** Could push harder on timeline and decision criteria

### Coaching Items
- [ ] Practice timeline questions (added 2025-12-24)
- [ ] Competitive positioning for retail CDP (added 2025-12-24)

### Notable Quotes
> "The way you connected identity resolution to our loyalty challenges really resonated" - VP Marketing
---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Save to feedback log? (y/n) y

✅ Feedback saved for Sarah Chen
   2024-12-15 | Nordstrom | Discovery | 2 competencies rated
   Transcript linked: data/transcripts/2024-12/2024-12-15-nordstrom-discovery.md
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

**Competencies file missing:**
```
Couldn't load competencies from config/competencies/meeting-competencies.yaml
```

## Natural Language Support

Triggers: "Log feedback for Sarah", "Add feedback for sarah-chen", "Record feedback"
