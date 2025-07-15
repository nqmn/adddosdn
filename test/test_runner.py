#!/usr/bin/env python3
"""
Unified Test Runner for SDN DDoS Dataset Testing Scripts

This script provides a menu-driven interface to run various dataset testing and validation scripts.
All scripts are executed in the test/ directory and maintain their original output locations.

Usage:
    python3 test_runner.py
"""

import os
import sys
import subprocess
from pathlib import Path

class TestRunner:
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.project_root = self.script_dir.parent
        
        # Available test scripts with descriptions
        self.test_scripts = {
            '1': {
                'name': 'Timeline Analysis',
                'script': 'analyze_timeline.py',
                'description': 'Analyze timeline alignment between packet and flow features',
                'args': ['test_output']  # Default output directory
            },
            '2': {
                'name': 'Calculate Statistics',
                'script': 'calculate_percentages.py',
                'description': 'Calculate attack type statistics and percentages',
                'args': ['test_output']  # Default output directory
            },
            '3': {
                'name': 'Change File Ownership',
                'script': 'change_ownership.py',
                'description': 'Change file ownership (requires sudo)',
                'args': []  # Will prompt for directory
            },
            '4': {
                'name': 'Check PCAP Timestamps',
                'script': 'check_pcap_timestamps.py',
                'description': 'Validate timestamps in PCAP files',
                'args': []
            },
            '5': {
                'name': 'Extract CICFlow Features',
                'script': 'extract_cicflow_features.py',
                'description': 'Extract network flow features using CICFlowMeter',
                'args': ['--pcap-dir', '.', '--output-dir', 'cicflow_output']
            },
            '6': {
                'name': 'Process PCAP to CSV',
                'script': 'run_process_pcap.py',
                'description': 'Process PCAP files to labeled CSV features',
                'args': []
            },
            '7': {
                'name': 'Validate CICFlow Dataset',
                'script': 'validate_cicflow_dataset.py',
                'description': 'Comprehensive validation of CICFlow dataset',
                'args': []  # Will prompt for CSV file
            }
        }
    
    def display_menu(self):
        """Display the main menu."""
        print("\n" + "="*70)
        print("SDN DDOS DATASET TEST RUNNER")
        print("="*70)
        print("Select a test script to run:")
        print()
        
        for key, script_info in self.test_scripts.items():
            print(f"{key}. {script_info['name']}")
            print(f"   {script_info['description']}")
            print()
        
        print("0. Exit")
        print("="*70)
    
    def get_user_input(self, prompt, choices):
        """Get valid user input."""
        while True:
            try:
                choice = input(prompt).strip()
                if choice in choices:
                    return choice
                else:
                    print(f"Invalid choice. Please select from: {', '.join(choices)}")
            except KeyboardInterrupt:
                print("\nExiting...")
                sys.exit(0)
    
    def run_script(self, script_key):
        """Run the selected script."""
        script_info = self.test_scripts[script_key]
        script_path = self.script_dir / script_info['script']
        
        print(f"\n{'='*50}")
        print(f"RUNNING: {script_info['name']}")
        print(f"{'='*50}")
        print(f"Script: {script_info['script']}")
        print(f"Description: {script_info['description']}")
        print()
        
        # Check if script exists
        if not script_path.exists():
            print(f"❌ ERROR: Script not found: {script_path}")
            return False
        
        # Prepare command
        cmd = ['python3', str(script_path)]
        
        # Handle special cases that need user input
        if script_key == '3':  # change_ownership.py
            directory = input("Enter directory path to change ownership: ").strip()
            if not directory:
                print("❌ ERROR: Directory path is required")
                return False
            cmd.append(directory)
        
        elif script_key == '7':  # validate_cicflow_dataset.py
            csv_file = input("Enter path to CICFlow CSV file (or press Enter for default): ").strip()
            if not csv_file:
                # Check for default locations
                default_paths = [
                    'cicflow_output/cicflow_features_all.csv',
                    '../dataset_generation/test_output/cicflow_features_all.csv',
                    '../dataset_generation/main_output/cicflow_features_all.csv'
                ]
                
                for path in default_paths:
                    if (self.script_dir / path).exists():
                        csv_file = path
                        break
                
                if not csv_file:
                    print("❌ ERROR: No CSV file found. Please specify path.")
                    return False
            
            cmd.append(csv_file)
            
            # Ask for visualizations
            viz_choice = self.get_user_input("Generate visualizations? (y/n): ", ['y', 'n', 'Y', 'N'])
            if viz_choice.lower() == 'y':
                cmd.extend(['--visualizations'])
        
        elif script_key == '2':  # calculate_percentages.py
            output_dir = self.get_user_input("Select output directory (main_output/test_output): ", 
                                           ['main_output', 'test_output'])
            cmd = ['python3', str(script_path), output_dir]
        
        else:
            # Add default arguments for other scripts
            cmd.extend(script_info['args'])
        
        # Show command being executed
        print(f"Executing: {' '.join(cmd)}")
        print("-" * 50)
        
        try:
            # Change to test directory to run script
            original_cwd = os.getcwd()
            os.chdir(self.script_dir)
            
            # Run the script
            result = subprocess.run(cmd, capture_output=False, text=True)
            
            # Restore original directory
            os.chdir(original_cwd)
            
            if result.returncode == 0:
                print(f"\n✅ {script_info['name']} completed successfully!")
                return True
            else:
                print(f"\n❌ {script_info['name']} failed with return code: {result.returncode}")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Error running {script_info['name']}: {e}")
            return False
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            return False
        finally:
            # Ensure we're back in original directory
            os.chdir(original_cwd)
    
    def show_script_help(self, script_key):
        """Show help for a specific script."""
        script_info = self.test_scripts[script_key]
        script_path = self.script_dir / script_info['script']
        
        print(f"\n{'='*50}")
        print(f"HELP: {script_info['name']}")
        print(f"{'='*50}")
        
        try:
            # Try to run with --help
            cmd = ['python3', str(script_path), '--help']
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.script_dir)
            
            if result.returncode == 0:
                print(result.stdout)
            else:
                print(f"Description: {script_info['description']}")
                print(f"Script: {script_info['script']}")
                print(f"Default args: {script_info['args']}")
                
        except Exception as e:
            print(f"Error getting help: {e}")
    
    def run(self):
        """Main execution loop."""
        print("Welcome to the SDN DDoS Dataset Test Runner!")
        print("This tool provides easy access to all dataset testing scripts.")
        
        while True:
            self.display_menu()
            
            choices = list(self.test_scripts.keys()) + ['0', 'h', 'H']
            choice = self.get_user_input("Enter your choice (or 'h' for help): ", choices)
            
            if choice == '0':
                print("Goodbye!")
                break
            elif choice.lower() == 'h':
                print("\nAvailable commands:")
                print("  1-7: Run the corresponding test script")
                print("  h: Show this help message")
                print("  0: Exit")
                print("\nFor help on a specific script, type the script number.")
                continue
            else:
                # Run the selected script
                success = self.run_script(choice)
                
                if success:
                    # Ask if user wants to run another script
                    another = self.get_user_input("\nRun another script? (y/n): ", ['y', 'n', 'Y', 'N'])
                    if another.lower() == 'n':
                        break
                else:
                    # On failure, ask if they want to try again or exit
                    retry = self.get_user_input("\nTry again or return to menu? (r/m): ", ['r', 'm', 'R', 'M'])
                    if retry.lower() == 'r':
                        continue
                    elif retry.lower() == 'm':
                        continue

def main():
    """Main entry point."""
    runner = TestRunner()
    runner.run()

if __name__ == "__main__":
    main()