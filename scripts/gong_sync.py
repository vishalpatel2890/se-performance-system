#!/usr/bin/env python3
"""
Gong Sync Script
================

Synchronizes call transcripts from Gong to the local data/transcripts directory.

Usage:
    python scripts/gong_sync.py [--days N] [--list] [--select SELECTION]

Options:
    --days N            Fetch calls from the last N days (default: 7)
    --list              List available calls without downloading
    --select SELECTION  Download specific calls: "1", "1,3", or "all"

Environment Variables Required:
    GONG_ACCESS_TOKEN   Your Gong OAuth access token

Setup Instructions:
    1. Log into Gong as an admin
    2. Go to Settings > API > Create API Key
    3. Generate an access token with 'api:calls:read' scope
    4. Set environment variable:
       export GONG_ACCESS_TOKEN="your_token_here"

Configuration:
    See config/integrations/gong.yaml for detailed settings.

Author: SE Performance Management System
"""

import os
import sys
import re
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

try:
    import requests
except ImportError:
    print("Error: 'requests' library not installed.")
    print("Install with: pip install requests")
    sys.exit(1)

try:
    import yaml
except ImportError:
    print("Error: 'pyyaml' library not installed.")
    print("Install with: pip install pyyaml")
    sys.exit(1)

try:
    from dateutil import parser as dateparser
except ImportError:
    print("Error: 'python-dateutil' library not installed.")
    print("Install with: pip install python-dateutil")
    sys.exit(1)


# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_PATH = PROJECT_ROOT / "config" / "integrations" / "gong.yaml"
TRANSCRIPTS_DIR = PROJECT_ROOT / "data" / "transcripts"
TEAM_DIR = PROJECT_ROOT / "team"


class GongAPIError(Exception):
    """Custom exception for Gong API errors."""
    pass


def load_config() -> dict:
    """Load Gong configuration from YAML file."""
    if not CONFIG_PATH.exists():
        print(f"Configuration file not found: {CONFIG_PATH}")
        print("Run '/setup' to initialize the system configuration.")
        sys.exit(1)

    with open(CONFIG_PATH, 'r') as f:
        return yaml.safe_load(f)


def get_access_token() -> Optional[str]:
    """Get Gong access token from environment."""
    return os.environ.get("GONG_ACCESS_TOKEN")


def display_setup_instructions():
    """Display setup instructions when credentials are missing (ADR-005 pattern)."""
    print("""
Gong integration not configured.

Set the following environment variable:
  GONG_ACCESS_TOKEN=<your_oauth_token>

To get your access token:
  1. Log into Gong as an admin
  2. Go to Settings > Technical Hub > API
  3. Create an API key with 'api:calls:read' scope
  4. Copy the access token

See scripts/gong_sync.py for detailed setup instructions.
""")


def get_se_profiles() -> dict:
    """Load SE profiles from team directory for participant matching."""
    se_profiles = {}

    if not TEAM_DIR.exists():
        return se_profiles

    for se_folder in TEAM_DIR.iterdir():
        if se_folder.is_dir() and not se_folder.name.startswith('_'):
            profile_path = se_folder / "profile.md"
            if profile_path.exists():
                # Extract display name from profile
                with open(profile_path, 'r') as f:
                    content = f.read()
                    # Look for "# Name - SE Profile" pattern
                    match = re.search(r'^# (.+?) - SE Profile', content, re.MULTILINE)
                    if match:
                        se_profiles[se_folder.name] = {
                            'folder': se_folder.name,
                            'display_name': match.group(1)
                        }

    return se_profiles


def match_participant_to_se(participant_name: str, se_profiles: dict) -> Optional[str]:
    """Match a participant name to a known SE profile."""
    participant_lower = participant_name.lower()

    for folder_name, profile in se_profiles.items():
        display_name = profile['display_name'].lower()
        # Match on full name or folder name
        if display_name in participant_lower or participant_lower in display_name:
            return profile['display_name']
        if folder_name.replace('-', ' ') in participant_lower:
            return profile['display_name']

    return None


