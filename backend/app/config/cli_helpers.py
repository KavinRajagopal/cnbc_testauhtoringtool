"""CLI helper utilities for the onboarding script."""

import sys
import shutil
from typing import Optional, Callable, Any
from pathlib import Path

from .models import ValidationResult, ConfigurationSummary


# Color codes for terminal
class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def colorize(text: str, color: str) -> str:
    """
    Colorize text for terminal output.
    
    Args:
        text: Text to colorize
        color: Color code from Colors class
        
    Returns:
        Colorized text
    """
    return f"{color}{text}{Colors.RESET}"


def print_header(text: str):
    """Print a formatted section header."""
    width = 60
    print()
    print("═" * width)
    print(text.center(width))
    print("═" * width)
    print()


def print_box(title: str, content: Optional[str] = None):
    """Print text in a box."""
    width = 63
    print()
    print("╔" + "═" * (width - 2) + "╗")
    print("║" + title.center(width - 2) + "║")
    if content:
        print("╠" + "═" * (width - 2) + "╣")
        for line in content.split('\n'):
            print("║ " + line.ljust(width - 3) + "║")
    print("╚" + "═" * (width - 2) + "╝")
    print()


def show_progress(message: str):
    """Show a simple progress message."""
    print(colorize(f"⏳ {message}", Colors.CYAN))


def show_success(message: str):
    """Show a success message with checkmark."""
    print(colorize(f"✓ {message}", Colors.GREEN))


def show_error(message: str, suggestion: Optional[str] = None):
    """Show an error message with optional suggestion."""
    print(colorize(f"✗ {message}", Colors.RED))
    if suggestion:
        print()
        print(colorize(suggestion, Colors.YELLOW))
        print()


def show_warning(message: str):
    """Show a warning message."""
    print(colorize(f"⚠ {message}", Colors.YELLOW))


def prompt_with_validation(
    prompt: str,
    validator: Callable[[str], ValidationResult],
    max_retries: int = 3,
    mask_input: bool = False
) -> Optional[str]:
    """
    Prompt user for input with validation and retry logic.
    
    Args:
        prompt: Prompt message to display
        validator: Function to validate input
        max_retries: Maximum number of retry attempts
        mask_input: Whether to mask the input (for sensitive data)
        
    Returns:
        Validated input string, or None if max retries exceeded
    """
    attempts = 0
    
    while attempts < max_retries:
        print()
        user_input = input(colorize(f"{prompt}\n> ", Colors.CYAN))
        
        if not user_input.strip():
            show_error("Input cannot be empty")
            attempts += 1
            continue
        
        # Validate input
        show_progress("Validating...")
        result = validator(user_input)
        
        if result.success:
            show_success("Valid!")
            return user_input
        else:
            attempts += 1
            remaining = max_retries - attempts
            
            show_error(result.error_message or "Validation failed")
            
            if result.retry_suggestion:
                print(colorize(result.retry_suggestion, Colors.YELLOW))
            
            if remaining > 0:
                print()
                print(colorize(f"Attempts remaining: {remaining}/{max_retries}", Colors.YELLOW))
                retry = input(colorize("Try again? (y/n): ", Colors.CYAN))
                if retry.lower() != 'y':
                    return None
            else:
                print()
                print(colorize("Max retries exceeded.", Colors.RED))
                return None
    
    return None


def prompt_optional(prompt: str, default: Any = None, help_text: Optional[str] = None) -> Optional[str]:
    """
    Prompt for optional input with skip option.
    
    Args:
        prompt: Prompt message to display
        default: Default value if user skips
        help_text: Optional help text to display
        
    Returns:
        User input or default value
    """
    print()
    print(colorize(f"[OPTIONAL] {prompt}", Colors.MAGENTA))
    if help_text:
        print(colorize(f"  {help_text}", Colors.CYAN))
    if default:
        print(colorize(f"  Default: {default}", Colors.CYAN))
    
    user_input = input(colorize("  > ", Colors.CYAN))
    
    if not user_input.strip():
        return default
    
    return user_input


def display_section(title: str, items: list):
    """
    Display a section with items.
    
    Args:
        title: Section title
        items: List of (key, value) tuples or strings
    """
    print()
    print(colorize(title, Colors.BOLD))
    print("═" * 60)
    
    for item in items:
        if isinstance(item, tuple):
            key, value = item
            print(f"{key:20s} : {value}")
        else:
            print(f"• {item}")
    print()


