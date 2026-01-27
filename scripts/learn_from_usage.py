#!/usr/bin/env python3
"""
learn_from_usage.py - Learn from skill usage patterns and feedback

This script analyzes usage logs and feedback to improve the skill:
1. Identifies frequently asked questions
2. Detects missing information
3. Suggests new scenarios to add
4. Collects error patterns

Usage:
    python3 learn_from_usage.py --feedback-file usage_log.txt
    python3 learn_from_usage.py --analyze-errors error_log.txt
    python3 learn_from_usage.py --suggest-improvements
"""

import argparse
import json
import os
import re
from datetime import datetime
from collections import Counter, defaultdict

class SkillLearner:
    def __init__(self, skill_dir):
        self.skill_dir = skill_dir
        self.learning_data_file = os.path.join(skill_dir, '.learning_data.json')
        self.suggestions_file = os.path.join(skill_dir, '.suggestions.md')
        self.load_learning_data()

    def load_learning_data(self):
        """Load existing learning data"""
        if os.path.exists(self.learning_data_file):
            with open(self.learning_data_file, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {
                'query_patterns': defaultdict(int),
                'module_usage': defaultdict(int),
                'error_patterns': defaultdict(int),
                'missing_apis': [],
                'feedback': [],
                'last_update': None
            }

    def save_learning_data(self):
        """Save learning data"""
        self.data['last_update'] = datetime.now().isoformat()

        # Convert defaultdicts to regular dicts for JSON serialization
        serializable_data = {
            'query_patterns': dict(self.data['query_patterns']),
            'module_usage': dict(self.data['module_usage']),
            'error_patterns': dict(self.data['error_patterns']),
            'missing_apis': self.data['missing_apis'],
            'feedback': self.data['feedback'],
            'last_update': self.data['last_update']
        }

        with open(self.learning_data_file, 'w') as f:
            json.dump(serializable_data, f, indent=2)

        print(f"Learning data saved to: {self.learning_data_file}")

    def analyze_feedback(self, feedback_file):
        """Analyze user feedback from log file"""
        print(f"\n=== Analyzing feedback from {feedback_file} ===\n")

        if not os.path.exists(feedback_file):
            print(f"ERROR: Feedback file not found: {feedback_file}")
            return

        with open(feedback_file, 'r') as f:
            lines = f.readlines()

        # Pattern detection
        module_pattern = re.compile(r'\b(VI|VPSS|VENC|VO|VB|RGN|GDC|SYS)\b', re.IGNORECASE)
        api_pattern = re.compile(r'CVI_(\w+)_(\w+)')
        error_pattern = re.compile(r'(error|failed|issue|problem|not working)', re.IGNORECASE)

        for line in lines:
            # Detect module mentions
            modules = module_pattern.findall(line)
            for module in modules:
                self.data['module_usage'][module.upper()] += 1

            # Detect API calls
            apis = api_pattern.findall(line)
            for module, func in apis:
                api_name = f"CVI_{module}_{func}"
                self.data['query_patterns'][api_name] += 1

            # Detect errors/issues
            if error_pattern.search(line):
                # Extract context around error
                context = line.strip()[:100]
                self.data['error_patterns'][context] += 1

            # Store raw feedback
            self.data['feedback'].append({
                'timestamp': datetime.now().isoformat(),
                'content': line.strip()
            })

        # Print analysis summary
        print("Module Usage Frequency:")
        for module, count in sorted(self.data['module_usage'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {module}: {count} mentions")

        print("\nMost Queried APIs:")
        top_apis = sorted(self.data['query_patterns'].items(), key=lambda x: x[1], reverse=True)[:10]
        for api, count in top_apis:
            print(f"  {api}: {count} times")

        print("\nCommon Error Patterns:")
        top_errors = sorted(self.data['error_patterns'].items(), key=lambda x: x[1], reverse=True)[:5]
        for error, count in top_errors:
            print(f"  [{count}x] {error}")

        self.save_learning_data()

    def suggest_improvements(self):
        """Generate improvement suggestions based on learned data"""
        print("\n=== Generating Improvement Suggestions ===\n")

        suggestions = []

        # Suggest expanding popular modules
        if self.data['module_usage']:
            top_module = max(self.data['module_usage'].items(), key=lambda x: x[1])
            suggestions.append(f"- **Expand {top_module[0]} documentation**: This module is most frequently queried ({top_module[1]} times)")

        # Suggest adding frequently queried but undocumented APIs
        if self.data['query_patterns']:
            # Check if APIs exist in references
            for api, count in sorted(self.data['query_patterns'].items(), key=lambda x: x[1], reverse=True)[:5]:
                module = api.split('_')[1].lower()
                ref_file = os.path.join(self.skill_dir, 'references', f'{module}.md')
                if os.path.exists(ref_file):
                    with open(ref_file, 'r') as f:
                        content = f.read()
                        if api not in content:
                            suggestions.append(f"- **Add {api} documentation**: Queried {count} times but not well documented")

        # Suggest addressing common errors
        if self.data['error_patterns']:
            top_error = max(self.data['error_patterns'].items(), key=lambda x: x[1])
            suggestions.append(f"- **Add troubleshooting for**: '{top_error[0][:80]}...' (reported {top_error[1]} times)")

        # Save suggestions
        if suggestions:
            with open(self.suggestions_file, 'w') as f:
                f.write("# Skill Improvement Suggestions\n\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("Based on usage analysis, consider these improvements:\n\n")
                for suggestion in suggestions:
                    f.write(f"{suggestion}\n")

            print(f"Suggestions saved to: {self.suggestions_file}\n")

            print("Suggestions:")
            for suggestion in suggestions:
                print(suggestion)
        else:
            print("No suggestions generated. Need more usage data.")

    def analyze_errors(self, error_log):
        """Analyze error logs to identify patterns"""
        print(f"\n=== Analyzing errors from {error_log} ===\n")

        if not os.path.exists(error_log):
            print(f"ERROR: Error log file not found: {error_log}")
            return

        with open(error_log, 'r') as f:
            lines = f.readlines()

        # Pattern detection for common errors
        common_errors = {
            'VB_GetBlock failed': 'VB pool exhaustion',
            'Out of memory': 'Memory allocation failure',
            'Lost frames': 'Frame drops / Buffer shortage',
            'failed to bind': 'Module binding error',
            'Invalid parameter': 'API parameter error',
            'Device not enabled': 'Module initialization error'
        }

        error_counts = defaultdict(int)

        for line in lines:
            for pattern, category in common_errors.items():
                if pattern.lower() in line.lower():
                    error_counts[category] += 1

        print("Error Category Frequency:")
        for category, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {category}: {count} occurrences")

        # Suggest debug sections to expand
        if error_counts:
            top_error = max(error_counts.items(), key=lambda x: x[1])
            print(f"\n💡 Suggestion: Expand debug.md section on '{top_error[0]}'")

        self.save_learning_data()

def main():
    parser = argparse.ArgumentParser(description='Learn from skill usage and improve documentation')
    parser.add_argument('--feedback-file', help='Path to usage/feedback log file')
    parser.add_argument('--analyze-errors', help='Path to error log file')
    parser.add_argument('--suggest-improvements', action='store_true', help='Generate improvement suggestions')
    parser.add_argument('--skill-dir', default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        help='Path to skill directory')

    args = parser.parse_args()

    learner = SkillLearner(args.skill_dir)

    if args.feedback_file:
        learner.analyze_feedback(args.feedback_file)

    if args.analyze_errors:
        learner.analyze_errors(args.analyze_errors)

    if args.suggest_improvements:
        learner.suggest_improvements()

    if not any([args.feedback_file, args.analyze_errors, args.suggest_improvements]):
        parser.print_help()

if __name__ == '__main__':
    main()
