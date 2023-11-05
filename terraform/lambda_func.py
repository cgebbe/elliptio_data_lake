import json


def lambda_handler(_event, _context):
    return {"statusCode": 200, "body": json.dumps("Hello from Lambda!")}
