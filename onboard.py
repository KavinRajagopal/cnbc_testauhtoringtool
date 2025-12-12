#!/usr/bin/env python3
"""
GitHub Test Authoring Tool - Onboarding Script

This script provides an interactive setup wizard for configuring the tool.
Users can choose between guided setup or manual configuration.
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from backend.app.config.cli_helpers import (
    Colors, colorize, print_box, print_header, show_progress,
    show_success, show_error, show_warning, prompt_with_validation,
    prompt_optional, display_summary, confirm_settings, edit_section_menu,
    backup_file, confirm_action, print_list, display_section
)
from backend.app.config.validator import (
    validate_openai_key, validate_github_token, validate_github_repo,
    detect_repository_info
)
from backend.app.config.models import (
    RequiredConfig, OptionalConfig, ConfigurationSummary, RepositoryInfo,
    RepoStructure, CoverageGoals, Exclusions, CodingStandards
)
from backend.app.config.state_manager import StateManager, update_state


def check_prerequisites() -> bool:
    """
    Check if prerequisites are met.
    
    Returns:
        True if all prerequisites are met
    """
    print_header("Prerequisites Check")
    
    # Check Python version
    show_progress("Checking Python version...")
    if sys.version_info < (3, 11):
        show_error(f"Python 3.11+ required. Current version: {sys.version}")
        return False
    show_success(f"Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Check if in correct directory
    if not (Path.cwd() / "backend" / "app").exists():
        show_error("Please run this script from the project root directory")
        return False
    
    show_success("All prerequisites met!")
    return True


def show_welcome():
    """Display welcome message and setup options."""
    print_box(
        "GitHub Test Authoring Tool - Setup Wizard",
        "Welcome! Let's configure your repository for automated testing."
    )
    
    print("How would you like to set up the tool?\n")
    print(colorize("  1. Guided Setup (Recommended)", Colors.GREEN + Colors.BOLD))
    print("     → Step-by-step interactive configuration")
    print("     → Validates credentials in real-time")
    print("     → Auto-detects your test framework")
    print("     → Takes 3-5 minutes\n")
    print(colorize("  2. Manual Setup", Colors.CYAN + Colors.BOLD))
    print("     → View example configuration files")
    print("     → Edit .env file yourself")
    print("     → For experienced users")
    print("     → Takes 1-2 minutes if you know what to do\n")


def check_existing_config() -> tuple[bool, Optional[dict]]:
    """
    Check if configuration already exists.
    
    Returns:
        Tuple of (exists, config_data)
    """
    env_file = Path.cwd() / ".env"
    state_manager = StateManager()
    
    if env_file.exists():
        state = state_manager.load()
        if state.onboarding_completed:
            return True, {
                "repo": state.configuration.repo if state.configuration else "Unknown",
                "configured_at": state.last_configured or "Unknown"
            }
    
    return False, None


def handle_existing_config(config_data: dict) -> str:
    """
    Handle existing configuration.
    
    Args:
        config_data: Existing configuration data
        
    Returns:
        User choice: 'e' (edit), 'f' (fresh), 'c' (cancel)
    """
    print_box("Existing Configuration Detected")
    
    print(f"Found existing configuration for:")
    print(f"  Repository: {config_data.get('repo', 'Unknown')}")
    print(f"  Configured: {config_data.get('configured_at', 'Unknown')}")
    print()
    
    print("What would you like to do?\n")
    print("  [e] Edit existing configuration")
    print("      → Load current values and modify them")
    print("      → Quick way to update settings\n")
    print("  [f] Start fresh (current config will be backed up)")
    print("      → Complete new onboarding")
    print("      → Old config saved to .env.backup\n")
    print("  [c] Cancel")
    print("      → Keep current configuration\n")
    
    while True:
        choice = input(colorize("Your choice (e/f/c): ", Colors.CYAN)).lower().strip()
        if choice in ['e', 'f', 'c']:
            return choice
        show_error("Invalid choice. Please enter e, f, or c.")


def manual_setup() -> bool:
    """
    Handle manual setup path.
    
    Returns:
        True if setup completed successfully
    """
    print_header("Manual Setup")
    
    print("Here are example configurations for common setups:\n")
    
    examples_dir = Path.cwd() / "examples"
    if examples_dir.exists():
        print_list("Available Examples:", [
            f"📄 Python + pytest: examples/.env.python.example",
            f"📄 JavaScript + jest: examples/.env.javascript.example",
            f"📄 TypeScript + playwright: examples/.env.typescript.example"
        ])
    else:
        show_warning("Examples directory not found. Creating basic template...")
    
    # Backup existing .env
    env_file = Path.cwd() / ".env"
    if env_file.exists():
        backup_file(env_file)
    
    # Copy env.example to .env
    env_example = Path.cwd() / "env.example"
    if env_example.exists():
        import shutil
        shutil.copy2(env_example, env_file)
        show_success(f"Created .env from template")
    
    print()
    print(colorize("Next steps:", Colors.BOLD))
    print("  1. Edit the .env file with your credentials")
    print("  2. Required fields:")
    print("     - OPENAI_API_KEY")
    print("     - GITHUB_TOKEN")
    print("     - GITHUB_REPO")
    print("  3. Run this script again to validate")
    print()
    
    if confirm_action("Would you like to validate your configuration now?", default=False):
        # TODO: Add validation of manual config
        show_success("Manual setup path complete!")
        return True
    
    return True


def collect_required_config() -> Optional[RequiredConfig]:
    """
    Collect required configuration with validation.
    
    Returns:
        RequiredConfig object or None if user cancels
    """
    print_header("Step 1/3: Required Configuration")
    
    # OpenAI API Key
    print(colorize("\n📝 OpenAI Configuration", Colors.BOLD))
    print("Get your API key from: https://platform.openai.com/api-keys\n")
    
    openai_key = prompt_with_validation(
        "Enter your OpenAI API key (starts with 'sk-'):",
        validate_openai_key,
        max_retries=3
    )
    
    if not openai_key:
        show_error("Failed to validate OpenAI key")
        return None
    
    # GitHub Token
    print(colorize("\n📝 GitHub Configuration", Colors.BOLD))
    print("Get your token from: https://github.com/settings/tokens")
    print("Required scopes: repo (full), workflow\n")
    
    github_token = prompt_with_validation(
        "Enter your GitHub Personal Access Token:",
        validate_github_token,
        max_retries=3
    )
    
    if not github_token:
        show_error("Failed to validate GitHub token")
        return None
    
    # GitHub Repository
    print(colorize("\n📝 Target Repository", Colors.BOLD))
    print("Format: owner/repository\n")
    
    github_repo = prompt_with_validation(
        "Enter repository (format: owner/repo):",
        lambda repo: validate_github_repo(github_token, repo),
        max_retries=3
    )
    
    if not github_repo:
        show_error("Failed to validate repository")
        return None
    
    return RequiredConfig(
        openai_api_key=openai_key,
        openai_model="gpt-4o-mini",
        github_token=github_token,
        github_repo=github_repo
    )


def analyze_repository(token: str, repo: str) -> Optional[RepositoryInfo]:
    """
    Analyze repository with shallow clone.
    
    Args:
        token: GitHub token
        repo: Repository name
        
    Returns:
        RepositoryInfo or None if analysis fails
    """
    print_header("Repository Analysis")
    
    show_progress("Cloning repository (shallow, latest commit only)...")
    show_progress("Detecting test framework...")
    show_progress("Scanning for existing tests...")
    
    repo_info = detect_repository_info(token, repo)
    
    if not repo_info:
        show_error("Failed to analyze repository")
        return None
    
    show_success("Analysis complete!")
    print()
    
    display_section("Detected Configuration:", [
        ("Framework", repo_info.framework),
        ("Language", repo_info.language),
        ("Test Directory", repo_info.test_directory),
        ("Existing Tests", f"{repo_info.existing_test_count} files"),
        ("Source Directory", repo_info.source_directory or "Not detected")
    ])
    
    if confirm_action("Does this look correct?", default=True):
        return repo_info
    
    # Allow override
    print()
    show_warning("Override not yet implemented. Using detected values.")
    return repo_info


def collect_optional_config() -> OptionalConfig:
    """
    Collect optional configuration.
    
    Returns:
        OptionalConfig object
    """
    print_header("Optional Configuration")
    
    print("The following settings are OPTIONAL. You can:")
    print("  • Configure them now")
    print("  • Skip all (press 's')")
    print("  • Configure some (press Enter on each)\n")
    
    skip_all = input(colorize("Press 's' to skip all, or Enter to continue: ", Colors.CYAN)).lower().strip()
    
    if skip_all == 's':
        show_success("Skipped all optional settings (using defaults)")
        return OptionalConfig()
    
    optional = OptionalConfig()
    
    # Coverage goals
    print()
    coverage_min = prompt_optional(
        "Minimum Coverage Goal",
        default=80,
        help_text="Set a minimum coverage percentage"
    )
    if coverage_min and coverage_min != 80:
        optional.coverage_goals = CoverageGoals(minimum_percent=int(coverage_min))
    
    # Exclusions
    print()
    exclude_dirs = prompt_optional(
        "Exclude Directories",
        default="migrations,__pycache__,node_modules",
        help_text="Comma-separated list of directories to exclude"
    )
    if exclude_dirs and exclude_dirs != "migrations,__pycache__,node_modules":
        optional.exclusions = Exclusions(directories=exclude_dirs.split(','))
    
    return optional


def save_configuration(
    required: RequiredConfig,
    optional: OptionalConfig,
    repo_info: Optional[RepositoryInfo],
    setup_method: str
):
    """
    Save configuration to files and update state.
    
    Args:
        required: Required configuration
        optional: Optional configuration
        repo_info: Repository information
        setup_method: How it was set up ("guided" or "manual")
    """
    print_header("Saving Configuration")
    
    # Backup existing .env
    env_file = Path.cwd() / ".env"
    if env_file.exists():
        show_progress("Backing up existing .env to .env.backup...")
        backup_file(env_file)
    
    # Generate .env file
    show_progress("Generating .env file...")
    env_content = f"""# GitHub Test Authoring Tool - Configuration
