from multiprocessing import Pool, current_process
import time

def process(x):
    try:
        time.sleep(3)
        return (x*x, current_process().name)
    except KeyboardInterrupt:
        print("Shutting down")

if __name__ == '__main__':
    with Pool(processes=20) as pool:
        tasks = pool.imap_unordered(process, range(0, 26))
        try:
            for n, name in tasks:
                print(n, name)
        except KeyboardInterrupt:
            print("Interrupt. Shutting down.")
            pool.terminate()
            pool.join()

