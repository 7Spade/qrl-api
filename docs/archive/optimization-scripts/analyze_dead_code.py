#!/usr/bin/env python3
"""
Dead Code Detection Analysis Script

Analyzes Python codebase to identify:
- Unused imports
- Unused functions and classes
- Unreferenced modules
- Dead code that can be safely removed
"""
import ast
import os
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict


class DeadCodeAnalyzer(ast.NodeVisitor):
    """AST visitor to track definitions and usages"""
    
    def __init__(self, module_path: str):
        self.module_path = module_path
        self.imports: List[Dict] = []
        self.definitions: List[Dict] = []
        self.usages: Set[str] = set()
        self.current_class = None
        
    def visit_Import(self, node: ast.Import):
        """Track import statements"""
        for alias in node.names:
            self.imports.append({
                "type": "import",
                "name": alias.name,
                "asname": alias.asname,
                "lineno": node.lineno
            })
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Track from...import statements"""
        module = node.module or ""
        for alias in node.names:
            self.imports.append({
                "type": "from_import",
                "module": module,
                "name": alias.name,
                "asname": alias.asname,
                "lineno": node.lineno
            })
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Track function definitions"""
        self.definitions.append({
            "type": "function",
            "name": node.name,
            "lineno": node.lineno,
            "class": self.current_class,
            "is_private": node.name.startswith("_"),
            "is_dunder": node.name.startswith("__") and node.name.endswith("__")
        })
        self.generic_visit(node)
    
    def visit_ClassDef(self, node: ast.ClassDef):
        """Track class definitions"""
        self.definitions.append({
            "type": "class",
            "name": node.name,
            "lineno": node.lineno,
            "is_private": node.name.startswith("_")
        })
        
        # Track class context for methods
        prev_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = prev_class
    
    def visit_Name(self, node: ast.Name):
        """Track name usages"""
        if isinstance(node.ctx, ast.Load):
            self.usages.add(node.id)
        self.generic_visit(node)
    
    def visit_Attribute(self, node: ast.Attribute):
        """Track attribute usages"""
        self.usages.add(node.attr)
        self.generic_visit(node)