# Generated on: {datetime.now().isoformat()}

# ═════════════════════════════════════════════════════════════
# REQUIRED CONFIGURATION
# ═════════════════════════════════════════════════════════════

OPENAI_API_KEY={required.openai_api_key}
OPENAI_MODEL={required.openai_model}

GITHUB_TOKEN={required.github_token}
GITHUB_REPO={required.github_repo}

# ═════════════════════════════════════════════════════════════
# OPTIONAL CONFIGURATION
# ═════════════════════════════════════════════════════════════

"""
    
    if optional.coverage_goals and optional.coverage_goals.minimum_percent:
        env_content += f"MINIMUM_COVERAGE_PERCENT={optional.coverage_goals.minimum_percent}\n"
    
    if optional.exclusions and optional.exclusions.directories:
        env_content += f"EXCLUDE_DIRECTORIES={','.join(optional.exclusions.directories)}\n"
    
    env_content += """
# Feature Toggles
ENABLE_COVERAGE_ANALYSIS=true
ENABLE_TEST_OPTIMIZATION=true
"""
    
    env_file.write_text(env_content)
    show_success(".env file created")
    
    # Update state
    show_progress("Saving tool state...")
    update_state("configuration", {
        "repo": required.github_repo,
        "framework": repo_info.framework if repo_info else "unknown",
        "language": repo_info.language if repo_info else "unknown",
        "setup_method": setup_method
    })
    show_success(".tool_state.json updated")
    
    print()
    print_box(
        "🎉 Setup Complete!",
        f"""Configuration saved successfully!

