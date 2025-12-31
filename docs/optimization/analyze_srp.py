#!/usr/bin/env python3
"""
Single Responsibility Principle (SRP) Violation Analysis

Identifies modules that have multiple responsibilities and should be split.
"""

import ast
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict
import json


class SRPAnalyzer:
    """Analyzes modules for Single Responsibility Principle violations"""
    
    # Keywords that indicate different responsibilities
    RESPONSIBILITY_KEYWORDS = {
        'validation': ['validate', 'check', 'verify', 'sanitize'],
        'transformation': ['transform', 'convert', 'parse', 'format', 'serialize'],
        'persistence': ['save', 'load', 'store', 'fetch', 'get', 'set', 'cache'],
        'computation': ['calculate', 'compute', 'process', 'analyze'],
        'communication': ['send', 'receive', 'publish', 'subscribe', 'emit'],
        'coordination': ['orchestrate', 'coordinate', 'manage', 'handle'],
        'presentation': ['render', 'display', 'show', 'format_output'],
    }
    
    def __init__(self, root_dir: str = "src/app"):
        self.root_dir = Path(root_dir)
        self.violations = []
    
    def analyze_all_modules(self) -> List[Dict]:
        """Analyze all modules for SRP violations"""
        for py_file in self.root_dir.rglob("*.py"):
            if "__pycache__" in str(py_file) or "__init__" in py_file.name:
                continue
            
            violation = self.analyze_module(py_file)
            if violation:
                self.violations.append(violation)
        
        return self.violations
    
    def analyze_module(self, file_path: Path) -> Dict:
        """Analyze a single module for SRP violations"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content)
            
            # Analyze responsibilities
            responsibilities = self._identify_responsibilities(tree)
            
            # Check for violations
            if len(responsibilities) <= 1:
                return None  # No violation
            
            # Count functions/classes
            functions = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
            classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
            
            return {
                'module': str(file_path.relative_to(self.root_dir.parent)),
                'responsibilities': list(responsibilities.keys()),
                'responsibility_details': responsibilities,
                'function_count': len(functions),
                'class_count': len(classes),
                'file_size': len(content.encode('utf-8')),
                'severity': self._calculate_severity(responsibilities, len(functions), len(classes)),
                'recommendation': self._generate_recommendation(file_path, responsibilities)
            }
            
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return None
    
    def _identify_responsibilities(self, tree: ast.AST) -> Dict[str, List[str]]:
        """Identify different responsibilities in a module"""
        responsibilities = defaultdict(list)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_name = node.name.lower()
                
                # Check each responsibility category
                for category, keywords in self.RESPONSIBILITY_KEYWORDS.items():
                    for keyword in keywords:
                        if keyword in func_name:
                            responsibilities[category].append(node.name)
                            break
        
        return dict(responsibilities)
    
    def _calculate_severity(self, responsibilities: Dict, func_count: int, class_count: int) -> str:
        """Calculate violation severity"""
        resp_count = len(responsibilities)
        
        if resp_count >= 4:
            return "CRITICAL"
        elif resp_count == 3:
            return "HIGH"
        elif resp_count == 2 and func_count > 10:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _generate_recommendation(self, file_path: Path, responsibilities: Dict) -> str:
        """Generate refactoring recommendation"""
        recommendations = []
        
        for resp, functions in responsibilities.items():
            new_module = file_path.stem + "_" + resp
            recommendations.append(
                f"Extract {len(functions)} {resp} functions to `{new_module}.py`"
            )
        
        return " | ".join(recommendations)
    
    def generate_report(self) -> str:
        """Generate SRP violation report"""
        report = ["# Single Responsibility Principle (SRP) Violations\n"]
        report.append(f"\n**Total Violations Found**: {len(self.violations)}\n")
        
        if not self.violations:
            report.append("\n✅ **No SRP violations detected!** All modules have single responsibilities.\n")
            return ''.join(report)
        
        # Group by severity
        by_severity = defaultdict(list)
        for v in self.violations:
            by_severity[v['severity']].append(v)
        
        # Summary
        report.append("\n## Summary by Severity\n")
        report.append(f"- **CRITICAL**: {len(by_severity['CRITICAL'])} modules\n")
        report.append(f"- **HIGH**: {len(by_severity['HIGH'])} modules\n")
        report.append(f"- **MEDIUM**: {len(by_severity['MEDIUM'])} modules\n")
        report.append(f"- **LOW**: {len(by_severity['LOW'])} modules\n")
        
        # Detailed violations
        for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            violations = by_severity.get(severity, [])
            if not violations:
                continue
            
            report.append(f"\n## {severity} Severity Violations\n")
            for v in sorted(violations, key=lambda x: len(x['responsibilities']), reverse=True):
                report.append(f"\n### {v['module']}\n")
                report.append(f"**Responsibilities**: {', '.join(v['responsibilities'])}\n")
                report.append(f"**Functions**: {v['function_count']} | **Classes**: {v['class_count']} | **Size**: {v['file_size']} bytes\n")
                report.append(f"\n**Details**:\n")
                for resp, funcs in v['responsibility_details'].items():
                    report.append(f"- {resp.title()}: {', '.join(funcs[:5])}")
                    if len(funcs) > 5:
                        report.append(f" (+{len(funcs)-5} more)")
                    report.append("\n")
                report.append(f"\n**Recommendation**: {v['recommendation']}\n")
        
        # Actionable summary
        report.append("\n## Action Items\n")
        report.append("\n### Immediate (CRITICAL/HIGH)\n")
        critical_high = by_severity['CRITICAL'] + by_severity['HIGH']
        for v in sorted(critical_high, key=lambda x: len(x['responsibilities']), reverse=True):
            report.append(f"- [ ] Split `{v['module']}` into {len(v['responsibilities'])} modules\n")
        
        report.append("\n### Future Improvements (MEDIUM/LOW)\n")
        medium_low = by_severity['MEDIUM'] + by_severity['LOW']
        for v in sorted(medium_low, key=lambda x: len(x['responsibilities']), reverse=True):
            report.append(f"- [ ] Consider refactoring `{v['module']}`\n")
        
        return ''.join(report)


def main():
    """Main entry point"""
    analyzer = SRPAnalyzer()
    analyzer.analyze_all_modules()
    
    # Generate report
    print(analyzer.generate_report())
    
    # Save JSON
    with open("docs/optimization/srp_violations.json", "w") as f:
        json.dump(analyzer.violations, f, indent=2)


if __name__ == "__main__":
    main()
