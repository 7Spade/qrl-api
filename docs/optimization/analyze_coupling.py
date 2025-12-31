#!/usr/bin/env python3
"""
Coupling & Dependency Analysis Script for Phase 3

Analyzes:
1. Dependency graph (module dependencies)
2. Coupling metrics (Ca, Ce, Instability, Abstractness)
3. Circular dependencies
4. Layer violations (upward dependencies)
5. Hidden dependencies (runtime imports)
"""

import ast
import os
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple

class DependencyAnalyzer(ast.NodeVisitor):
    def __init__(self, module_path: str):
        self.module_path = module_path
        self.imports = []
        
    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)
        
    def visit_ImportFrom(self, node):
        if node.module:
            self.imports.append(node.module)
        self.generic_visit(node)

def analyze_module_imports(file_path: str) -> List[str]:
    """Extract all imports from a module"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=file_path)
        analyzer = DependencyAnalyzer(file_path)
        analyzer.visit(tree)
        return analyzer.imports
    except Exception as e:
        return []

def get_module_layer(module_path: str) -> str:
    """Determine which architectural layer a module belongs to"""
    if 'interfaces' in module_path:
        return 'interfaces'
    elif 'application' in module_path:
        return 'application'
    elif 'domain' in module_path:
        return 'domain'
    elif 'infrastructure' in module_path:
        return 'infrastructure'
    return 'unknown'

def calculate_coupling_metrics(dependencies: Dict[str, List[str]]) -> Dict:
    """Calculate coupling metrics for each module"""
    metrics = {}
    
    # Build reverse dependency map (who depends on this module)
    dependents = defaultdict(list)
    for module, deps in dependencies.items():
        for dep in deps:
            dependents[dep].append(module)
    
    for module in dependencies.keys():
        # Efferent Coupling (Ce): outgoing dependencies
        ce = len(dependencies[module])
        
        # Afferent Coupling (Ca): incoming dependencies
        ca = len(dependents[module])
        
        # Instability (I): Ce / (Ce + Ca)
        # 0 = stable (hard to change), 1 = unstable (easy to change)
        instability = ce / (ce + ca) if (ce + ca) > 0 else 0
        
        metrics[module] = {
            'ce': ce,  # Efferent coupling
            'ca': ca,  # Afferent coupling
            'instability': instability,
            'dependents': dependents[module]
        }
    
    return metrics

def find_circular_dependencies(dependencies: Dict[str, List[str]]) -> List[List[str]]:
    """Find circular dependency chains"""
    cycles = []
    visited = set()
    rec_stack = set()
    
    def dfs(module, path):
        visited.add(module)
        rec_stack.add(module)
        path.append(module)
        
        for dep in dependencies.get(module, []):
            if dep not in visited:
                dfs(dep, path[:])
            elif dep in rec_stack:
                # Found cycle
                cycle_start = path.index(dep)
                cycle = path[cycle_start:] + [dep]
                if cycle not in cycles:
                    cycles.append(cycle)
        
        rec_stack.remove(module)
    
    for module in dependencies.keys():
        if module not in visited:
            dfs(module, [])
    
    return cycles

def find_layer_violations(dependencies: Dict[str, List[str]], module_layers: Dict[str, str]) -> List[Dict]:
    """Find upward dependencies (layer violations)"""
    layer_order = ['infrastructure', 'domain', 'application', 'interfaces']
    violations = []
    
    for module, deps in dependencies.items():
        module_layer = module_layers.get(module, 'unknown')
        if module_layer == 'unknown':
            continue
            
        module_level = layer_order.index(module_layer) if module_layer in layer_order else -1
        
        for dep in deps:
            dep_layer = module_layers.get(dep, 'unknown')
            if dep_layer == 'unknown':
                continue
                
            dep_level = layer_order.index(dep_layer) if dep_layer in layer_order else -1
            
            # Violation: depending on higher layer
            if module_level != -1 and dep_level != -1 and module_level < dep_level:
                violations.append({
                    'from': module,
                    'from_layer': module_layer,
                    'to': dep,
                    'to_layer': dep_layer,
                    'severity': 'HIGH' if dep_level - module_level > 1 else 'MEDIUM'
                })
    
    return violations

def main():
    src_path = Path('src/app')
    
    # Collect all Python modules
    modules = {}
    module_layers = {}
    
    for py_file in src_path.rglob('*.py'):
        if '__init__' in str(py_file):
            continue
            
        rel_path = str(py_file.relative_to(src_path.parent))
        module_name = rel_path.replace('/', '.').replace('.py', '')
        
        imports = analyze_module_imports(str(py_file))
        # Filter to only src.app imports
        src_imports = [imp for imp in imports if imp.startswith('src.app')]
        
        modules[module_name] = src_imports
        module_layers[module_name] = get_module_layer(rel_path)
    
    # Calculate metrics
    coupling_metrics = calculate_coupling_metrics(modules)
    circular_deps = find_circular_dependencies(modules)
    layer_violations = find_layer_violations(modules, module_layers)
    
    # Generate report
    report = {
        'total_modules': len(modules),
        'coupling_metrics': coupling_metrics,
        'circular_dependencies': circular_deps,
        'layer_violations': layer_violations,
        'high_coupling_modules': [
            {'module': m, **metrics} 
            for m, metrics in coupling_metrics.items() 
            if metrics['ce'] > 10 or metrics['ca'] > 10
        ]
    }
    
    # Save JSON
    with open('docs/optimization/coupling_analysis.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    # Generate Markdown Report
    with open('docs/optimization/coupling_analysis.md', 'w') as f:
        f.write('# Coupling & Dependency Analysis\n\n')
        f.write(f'**Total Modules Analyzed**: {len(modules)}\n\n')
        
        f.write('## Circular Dependencies\n\n')
        if circular_deps:
            f.write(f'**Found**: {len(circular_deps)} circular dependency chains\n\n')
            for i, cycle in enumerate(circular_deps, 1):
                f.write(f'### Cycle {i}\n')
                f.write(' → '.join(cycle) + '\n\n')
        else:
            f.write('✅ **No circular dependencies found**\n\n')
        
        f.write('## Layer Violations\n\n')
        if layer_violations:
            f.write(f'**Found**: {len(layer_violations)} layer violations\n\n')
            for v in layer_violations:
                f.write(f'- **{v["severity"]}**: {v["from"]} ({v["from_layer"]}) → {v["to"]} ({v["to_layer"]})\n')
        else:
            f.write('✅ **No layer violations found**\n\n')
        
        f.write('## High Coupling Modules\n\n')
        high_coupling = report['high_coupling_modules']
        if high_coupling:
            f.write(f'**Found**: {len(high_coupling)} modules with high coupling\n\n')
            f.write('| Module | Ce | Ca | Instability |\n')
            f.write('|--------|----|----|-------------|\n')
            for m in high_coupling:
                f.write(f'| {m["module"]} | {m["ce"]} | {m["ca"]} | {m["instability"]:.2f} |\n')
        else:
            f.write('✅ **No high coupling modules found**\n\n')
        
        f.write('\n## Coupling Metrics Legend\n\n')
        f.write('- **Ce (Efferent Coupling)**: Number of outgoing dependencies\n')
        f.write('- **Ca (Afferent Coupling)**: Number of incoming dependencies\n')
        f.write('- **Instability (I)**: Ce / (Ce + Ca) - Ratio between 0 (stable) and 1 (unstable)\n')
    
    print('✅ Coupling analysis complete')
    print(f'   Total modules: {len(modules)}')
    print(f'   Circular dependencies: {len(circular_deps)}')
    print(f'   Layer violations: {len(layer_violations)}')
    print(f'   High coupling modules: {len(high_coupling)}')

if __name__ == '__main__':
    main()
