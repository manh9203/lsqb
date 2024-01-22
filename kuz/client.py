import time
import psutil
import sys
import kuzu
import logging

def run_query(conn, numThreads, sf, query_id, query_spec, results_file):
    start_time = time.time()

    # Monitor initial system usage
    initial_ram_usage = psutil.virtual_memory().used

    try:
        results = conn.execute(query_spec)
        if results.has_next():
            result = results.get_next()
    except RuntimeError:
        return -1, -1, -1

    end_time = time.time()
    duration = end_time - start_time

    # Monitor final system usage
    final_ram_usage = psutil.virtual_memory().used
    ram_change = max(0, final_ram_usage - initial_ram_usage)

    return duration, ram_change, result


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

    with open(f"results/kuzudb_results.csv", "a+") as results_file:
        for i in range(1, 10):
            print(i)
            with open(f"kuz/q{i}.cypher", "r") as query_file:
                query_spec = query_file.read()
                duration, memory, result = run_query(conn, numThreads, sf, i, query_spec, results_file)

                if duration == -1:
                    results_file.write(f"KuzuDB\t{i}\t{numThreads} threads\t{sf}\tTimeout\tNA\tNA\t\n")
                    results_file.flush()
                else:
                    durations = [duration]
                    memories = [memory]

                    num_trials = 3

                    # Run the queries multiple times
                    for _ in range(num_trials):
                        duration, memory, result = run_query(conn, numThreads, sf, i, query_spec, results_file)
                        durations.append(duration)
                        memories.append(memory)

                    # Get avg duration
                    max_duration = max(durations)
                    durations.remove(max_duration) # Remove the worst record
                    duration = sum(durations) / len(durations)

                    # Get avg memory
                    filtered_memories = [x for x in memories if x != 0]
                    if len(filtered_memories) == 0:
                        memory = 0
                    else:
                        memory = sum(filtered_memories) / len(filtered_memories)
                    
                    # Print the result
                    results_file.write(f"KuzuDB\t{i}\t{numThreads} threads\t{sf}\t{duration:.4f}\t{memory / (1024 ** 3):.2f} GB\t{result[0]}\n")
                    results_file.flush()

if __name__ == "__main__":
    logging.basicConfig(format='%(process)d-%(levelname)s-%(message)s', level=logging.DEBUG)
    main()
