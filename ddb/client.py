import duckdb
import time
import psutil
import sys
import signal
from contextlib import contextmanager

@contextmanager
def timeout(t):
    signal.signal(signal.SIGALRM, raise_timeout)
    signal.alarm(t)

    try:
        yield
    except TimeoutError:
        raise
    finally:
        signal.signal(signal.SIGALRM, signal.SIG_IGN)

def raise_timeout(signum, frame):
    raise TimeoutError

def run_query(con, sf, query_id, query_spec, numThreads, results_file):
    start = time.time()
    initial_ram_usage = psutil.virtual_memory().used
    try:
        with timeout(600):
            con.execute(f"PRAGMA threads={numThreads};\n" + query_spec)
    except TimeoutError:
        return -1, -1, -1
    result = con.fetchall()
    end = time.time()
    duration = end - start
    final_ram_usage = psutil.virtual_memory().used
    ram_change = max(0, final_ram_usage - initial_ram_usage)
    return duration, ram_change, result

if len(sys.argv) < 2:
    print("Usage: client.py sf [threads]")
    print("where sf is the scale factor")
    exit(1)
else:
    sf = sys.argv[1]

if len(sys.argv) > 2:
    numThreads = int(sys.argv[2])
else:
    numThreads = 4

con = duckdb.connect(database='ddb/scratch/ldbc.duckdb', read_only=True)

with open(f"results/duckdb_results.csv", "a+") as results_file:
    for i in range(1, 10):
        print(i)
        with open(f"sql/q{i}.sql", "r") as query_file:
            query_spec = query_file.read()
            durations = []
            memories = []
            duration, memory, result = run_query(con, sf, i, query_spec, numThreads, results_file)
            if duration == -1:
                results_file.write(f"DuckDB\t{i}\t{numThreads} threads\t{sf}\tTimeout\tNA\tNA\t\n")
                results_file.flush()
            else:
                durations.append(duration)
                memories.append(memory)
                if duration <= 60:
                    num_trials = 5
                else:
                    num_trials = 3
                # Run the queries multiple times
                for j in range(1, num_trials):
                    duration, memory, result = run_query(con, sf, i, query_spec, numThreads, results_file)
                    durations.append(duration)
                    memories.append(memory)
                # Get avg duration
                max_number = max(durations)
                durations.remove(max_number) # Remove the worst record
                duration = sum(durations) / len(durations)
                # Get max memory
                memory = max(memories)
                # Print the result
                results_file.write(f"DuckDB\t{i}\t{numThreads} threads\t{sf}\t{duration:.4f}\t{memory / (1024 ** 3):.2f} GB\t{result[0][0]}\t")
                results_file.write(f"{num_trials} times\n")
                results_file.flush()

con.close()
