# /competencies - Competency Framework Management

View, add, edit, delete, and manage competencies in the SE performance rating framework.

## What This Does

1. Displays interactive menu for competency management
2. Views all meeting and role competencies with details
3. Adds new meeting or role competencies with validation
4. Edits existing competencies while preserving other fields
5. Deletes competencies with usage checks
6. Modifies role mappings for meeting competencies

## Usage

```
/competencies                      # Show main menu
/competencies view                 # List all competencies
/competencies view meeting         # List meeting competencies only
/competencies view role            # List role competencies only
/competencies view eli5            # Show details for specific competency
/competencies add meeting          # Add new meeting competency
/competencies add role             # Add new role competency
/competencies edit eli5            # Edit specific competency
/competencies delete eli5          # Delete specific competency
/competencies mappings eli5        # Modify role mappings for competency
```

## Implementation

When this command is run, follow these steps exactly:

### Step 1: Display Main Menu

If no action specified, display the interactive menu:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 Competency Framework Management
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Select an action:

[a] Add meeting competency
[b] Add role competency
[e] Edit competency
[m] Modify mappings
[d] Delete competency
[v] View details
[q] Quit

Enter your choice:
```

Wait for user input. Parse the response:
- "a" → Go to Step 3 (Add Meeting Competency)
- "b" → Go to Step 4 (Add Role Competency)
- "e" → Go to Step 5 (Edit Competency)
- "m" → Go to Step 6 (Modify Mappings)
- "d" → Go to Step 7 (Delete Competency)
- "v" → Go to Step 2 (View Details)
- "q" → Display "Exiting competency management." and end

After completing any action, return to the main menu unless user selected [q].

### Step 2: View Details

**2.1 Load Competency Files:**

Read both competency configuration files:
- `config/competencies/meeting-competencies.yaml`
- `config/competencies/role-competencies.yaml`

**2.2 Parse and Count Competencies:**

Parse the YAML files and count:
- Number of meeting competencies (from `competencies:` section)
- Number of role competencies (from `competencies:` section)

**2.3 Display Summary:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Competency Framework Overview
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌─────────────────────────────────────────────────────────────────────────────┐
│  MEETING COMPETENCIES ({count})                                             │
│  Observable skills assessed during customer calls                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ID                          Name                                           │
│  ─────────────────────────   ───────────────────────────────────────────    │
{for each competency}
│  {id:<25}   {name:<43}   │
{end for}
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  ROLE COMPETENCIES ({count})                                                │
│  Overall performance dimensions for SE career growth                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ID                          Name                                           │
│  ─────────────────────────   ───────────────────────────────────────────    │
{for each competency}
│  {id:<25}   {name:<43}   │
{end for}
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Enter competency ID for details, or press Enter to return to menu:
```

**2.4 Show Competency Details (if ID provided):**

If user enters a competency ID:

