import time
import psutil
import sys
import kuzu
import logging

def run_query(conn, numThreads, sf, query_id, query_spec, results_file):
    start_time = time.time()

    # Monitor initial system usage
    initial_ram_usage = psutil.virtual_memory().used
    initial_disk_usage = psutil.disk_usage('/').used

    try:
        results = conn.execute(query_spec)
        if results.has_next():
            result = results.get_next()
    except RuntimeError:
        return

    end_time = time.time()
    duration = end_time - start_time

    # Monitor final system usage
    final_ram_usage = psutil.virtual_memory().used
    final_disk_usage = psutil.disk_usage('/').used

    ram_change = final_ram_usage - initial_ram_usage
    disk_change = final_disk_usage - initial_disk_usage
    
    results_file.write(f"KuzuDB\t{query_id}\t{numThreads} threads\t{sf}\t{duration:.4f}\t{result[0]}\t")
    results_file.write(f"{ram_change / (1024 ** 3):.2f} GB\n")
    results_file.flush()

    return (duration, result)


def main():
    if len(sys.argv) < 2:
        print("Usage: client.py sf")
        print("Where sf is the scale factor)")
        exit(1)
    else:
        sf = sys.argv[1]
    
    if len(sys.argv) > 2:
        numThreads = int(sys.argv[2])
    else:
        numThreads = 4

    db = kuzu.Database('kuz/scratch/lsqb-database')
    conn = kuzu.Connection(db, num_threads=numThreads)
    conn.set_query_timeout(600000) # Set timeout to 10 minutes

    with open(f"results/results.csv", "a+") as results_file:
        for i in range(1, 10):
            if sf != "example" and float(sf) >= 1 and i == 3:
                continue
            print(i)
            with open(f"kuz/q{i}.cypher", "r") as query_file:
                run_query(conn, numThreads, sf, i, query_file.read(), results_file)

if __name__ == "__main__":
    logging.basicConfig(format='%(process)d-%(levelname)s-%(message)s', level=logging.DEBUG)
    main()
