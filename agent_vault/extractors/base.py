from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Optional

class BaseExtractor(ABC):
    """Abstract base class for AI coding agent session extractors."""

    @abstractmethod
    def name(self) -> str:
        """Name of the AI agent source (e.g. 'antigravity', 'cursor')."""
        pass

    @abstractmethod
    def discover_sessions(self) -> List[Path]:
        """Discover existing session directories or files."""
        pass

    @abstractmethod
    def parse_session(self, session_path: Path) -> Optional[Dict[str, Any]]:
        """
        Parses a single session and returns a normalized dictionary:
        {
            'title': str,
            'turns': [
                {
                    'timestamp': str,
                    'prompt': str,
                    'responses': [str],
                    'files': set(),
                    'commands': set()
                }
            ],
            'all_files': [str],
            'all_commands': [str]
        }
        """
        pass
