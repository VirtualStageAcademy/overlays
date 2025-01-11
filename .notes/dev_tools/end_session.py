"""
End of Session Documentation Update Tool
--------------------------------------
This tool helps maintain project documentation accuracy by updating
relevant files at the end of development sessions.

Usage:
    python .notes/dev_tools/end_session.py
"""

import os
import json
import datetime
from pathlib import Path
from typing import Dict, List, Optional

class SessionFinalizer:
    def __init__(self):
        self.notes_dir = Path('.notes')
        self.session_changes: Dict[str, List[str]] = {}
        self.current_time = datetime.datetime.now()
        self.core_docs = {
            'project_overview.md': {
                'path': self.notes_dir / 'project_overview.md',
                'sections': ['Current Status', 'Technical Implementation', 'Known Issues']
            },
            'development_guidelines.md': {
                'path': self.notes_dir / 'development_guidelines.md',
                'sections': ['Environment Setup', 'Development Workflow', 'Testing Protocol']
            },
            'config_overview.md': {
                'path': self.notes_dir / 'config_overview.md',
                'sections': ['Environment Variables', 'Configuration Sources', 'Security Features']
            },
            'zoom_integration.md': {
                'path': self.notes_dir / 'zoom_integration.md',
                'sections': ['Implementation Details', 'Troubleshooting Guide', 'Known Issues']
            }
        }

    def get_current_structure(self) -> str:
        """Get current project structure using system commands"""
        try:
            import subprocess
            result = subprocess.run(
                ['tree', '-a', '-I', 'node_modules|.git|__pycache__|.venv'],
                capture_output=True,
                text=True
            )
            return result.stdout
        except:
            print("❌ 'tree' command not available.")
            print("Please run: find . -not -path '*/\\.*' -not -path '*/node_modules/*' -not -path '*/__pycache__/*' -not -path '*/.venv/*' -print | sed -e 's;[^/]*/;|____;g;s;____|; |;g'")
            return input("Paste the directory structure here: ")

    def prompt_for_changes(self) -> Dict[str, List[str]]:
        """Prompt for changes made during the session"""
        changes: Dict[str, List[str]] = {}
        
        categories = [
            "project_overview",
            "directory_structure",
            "development_guidelines",
            "zoom_integration",
            "cursor_rules",
            "other"
        ]
        
        print("\n📝 Session Changes Documentation")
        print("--------------------------------")
        for category in categories:
            print(f"\nWere there changes to {category.replace('_', ' ')}? (y/n)")
            if input().lower() == 'y':
                changes[category] = []
                print(f"Enter changes (one per line, empty line to finish):")
                while True:
                    change = input()
                    if not change:
                        break
                    changes[category].append(change)
        
        return changes

    def update_directory_structure(self, structure: str) -> None:
        """Update directory_structure.md with current project structure"""
        structure_path = self.notes_dir / 'directory_structure.md'
        if structure_path.exists():
            with open(structure_path, 'r') as f:
                content = f.read()
            
            # Update the tree structure section
            start_marker = "```\n/TechHub"
            end_marker = "```\n\n## Configuration Files"
            start_idx = content.find(start_marker)
            end_idx = content.find(end_marker)
            
            if start_idx != -1 and end_idx != -1:
                new_content = (
                    content[:start_idx] +
                    "```\n" + structure + "```\n\n" +
                    content[end_idx + len("```\n"):]
                )
                
                with open(structure_path, 'w') as f:
                    f.write(new_content)
                print("✅ Updated directory_structure.md")

    def update_meeting_notes(self) -> None:
        """Update meeting_notes.md with session changes"""
        notes_path = self.notes_dir / 'meeting_notes.md'
        
        session_date = self.current_time.strftime("%Y-%m-%d %H:%M:%S")
        
        new_entry = f"\n\n## Development Session - {session_date}\n\n"
        
        for category, changes in self.session_changes.items():
            if changes:
                new_entry += f"### {category.replace('_', ' ').title()}\n"
                for change in changes:
                    new_entry += f"- {change}\n"
        
        with open(notes_path, 'a') as f:
            f.write(new_entry)
        
        print("✅ Updated meeting_notes.md")

    def update_core_documentation(self) -> None:
        """Update core documentation files based on session changes"""
        print("\n📚 Updating core documentation...")
        
        for doc_name, doc_info in self.core_docs.items():
            if not doc_info['path'].exists():
                print(f"⚠️  Warning: {doc_name} not found")
                continue
                
            print(f"\n🔄 Reviewing {doc_name}...")
            
            # Prompt for section updates
            updates = {}
            for section in doc_info['sections']:
                print(f"\nAny updates to '{section}' section? (y/n)")
                if input().lower() == 'y':
                    print(f"Enter updates for {section} (empty line to finish):")
                    section_updates = []
                    while True:
                        update = input()
                        if not update:
                            break
                        section_updates.append(update)
                    if section_updates:
                        updates[section] = section_updates

            # Apply updates if any
            if updates:
                self.apply_doc_updates(doc_info['path'], updates)
                print(f"✅ Updated {doc_name}")

    def apply_doc_updates(self, doc_path: Path, updates: Dict[str, List[str]]) -> None:
        """Apply updates to specific sections in a markdown file"""
        with open(doc_path, 'r') as f:
            content = f.read()

        for section, changes in updates.items():
            # Find section in content
            section_pattern = f"## {section}"
            section_start = content.find(section_pattern)
            if section_start == -1:
                print(f"⚠️  Section '{section}' not found in {doc_path.name}")
                continue

            # Find next section or end of file
            next_section_start = content.find("\n## ", section_start + len(section_pattern))
            if next_section_start == -1:
                next_section_start = len(content)

            # Insert updates at the end of the section
            section_content = content[section_start:next_section_start]
            updated_section = section_content + "\n\n" + "\n".join(f"- {change}" for change in changes)
            
            content = (
                content[:section_start] +
                updated_section +
                content[next_section_start:]
            )

        with open(doc_path, 'w') as f:
            f.write(content)

    def finalize_session(self) -> None:
        """Run complete session finalization"""
        print("\n🔄 Starting session finalization...\n")
        
        # Update core documentation first
        self.update_core_documentation()
        
        # Get current project structure
        print("\n📂 Gathering current project structure...")
        structure = self.get_current_structure()
        
        # Get session changes
        self.session_changes = self.prompt_for_changes()
        
        # Update directory structure
        if structure:
            self.update_directory_structure(structure)
        
        # Update meeting notes
        self.update_meeting_notes()
        
        print("\n✨ Session finalized successfully!")
        print("\nNext steps:")
        print("1. Review updated documentation")
        print("2. Commit documentation changes")
        print("3. Verify all changes are accurate")

if __name__ == "__main__":
    finalizer = SessionFinalizer()
    finalizer.finalize_session() 