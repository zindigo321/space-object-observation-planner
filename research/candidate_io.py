"""Decode frozen NDJSON in bounded batches with shared keys and repeated values."""
import gzip
import json
from itertools import islice

def read_candidates(path):
    rows = []
    times, windows, priorities, statuses, numbers = {}, {}, {}, {}, {}
    with gzip.open(path, 'rb') as f:
        while True:
            lines = list(islice(f, 2048))
            if not lines:
                return rows
            batch = json.loads(b'[' + b','.join(line for line in lines if line.strip()) + b']')
            for row in batch:
                for key, pool in (('start_utc', times), ('end_utc', times), ('window_id', windows),
                                  ('priority', priorities), ('status', statuses), ('satnum', numbers)):
                    value = row[key]
                    row[key] = pool.setdefault(value, value)
                if row['task_id'] == row['candidate_id']:
                    row['task_id'] = row['candidate_id']
            rows.extend(batch)

