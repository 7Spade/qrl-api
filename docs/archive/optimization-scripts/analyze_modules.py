#!/usr/bin/env python3
"""
Module Analysis Script

Generates comprehensive inventory of all modules with metrics:
- Primary responsibility
- Public API surface
- Dependencies
- File size
- Complexity metrics
"""

import ast
import os
from pathlib import Path
from typing import Dict, List, Set
from dataclasses import dataclass, asdict
import json


@dataclass
class ModuleMetrics:
    """Metrics for a single module"""
    path: str
    responsibility: str
    public_functions: List[str]
    public_classes: List[str]
    imports: List[str]
    file_size_bytes: int
    line_count: int
    function_count: int
    class_count: int
    complexity_score: int


class ModuleAnalyzer:
    """Analyzes Python modules for architecture compliance"""
    
    def __init__(self, root_dir: str = "src/app"):
        self.root_dir = Path(root_dir)
        self.modules: List[ModuleMetrics] = []
    
    def analyze_all_modules(self) -> List[ModuleMetrics]:
        """Analyze all Python modules in the project"""
        for py_file in self.root_dir.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            metrics = self.analyze_module(py_file)
            if metrics:
                self.modules.append(metrics)
        return self.modules
    
    def analyze_module(self, file_path: Path) -> ModuleMetrics:
        """Analyze a single module"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content)
            
            return ModuleMetrics(
                path=str(file_path.relative_to(self.root_dir.parent)),
                responsibility=self._infer_responsibility(file_path, tree),
                public_functions=self._get_public_functions(tree),
                public_classes=self._get_public_classes(tree),
                imports=self._get_imports(tree),
                file_size_bytes=len(content.encode('utf-8')),
                line_count=content.count('\n') + 1,
                function_count=len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]),
                class_count=len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]),
                complexity_score=self._calculate_complexity(tree)
            )
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return None
    
    def _infer_responsibility(self, file_path: Path, tree: ast.AST) -> str:
        """Infer the primary responsibility of a module"""
        # Get module docstring
        docstring = ast.get_docstring(tree)
        if docstring:
            return docstring.split('\n')[0]  # First line
        
        # Infer from path structure
        parts = file_path.parts
        if 'interfaces' in parts:
            if 'http' in parts:
                return "HTTP endpoint handler"
            elif 'templates' in parts:
                return "UI template or static asset"
        elif 'application' in parts:
            return "Application use case / business logic orchestration"
        elif 'domain' in parts:
            return "Domain model or business rule"
        elif 'infrastructure' in parts:
            if 'persistence' in parts:
                return "Data persistence adapter"
            elif 'external' in parts:
                return "External API client"
            elif 'config' in parts:
                return "Configuration management"
        
        return "Unknown responsibility"
    
    def _get_public_functions(self, tree: ast.AST) -> List[str]:
        """Get all public functions (not starting with _)"""
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not node.name.startswith('_'):
                    functions.append(node.name)
        return functions
    
    def _get_public_classes(self, tree: ast.AST) -> List[str]:
        """Get all public classes (not starting with _)"""
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if not node.name.startswith('_'):
                    classes.append(node.name)
        return classes
    
    def _get_imports(self, tree: ast.AST) -> List[str]:
        """Get all import statements"""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")
        return imports
    
    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity estimate"""
        complexity = 0
        for node in ast.walk(tree):
            # Count decision points
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
        return complexity
    
    def generate_report(self, output_format: str = "markdown") -> str:
        """Generate analysis report"""
        if output_format == "markdown":
            return self._generate_markdown_report()
        elif output_format == "json":
            return self._generate_json_report()
        else:
            raise ValueError(f"Unknown format: {output_format}")
    
    def _generate_markdown_report(self) -> str:
        """Generate markdown report"""
        report = ["# Module Inventory Analysis\n"]
        report.append(f"**Total Modules Analyzed**: {len(self.modules)}\n")
        report.append("\n## Summary Statistics\n")
        
        total_size = sum(m.file_size_bytes for m in self.modules)
        total_lines = sum(m.line_count for m in self.modules)
        avg_size = total_size / len(self.modules) if self.modules else 0
        avg_complexity = sum(m.complexity_score for m in self.modules) / len(self.modules) if self.modules else 0
        
        report.append(f"- **Total Size**: {total_size:,} bytes ({total_size/1024:.1f} KB)\n")
        report.append(f"- **Total Lines**: {total_lines:,}\n")
        report.append(f"- **Average Module Size**: {avg_size:.0f} bytes\n")
        report.append(f"- **Average Complexity**: {avg_complexity:.1f}\n")
        report.append(f"- **Modules >4KB**: {len([m for m in self.modules if m.file_size_bytes > 4000])}\n")
        
        report.append("\n## Modules by Layer\n")
        layers = {}
        for module in self.modules:
            layer = module.path.split('/')[0] if '/' in module.path else 'root'
            layers.setdefault(layer, []).append(module)
        
        for layer, modules in sorted(layers.items()):
            report.append(f"\n### {layer.title()} ({len(modules)} modules)\n")
            report.append("\n| Module | Size | LOC | Functions | Classes | Complexity |\n")
            report.append("|--------|------|-----|-----------|---------|------------|\n")
            for m in sorted(modules, key=lambda x: x.file_size_bytes, reverse=True):
                name = m.path.split('/')[-1]
                report.append(f"| {name} | {m.file_size_bytes}B | {m.line_count} | {m.function_count} | {m.class_count} | {m.complexity_score} |\n")
        
        report.append("\n## Large Modules (>4KB)\n")
        large_modules = [m for m in self.modules if m.file_size_bytes > 4000]
        if large_modules:
            report.append("\n| Module | Size | Responsibility |\n")
            report.append("|--------|------|----------------|\n")
            for m in sorted(large_modules, key=lambda x: x.file_size_bytes, reverse=True):
                report.append(f"| {m.path} | {m.file_size_bytes}B | {m.responsibility} |\n")
        else:
            report.append("\n✅ All modules are under 4KB!\n")
        
        report.append("\n## High Complexity Modules (>20)\n")
        complex_modules = [m for m in self.modules if m.complexity_score > 20]
        if complex_modules:
            report.append("\n| Module | Complexity | Functions | Recommendation |\n")
            report.append("|--------|------------|-----------|----------------|\n")
            for m in sorted(complex_modules, key=lambda x: x.complexity_score, reverse=True):
                report.append(f"| {m.path} | {m.complexity_score} | {m.function_count} | Extract sub-modules |\n")
        else:
            report.append("\n✅ All modules have acceptable complexity!\n")
        
        return ''.join(report)
    
    def _generate_json_report(self) -> str:
        """Generate JSON report"""
        return json.dumps([asdict(m) for m in self.modules], indent=2)


def main():
    """Main entry point"""
    analyzer = ModuleAnalyzer()
    analyzer.analyze_all_modules()
    
    # Generate markdown report
    print(analyzer.generate_report("markdown"))
    
    # Save JSON for programmatic access
    with open("docs/optimization/module_inventory.json", "w") as f:
        f.write(analyzer.generate_report("json"))


if __name__ == "__main__":
    main()