def display_summary(config: ConfigurationSummary):
    """
    Format and display configuration summary.
    
    Args:
        config: ConfigurationSummary object
    """
    print_box("CONFIGURATION SUMMARY")
    
    print(colorize("✓ Required Settings (Validated)", Colors.GREEN + Colors.BOLD))
    print("═" * 60)
    print(f"{'OpenAI API Key':<20s} : {config.get_masked_openai_key()} (✓ Valid, Model: {config.required.openai_model})")
    print(f"{'GitHub Token':<20s} : {config.get_masked_github_token()} (✓ Valid)")
    print(f"{'Target Repository':<20s} : {config.required.github_repo} (✓ Accessible)")
    print()
    
    if config.detected:
        print(colorize("✓ Detected Settings", Colors.GREEN + Colors.BOLD))
        print("═" * 60)
        print(f"{'Framework':<20s} : {config.detected.framework}")
        print(f"{'Language':<20s} : {config.detected.language}")
        print(f"{'Test Directory':<20s} : {config.detected.test_directory}")
        print(f"{'Existing Tests':<20s} : {config.detected.existing_test_count} files")
        if config.detected.source_directory:
            print(f"{'Source Directory':<20s} : {config.detected.source_directory}")
        print()
    
    print(colorize("⚙ Optional Settings", Colors.CYAN + Colors.BOLD))
    print("═" * 60)
    
    # Show configured optional settings
    any_configured = False
    
    if config.optional.repo_structure and config.optional.repo_structure.test_file_pattern:
        print(f"{'Test Pattern':<20s} : {config.optional.repo_structure.test_file_pattern}")
        any_configured = True
    
    if config.optional.coverage_goals and config.optional.coverage_goals.minimum_percent:
        print(f"{'Coverage Goal':<20s} : {config.optional.coverage_goals.minimum_percent}%")
        any_configured = True
    
    if config.optional.exclusions and config.optional.exclusions.directories:
        dirs = ', '.join(config.optional.exclusions.directories[:3])
        print(f"{'Exclusions':<20s} : {dirs}")
        any_configured = True
    
    if config.optional.coding_standards and config.optional.coding_standards.style_guide:
        print(f"{'Coding Standards':<20s} : {config.optional.coding_standards.style_guide}")
        any_configured = True
    
    if not any_configured:
        print("No optional settings configured (using defaults)")
    
    print()
    print("═" * 60)
    print()


def confirm_settings(config: ConfigurationSummary) -> str:
    """
    Show summary and get user confirmation.
    
    Args:
        config: ConfigurationSummary object
        
    Returns:
        User choice: 'y' (yes), 'n' (no), or 'e' (edit)
    """
    display_summary(config)
    
    print("Does this configuration look correct?")
    print()
    print("Options:")
    print("  [y] Yes, save this configuration")
    print("  [n] No, cancel and exit")
    print("  [e] Edit specific sections")
    print()
    
    while True:
        choice = input(colorize("Your choice (y/n/e): ", Colors.CYAN)).lower().strip()
        if choice in ['y', 'n', 'e']:
            return choice
        print(colorize("Invalid choice. Please enter y, n, or e.", Colors.RED))


def edit_section_menu(config: ConfigurationSummary) -> int:
    """
    Show menu for editing specific sections.
    
    Args:
        config: Current configuration
        
    Returns:
        Section number to edit (1-5), or 0 to go back
    """
    print()
    print(colorize("Which section would you like to edit?", Colors.BOLD))
    print()
    print("1. OpenAI Configuration")
    print("2. GitHub Configuration")
    print("3. Target Repository")
    print("4. Optional Settings")
    print("5. Back to summary")
    print()
    
    while True:
        try:
            choice = input(colorize("Select (1-5): ", Colors.CYAN)).strip()
            num = int(choice)
            if 1 <= num <= 5:
                return num
            print(colorize("Invalid choice. Please enter 1-5.", Colors.RED))
        except ValueError:
            print(colorize("Invalid input. Please enter a number 1-5.", Colors.RED))


def backup_file(filepath: Path):
    """
    Backup file to .backup extension.
    
    Args:
        filepath: Path to file to backup
    """
    if filepath.exists():
        backup_path = filepath.with_suffix(filepath.suffix + '.backup')
        shutil.copy2(filepath, backup_path)
        show_success(f"Backed up existing {filepath.name} to {backup_path.name}")


def confirm_action(prompt: str, default: bool = False) -> bool:
    """
    Ask user to confirm an action.
    
    Args:
        prompt: Prompt message
        default: Default value if user just presses Enter
        
    Returns:
        True if user confirms, False otherwise
    """
    default_str = "Y/n" if default else "y/N"
    user_input = input(colorize(f"{prompt} ({default_str}): ", Colors.CYAN)).lower().strip()
    
    if not user_input:
        return default
    
    return user_input in ['y', 'yes']


def clear_screen():
    """Clear the terminal screen (cross-platform)."""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')


def print_list(title: str, items: list, color: str = Colors.CYAN):
    """
    Print a formatted list.
    
    Args:
        title: List title
        items: List of items to print
        color: Color for the title
    """
    print()
    print(colorize(title, color + Colors.BOLD))
    for item in items:
        print(f"  • {item}")
    print()