Generated Files:
  ✓ .env (required settings)
  ✓ .tool_state.json (state tracking)
  {"✓ .env.backup (previous config)" if (Path.cwd() / ".env.backup").exists() else ""}

Next Steps:
  1. Start the server:
     $ cd backend
     $ uvicorn app.main:app --reload

  2. Use any of the three features:
     
     Feature 1: Generate Tests
     $ curl -X POST http://localhost:8000/github/generate-tests \\
       -d '{{"issue_number": 123}}'
     
     Feature 2: Analyze Coverage
     $ curl -X POST http://localhost:8000/github/analyze-coverage
     
     Feature 3: Optimize Tests
     $ curl -X POST http://localhost:8000/github/optimize-tests

  3. Read the documentation:
     • README.md - Complete guide
     • docs/ - Feature-specific guides

Need help? Run: python onboard.py --help"""
    )


def guided_setup() -> bool:
    """
    Handle guided setup path.
    
    Returns:
        True if setup completed successfully
    """
    # Collect required config
    required = collect_required_config()
    if not required:
        return False
    
    # Analyze repository
    repo_info = analyze_repository(required.github_token, required.github_repo)
    if not repo_info:
        show_warning("Continuing without repository analysis")
    
    # Collect optional config
    optional = collect_optional_config()
    
    # Show summary and confirm
    config_summary = ConfigurationSummary(
        required=required,
        optional=optional,
        detected=repo_info
    )
    
    while True:
        choice = confirm_settings(config_summary)
        
        if choice == 'y':
            # Save configuration
            save_configuration(required, optional, repo_info, "guided")
            return True
        elif choice == 'n':
            show_warning("Setup cancelled")
            return False
        elif choice == 'e':
            # Edit specific sections
            section = edit_section_menu(config_summary)
            if section == 5:
                continue  # Back to summary
            else:
                show_warning("Edit functionality not yet fully implemented")
                if not confirm_action("Continue with current configuration?"):
                    return False
                # For now, just continue


def main():
    """Main entry point for onboarding script."""
    try:
        # Check prerequisites
        if not check_prerequisites():
            sys.exit(1)
        
        # Show welcome
        show_welcome()
        
        # Check for existing config
        config_exists, config_data = check_existing_config()
        if config_exists:
            choice = handle_existing_config(config_data)
            if choice == 'c':
                print()
                show_success("Keeping existing configuration")
                sys.exit(0)
            elif choice == 'f':
                # Continue with fresh setup
                pass
            elif choice == 'e':
                # Load and edit existing
                show_warning("Edit mode not yet fully implemented. Starting fresh.")
        
        # Get setup method choice
        while True:
            choice = input(colorize("\nEnter your choice (1 or 2): ", Colors.CYAN)).strip()
            
            if choice == '1':
                # Guided setup
                if guided_setup():
                    sys.exit(0)
                else:
                    sys.exit(1)
            elif choice == '2':
                # Manual setup
                if manual_setup():
                    sys.exit(0)
                else:
                    sys.exit(1)
            else:
                show_error("Invalid choice. Please enter 1 or 2.")
    
    except KeyboardInterrupt:
        print()
        print()
        show_warning("Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print()
        show_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

