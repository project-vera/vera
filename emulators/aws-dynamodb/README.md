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

Options:

```bash
python eval_emulator.py --start-from 10               # resume from command 10
python eval_emulator.py --checkpoint out.json         # custom output file
python eval_emulator.py --endpoint http://localhost:5006
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

## API Coverage

### Supported operations

vera supports all operations that DynamoDB Local 3.3.0 implements. Table lifecycle operations go through vera's state machine; all others are proxied directly.

| Layer | Operations |
|---|---|
| State machine | `CreateTable`, `DeleteTable`, `UpdateTable` |
| Proxied directly | `DescribeTable`, `ListTables`, `PutItem`, `GetItem`, `UpdateItem`, `DeleteItem`, `BatchGetItem`, `BatchWriteItem`, `Query`, `Scan`, `TransactGetItems`, `TransactWriteItems`, `DescribeTimeToLive`, `UpdateTimeToLive`, `DescribeLimits`, and all other core data-plane operations |

### Unsupported operations

The following operations are not implemented by DynamoDB Local 3.3.0 and return `UnknownOperationException`. They are not emulated by vera either.

| Category | Operations |
|---|---|
| Backups | `CreateBackup`, `DeleteBackup`, `DescribeBackup`, `ListBackups`, `RestoreTableFromBackup`, `RestoreTableToPointInTime`, `DescribeContinuousBackups`, `UpdateContinuousBackups` |
| Global Tables | `CreateGlobalTable`, `DescribeGlobalTable`, `DescribeGlobalTableSettings`, `ListGlobalTables`, `UpdateGlobalTable`, `UpdateGlobalTableSettings` |
| Contributor Insights | `DescribeContributorInsights`, `ListContributorInsights`, `UpdateContributorInsights` |
| Other | `DescribeEndpoints`, `DescribeTableReplicaAutoScaling`, `UpdateTableReplicaAutoScaling` |

## Test Coverage

Test commands are sourced from 41 RST example files crawled from the [aws-cli examples](https://github.com/aws/aws-cli/tree/develop/awscli/examples/dynamodb) repo, covering 74 example commands in total.

### Command filtering

| Filter | Count | Reason |
|---|---|---|
| Contains `--*-id` / `--*-arn` parameters | 7 | Require dynamically generated IDs unavailable at test time |
| Contains `file://` parameters | 23 | Require local fixture files not present in the test environment |
| **Runnable** | **44** | Executed by the evaluator |

### Output comparison

The evaluator compares actual emulator output against the RST golden output after stripping fields whose values are inherently dynamic or environment-specific:

| Ignored field | Reason |
|---|---|
| `TableStatus` | vera completes state transitions synchronously; RST shows transient states (`CREATING`, `DELETING`) that never appear in practice |
| `CreationDateTime`, `LastIncreaseDateTime`, `LastDecreaseDateTime`, `LastUpdateToPayPerRequestDateTime`, `LatestStreamLabel` | Timestamps differ every run |
| `TableArn`, `IndexArn`, `LatestStreamArn` | ARNs contain account ID and region, which differ from real AWS |
| `TableId` | UUID generated per-run |
| `ItemCount`, `TableSizeBytes`, `IndexSizeBytes` | Runtime data, not present at table creation |
| `TableNames` | RST golden output contains real AWS account table names |
| `NextToken` | RST pagination tokens are fake placeholders |

Comparison uses **subset matching**: expected fields must be present and equal in the actual response, but the actual response may contain additional fields. List fields (e.g. `AttributeDefinitions`, `KeySchema`) are compared order-independently.

`TableId` and `TableArn` are not used as inputs to any subsequent command in the RST examples — DynamoDB always references tables by name, not ID or ARN — so ignoring them does not mask cross-command dependency issues.

### Results

| Metric | Count | % of runnable |
|---|---|---|
| Runnable commands | 44 | — |
| Exit OK + output match | 7 | 15.9% |
| Exit failed (UnknownOperationException) | 22 | 50.0% |
| Exit failed (table not found / state ordering) | 12 | 27.3% |
| Exit failed (shell parse error) | 3 | 6.8% |

The 22 `UnknownOperationException` failures are expected — they correspond exactly to the unsupported operations listed above. The 12 "table not found" failures are caused by RST files that assume a pre-existing table without a preceding `CreateTable` step (single-command examples that expect the table to already exist). The 3 shell parse errors are RST formatting issues in the aws-cli examples themselves (unbalanced quotes).

Excluding the structurally-unrunnable commands (UnknownOperationException + shell errors), the effective pass rate is **7/19 = 36.8%** for commands that could succeed.

## Configuration

| Environment variable | Default | Description |
|---|---|---|
| `VERA_HOST` | `127.0.0.1` | Bind address |
| `VERA_PORT` | `5005` | Listen port |
| `DYNAMODB_LOCAL_URL` | `http://localhost:8000` | DynamoDB Local endpoint |
| `DYNAMODB_LOCAL_JAR` | `./dynamodb-local/DynamoDBLocal.jar` | Path to DynamoDB Local JAR |
| `DYNAMODB_LOCAL_LIB` | `./dynamodb-local/DynamoDBLocal_lib` | Path to native libs |