class GongClient:
    """Client for interacting with the Gong API."""

    def __init__(self, access_token: str, config: dict):
        self.access_token = access_token
        self.config = config
        self.base_url = config.get('api', {}).get('base_url', 'https://api.gong.io/v2')
        self.timeout = config.get('api', {}).get('timeout_seconds', 30)
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        })

    def _make_request(self, method: str, endpoint: str, params: dict = None,
                      data: dict = None, retry_count: int = 0) -> dict:
        """Make an API request with error handling and retry logic."""
        url = f"{self.base_url}{endpoint}"

        try:
            if method == 'GET':
                response = self.session.get(url, params=params, timeout=self.timeout)
            elif method == 'POST':
                response = self.session.post(url, json=data, timeout=self.timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            # Handle rate limiting (429)
            if response.status_code == 429:
                if retry_count < 1:
                    import time
                    retry_after = int(response.headers.get('Retry-After', 5))
                    print(f"Rate limited. Waiting {retry_after} seconds...")
                    time.sleep(retry_after)
                    return self._make_request(method, endpoint, params, data, retry_count + 1)
                else:
                    raise GongAPIError("Rate limit exceeded. Please try again later.")

            # Handle authentication errors
            if response.status_code == 401:
                raise GongAPIError(
                    "Authentication failed. Please check your GONG_ACCESS_TOKEN.\n"
                    "Your token may have expired - generate a new one from Gong settings."
                )

            # Handle other errors
            if response.status_code >= 400:
                raise GongAPIError(f"API error ({response.status_code}): {response.text}")

            return response.json()

        except requests.exceptions.Timeout:
            if retry_count < 1:
                print("Request timed out. Retrying...")
                return self._make_request(method, endpoint, params, data, retry_count + 1)
            raise GongAPIError("Request timed out after retry. Please check your network connection.")

        except requests.exceptions.ConnectionError:
            raise GongAPIError("Could not connect to Gong API. Please check your network connection.")

    def list_calls(self, from_date: datetime, to_date: datetime = None) -> list:
        """List calls within a date range."""
        if to_date is None:
            to_date = datetime.now()

        # Gong API uses POST for listing calls with filters
        data = {
            'filter': {
                'fromDateTime': from_date.isoformat() + 'Z',
                'toDateTime': to_date.isoformat() + 'Z'
            }
        }

        all_calls = []
        cursor = None

        while True:
            if cursor:
                data['cursor'] = cursor

            result = self._make_request('POST', '/calls/extensive', data=data)

            calls = result.get('calls', [])
            all_calls.extend(calls)

            # Handle pagination
            records = result.get('records', {})
            cursor = records.get('cursor')
            if not cursor or not records.get('currentPageSize', 0):
                break

        return all_calls

    def get_transcript(self, call_id: str) -> dict:
        """Get transcript for a specific call."""
        # Gong uses POST with call IDs in body
        data = {
            'filter': {
                'callIds': [call_id]
            }
        }

        result = self._make_request('POST', '/calls/transcript', data=data)

        transcripts = result.get('callTranscripts', [])
        if transcripts:
            return transcripts[0]
        return {}


def format_duration(seconds: int) -> str:
    """Format duration in seconds to human-readable format."""
    minutes = seconds // 60
    if minutes >= 60:
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours}h {mins}m"
    return f"{minutes} minutes"


def format_timestamp(seconds: float) -> str:
    """Format timestamp seconds to [MM:SS] format."""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"[{minutes:02d}:{secs:02d}]"


def sanitize_filename(name: str) -> str:
    """Sanitize a string for use in a filename."""
    # Convert to lowercase and replace spaces with hyphens
    name = name.lower().strip()
    name = re.sub(r'\s+', '-', name)
    # Remove or replace special characters
    name = re.sub(r'[^a-z0-9\-]', '', name)
    # Remove multiple consecutive hyphens
    name = re.sub(r'-+', '-', name)
    return name.strip('-')


def infer_call_type(call_data: dict) -> str:
    """Infer call type from Gong metadata."""
    title = call_data.get('title', '').lower()

    # Common patterns
    if 'discovery' in title:
        return 'discovery'
    elif 'demo' in title or 'demonstration' in title:
        return 'demo'
    elif 'poc' in title or 'proof of concept' in title:
        if 'kick' in title or 'kickoff' in title:
            return 'poc-kickoff'
        elif 'review' in title:
            return 'poc-review'
        return 'poc'
    elif 'technical' in title or 'deep dive' in title:
        return 'technical'
    elif 'exec' in title or 'executive' in title:
        return 'executive'

    # Default based on Gong call type
    gong_type = call_data.get('type', '').lower()
    if gong_type in ['external', 'customer']:
        return 'call'

    return 'call'


