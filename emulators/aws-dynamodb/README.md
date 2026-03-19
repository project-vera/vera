# Vera AWS DynamoDB

Local Amazon DynamoDB emulator with state machine enforcement.

Built on top of [DynamoDB Local](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html) (official AWS image) as the data backend. Vera adds a state machine layer that enforces table lifecycle transitions and blocks invalid operations — matching the behavior of real DynamoDB.

## Architecture

```
Client (AWS CLI / boto3 / SDK)
        │
        ▼
vera-dynamodb  :5005   ← state machine + proxy (this service)
        │
        ▼
dynamodb-local :8000   ← data storage (official AWS image, embedded)
```

**vera-dynamodb** intercepts table lifecycle operations (`CreateTable`, `DeleteTable`, `UpdateTable`) to enforce state transitions:

```
CREATING → ACTIVE → UPDATING → ACTIVE
                 ↘           ↗
                  DELETING (terminal)
```

All other operations (`PutItem`, `GetItem`, `Query`, `Scan`, `BatchWriteItem`, etc.) are passed straight through to DynamoDB Local.

On startup, vera syncs existing tables from DynamoDB Local into its state machine as `ACTIVE`.

## Setup

### Local development

```bash
./install.sh
```

This will:
- Install Python dependencies via `uv`
- Install Java if not present (required by DynamoDB Local)
- Download the DynamoDB Local JAR to `./dynamodb-local/`
- Add a `[vera]` profile to `~/.aws/credentials`
- Create an `awscli` wrapper in `.venv/bin/` that points to `http://localhost:5005`

Then start the emulator:

```bash
uv run python main.py
```

vera-dynamodb starts DynamoDB Local as a subprocess on port 8000, then listens on port 5005.

Use the `awscli` wrapper to avoid typing `--endpoint-url` every time:

```bash
uv run awscli dynamodb list-tables
uv run awscli dynamodb create-table \
  --table-name Users \
  --attribute-definitions AttributeName=id,AttributeType=S \
  --key-schema AttributeName=id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST
```

### With Docker Compose

vera-dynamodb bundles DynamoDB Local inside the same container — no separate service needed.

From the repo root:

```bash
docker compose up vera-dynamodb
```

vera-dynamodb is available at `http://localhost:5005`.

## Usage

Point any AWS CLI or SDK at `http://localhost:5005` with any credentials (DynamoDB Local ignores auth).

### AWS CLI

```bash
aws dynamodb create-table \
  --endpoint-url http://localhost:5005 \
  --table-name Users \
  --attribute-definitions AttributeName=id,AttributeType=S \
  --key-schema AttributeName=id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST

aws dynamodb put-item \
  --endpoint-url http://localhost:5005 \
  --table-name Users \
  --item '{"id": {"S": "user-1"}, "name": {"S": "Alice"}}'

aws dynamodb get-item \
  --endpoint-url http://localhost:5005 \
  --table-name Users \
  --key '{"id": {"S": "user-1"}}'

aws dynamodb list-tables --endpoint-url http://localhost:5005
aws dynamodb delete-table --endpoint-url http://localhost:5005 --table-name Users
```

Set `AWS_ENDPOINT_URL_DYNAMODB` to avoid repeating `--endpoint-url`:

```bash
export AWS_ENDPOINT_URL_DYNAMODB=http://localhost:5005
aws dynamodb list-tables
```

### boto3 (Python)

```python
import boto3

ddb = boto3.client(
    "dynamodb",
    endpoint_url="http://localhost:5005",
    region_name="us-east-1",
    aws_access_key_id="fake",
    aws_secret_access_key="fake",
)

ddb.create_table(
    TableName="Orders",
    AttributeDefinitions=[{"AttributeName": "order_id", "AttributeType": "S"}],
    KeySchema=[{"AttributeName": "order_id", "KeyType": "HASH"}],
    BillingMode="PAY_PER_REQUEST",
)

ddb.put_item(
    TableName="Orders",
    Item={"order_id": {"S": "ord-123"}, "status": {"S": "pending"}},
)

resp = ddb.get_item(TableName="Orders", Key={"order_id": {"S": "ord-123"}})
print(resp["Item"])
# {'order_id': {'S': 'ord-123'}, 'status': {'S': 'pending'}}
```

## Testing

Tests live in `tests/`. The test suite uses 44 AWS CLI commands crawled from the official [aws-cli examples](https://github.com/aws/aws-cli/tree/develop/awscli/examples/dynamodb) (stored in `tests/cli/dynamodb/`).

### Run the evaluator

With the emulator running (`uv run python main.py`):

```bash
cd tests
python eval_emulator.py test.sh
```

The evaluator runs each command and reports pass/fail based on exit code (0 = pass). Results are saved to `eval_results.json` with full stdout/stderr for inspection.

```
Passed:  36  (81.1%)
Failed:  8   (18.9%)
```

Failures are DynamoDB Local limitations — operations it doesn't implement (tagging, backups, DAX-adjacent endpoints). These are not vera state machine failures.

Options:

```bash
python eval_emulator.py test.sh --start-from 10      # resume from command 10
python eval_emulator.py test.sh --checkpoint out.json # custom output file
python eval_emulator.py test.sh --endpoint http://localhost:5006
```

### Regenerate test.sh

```bash
cd tests
python -c "
import sys; sys.path.insert(0, '.')
from utils.print_commands_with_endpoint import print_commands
from utils.parse_aws_commands import parse_aws_commands_from_directory
from pathlib import Path
data = parse_aws_commands_from_directory(Path('cli/dynamodb'), quiet=True)
print_commands(data, include_id=False, include_file=False)
" > test.sh
```

### e2e tests (boto3)

```bash
cd tests
uv run pytest test_e2e.py -v
```

## State Machine Enforcement

vera blocks operations that would be invalid on real DynamoDB:

| Operation | Blocked when table is |
|---|---|
| `CreateTable` | Already exists (`ACTIVE`, `CREATING`, `UPDATING`) |
| `DeleteTable` | `CREATING` or already `DELETING` |
| `UpdateTable` | `CREATING` or `DELETING` |

Blocked operations return the same error codes as real DynamoDB:
- `ResourceInUseException` — table exists or is in a conflicting state
- `ResourceNotFoundException` — table does not exist

## Configuration

| Environment variable | Default | Description |
|---|---|---|
| `VERA_HOST` | `127.0.0.1` | Bind address |
| `VERA_PORT` | `5005` | Listen port |
| `DYNAMODB_LOCAL_URL` | `http://localhost:8000` | DynamoDB Local endpoint |
| `DYNAMODB_LOCAL_JAR` | `./dynamodb-local/DynamoDBLocal.jar` | Path to DynamoDB Local JAR |
| `DYNAMODB_LOCAL_LIB` | `./dynamodb-local/DynamoDBLocal_lib` | Path to native libs |

## Supported Operations

All DynamoDB API operations are supported. Table lifecycle operations go through vera's state machine; all others are proxied directly.

**State machine layer:** `CreateTable`, `DeleteTable`, `UpdateTable`

**Proxied directly:** `DescribeTable`, `ListTables`, `PutItem`, `GetItem`, `UpdateItem`, `DeleteItem`, `BatchGetItem`, `BatchWriteItem`, `Query`, `Scan`, `TransactGetItems`, `TransactWriteItems`, `DescribeTimeToLive`, `UpdateTimeToLive`, and all other DynamoDB operations.