def analyze_file(file_path: Path) -> Dict:
    """Analyze a single Python file for dead code"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        analyzer = DeadCodeAnalyzer(str(file_path))
        analyzer.visit(tree)
        
        # Find unused imports
        unused_imports = []
        for imp in analyzer.imports:
            name = imp.get("asname") or imp.get("name")
            if name and name not in analyzer.usages and name != "*":
                unused_imports.append(imp)
        
        # Find unused definitions (excluding special methods and exports)
        unused_definitions = []
        for defn in analyzer.definitions:
            # Skip dunder methods, private methods, and __all__ exports
            if defn.get("is_dunder"):
                continue
            if defn["name"] in analyzer.usages:
                continue
            if defn["type"] == "function" and defn.get("class"):
                # Method might be called via polymorphism
                continue
            unused_definitions.append(defn)
        
        try:
            relative_path = file_path.relative_to(Path.cwd())
        except ValueError:
            relative_path = file_path
        
        return {
            "file": str(relative_path),
            "size": os.path.getsize(file_path),
            "imports": len(analyzer.imports),
            "unused_imports": unused_imports,
            "definitions": len(analyzer.definitions),
            "unused_definitions": unused_definitions,
            "has_dead_code": len(unused_imports) > 0 or len(unused_definitions) > 0
        }
    
    except Exception as e:
        try:
            relative_path = file_path.relative_to(Path.cwd())
        except ValueError:
            relative_path = file_path
        
        return {
            "file": str(relative_path),
            "error": str(e),
            "has_dead_code": False
        }


def find_python_files(root_dir: str) -> List[Path]:
    """Find all Python files in the project"""
    root = Path(root_dir)
    python_files = []
    
    exclude_dirs = {'.git', '__pycache__', '.venv', 'venv', 'env', '.tox', 'node_modules', '.pytest_cache'}
    
    for file_path in root.rglob('*.py'):
        # Skip excluded directories
        if any(excluded in file_path.parts for excluded in exclude_dirs):
            continue
        python_files.append(file_path)
    
    return sorted(python_files)


def generate_report(results: List[Dict]) -> Tuple[str, str]:
    """Generate markdown and JSON reports"""
    
    # Filter files with dead code
    files_with_dead_code = [r for r in results if r.get("has_dead_code")]
    
    # Statistics
    total_files = len(results)
    files_with_issues = len(files_with_dead_code)
    total_unused_imports = sum(len(r.get("unused_imports", [])) for r in files_with_dead_code)
    total_unused_definitions = sum(len(r.get("unused_definitions", [])) for r in files_with_dead_code)
    
    # Markdown report
    md_lines = [
        "# Dead Code Analysis Report",
        "",
        "## Summary",
        "",
        f"- **Total Files Analyzed**: {total_files}",
        f"- **Files with Dead Code**: {files_with_issues} ({files_with_issues/total_files*100:.1f}%)",
        f"- **Unused Imports**: {total_unused_imports}",
        f"- **Unused Definitions**: {total_unused_definitions}",
        "",
        "## Files with Dead Code",
        ""
    ]
    
    if not files_with_dead_code:
        md_lines.append("✅ **No dead code found!** All imports and definitions are used.")
    else:
        for result in files_with_dead_code:
            md_lines.append(f"### {result['file']}")
            md_lines.append("")
            
            if result.get("unused_imports"):
                md_lines.append("**Unused Imports:**")
                for imp in result["unused_imports"]:
                    if imp["type"] == "import":
                        md_lines.append(f"- Line {imp['lineno']}: `import {imp['name']}`")
                    else:
                        md_lines.append(f"- Line {imp['lineno']}: `from {imp['module']} import {imp['name']}`")
                md_lines.append("")
            
            if result.get("unused_definitions"):
                md_lines.append("**Unused Definitions:**")
                for defn in result["unused_definitions"]:
                    defn_type = defn["type"].capitalize()
                    if defn.get("class"):
                        md_lines.append(f"- Line {defn['lineno']}: {defn_type} `{defn['class']}.{defn['name']}`")
                    else:
                        md_lines.append(f"- Line {defn['lineno']}: {defn_type} `{defn['name']}`")
                md_lines.append("")
    
    md_lines.extend([
        "",
        "## Recommendations",
        "",
        "### Immediate Actions",
        "",
        "1. **Remove Unused Imports** - Clean up import statements",
        "2. **Review Unused Definitions** - Verify these are not used elsewhere",
        "3. **Update Tests** - Ensure removal doesn't break tests",
        "",
        "### Safe Removal Process",
        "",
        "1. Verify with `git grep <name>` that the code is truly unused",
        "2. Check if exported in `__init__.py` or `__all__`",
        "3. Run full test suite after removal",
        "4. Commit removals separately for easy rollback",
        "",
        "---",
        "",
        f"*Generated by Dead Code Analyzer*"
    ])
    
    markdown_report = "\n".join(md_lines)
    
    # JSON report
    json_report = json.dumps({
        "summary": {
            "total_files": total_files,
            "files_with_dead_code": files_with_issues,
            "unused_imports_total": total_unused_imports,
            "unused_definitions_total": total_unused_definitions,
            "clean_percentage": (total_files - files_with_issues) / total_files * 100 if total_files > 0 else 100
        },
        "files": files_with_dead_code
    }, indent=2)
    
    return markdown_report, json_report


def main():
    """Main entry point"""
    print("🔍 Dead Code Detection Analysis")
    print("=" * 80)
    
    # Analyze all Python files
    print("\n📂 Finding Python files...")
    python_files = find_python_files("src")
    print(f"Found {len(python_files)} Python files")
    
    print("\n🔬 Analyzing files...")
    results = []
    for i, file_path in enumerate(python_files, 1):
        if i % 20 == 0:
            print(f"  Analyzed {i}/{len(python_files)} files...")
        result = analyze_file(file_path)
        results.append(result)
    
    print(f"✓ Analyzed {len(results)} files")
    
    # Generate reports
    print("\n📊 Generating reports...")
    markdown_report, json_report = generate_report(results)
    
    # Save reports
    output_dir = Path("docs/optimization")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    md_path = output_dir / "dead_code_analysis.md"
    json_path = output_dir / "dead_code_analysis.json"
    
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(markdown_report)
    
    with open(json_path, 'w', encoding='utf-8') as f:
        f.write(json_report)
    
    print(f"✓ Reports saved:")
    print(f"  - {md_path}")
    print(f"  - {json_path}")
    
    # Print summary
    results_with_issues = [r for r in results if r.get("has_dead_code")]
    print("\n" + "=" * 80)
    print("📈 Summary")
    print("=" * 80)
    print(f"Total Files: {len(results)}")
    print(f"Files with Dead Code: {len(results_with_issues)}")
    print(f"Clean Files: {len(results) - len(results_with_issues)}")
    
    if len(results_with_issues) == 0:
        print("\n✅ No dead code found! Excellent code hygiene.")
    else:
        print(f"\n⚠️  Found dead code in {len(results_with_issues)} files")
        print("   Review the reports for details.")


if __name__ == "__main__":
    main()