def normalize_speaker_label(speaker: str) -> str:
    """Normalize speaker label to consistent format."""
    # Clean up the speaker name
    speaker = speaker.strip()
    # Remove email suffixes if present
    if '@' in speaker:
        speaker = speaker.split('@')[0]
    # Capitalize properly
    speaker = ' '.join(word.capitalize() for word in speaker.split())
    return speaker


def build_transcript_content(call_data: dict, transcript_data: dict, se_profiles: dict) -> str:
    """Build normalized transcript markdown content."""
    # Extract metadata
    customer = call_data.get('primaryCompany', {}).get('name', 'Unknown Customer')
    call_type = infer_call_type(call_data)
    call_type_display = call_type.replace('-', ' ').title()

    # Parse date
    started = call_data.get('started', '')
    if started:
        call_date = dateparser.parse(started)
        date_str = call_date.strftime('%Y-%m-%d')
    else:
        date_str = datetime.now().strftime('%Y-%m-%d')

    # Format duration
    duration_seconds = call_data.get('duration', 0)
    duration_str = format_duration(duration_seconds)

    # Build participants list
    participants_list = []
    parties = call_data.get('parties', [])

    for party in parties:
        name = party.get('name', party.get('emailAddress', 'Unknown'))
        name = normalize_speaker_label(name)

        # Check if this is a known SE
        se_match = match_participant_to_se(name, se_profiles)
        if se_match:
            participants_list.append(f"- {se_match} (SE)")
        else:
            # Try to get role from Gong
            role = party.get('title', '')
            if role:
                participants_list.append(f"- {name} ({role})")
            else:
                participants_list.append(f"- {name}")

    participants_str = '\n'.join(participants_list)

    # Build transcript content
    transcript_lines = []
    sentences = transcript_data.get('transcript', [])

    for sentence in sentences:
        speaker = sentence.get('speakerName', sentence.get('speaker', 'Unknown'))
        speaker = normalize_speaker_label(speaker)

        # Mark SE speakers
        se_match = match_participant_to_se(speaker, se_profiles)
        if se_match:
            speaker = se_match

        text = sentence.get('text', '').strip()

        # Get timestamp
        start_time = sentence.get('startTime', 0)
        timestamp = format_timestamp(start_time)

        if text:
            transcript_lines.append(f"{timestamp} **{speaker}:** {text}")

    transcript_str = '\n\n'.join(transcript_lines)

    # Build full markdown content
    content = f"""# {customer} - {call_type_display}

**Date:** {date_str}
**Duration:** {duration_str}
**Participants:**
{participants_str}

**Source:** gong

---

## Transcript

{transcript_str}
"""

    return content, {
        'customer': customer,
        'call_type': call_type,
        'date': date_str,
        'date_obj': call_date if started else datetime.now()
    }


def generate_file_path(metadata: dict) -> Path:
    """Generate file path following naming convention."""
    date_obj = metadata['date_obj']
    date_str = metadata['date']
    customer = sanitize_filename(metadata['customer'])
    call_type = sanitize_filename(metadata['call_type'])

    # Create monthly directory
    month_dir = TRANSCRIPTS_DIR / date_obj.strftime('%Y-%m')
    month_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename
    filename = f"{date_str}-{customer}-{call_type}.md"
    file_path = month_dir / filename

    # Handle duplicates (append -2, -3, etc.)
    counter = 2
    base_filename = f"{date_str}-{customer}-{call_type}"
    while file_path.exists():
        filename = f"{base_filename}-{counter}.md"
        file_path = month_dir / filename
        counter += 1

    return file_path


