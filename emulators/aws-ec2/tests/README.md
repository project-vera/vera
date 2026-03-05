# AWS EC2 CLI Tests

This directory contains automated tests for AWS EC2 CLI commands, supporting both:
- **EC2 Emulator** (custom implementation)
- **LocalStack** (AWS cloud emulator)

## Quick Start

### Generate Test Commands

The test commands are automatically extracted from AWS CLI documentation (RST files in `cli/` directory).

```bash
# For EC2 Emulator (uses awscli wrapper)
python print_commands_with_endpoint.py > test.sh

# For LocalStack (adds --endpoint-url)
python print_commands_with_endpoint.py --ls > test_ls.sh

# Include commands with ID parameters
python print_commands_with_endpoint.py --include-id > test.sh

# Include all commands (with ID and file parameters)
python print_commands_with_endpoint.py --include-id --include-file > test_full.sh

# Custom LocalStack endpoint
python print_commands_with_endpoint.py --ls --endpoint http://localhost:8080 > test.sh
```

**Default filtering:** Commands requiring resource IDs or file paths are excluded (260/901 commands).

## Running Tests

### Test Against EC2 Emulator

1. **Start the emulator:**
   ```bash
   # Start emulator on port 5003
   uv run main.py
   ```

2. **Generate and run tests:**
   ```bash
   python print_commands_with_endpoint.py > test.sh

   # under aws-ec2/
   source .venv/bin/activate 
   python eval_emulator.py test.sh
   ```

3. **Resume from checkpoint:**
   ```bash
   # Resume from command index 100
   python eval_emulator.py test.sh --start-from 100
   ```

### Test Against LocalStack

1. **Start LocalStack:**
   ```bash
   localstack start
   ```

2. **Generate and run tests:**
   ```bash
   python print_commands_with_endpoint.py --ls > test_ls.sh
   python eval_ls.py test_ls.sh
   ```

**Note:** `eval_ls.py` restarts LocalStack before each command to ensure clean state.

**Output example:**
```
================================================================================
Command 249/260
================================================================================
Command: aws --endpoint-url=http://localhost:4566 ec2 register-image --name my-image...
  → Restarting LocalStack...
  → Waiting for LocalStack to be ready...
  → Running command...
  ✓ Success (exit code: 0)
  → Saving checkpoint...
```

## Results & Analysis

Results are saved in JSON format with checkpoints after each command.

**View results:**
```bash
# Emulator results
cat eval_results_emulator.json

# LocalStack results  
cat eval_results.json

# Analyze results
python analyze_results.py eval_results_emulator.json
```

**Summary:**
```
================================================================================
LocalStack: EVALUATION COMPLETE
================================================================================
Total commands: 260
Successful: 122 (46.9%)
Failed: 138 (53.1%)
Total runtime: 1947.95s (32.47 minutes)

================================================================================
EVALUATION COMPLETE
================================================================================
Total commands: 274
Successful: 221 (80.7%)
Failed: 53 (19.3%)
Total runtime: 248.73s (4.15 minutes)
```
