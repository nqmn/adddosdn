#!/usr/bin/env python3
"""
Multiple Run Script for mainv2.py
Runs mainv2.py multiple times with different output directories
"""

import os
import sys
import time
import shutil
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description="Run mainv2.py multiple times with different output directories")
    parser.add_argument('--runs', type=int, default=4, help='Number of times to run mainv2.py (default: 4)')
    parser.add_argument('--config', type=str, default='config.json', help='Configuration file to use (default: config.json)')
    parser.add_argument('--cores', type=int, help='Number of CPU cores for PCAP processing')
    parser.add_argument('--max-cores', type=int, help='Maximum number of CPU cores available')
    args = parser.parse_args()
    
    # Check if running as root
    if os.geteuid() != 0:
        print("ERROR: This script must be run as root for Mininet.")
        sys.exit(1)
    
    # Get base directory
    base_dir = Path(__file__).parent.resolve()
    mainv2_script = base_dir / "mainv2.py"
    
    # Check if mainv2.py exists
    if not mainv2_script.exists():
        print(f"ERROR: mainv2.py not found at {mainv2_script}")
        sys.exit(1)
    
    # Check if config file exists
    config_file = base_dir / args.config
    if not config_file.exists():
        print(f"ERROR: Config file not found at {config_file}")
        sys.exit(1)
    
    print(f"Starting {args.runs} runs of mainv2.py")
    print(f"Using config file: {config_file}")
    print(f"Base directory: {base_dir}")
    print("=" * 60)
    
    successful_runs = 0
    failed_runs = 0
    run_results = []
    
    for run_num in range(1, args.runs + 1):
        print(f"\n🚀 Starting Run {run_num}/{args.runs}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Create unique output directory for this run with format DDMMYY-run
        date_str = datetime.now().strftime('%d%m%y')
        output_dir = base_dir / f"main_output" / f"{date_str}-{run_num}"
        
        # Remove existing output directory if it exists
        if output_dir.exists():
            print(f"Removing existing output directory: {output_dir}")
            shutil.rmtree(output_dir)
        
        # Create the output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Modify the mainv2.py script temporarily to use our output directory
        # We'll do this by copying the script and modifying the OUTPUT_DIR line
        temp_script = base_dir / f"mainv2_run_{run_num}.py"
        
        try:
            # Read original script
            with open(mainv2_script, 'r') as f:
                script_content = f.read()
            
            # Replace OUTPUT_DIR line
            original_line = 'OUTPUT_DIR = BASE_DIR / "main_output"'
            new_line = f'OUTPUT_DIR = BASE_DIR / "main_output" / "{date_str}-{run_num}"'
            modified_content = script_content.replace(original_line, new_line)
            
            # Write modified script
            with open(temp_script, 'w') as f:
                f.write(modified_content)
            
            # Make it executable
            os.chmod(temp_script, 0o755)
            
            # Prepare command
            cmd = [sys.executable, str(temp_script), str(config_file)]
            
            # Add optional arguments
            if args.cores:
                cmd.extend(['--cores', str(args.cores)])
            if args.max_cores:
                cmd.extend(['--max-cores', str(args.max_cores)])
            
            print(f"Command: {' '.join(cmd)}")
            print(f"Output directory: {output_dir}")
            
            # Run the script
            start_time = time.time()
            result = subprocess.run(cmd, cwd=base_dir)
            end_time = time.time()
            
            execution_time = end_time - start_time
            
            if result.returncode == 0:
                print(f"✅ Run {run_num} completed successfully")
                print(f"⏱️  Execution time: {execution_time:.2f} seconds ({execution_time/60:.2f} minutes)")
                successful_runs += 1
                status = "SUCCESS"
            else:
                print(f"❌ Run {run_num} failed with return code {result.returncode}")
                print(f"⏱️  Execution time: {execution_time:.2f} seconds ({execution_time/60:.2f} minutes)")
                failed_runs += 1
                status = "FAILED"
            
            run_results.append({
                'run': run_num,
                'status': status,
                'execution_time': execution_time,
                'output_dir': output_dir,
                'return_code': result.returncode
            })
            
        except Exception as e:
            print(f"❌ Run {run_num} failed with exception: {e}")
            failed_runs += 1
            run_results.append({
                'run': run_num,
                'status': 'EXCEPTION',
                'execution_time': 0,
                'output_dir': output_dir,
                'return_code': -1,
                'error': str(e)
            })
        
        finally:
            # Clean up temporary script
            if temp_script.exists():
                temp_script.unlink()
        
        print(f"Run {run_num} completed")
        print("-" * 40)
    
    # Print final summary
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    print(f"Total runs: {args.runs}")
    print(f"Successful runs: {successful_runs}")
    print(f"Failed runs: {failed_runs}")
    print(f"Success rate: {(successful_runs/args.runs)*100:.1f}%")
    
    print("\nDetailed Results:")
    for result in run_results:
        status_emoji = "✅" if result['status'] == "SUCCESS" else "❌"
        print(f"  {status_emoji} Run {result['run']}: {result['status']} "
              f"({result['execution_time']:.1f}s) -> {result['output_dir'].name}")
        if 'error' in result:
            print(f"    Error: {result['error']}")
    
    print(f"\nOutput directories created in: {base_dir / 'main_output'}")
    date_example = datetime.now().strftime('%d%m%y')
    print(f"You can find the results in directories named: {date_example}-1, {date_example}-2, etc.")
    
    # Return appropriate exit code
    if failed_runs > 0:
        print(f"\nWARNING: {failed_runs} runs failed!")
        sys.exit(1)
    else:
        print("\n🎉 All runs completed successfully!")
        sys.exit(0)

if __name__ == "__main__":
    main()