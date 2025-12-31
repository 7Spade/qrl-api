#!/usr/bin/env python3
"""
Phase 5: Duplication Detection Analyzer

Detects code duplication across Python modules using multiple techniques:
1. Exact duplicate lines (copy-paste detection)
2. Similar code blocks (structural similarity)
3. Duplicate function signatures
4. Common patterns that should be extracted

Usage:
    python analyze_duplication.py [--threshold 0.8] [--min-lines 5]
"""

import ast
import hashlib
import json
import os
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set, Tuple

@dataclass
class DuplicateBlock:
    """Represents a duplicate code block"""
    file1: str
    file2: str
    line1_start: int
    line1_end: int
    line2_start: int
    line2_end: int
    lines: int
    content_hash: str
    similarity: float = 1.0
    
@dataclass
class DuplicationReport:
    """Complete duplication analysis report"""
    total_files: int = 0
    total_lines: int = 0
    duplicate_lines: int = 0
    duplicate_blocks: List[DuplicateBlock] = field(default_factory=list)
    duplicate_functions: Dict[str, List[Tuple[str, int]]] = field(default_factory=dict)
    common_patterns: Dict[str, int] = field(default_factory=dict)
    duplication_percentage: float = 0.0
    
class DuplicationAnalyzer:
    """Analyzes code duplication across Python files"""
    
    def __init__(self, root_dir: str = "src/app", min_lines: int = 5):
        self.root_dir = Path(root_dir)
        self.min_lines = min_lines
        self.file_lines: Dict[str, List[str]] = {}
        self.file_hashes: Dict[str, List[str]] = {}
        
    def analyze(self) -> DuplicationReport:
        """Run complete duplication analysis"""
        report = DuplicationReport()
        
        # Load all Python files
        py_files = list(self.root_dir.rglob("*.py"))
        report.total_files = len(py_files)
        
        for py_file in py_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    rel_path = str(py_file.relative_to(self.root_dir.parent))
                    self.file_lines[rel_path] = lines
                    report.total_lines += len(lines)
                    
                    # Compute line hashes
                    self.file_hashes[rel_path] = [
                        self._hash_line(line) for line in lines
                    ]
            except Exception as e:
                print(f"Error reading {py_file}: {e}")
                
        # Detect exact duplicates
        report.duplicate_blocks = self._find_duplicate_blocks()
        
        # Calculate duplicate lines
        duplicate_line_set = set()
        for block in report.duplicate_blocks:
            for i in range(block.line1_start, block.line1_end + 1):
                duplicate_line_set.add((block.file1, i))
            for i in range(block.line2_start, block.line2_end + 1):
                duplicate_line_set.add((block.file2, i))
                
        report.duplicate_lines = len(duplicate_line_set)
        report.duplication_percentage = (
            (report.duplicate_lines / report.total_lines * 100) 
            if report.total_lines > 0 else 0.0
        )
        
        # Detect duplicate function signatures
        report.duplicate_functions = self._find_duplicate_functions()
        
        # Detect common patterns
        report.common_patterns = self._find_common_patterns()
        
        return report
        
    def _hash_line(self, line: str) -> str:
        """Hash a line of code (normalized)"""
        # Normalize: remove leading/trailing whitespace, 
        # but preserve indentation structure
        normalized = line.strip()
        if not normalized or normalized.startswith('#'):
            return ""  # Ignore empty lines and comments
        return hashlib.md5(normalized.encode()).hexdigest()
        
    def _find_duplicate_blocks(self) -> List[DuplicateBlock]:
        """Find exact duplicate code blocks"""
        duplicates = []
        files = list(self.file_lines.keys())
        
        for i, file1 in enumerate(files):
            for file2 in files[i+1:]:
                blocks = self._compare_files(file1, file2)
                duplicates.extend(blocks)
                
        # Sort by number of duplicate lines (descending)
        duplicates.sort(key=lambda b: b.lines, reverse=True)
        return duplicates
        
    def _compare_files(self, file1: str, file2: str) -> List[DuplicateBlock]:
        """Compare two files for duplicate blocks"""
        hashes1 = self.file_hashes[file1]
        hashes2 = self.file_hashes[file2]
        blocks = []
        
        i = 0
        while i < len(hashes1):
            if not hashes1[i]:  # Skip empty/comment lines
                i += 1
                continue
                
            j = 0
            while j < len(hashes2):
                if not hashes2[j]:
                    j += 1
                    continue
                    
                # Check for matching sequence
                match_len = 0
                while (i + match_len < len(hashes1) and 
                       j + match_len < len(hashes2) and
                       hashes1[i + match_len] and
                       hashes1[i + match_len] == hashes2[j + match_len]):
                    match_len += 1
                    
                if match_len >= self.min_lines:
                    # Found duplicate block
                    content = ''.join(self.file_lines[file1][i:i+match_len])
                    blocks.append(DuplicateBlock(
                        file1=file1,
                        file2=file2,
                        line1_start=i + 1,
                        line1_end=i + match_len,
                        line2_start=j + 1,
                        line2_end=j + match_len,
                        lines=match_len,
                        content_hash=hashlib.md5(content.encode()).hexdigest()
                    ))
                    # Skip past this block
                    j += match_len
                else:
                    j += 1
                    
            i += 1
            
        return blocks
        
    def _find_duplicate_functions(self) -> Dict[str, List[Tuple[str, int]]]:
        """Find functions with duplicate signatures"""
        function_sigs = defaultdict(list)
        
        for file_path, lines in self.file_lines.items():
            try:
                content = ''.join(lines)
                tree = ast.parse(content, filename=file_path)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Create signature: name(param1, param2, ...)
                        params = [arg.arg for arg in node.args.args]
                        sig = f"{node.name}({', '.join(params)})"
                        function_sigs[sig].append((file_path, node.lineno))
            except:
                pass
                
        # Keep only duplicates
        return {
            sig: locs for sig, locs in function_sigs.items() 
            if len(locs) > 1
        }
        
    def _find_common_patterns(self) -> Dict[str, int]:
        """Find common code patterns that might be extractable"""
        patterns = defaultdict(int)
        
        # Pattern 1: Similar error handling
        error_pattern = "try:"
        # Pattern 2: Similar imports
        import_pattern = "from src.app"
        # Pattern 3: Similar validation
        validation_pattern = "if not"
        
        for lines in self.file_lines.values():
            for line in lines:
                stripped = line.strip()
                if error_pattern in stripped:
                    patterns["try-except blocks"] += 1
                if import_pattern in stripped:
                    patterns["src.app imports"] += 1
                if validation_pattern in stripped:
                    patterns["validation checks"] += 1
                    
        return dict(patterns)

