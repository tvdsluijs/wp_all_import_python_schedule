import time


def pc():
    start = time.perf_counter()
    time.sleep(10)
    print(time.perf_counter()-start)


def pt():
    start = time.process_time()
    time.sleep(10)
    print(time.process_time()-start)


pc()
pt()
