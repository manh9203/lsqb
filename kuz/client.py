import time
import psutil
from timeout_decorator import timeout, TimeoutError
import sys
import kuzu
import logging

@timeout(600)  # Set the timeout to 10 minutes (600 seconds)
def run_query(conn, system_variant, sf, query_id, query_spec, results_file):
    start_time = time.time()

    # Monitor initial system usage
    initial_ram_usage = psutil.virtual_memory().used
    initial_disk_usage = psutil.disk_usage('/').used

    results = conn.execute(query_spec)
    if results.has_next():
        result = results.get_next()

    end_time = time.time()
    duration = end_time - start_time

    # Monitor final system usage
    final_ram_usage = psutil.virtual_memory().used
    final_disk_usage = psutil.disk_usage('/').used

    ram_change = final_ram_usage - initial_ram_usage
    disk_change = final_disk_usage - initial_disk_usage

    return duration, result


def main():
    if len(sys.argv) < 1:
        print("Usage: client.py sf")
        print("Where sf is the scale factor)")
        exit(1)
    else:
        sf = sys.argv[1]

    db = kuzu.Database('kuz/scratch/lsqb-database')
    conn = kuzu.Connection(db)

    with open(f"results/kuzudb_results.csv", "a+") as results_file:
        for i in range(1, 10):
            print(i)
            with open(f"kuz/q{i}.cypher", "r") as query_file:
                try:
                    runtime, result = run_query(conn, "", sf, i, query_file.read(), results_file)
                except TimeoutError:
                    results_file.write(f"{i},\tkuz/q{i}.cypher,\t{sf},\t,\t,\tTimeout,\tTime limit is set to 10 minutes\n")
                    results_file.flush()
                else:
                    results_file.write(f"{i},\tkuz/q{i}.cypher,\t{sf},\t{runtime:4f},\t{result[0]},\tSuccess,\t\n")
                    results_file.flush()

if __name__ == "__main__":
    logging.basicConfig(format='%(process)d-%(levelname)s-%(message)s', level=logging.DEBUG)
    main()
