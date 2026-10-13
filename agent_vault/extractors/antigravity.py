import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

from agent_vault.extractors.base import BaseExtractor
from agent_vault.config import discover_antigravity_sources

def normalize_path(p_str: str) -> str:
    return p_str.replace('\\\\', '/').replace('\\', '/').strip('\"\'')

def clean_user_prompt(raw_text: str) -> str:
    if not raw_text:
        return ""
    req_match = re.search(r'<USER_REQUEST>(.*?)</USER_REQUEST>', raw_text, re.DOTALL)
    text = req_match.group(1).strip() if req_match else raw_text.strip()
    
    text = re.sub(r'<ADDITIONAL_METADATA>.*?</ADDITIONAL_METADATA>', '', text, flags=re.DOTALL)
    text = re.sub(r'<USER_SETTINGS_CHANGE>.*?</USER_SETTINGS_CHANGE>', '', text, flags=re.DOTALL)
    text = re.sub(r'<SYSTEM_MESSAGE>.*?</SYSTEM_MESSAGE>', '', text, flags=re.DOTALL)
    return text.strip()

def format_turn_response(responses: List[str]) -> str:
    if not responses:
        return "*No textual response recorded.*"
    substantive = [r for r in responses if len(r) > 100 or '```' in r]
    if substantive:
        return "\n\n".join(substantive)
    return "\n\n".join(responses)

class AntigravityExtractor(BaseExtractor):
    """Extractor for Google Antigravity Desktop & CLI session transcripts."""

    def name(self) -> str:
        return "antigravity"

    def discover_sessions(self) -> List[tuple[str, Path]]:
        """Returns list of (source_label, session_dir)."""
        sources = discover_antigravity_sources()
        results = []
        for label, brain_dir in sources:
            if not brain_dir.exists():
                continue
            for conv_dir in brain_dir.iterdir():
                if conv_dir.is_dir():
                    transcript = conv_dir / ".system_generated" / "logs" / "transcript.jsonl"
                    if transcript.exists():
                        results.append((label, conv_dir))
        return results

    def parse_session(self, session_dir: Path) -> Optional[Dict[str, Any]]:
        transcript_path = session_dir / ".system_generated" / "logs" / "transcript.jsonl"
        if not transcript_path.exists():
            return None

        turns = []
        current_turn = None
        all_files_touched = set()
        all_commands_run = set()
        convo_title = None

        try:
            with open(transcript_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                    except Exception:
                        continue

                    entry_type = entry.get('type')
                    created_at = entry.get('created_at', '')

                    if entry_type == 'USER_INPUT':
                        raw_content = entry.get('content', '')
                        clean_prompt = clean_user_prompt(raw_content)

                        if not clean_prompt or clean_prompt.startswith('[Message]') or clean_prompt.startswith('Task id'):
                            continue

                        if not convo_title:
                            first_line = clean_prompt.split('\n')[0].strip()
                            first_line = re.sub(r'^[#*\-`\s]+', '', first_line)
                            convo_title = first_line[:100]

                        if current_turn:
                            turns.append(current_turn)

                        current_turn = {
                            'timestamp': created_at,
                            'prompt': clean_prompt,
                            'responses': [],
                            'files': set(),
                            'commands': set()
                        }

                    elif entry_type == 'PLANNER_RESPONSE' and current_turn:
                        resp_content = entry.get('content', '')
                        if resp_content:
                            clean_resp = resp_content.strip()
                            if clean_resp:
                                current_turn['responses'].append(clean_resp)

                        for tc in entry.get('tool_calls', []):
                            args = tc.get('args', {})
                            tc_name = tc.get('name', '')
                            for key in ['AbsolutePath', 'TargetFile', 'path', 'file_path', 'SearchPath']:
                                if key in args:
                                    val = str(args[key]).strip('\"\'')
                                    if val and len(val) < 250 and not val.startswith('tmp'):
                                        all_files_touched.add(val)
                            if tc_name == 'run_command' and 'CommandLine' in args:
                                cmd = str(args['CommandLine']).strip('\"\'')
                                if cmd and len(cmd) < 200:
                                    all_commands_run.add(cmd)

            if current_turn:
                turns.append(current_turn)

        except Exception:
            return None

        if not turns:
            return None

        return {
            'title': convo_title or 'Untitled Conversation',
            'turns': turns,
            'all_files': sorted(list(all_files_touched)),
            'all_commands': sorted(list(all_commands_run))
        }

    def render_markdown(self, conv_id: str, source_label: str, data: Dict[str, Any]) -> str:
        title = data['title']
        first_ts = data['turns'][0]['timestamp'] if data['turns'] else 'Unknown'

        md_lines = [
            f"# {title}",
            "",
            f"- **Conversation ID:** `{conv_id}`",
            f"- **Source:** `{source_label}`",
            f"- **Date:** {first_ts}",
        ]

        if data['all_files']:
            md_lines.append("\n### Key Files & Modules Referenced")
            for f in data['all_files']:
                norm_f = normalize_path(f)
                md_lines.append(f"- `{norm_f}`")

        if data['all_commands']:
            md_lines.append("\n### Key Commands Executed")
            for c in data['all_commands']:
                md_lines.append(f"- `{c}`")

        md_lines.append("\n---\n")

        for i, turn in enumerate(data['turns'], 1):
            md_lines.append(f"## Turn {i} ({turn['timestamp']})")
            md_lines.append("\n### User Request")
            md_lines.append(turn['prompt'])

            md_lines.append("\n### Solution & Analysis")
            resp_text = format_turn_response(turn['responses'])
            md_lines.append(resp_text)
            md_lines.append("\n---\n")

        return "\n".join(md_lines)
