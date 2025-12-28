# /archive - Archive an SE Profile

Archive an SE who has left the team. Moves their folder to `team/_archived/` with all data preserved.

## What This Does

1. Verifies the SE exists in `team/` directory
2. Displays a confirmation warning (y/n gate)
3. Creates `team/_archived/` directory if needed
4. Moves the SE's folder to `team/_archived/`
5. Adds `archived_date` field to their profile

## Usage

```
/archive sarah-chen
/archive Sarah Chen
Archive sarah-chen
Archive Sarah
```

## Arguments

- `se-name`: The SE's name (supports fuzzy matching)

## Implementation

When this command is run, follow these steps exactly:

### Step 1: Parse and Normalize SE Name

Take the argument provided and normalize it:

**Normalization Rules:**
1. Convert to lowercase
2. Replace spaces with hyphens
3. Remove special characters except hyphens
4. Collapse multiple hyphens to single hyphen
5. Trim leading/trailing hyphens

**Examples:**
- `"Sarah Chen"` → `sarah-chen`
- `"sarah chen"` → `sarah-chen`
- `"SARAH-CHEN"` → `sarah-chen`

### Step 2: Resolve SE Name (Fuzzy Matching)

**2.1 List all SE folders:**
```
List all subdirectories in team/ directory
Exclude: _template/, _archived/, any files (only directories)
```

**2.2 Find Best Match:**

For each SE folder name, check:
- Exact match (normalized input = folder name)
- Very close match (Levenshtein distance ≤ 2)
- Input is a substring of folder name
- Folder name starts with input

**Matching Rules:**
1. **Exact match found** → Use that SE
2. **Single close match found** → Use that SE (with brief confirmation in output)
3. **Multiple matches found** → List all and ask user to clarify
4. **No matches found** → Display conversational error

**If no SEs exist:**
```
There are no SE profiles yet.

Run `/add-se {name}` to create your first SE profile.
```

**If no match found but SEs exist:**
```
I couldn't find an SE named "{input}".

Did you mean one of these?
  - sarah-chen
  - marcus-johnson

Or run `/add-se {input}` to create a new profile.
```

### Step 3: Display Confirmation Warning

Archive is a significant operation. Always show a warning first:

```
⚠️ Are you sure you want to archive {display_name}?

This will move their folder to team/_archived/. The data will be preserved
but they will no longer appear in active SE lists.

This action can be reversed by manually moving the folder back.

Confirm archive? (y/n)
```

Wait for user response:
- If "y" or "yes": Proceed to Step 4
- If "n" or "no": Display "Archive cancelled. No changes were made." and exit
- If unclear: Ask for clarification

### Step 4: Create Archive Directory (if needed)

Check if `team/_archived/` directory exists:
- If not exists: Create `team/_archived/` directory

### Step 5: Move SE Folder

Move entire `team/{se-name}/` folder to `team/_archived/{se-name}/`

This includes all contents:
- profile.md
- feedback-log.md
- 1on1-notes/ directory
- reviews/ directory

### Step 6: Add Archive Date to Profile

1. Read `team/_archived/{se-name}/profile.md`
2. Find the metadata section (lines with **Created:** and **Last Updated:**)
3. Add `**Archived Date:** YYYY-MM-DD` line after **Last Updated:**
4. Write the updated file

### Step 7: Display Success Message

```
✅ Archived {display_name}

**Archive Location:** team/_archived/{se-name}/
**Archived Date:** {today's date}

Their data has been preserved and can be accessed at the archive location.
To restore, manually move the folder back to team/{se-name}/
```

## Error Handling

All error messages should follow ADR-005 Conversational Error Handling:

**If team/ directory doesn't exist:**
```
I can't find the team directory. The project may not be set up yet.

Try running `/setup` first, or check that the `team/` directory exists.
```

**If SE folder doesn't exist:**
```
I couldn't find an SE named "{input}".

Did you mean one of these?
  - {list available SEs}

Or run `/add-se {input}` to create a new profile.
```

**If archive folder already exists:**
```
There's already an archived SE named "{se-name}" in team/_archived/.

This might mean:
1. This SE was already archived
2. There's a naming conflict

You can:
- Check team/_archived/{se-name}/ to see if it's the same person
- Manually rename one of the folders
- Delete the old archive if it's no longer needed
```

**If folder move fails:**
```
I couldn't archive {se-name}. There was an error moving the folder.

This might happen if:
- File permissions prevent the move
- The _archived directory couldn't be created
- Files are open in another application

You can try:
1. Close any open files from team/{se-name}/
2. Check folder permissions
3. Manually move the folder: team/{se-name}/ → team/_archived/{se-name}/
```

## Example Sessions

### Example 1: Successful Archive
```
> Archive test-archive

⚠️ Are you sure you want to archive Test Archive?

This will move their folder to team/_archived/. The data will be preserved
but they will no longer appear in active SE lists.

This action can be reversed by manually moving the folder back.

Confirm archive? (y/n)
> y

✅ Archived Test Archive

**Archive Location:** team/_archived/test-archive/
**Archived Date:** 2025-12-23

Their data has been preserved and can be accessed at the archive location.
To restore, manually move the folder back to team/test-archive/
```

### Example 2: Archive Cancelled
```
> Archive test-archive

⚠️ Are you sure you want to archive Test Archive?

This will move their folder to team/_archived/. The data will be preserved
but they will no longer appear in active SE lists.

This action can be reversed by manually moving the folder back.

Confirm archive? (y/n)
> n

Archive cancelled. No changes were made.
```

### Example 3: Fuzzy Match
```
> Archive sarah

I found a close match: sarah-chen

⚠️ Are you sure you want to archive Sarah Chen?
...
```

### Example 4: No Match Found
```
> Archive john

I couldn't find an SE named "john".

Did you mean one of these?
  - sarah-chen
  - test-archive

Or run `/add-se john` to create a new profile.
```

## Natural Language Support

This command responds to these natural language patterns:

- "Archive {se-name}"
- "Archive {SE Display Name}"
- "Offboard {se-name}"
- "Deactivate {se-name}"
- "Remove {se-name} from team"

When Claude receives these requests, it should follow the implementation steps above.
