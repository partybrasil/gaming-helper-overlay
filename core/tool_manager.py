"""
Tool Manager
Manages and executes scripts from the tools directory.
"""

import os
import sys
import logging
import subprocess
import ast
import re
from typing import Dict, List, Optional, Any
from pathlib import Path


class ToolInfo:
    """Information about a tool/script."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.name = Path(file_path).stem
        self.filename = os.path.basename(file_path)
        self.description = "No description available"
        self.version = "Unknown"
        self.author = "Unknown"
        self.requires_admin = False
        self.requires_gui = True
        self.category = "General"
        
        # Parse script for metadata
        self._parse_script_metadata()
    
    def _parse_script_metadata(self):
        """Parse the script file to extract metadata."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for common metadata patterns
            self._extract_from_comments(content)
            self._extract_from_docstrings(content)
            self._extract_from_variables(content)
            self._detect_requirements(content)
            
        except Exception as e:
            logging.warning(f"Failed to parse metadata for {self.filename}: {e}")
    
    def _extract_from_comments(self, content: str):
        """Extract metadata from comments."""
        lines = content.split('\n')
        
        for line in lines[:50]:  # Check first 50 lines
            line = line.strip()
            if line.startswith('#'):
                # Remove # and clean
                comment = line[1:].strip()
                
                # Look for patterns
                if comment.lower().startswith('description:'):
                    self.description = comment[12:].strip()
                elif comment.lower().startswith('author:'):
                    self.author = comment[7:].strip()
                elif comment.lower().startswith('version:'):
                    self.version = comment[8:].strip()
                elif comment.lower().startswith('category:'):
                    self.category = comment[9:].strip()
                elif 'admin' in comment.lower() and 'require' in comment.lower():
                    self.requires_admin = True
    
    def _extract_from_docstrings(self, content: str):
        """Extract metadata from module docstring."""
        try:
            # Try to parse the AST to get the module docstring
            tree = ast.parse(content)
            docstring = ast.get_docstring(tree)
            
            if docstring:
                # Look for title/description in first line
                lines = docstring.split('\n')
                if lines and self.description == "No description available":
                    # First line as description
                    first_line = lines[0].strip()
                    if first_line and not first_line.lower().startswith(('rtx diagnostic tool', 'advanced diagnostic')):
                        self.description = first_line
                    elif len(lines) > 2:
                        # Try second or third line
                        for line in lines[1:4]:
                            line = line.strip()
                            if line and len(line) > 10:
                                self.description = line
                                break
                
                # Look for metadata in docstring
                for line in lines:
                    line_lower = line.strip().lower()
                    line_original = line.strip()
                    
                    if line_lower.startswith('author:'):
                        self.author = line_original.split(':', 1)[1].strip()
                    elif line_lower.startswith('version:'):
                        self.version = line_original.split(':', 1)[1].strip()
                    elif line_lower.startswith('category:'):
                        self.category = line_original.split(':', 1)[1].strip()
                    elif line_lower.startswith('description:'):
                        self.description = line_original.split(':', 1)[1].strip()
                    elif line_lower.startswith('requires admin:'):
                        admin_text = line_original.split(':', 1)[1].strip().lower()
                        self.requires_admin = admin_text in ['true', 'yes', '1']
                        
        except Exception:
            pass
    
    def _extract_from_variables(self, content: str):
        """Extract metadata from module-level variables."""
        # Look for common variable patterns
        patterns = {
            'version': r'__version__\s*=\s*["\']([^"\']+)["\']',
            'author': r'__author__\s*=\s*["\']([^"\']+)["\']',
            'description': r'__description__\s*=\s*["\']([^"\']+)["\']',
        }
        
        for attr, pattern in patterns.items():
            match = re.search(pattern, content)
            if match:
                value = match.group(1)
                if attr == 'version' and value:
                    self.version = value
                elif attr == 'author' and value:
                    self.author = value
                elif attr == 'description' and value:
                    self.description = value
    
    def _detect_requirements(self, content: str):
        """Detect what the script requires."""
        content_lower = content.lower()
        
        # Check for GUI frameworks
        gui_frameworks = ['pyside6', 'pyqt5', 'pyqt6', 'tkinter', 'kivy']
        self.requires_gui = any(framework in content_lower for framework in gui_frameworks)
        
        # Check for admin requirements (common patterns)
        admin_patterns = ['winreg', 'ctypes.windll', 'os.system', 'subprocess.*runas']
        self.requires_admin = any(re.search(pattern, content_lower) for pattern in admin_patterns)
        
        # Detect category based on content
        if 'gpu' in content_lower or 'nvidia' in content_lower or 'cuda' in content_lower:
            self.category = "GPU/Graphics"
        elif 'network' in content_lower or 'socket' in content_lower:
            self.category = "Network"
        elif 'system' in content_lower or 'psutil' in content_lower:
            self.category = "System"
        elif 'game' in content_lower or 'gaming' in content_lower:
            self.category = "Gaming"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for display."""
        return {
            'name': self.name,
            'filename': self.filename,
            'description': self.description,
            'version': self.version,
            'author': self.author,
            'category': self.category,
            'requires_admin': self.requires_admin,
            'requires_gui': self.requires_gui,
            'file_path': self.file_path
        }


class ToolManager:
    """Manages tools and scripts in the tools directory."""
    
    def __init__(self, tools_directory: str = "tools"):
        self.tools_directory = Path(tools_directory)
        self.logger = logging.getLogger("ToolManager")
        self.tools: Dict[str, ToolInfo] = {}
        
        # Ensure tools directory exists
        self.tools_directory.mkdir(exist_ok=True)
        
        # Discover tools
        self.discover_tools()
    
    def discover_tools(self) -> None:
        """Discover all tools in the tools directory."""
        self.tools.clear()
        
        if not self.tools_directory.exists():
            self.logger.warning(f"Tools directory does not exist: {self.tools_directory}")
            return
        
        # Find all Python scripts
        python_files = list(self.tools_directory.glob("*.py"))
        
        for file_path in python_files:
            try:
                tool_info = ToolInfo(str(file_path))
                self.tools[tool_info.name] = tool_info
                self.logger.debug(f"Discovered tool: {tool_info.name}")
                
            except Exception as e:
                self.logger.error(f"Failed to load tool {file_path}: {e}")
        
        self.logger.info(f"Discovered {len(self.tools)} tools")
    
    def get_tools(self) -> Dict[str, ToolInfo]:
        """Get all discovered tools."""
        return self.tools.copy()
    
    def get_tool(self, tool_name: str) -> Optional[ToolInfo]:
        """Get specific tool by name."""
        return self.tools.get(tool_name)
    
    def run_tool(self, tool_name: str, as_admin: bool = False, new_terminal: bool = False) -> bool:
        """Run a tool with specified options."""
        tool = self.get_tool(tool_name)
        if not tool:
            self.logger.error(f"Tool not found: {tool_name}")
            return False
        
        try:
            return self._execute_tool(tool, as_admin, new_terminal)
            
        except Exception as e:
            self.logger.error(f"Failed to run tool {tool_name}: {e}")
            return False
    
    def _execute_tool(self, tool: ToolInfo, as_admin: bool = False, new_terminal: bool = False) -> bool:
        """Execute a tool with specified parameters."""
        python_exe = sys.executable
        script_path = tool.file_path
        
        # Build command
        if new_terminal:
            # Run in new terminal window
            if as_admin:
                # PowerShell command to run as admin in new window
                cmd = [
                    'powershell', '-Command', 
                    f'Start-Process -FilePath "{python_exe}" -ArgumentList \'"{script_path}"\' -Verb RunAs -WindowStyle Normal'
                ]
            else:
                # Run in new cmd window
                cmd = ['cmd', '/c', 'start', 'cmd', '/k', f'"{python_exe}" "{script_path}"']
        else:
            # Run in current process
            if as_admin:
                # Use PowerShell to run as admin
                cmd = [
                    'powershell', '-Command', 
                    f'Start-Process -FilePath "{python_exe}" -ArgumentList \'"{script_path}"\' -Verb RunAs -Wait'
                ]
            else:
                # Direct execution
                cmd = [python_exe, script_path]
        
        # Execute
        self.logger.info(f"Running tool: {tool.name} (admin={as_admin}, new_terminal={new_terminal})")
        
        if new_terminal or as_admin:
            # Non-blocking execution
            subprocess.Popen(cmd, shell=True)
            return True
        else:
            # Blocking execution - run in background thread if GUI
            if tool.requires_gui:
                subprocess.Popen(cmd)
                return True
            else:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    self.logger.info(f"Tool {tool.name} completed successfully")
                    return True
                else:
                    self.logger.error(f"Tool {tool.name} failed with code {result.returncode}: {result.stderr}")
                    return False
    
    def refresh_tools(self) -> None:
        """Refresh the tools list."""
        self.logger.info("Refreshing tools...")
        self.discover_tools()
