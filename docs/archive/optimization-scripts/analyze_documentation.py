#!/usr/bin/env python3
"""
Documentation Redundancy Analyzer

Analyzes all markdown documentation for:
- Obsolete migration plans (completed phases)
- Temporary process tracking files
- Duplicate content across files
- Outdated architecture documentation
- Redundant Chinese-named temporary files
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple


def analyze_documentation(repo_root: str) -> Dict:
    """Analyze all documentation files for redundancy."""
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "total_files": 0,
        "total_size_bytes": 0,
        "categories": {
            "obsolete_migration": [],
            "temporary_tracking": [],
            "redundant_chinese": [],
            "legacy_api_docs": [],
            "outdated_architecture": [],
            "duplicate_content": [],
            "keep_active": []
        },
        "recommendations": {
            "delete": [],
            "archive": [],
            "consolidate": []
        }
    }
    
    # Find all markdown files
    md_files = []
    for root, dirs, files in os.walk(repo_root):
        # Skip .git and node_modules
        if '.git' in root or 'node_modules' in root:
            continue
        for file in files:
            if file.endswith('.md'):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, repo_root)
                size = os.path.getsize(full_path)
                md_files.append({
                    "path": rel_path,
                    "size": size,
                    "name": file
                })
                results["total_size_bytes"] += size
    
    results["total_files"] = len(md_files)
    
    # Categorize files
    for file_info in md_files:
        path = file_info["path"]
        name = file_info["name"]
        size = file_info["size"]
        
        categorized = False
        
        # Obsolete migration plans (completed)
        if "REMAINING_MIGRATION_PLAN" in name or "MIGRATION_CHECKLIST" in name:
            results["categories"]["obsolete_migration"].append(file_info)
            results["recommendations"]["delete"].append({
                **file_info,
                "reason": "Migration completed - all 8 phases done"
            })
            categorized = True
        
        # Temporary Copilot tracking
        elif "Copilot-Processing" in name:
            results["categories"]["temporary_tracking"].append(file_info)
            results["recommendations"]["delete"].append({
                **file_info,
                "reason": "Temporary processing tracker - no longer needed"
            })
            categorized = True
        
        # Redundant Chinese temporary files
        elif any(cn in name for cn in ["結構", "調整", "網頁"]):
            results["categories"]["redundant_chinese"].append(file_info)
            results["recommendations"]["delete"].append({
                **file_info,
                "reason": "Temporary Chinese planning docs - superseded by ARCHITECTURE_TREE.md"
            })
            categorized = True
        
        # Legacy API documentation (pre-migration)
        elif name.startswith("MEXC_v3") or name.startswith("websocket"):
            results["categories"]["legacy_api_docs"].append(file_info)
            results["recommendations"]["archive"].append({
                **file_info,
                "reason": "Legacy API docs - move to docs/archive/legacy-api/"
            })
            categorized = True
        
        # Outdated deployment docs (00- prefix)
        elif name.startswith("00-"):
            results["categories"]["legacy_api_docs"].append(file_info)
            results["recommendations"]["consolidate"].append({
                **file_info,
                "reason": "Legacy deployment docs - consolidate into main deployment guide"
            })
            categorized = True
        
        # Cleanup and optimization plan (reference doc, keep)
        elif "CLEANUP_AND_OPTIMIZATION_PLAN" in name:
            results["categories"]["keep_active"].append(file_info)
            categorized = True
        
        # Phase analysis reports (valuable, keep)
        elif "PHASE" in name and "REPORT" in name:
            results["categories"]["keep_active"].append(file_info)
            categorized = True
        
        # Analysis raw data (large, can archive)
        elif name in ["dead_code_analysis.md", "module_inventory.md", "coupling_analysis.md", "duplication_analysis.md"]:
            results["categories"]["duplicate_content"].append(file_info)
            results["recommendations"]["archive"].append({
                **file_info,
                "reason": "Raw analysis data - archive to docs/optimization/archive/"
            })
            categorized = True
        
        # Keep active documentation
        if not categorized:
            results["categories"]["keep_active"].append(file_info)
    
    return results


def generate_markdown_report(results: Dict) -> str:
    """Generate markdown report of documentation analysis."""
    
    report = []
    report.append("# Documentation Redundancy Analysis Report")
    report.append("")
    report.append(f"**Analysis Date**: {results['timestamp']}")
    report.append(f"**Total Files**: {results['total_files']}")
    report.append(f"**Total Size**: {results['total_size_bytes'] / 1024:.1f} KB")
    report.append("")
    
    # Summary statistics
    delete_count = len(results["recommendations"]["delete"])
    archive_count = len(results["recommendations"]["archive"])
    consolidate_count = len(results["recommendations"]["consolidate"])
    keep_count = len(results["categories"]["keep_active"])
    
    report.append("## Executive Summary")
    report.append("")
    report.append(f"- **Files to Delete**: {delete_count} ({delete_count/results['total_files']*100:.1f}%)")
    report.append(f"- **Files to Archive**: {archive_count} ({archive_count/results['total_files']*100:.1f}%)")
    report.append(f"- **Files to Consolidate**: {consolidate_count}")
    report.append(f"- **Files to Keep**: {keep_count} ({keep_count/results['total_files']*100:.1f}%)")
    report.append("")
    
    # Recommendations by action
    report.append("## Recommendations")
    report.append("")
    
    report.append("### 1. DELETE - Obsolete Files (Immediate)")
    report.append("")
    report.append("These files are no longer needed and should be deleted:")
    report.append("")
    for item in results["recommendations"]["delete"]:
        report.append(f"- `{item['path']}` ({item['size']} bytes)")
        report.append(f"  - **Reason**: {item['reason']}")
    report.append("")
    
    report.append("### 2. ARCHIVE - Historical Reference")
    report.append("")
    report.append("Move to `docs/archive/` for historical reference:")
    report.append("")
    for item in results["recommendations"]["archive"]:
        report.append(f"- `{item['path']}` ({item['size']} bytes)")
        report.append(f"  - **Reason**: {item['reason']}")
    report.append("")
    
    report.append("### 3. CONSOLIDATE - Merge Content")
    report.append("")
    report.append("Consolidate into main documentation:")
    report.append("")
    for item in results["recommendations"]["consolidate"]:
        report.append(f"- `{item['path']}` ({item['size']} bytes)")
        report.append(f"  - **Reason**: {item['reason']}")
    report.append("")
    
    return "\n".join(report)


if __name__ == "__main__":
    repo_root = "/home/runner/work/qrl-api/qrl-api"
    
    print("Analyzing documentation...")
    results = analyze_documentation(repo_root)
    
    # Save JSON
    json_path = os.path.join(repo_root, "docs/optimization/documentation_analysis.json")
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved JSON: {json_path}")
    
    # Save Markdown
    md_path = os.path.join(repo_root, "docs/optimization/documentation_analysis.md")
    report = generate_markdown_report(results)
    with open(md_path, "w") as f:
        f.write(report)
    print(f"Saved report: {md_path}")
    
    print("\nDone!")