def update_last_sync(config_path: Path):
    """Update last_sync timestamp in gong.yaml."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    config['last_sync'] = datetime.now().isoformat()
    config['enabled'] = True

    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)


def display_call_list(calls: list, se_profiles: dict):
    """Display formatted list of calls."""
    print("\n" + "=" * 60)
    print("RECENT GONG CALLS")
    print("=" * 60 + "\n")

    for i, call in enumerate(calls, 1):
        customer = call.get('primaryCompany', {}).get('name', 'Unknown')

        # Parse and format date
        started = call.get('started', '')
        if started:
            call_date = dateparser.parse(started)
            date_str = call_date.strftime('%Y-%m-%d %H:%M')
        else:
            date_str = 'Unknown date'

        # Format duration
        duration = format_duration(call.get('duration', 0))

        # Find SEs in participants
        se_names = []
        for party in call.get('parties', []):
            name = party.get('name', party.get('emailAddress', ''))
            if name:
                se_match = match_participant_to_se(name, se_profiles)
                if se_match:
                    se_names.append(se_match)

        se_str = ', '.join(se_names) if se_names else 'Unknown SE'

        print(f"  [{i}] {date_str}")
        print(f"      Customer: {customer}")
        print(f"      SE(s): {se_str}")
        print(f"      Duration: {duration}")
        print()


def parse_selection(selection: str, max_count: int) -> list:
    """Parse user selection string into list of indices."""
    selection = selection.strip().lower()

    if selection == 'all':
        return list(range(max_count))

    indices = []
    parts = selection.replace(' ', '').split(',')

    for part in parts:
        try:
            idx = int(part) - 1  # Convert to 0-indexed
            if 0 <= idx < max_count:
                indices.append(idx)
        except ValueError:
            continue

    return sorted(set(indices))


def main():
    """Main entry point for Gong sync."""
    parser = argparse.ArgumentParser(description='Sync transcripts from Gong')
    parser.add_argument('--days', type=int, default=7,
                        help='Fetch calls from the last N days (default: 7)')
    parser.add_argument('--list', action='store_true',
                        help='List available calls without downloading')
    parser.add_argument('--select', type=str,
                        help='Download specific calls: "1", "1,3", or "all"')

    args = parser.parse_args()

    # Check for access token
    access_token = get_access_token()
    if not access_token:
        display_setup_instructions()
        return 1

    # Load configuration
    config = load_config()

    # Load SE profiles for participant matching
    se_profiles = get_se_profiles()

    # Initialize Gong client
    client = GongClient(access_token, config)

    # Calculate date range
    to_date = datetime.now()
    from_date = to_date - timedelta(days=args.days)

    print(f"Fetching Gong calls from last {args.days} days...")

    try:
        # List calls
        calls = client.list_calls(from_date, to_date)

        if not calls:
            print("\nNo calls found in the specified date range.")
            return 0

        print(f"Found {len(calls)} calls.")

        # Display call list
        display_call_list(calls, se_profiles)

        # If just listing, exit here
        if args.list and not args.select:
            print("Use --select to download transcripts (e.g., --select '1,3' or --select 'all')")
            return 0

        # Get selection
        if args.select:
            selection = args.select
        else:
            print("Select calls to download (e.g., '1,3' or 'all'):")
            selection = input("> ").strip()

        if not selection:
            print("No selection made. Exiting.")
            return 0

        # Parse selection
        selected_indices = parse_selection(selection, len(calls))

        if not selected_indices:
            print("Invalid selection. Exiting.")
            return 0

        print(f"\nDownloading {len(selected_indices)} transcript(s)...")

        downloaded_count = 0
        for idx in selected_indices:
            call = calls[idx]
            call_id = call.get('id', call.get('callId'))
            customer = call.get('primaryCompany', {}).get('name', 'Unknown')

            print(f"\n  Downloading: {customer}...")

            try:
                # Get transcript
                transcript_data = client.get_transcript(call_id)

                if not transcript_data:
                    print(f"    ⚠ No transcript available for this call")
                    continue

                # Build normalized content
                content, metadata = build_transcript_content(call, transcript_data, se_profiles)

                # Generate file path
                file_path = generate_file_path(metadata)

                # Write file
                with open(file_path, 'w') as f:
                    f.write(content)

                rel_path = file_path.relative_to(PROJECT_ROOT)
                print(f"    ✓ Saved to: {rel_path}")
                downloaded_count += 1

            except GongAPIError as e:
                print(f"    ✗ Error: {e}")

        print(f"\n{'=' * 60}")
        print(f"Downloaded {downloaded_count} transcript(s) to data/transcripts/")
        print('=' * 60)

        # Update last_sync if any downloads succeeded
        if downloaded_count > 0:
            update_last_sync(CONFIG_PATH)
            print("Updated last_sync timestamp in gong.yaml")

        return 0

    except GongAPIError as e:
        print(f"\nError: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
