"""Exclude pattern matching utilities (.gitignore-style patterns)."""

import fnmatch
import re
from pathlib import Path
from typing import Optional


class ExcludePatternMatcher:
    """.gitignore-style pattern matching for excluding files.

    Supports:
    - Glob patterns: *.tmp, *.log
    - Directory patterns: **/cache/, node_modules/
    - Negation: !important.log (include)
    - Comments: # This is a comment
    """

    def __init__(self, patterns: Optional[list[str]] = None):
        """Initialize with list of patterns.

        Args:
            patterns: List of pattern strings
        """
        self.patterns: list[tuple[bool, re.Pattern]] = []

        if patterns:
            for pattern in patterns:
                self.add_pattern(pattern)

    def add_pattern(self, pattern: str) -> None:
        """Add a pattern to the matcher.

        Args:
            pattern: Pattern string (supports glob and gitignore syntax)
        """
        # Skip empty lines and comments
        pattern = pattern.strip()
        if not pattern or pattern.startswith("#"):
            return

        # Check for negation (!)
        is_negation = pattern.startswith("!")
        if is_negation:
            pattern = pattern[1:].strip()

        # Convert glob pattern to regex
        regex_pattern = self._glob_to_regex(pattern)

        # Compile regex
        compiled_pattern = re.compile(regex_pattern)

        self.patterns.append((is_negation, compiled_pattern))

    def _glob_to_regex(self, pattern: str) -> str:
        """Convert glob pattern to regex.

        Args:
            pattern: Glob pattern

        Returns:
            Regex pattern string
        """
        # Handle **/ (match any directory depth)
        pattern = pattern.replace("**/", "(?:.*/)?")

        # Handle remaining ** (match anything including /)
        pattern = pattern.replace("**", ".*")

        # Handle * (match anything except /)
        pattern = pattern.replace("*", "[^/]*")

        # Handle ? (match single character except /)
        pattern = pattern.replace("?", "[^/]")

        # If pattern ends with /, match entire directory
        if pattern.endswith("/"):
            pattern = pattern + ".*"

        # Anchor pattern
        # If it starts with /, it's from root
        if pattern.startswith("/"):
            pattern = "^" + pattern[1:]
        else:
            # Otherwise it can match anywhere
            pattern = "(?:^|.*/)" + pattern

        # Add end anchor if not a directory pattern
        if not pattern.endswith(".*"):
            pattern = pattern + "$"

        return pattern

    def should_exclude(self, path: str) -> bool:
        """Check if a path should be excluded.

        Args:
            path: Path to check (can be absolute or relative)

        Returns:
            True if path should be excluded, False otherwise
        """
        # Normalize path (remove leading ./)
        if path.startswith("./"):
            path = path[2:]

        excluded = False

        # Process patterns in order
        for is_negation, pattern in self.patterns:
            if pattern.search(path):
                # If it's a negation pattern and matches, include the file
                # Otherwise, exclude it
                excluded = not is_negation

        return excluded

    @classmethod
    def from_file(cls, file_path: Path) -> "ExcludePatternMatcher":
        """Create matcher from a file containing patterns.

        Args:
            file_path: Path to file with patterns (one per line)

        Returns:
            ExcludePatternMatcher instance
        """
        patterns = []

        if file_path.exists():
            with open(file_path, "r") as f:
                patterns = [line.strip() for line in f if line.strip()]

        return cls(patterns)

    @classmethod
    def from_default_patterns(cls) -> "ExcludePatternMatcher":
        """Create matcher with default exclusion patterns.

        Returns:
            ExcludePatternMatcher with common exclusions
        """
        default_patterns = [
            # Cache directories
            "**/.cache/*",
            "**/Cache/*",
            "**/cache/*",
            "**/.thumbnails/*",
            # Lock and PID files
            "**/*.lock",
            "**/*.pid",
            # Temporary files
            "**/*.tmp",
            "**/*.temp",
            "**/tmp/*",
            # Browser caches
            "**/.mozilla/firefox/*/cache2/*",
            "**/.config/google-chrome/*/Cache/*",
            "**/.config/chromium/*/Cache/*",
            "**/.config/Code/Cache/*",
            "**/.config/Code/CachedData/*",
            # Development
            "**/node_modules/*",
            "**/.npm/*",
            "**/.cargo/registry/*",
            "**/.rustup/toolchains/*",
            "**/__pycache__/*",
            "**/.venv/*",
            "**/venv/*",
            "**/.gradle/*",
            "**/.m2/*",
            # Build artifacts
            "**/build/*",
            "**/dist/*",
            "**/target/*",
            # Logs
            "**/*.log",
            # Trash
            "**/.local/share/Trash/*",
        ]

        return cls(default_patterns)

    def get_patterns(self) -> list[str]:
        """Get list of active patterns (for debugging).

        Returns:
            List of pattern strings
        """
        result = []
        for is_negation, pattern in self.patterns:
            prefix = "!" if is_negation else ""
            result.append(f"{prefix}{pattern.pattern}")
        return result


def should_exclude_path(path: Path, patterns: list[str]) -> bool:
    """Helper function to check if a path should be excluded.

    Args:
        path: Path to check
        patterns: List of exclusion patterns

    Returns:
        True if path should be excluded
    """
    matcher = ExcludePatternMatcher(patterns)
    return matcher.should_exclude(str(path))