1. Search both files for matching ID (case-insensitive)
2. If found, display full details:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 {name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ID: {id}                                    Type: {Meeting/Role} Competency

{description}

┌─────────────────────────────────────────────────────────────────────────────┐
│  PROFICIENCY LEVELS                                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Level 1 · Unconscious Incompetence                                         │
│  ───────────────────────────────────────────────────────────────────────    │
│  {level_examples.1.description}                                             │
│                                                                             │
│  Example: "{level_examples.1.example}"                                      │
│                                                                             │
│  Level 2 · Conscious Incompetence                                           │
│  ───────────────────────────────────────────────────────────────────────    │
│  {level_examples.2.description}                                             │
│                                                                             │
│  Example: "{level_examples.2.example}"                                      │
│                                                                             │
│  Level 3 · Conscious Competence                                             │
│  ───────────────────────────────────────────────────────────────────────    │
│  {level_examples.3.description}                                             │
│                                                                             │
│  Example: "{level_examples.3.example}"                                      │
│                                                                             │
│  Level 4 · Unconscious Competence                                           │
│  ───────────────────────────────────────────────────────────────────────    │
│  {level_examples.4.description}                                             │
│                                                                             │
│  Example: "{level_examples.4.example}"                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

{if meeting competency}
┌─────────────────────────────────────────────────────────────────────────────┐
│  EVIDENCE PROMPTS                                                           │
│  Questions to identify this competency during call reviews                  │
├─────────────────────────────────────────────────────────────────────────────┤
{for each prompt}
│  • {prompt}                                                                 │
{end for}
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  MAPS TO ROLE COMPETENCIES                                                  │
├─────────────────────────────────────────────────────────────────────────────┤
{for each mapping}
│  → {role_id}                                                                │
{end for}
└─────────────────────────────────────────────────────────────────────────────┘
{end if}

{if role competency with key_behaviors}
┌─────────────────────────────────────────────────────────────────────────────┐
│  KEY BEHAVIORS                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
{for each behavior}
│  • {behavior}                                                               │
{end for}
└─────────────────────────────────────────────────────────────────────────────┘
{end if}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

3. If not found, display error:
```
I couldn't find a competency with ID "{input}".

Did you mean one of these?
{list similar competency IDs using fuzzy matching}

Or run `/competencies view` to see all available competencies.
```

### Step 3: Add Meeting Competency

**3.1 Prompt for ID:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
➕ Add Meeting Competency
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Enter competency ID (lowercase_underscore format, e.g., "stakeholder_management"):
```

**Validate ID:**
- Must be lowercase letters and underscores only (regex: `^[a-z][a-z0-9_]*$`)
- Must not already exist in meeting-competencies.yaml
- If invalid format:
  ```
  Invalid ID format: "{input}"

  Competency IDs must:
  - Start with a lowercase letter
  - Contain only lowercase letters, numbers, and underscores
  - Use underscores to separate words

  Examples: stakeholder_management, technical_depth, roi_articulation

  Please enter a valid ID:
  ```
- If already exists:
  ```
  A meeting competency with ID "{input}" already exists.

  Choose a different ID, or use `/competencies edit {input}` to modify the existing one.
  ```

**3.2 Prompt for Name:**

```
Enter competency name (display name, e.g., "Stakeholder Management"):
```

Validate: Must be non-empty.

**3.3 Prompt for Description:**

```
Enter description (1-2 sentences explaining what this competency measures):
```

Validate: Must be non-empty.

**3.4 Prompt for Level Examples (1-4):**

For each level 1-4:

```
Level {n} - {stage_name}:
Enter description for this level:
```

Where stage_name is:
- Level 1: "Unconscious Incompetence"
- Level 2: "Conscious Incompetence"
- Level 3: "Conscious Competence"
- Level 4: "Unconscious Competence"

After description, prompt for example:

```
Enter a brief example behavior for Level {n}:
```

Validate: Both description and example must be non-empty.

**3.5 Prompt for Evidence Prompts:**

```
Enter 2-3 evidence prompts (questions to help identify this competency in calls).
These should be yes/no or observation-based questions.

Evidence prompt 1:
```

After first prompt:
```
Evidence prompt 2:
```

After second prompt:
```
Evidence prompt 3 (optional, press Enter to skip):
```

Validate: Must have at least 2, maximum 3.

**3.6 Prompt for Maps to Role:**

First, list available role competencies:

```
Which role competencies does this meeting competency map to?

Available role competencies:
├─ technical_credibility: Technical Credibility
├─ discovery_quality: Discovery Quality
├─ demo_excellence: Demo Excellence
├─ deal_influence: Deal Influence
├─ commercial_acumen: Commercial Acumen
├─ cross_functional_impact: Cross-Functional Impact
└─ workload_management: Workload Management

Enter role competency IDs (comma-separated), or press Enter to skip:
```

Validate: Each ID must exist in role-competencies.yaml.

**3.7 Show Summary and Confirmation:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 New Meeting Competency Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**ID:** {id}
**Name:** {name}
**Description:** {description}

**Level Examples:**
├─ L1: {level_1_desc}
├─ L2: {level_2_desc}
├─ L3: {level_3_desc}
└─ L4: {level_4_desc}

**Evidence Prompts:** {count} items
**Maps to Role:** {list of role IDs or "None"}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Add this competency to meeting-competencies.yaml? (y/n)
```

Wait for response:
- If "n" or "no": Display "Competency creation cancelled." and return to menu
- If "y" or "yes": Proceed to Step 3.8

**3.8 Append to YAML File:**

Read `config/competencies/meeting-competencies.yaml` and append the new competency entry to the `competencies:` section, preserving the existing format.

New entry format:
```yaml
  {id}:
    name: "{name}"
    description: "{description}"
    evidence_prompts:
      - "{prompt_1}"
      - "{prompt_2}"
      {- "{prompt_3}" if provided}
    level_examples:
      1:
        stage: "Unconscious Incompetence"
        description: "{level_1_desc}"
        example: "{level_1_example}"
      2:
        stage: "Conscious Incompetence"
        description: "{level_2_desc}"
        example: "{level_2_example}"
      3:
        stage: "Conscious Competence"
        description: "{level_3_desc}"
        example: "{level_3_example}"
      4:
        stage: "Unconscious Competence"
        description: "{level_4_desc}"
        example: "{level_4_example}"
    maps_to_role:
      {- {role_id} for each mapping}
```

**3.9 Validate Saved File:**

After saving, re-read the file and verify:
- YAML syntax is valid
- New competency appears in the file
- All required fields are present

**3.10 Display Result:**

If successful:
```
✅ Meeting competency "{name}" added successfully!

View it with: /competencies view {id}
```

If validation error (per ADR-005):
```
Configuration Error: meeting-competencies.yaml

There was an issue saving the competency. The file may have been corrupted.

Error details: {error_message}

The competency was not saved. You can try again or manually edit:
config/competencies/meeting-competencies.yaml
```

### Step 4: Add Role Competency

Similar to Step 3, but with these differences:

**4.1 Prompt for ID:**
Same validation as meeting competencies, but check uniqueness in role-competencies.yaml.

**4.2-4.4 Prompt for Name, Description, Level Examples:**
Same as meeting competencies.

**4.5 Show Summary:**
Role competencies don't have evidence_prompts or maps_to_role, but may have key_behaviors (optional):

```
Would you like to add key behaviors? (y/n)
```

If yes:
```
Enter key behaviors (one per line, empty line to finish):
```

**4.6-4.8 Confirmation, Append, Validate:**
Same process, but append to role-competencies.yaml.

Format for new entry:
```yaml
  {id}:
    name: "{name}"
    description: "{description}"
    {if key_behaviors}
    key_behaviors:
      - "{behavior_1}"
      - "{behavior_2}"
    {end if}
    level_examples:
      1:
        stage: "Unconscious Incompetence"
        description: "{level_1_desc}"
        example: "{level_1_example}"
      2:
        stage: "Conscious Incompetence"
        description: "{level_2_desc}"
        example: "{level_2_example}"
      3:
        stage: "Conscious Competence"
        description: "{level_3_desc}"
        example: "{level_3_example}"
      4:
        stage: "Unconscious Competence"
        description: "{level_4_desc}"
        example: "{level_4_example}"
```

### Step 5: Edit Competency

**5.1 Prompt for Competency ID:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✏️ Edit Competency
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Enter competency ID to edit (or partial name for fuzzy match):
```

**5.2 Load Current Competency:**

Search both files for the competency. Apply fuzzy matching if exact match not found:
- Check if input is substring of any competency ID
- Check if input is substring of any competency name
- Calculate Levenshtein distance for close matches

If multiple matches, list them:
```
Multiple competencies match "{input}":
├─ eli5 (Meeting): ELI5 (Explain Like I'm 5)
├─ eli5_advanced (Meeting): Advanced ELI5

Enter the exact ID to edit:
```

If no match:
```
I couldn't find a competency matching "{input}".

Available competencies:
{list all IDs}

Try again with an exact ID.
```

**5.3 Display Current Values:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✏️ Editing: {name} ({id})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Current values:

1. Name: {name}
2. Description: {description}
3. Level 1 example: {level_1_desc}
4. Level 2 example: {level_2_desc}
5. Level 3 example: {level_3_desc}
6. Level 4 example: {level_4_desc}
{if meeting competency}
7. Evidence prompts: {count} items
8. Maps to role: {list or "None"}
{end if}

Enter the number of the field to edit (or "done" to finish):
```

**5.4 Edit Selected Field:**

For each field, show current value and prompt for new value:

```
Current {field_name}: {current_value}

Enter new value (or press Enter to keep current):
```

**5.5 Preserve Unmodified Fields:**

After editing, only modify the fields that were changed. Keep all other fields exactly as they were.

**5.6 Show Confirmation:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 Changes to {name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{for each changed field}
{field_name}:
  Before: {old_value}
  After:  {new_value}
{end for}

Save changes? (y/n)
```

**5.7-5.8 Update File and Validate:**

If confirmed, update the competency in the appropriate file, preserving all other content.

### Step 6: Modify Mappings

**6.1 List Meeting Competencies with Mappings:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔗 Modify Role Mappings
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Meeting competencies and their role mappings:

{for each meeting competency}
├─ {id}: {name}
│  └─ Maps to: {maps_to_role list or "None"}
{end for}

Enter competency ID to modify mappings:
```

**6.2 Prompt for Competency:**

Validate the ID exists as a meeting competency.

**6.3 Show Available Role Competencies:**

```
Current mappings for {name}: {current_mappings or "None"}

Available role competencies:
{for each role competency}
├─ [{x if mapped, else space}] {id}: {name}
{end for}

Enter role IDs to toggle (comma-separated), or "done" to save:
```

**6.4 Allow Adding/Removing Mappings:**

Toggle mappings based on user input. Show updated state after each change.

**6.5 Update and Save:**

After user enters "done":

```
Update mappings for {name}?

Old: {old_mappings or "None"}
New: {new_mappings or "None"}

Confirm? (y/n)
```

**6.6 Validate After Save:**

Same validation as other operations.

### Step 7: Delete Competency

**7.1 Prompt for Competency ID:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🗑️ Delete Competency
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Enter competency ID to delete:
```

**7.2 Check for Usage in Feedback Logs:**

Scan all files matching `team/*/feedback-log.md` pattern.

For each file, search for the competency ID in:
- Rating table headers
- Competency references in text

Count total occurrences across all files.

**7.3 Show Warning if Used:**

If usage count > 0:
```
⚠️ Warning: "{id}" is used {count} times in feedback logs.

Files with references:
{list files with counts}

Deleting this competency will orphan this feedback data.
The historical ratings will remain but won't link to a competency definition.

Proceed with deletion? (y/n)
```

**7.4 Show Simple Confirmation if Not Used:**

If usage count = 0:
```
Delete competency "{id}" ({name})? (y/n)
```

**7.5 Remove from YAML:**

If confirmed:
1. Read the appropriate YAML file
2. Remove the entire competency entry
3. Write back the file

**7.6 Validate After Deletion:**

Verify:
- File is still valid YAML
- Competency no longer appears in file

Display:
```
✅ Competency "{id}" deleted successfully.
```

### Step 8: Validation (Applied Throughout)

**8.1 YAML Syntax Validation:**

When reading/writing YAML files, catch parse errors and report with line numbers:

```
Configuration Error: {filename}

YAML syntax error at line {line_number}:
{error_message}

The file could not be parsed. Please check the file manually:
{file_path}
```

**8.2 Required Fields Validation:**

For meeting competencies, verify:
- id (must be unique, lowercase_underscore)
- name (non-empty string)
- description (non-empty string)
- level_examples (must have 1, 2, 3, 4)
- evidence_prompts (2-3 items)

For role competencies, verify:
- id (must be unique, lowercase_underscore)
- name (non-empty string)
- description (non-empty string)
- level_examples (must have 1, 2, 3, 4)

**8.3 Level Examples Validation:**

Each level_examples entry must have:
- stage (matches the level: UI/CI/CC/UC)
- description (non-empty)
- example (non-empty)

If missing:
```
Configuration Error: {filename}

Competency '{id}' is missing level_examples for level {n}.

Each competency needs examples for all 4 levels:
  1: Unconscious Incompetence
  2: Conscious Incompetence
  3: Conscious Competence
  4: Unconscious Competence

Example:
  level_examples:
    1:
      stage: "Unconscious Incompetence"
      description: "Description of this level"
      example: "Example behavior"
```

**8.4 Evidence Prompts Validation:**

Must have 2-3 items:
```
Configuration Error: {filename}

Competency '{id}' has {count} evidence_prompts.

Meeting competencies require 2-3 evidence prompts.
These are questions to help identify this competency during call reviews.

Example:
  evidence_prompts:
    - "Did the SE adapt language to the audience?"
    - "Were technical concepts explained clearly?"
```

**8.5 Maps to Role Validation:**

Each ID in maps_to_role must exist in role-competencies.yaml:

```
Configuration Error: {filename}

Competency '{id}' references unknown role competency: '{bad_ref}'

Valid role competency IDs:
{list all valid IDs}

Update maps_to_role to use valid role competency IDs.
```

**8.6 ID Uniqueness Validation:**

If duplicate ID found:
```
Configuration Error: {filename}

Duplicate competency ID found: '{id}'

Each competency must have a unique ID within its category.
Please rename one of the duplicates.
```

**8.7 Error Message Format (ADR-005):**

All errors follow the conversational, suggestion-rich format:
- State the problem clearly
- Explain what's wrong
- Show an example of correct format
- Suggest how to fix it

## Error Handling

**If config/competencies/ directory doesn't exist:**
```
I can't find the competencies configuration directory.
The project may not be set up yet.

Try running `/setup` first, or check that `config/competencies/` exists.
```

**If competency files are missing:**
```
I couldn't find the competency configuration files.

Expected files:
- config/competencies/meeting-competencies.yaml
- config/competencies/role-competencies.yaml

Run `/setup` to create the default configuration.
```

**If file write fails:**
```
I couldn't save changes to {filename}.

This might happen if:
- File permissions prevent writing
- The file is locked by another process
- Disk is full

You can try manually editing: {file_path}
```

## Example Sessions

### Example 1: View All Competencies
```
> /competencies

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 Competency Framework Management
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Select an action:

[a] Add meeting competency
[b] Add role competency
[e] Edit competency
[m] Modify mappings
[d] Delete competency
[v] View details
[q] Quit

Enter your choice:
> v

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Competency Framework Overview
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌─────────────────────────────────────────────────────────────────────────────┐
│  MEETING COMPETENCIES (7)                                                   │
│  Observable skills assessed during customer calls                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ID                          Name                                           │
│  ─────────────────────────   ───────────────────────────────────────────    │
│  eli5                        ELI5 (Explain Like I'm 5)                      │
│  checking_understanding      Checking Understanding                         │
│  dynamic_engagement          Dynamic Engagement                             │
│  objection_handling          Objection Handling                             │
│  competitive_positioning     Competitive Positioning                        │
│  discovery_depth             Discovery Depth                                │
│  demo_storytelling           Demo Storytelling                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  ROLE COMPETENCIES (7)                                                      │
│  Overall performance dimensions for SE career growth                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ID                          Name                                           │
│  ─────────────────────────   ───────────────────────────────────────────    │
│  technical_credibility       Technical Credibility                          │
│  discovery_quality           Discovery Quality                              │
│  demo_excellence             Demo Excellence                                │
│  deal_influence              Deal Influence                                 │
│  commercial_acumen           Commercial Acumen                              │
│  cross_functional_impact     Cross-Functional Impact                        │
│  workload_management         Workload Management                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Enter competency ID for details, or press Enter to return to menu:
> eli5

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 ELI5 (Explain Like I'm 5)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ID: eli5                                    Type: Meeting Competency

Ability to simplify complex technical concepts for non-technical audiences

┌─────────────────────────────────────────────────────────────────────────────┐
│  PROFICIENCY LEVELS                                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Level 1 · Unconscious Incompetence                                         │
│  ───────────────────────────────────────────────────────────────────────    │
│  Uses technical jargon without awareness; assumes audience understands      │
│  technical terms                                                            │
│                                                                             │
│  Example: "Explains API integration using developer terminology to a CMO    │
│  without realizing the confusion"                                           │
│                                                                             │
│  Level 2 · Conscious Incompetence                                           │
│  ───────────────────────────────────────────────────────────────────────    │
│  Recognizes when explanations are too technical but struggles to simplify   │
│                                                                             │
│  Example: "Notices customer confusion and tries to clarify but falls back   │
│  into technical language"                                                   │
│                                                                             │
│  Level 3 · Conscious Competence                                             │
│  ───────────────────────────────────────────────────────────────────────    │
│  Deliberately uses analogies and simple language; checks for understanding  │
│                                                                             │
│  Example: "Compares identity resolution to 'connecting puzzle pieces' and   │
│  asks 'Does that make sense?'"                                              │
│                                                                             │
│  Level 4 · Unconscious Competence                                           │
│  ───────────────────────────────────────────────────────────────────────    │
│  Naturally adapts language to audience; seamlessly translates complex       │
│  concepts                                                                   │
│                                                                             │
│  Example: "Effortlessly switches between technical depth with engineers     │
│  and business value with executives"                                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  EVIDENCE PROMPTS                                                           │
│  Questions to identify this competency during call reviews                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  • Did the SE avoid jargon when speaking with non-technical stakeholders?   │
│  • Were analogies or relatable examples used to explain technical concepts? │
│  • Did the customer demonstrate understanding after the explanation?        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  MAPS TO ROLE COMPETENCIES                                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  → technical_credibility                                                    │
│  → demo_excellence                                                          │
└─────────────────────────────────────────────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Example 2: Add Meeting Competency
```
> /competencies

[Select a from menu]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
➕ Add Meeting Competency
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Enter competency ID (lowercase_underscore format):
> stakeholder_management

Enter competency name:
> Stakeholder Management

Enter description:
> Effectively engaging and managing multiple stakeholders with different priorities

Level 1 - Unconscious Incompetence:
Enter description: Focuses on one stakeholder; ignores others in the room
Enter example: Talks only to technical lead while executives disengage

[Continue through all 4 levels...]

Evidence prompt 1:
> Did the SE address all stakeholders in the meeting?

Evidence prompt 2:
> Were different stakeholder priorities acknowledged?

Evidence prompt 3 (optional):
> [Enter pressed to skip]

Enter role competency IDs to map (comma-separated):
> deal_influence, commercial_acumen

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 New Meeting Competency Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**ID:** stakeholder_management
**Name:** Stakeholder Management
**Description:** Effectively engaging and managing multiple stakeholders...

...

Add this competency? (y/n)
> y

✅ Meeting competency "Stakeholder Management" added successfully!

View it with: /competencies view stakeholder_management
```

### Example 3: Delete Competency with Usage Warning
```
> /competencies

[Select d from menu]

Enter competency ID to delete:
> eli5

⚠️ Warning: "eli5" is used 15 times in feedback logs.

Files with references:
├─ team/sarah-chen/feedback-log.md: 8 references
├─ team/marcus-johnson/feedback-log.md: 5 references
└─ team/alex-rivera/feedback-log.md: 2 references

Deleting this competency will orphan this feedback data.
The historical ratings will remain but won't link to a competency definition.

Proceed with deletion? (y/n)
> n

Deletion cancelled. Competency preserved.
```

### Example 4: Validation Error
```
> /competencies

[Select a from menu]

Enter competency ID:
> Has Spaces

Invalid ID format: "Has Spaces"

Competency IDs must:
- Start with a lowercase letter
- Contain only lowercase letters, numbers, and underscores
- Use underscores to separate words

Examples: stakeholder_management, technical_depth, roi_articulation

Please enter a valid ID:
```

## Natural Language Support

This command also responds to natural language requests:

**View Triggers:**
- "Show me the competencies"
- "List all competencies"
- "What competencies are there?"
- "Show eli5 details"

**Add Triggers:**
- "Add a new competency"
- "Create a meeting competency"
- "Add a role competency"

**Edit Triggers:**
- "Edit eli5"
- "Change the eli5 competency"
- "Update eli5 description"

**Delete Triggers:**
- "Delete eli5"
- "Remove the eli5 competency"

**Mapping Triggers:**
- "Change eli5 mappings"
- "What does eli5 map to?"
- "Update role mappings for eli5"

When Claude receives these natural language requests, it should follow the implementation steps above.