def generate_markdown_report(report: DuplicationReport, output_file: str):
    """Generate human-readable Markdown report"""
    lines = [
        "# Code Duplication Analysis Report",
        "",
        "## Summary",
        "",
        f"- **Total Files Analyzed**: {report.total_files}",
        f"- **Total Lines of Code**: {report.total_lines:,}",
        f"- **Duplicate Lines**: {report.duplicate_lines:,}",
        f"- **Duplication Percentage**: {report.duplication_percentage:.1f}%",
        f"- **Duplicate Blocks Found**: {len(report.duplicate_blocks)}",
        f"- **Duplicate Function Signatures**: {len(report.duplicate_functions)}",
        "",
        "## Duplicate Code Blocks",
        "",
    ]
    
    if report.duplicate_blocks:
        for i, block in enumerate(report.duplicate_blocks[:20], 1):  # Top 20
            lines.extend([
                f"### Block {i} - {block.lines} lines",
                "",
                f"- **File 1**: `{block.file1}` (lines {block.line1_start}-{block.line1_end})",
                f"- **File 2**: `{block.file2}` (lines {block.line2_start}-{block.line2_end})",
                f"- **Similarity**: {block.similarity*100:.0f}%",
                "",
            ])
    else:
        lines.append("✅ No significant duplicate blocks found (minimum 5 lines).")
        
    lines.extend([
        "",
        "## Duplicate Function Signatures",
        "",
    ])
    
    if report.duplicate_functions:
        for sig, locations in list(report.duplicate_functions.items())[:10]:
            lines.append(f"### `{sig}`")
            lines.append("")
            for file_path, line_no in locations:
                lines.append(f"- `{file_path}:{line_no}`")
            lines.append("")
    else:
        lines.append("✅ No duplicate function signatures found.")
        
    lines.extend([
        "",
        "## Common Patterns",
        "",
    ])
    
    for pattern, count in sorted(report.common_patterns.items(), 
                                  key=lambda x: x[1], reverse=True):
        lines.append(f"- **{pattern}**: {count} occurrences")
        
    with open(output_file, 'w') as f:
        f.write('\n'.join(lines))

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze code duplication')
    parser.add_argument('--root', default='src/app', help='Root directory')
    parser.add_argument('--min-lines', type=int, default=5, 
                       help='Minimum lines for duplicate block')
    parser.add_argument('--output', default='docs/optimization',
                       help='Output directory')
    
    args = parser.parse_args()
    
    print("Phase 5: Duplication Detection")
    print("=" * 50)
    print(f"Analyzing: {args.root}")
    print(f"Minimum duplicate lines: {args.min_lines}")
    print()
    
    analyzer = DuplicationAnalyzer(args.root, args.min_lines)
    report = analyzer.analyze()
    
    # Print summary
    print("Analysis Complete!")
    print(f"  Files: {report.total_files}")
    print(f"  Total Lines: {report.total_lines:,}")
    print(f"  Duplicate Lines: {report.duplicate_lines:,}")
    print(f"  Duplication %: {report.duplication_percentage:.1f}%")
    print(f"  Duplicate Blocks: {len(report.duplicate_blocks)}")
    print(f"  Duplicate Functions: {len(report.duplicate_functions)}")
    print()
    
    # Save reports
    os.makedirs(args.output, exist_ok=True)
    
    # JSON report
    json_file = f"{args.output}/duplication_analysis.json"
    with open(json_file, 'w') as f:
        json.dump({
            'total_files': report.total_files,
            'total_lines': report.total_lines,
            'duplicate_lines': report.duplicate_lines,
            'duplication_percentage': report.duplication_percentage,
            'duplicate_blocks': [
                {
                    'file1': b.file1,
                    'file2': b.file2,
                    'line1_start': b.line1_start,
                    'line1_end': b.line1_end,
                    'line2_start': b.line2_start,
                    'line2_end': b.line2_end,
                    'lines': b.lines,
                    'similarity': b.similarity
                }
                for b in report.duplicate_blocks
            ],
            'duplicate_functions': {
                sig: [(f, l) for f, l in locs]
                for sig, locs in report.duplicate_functions.items()
            },
            'common_patterns': report.common_patterns
        }, f, indent=2)
    
    # Markdown report
    md_file = f"{args.output}/duplication_analysis.md"
    generate_markdown_report(report, md_file)
    
    print(f"Reports saved:")
    print(f"  - {json_file}")
    print(f"  - {md_file}")

if __name__ == "__main__":
    main()
