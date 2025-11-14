_benchmark_call_stack = []

import functools
import logging
import time


def benchmark(func, level=logging.INFO):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Get nesting depth
        depth = len(_benchmark_call_stack)
        indent = "  " * depth

        # Start timing
        start_time = time.time()
        _benchmark_call_stack.append(
            {"func_name": func.__name__, "start_time": start_time}
        )

        logging.log(level, f"{indent}┌{'─' * 38}")
        logging.log(level, f"{indent}│ BENCHMARK: {func.__name__:<25} │")
        logging.log(level, f"{indent}├{'─' * 38}")
        logging.log(level, f"{indent}│ Started at: {start_time:.6f}           │")
        logging.log(level, f"{indent}│{' ' * 36}│")

        try:
            result = func(*args, **kwargs)
            return result
        finally:
            end_time = time.time()
            total_time = end_time - start_time

            logging.log(level, f"{indent}│{' ' * 36}│")
            logging.log(level, f"{indent}│ Ended at: {end_time:.6f}             │")
            logging.log(level, f"{indent}│ Total time: {total_time:.6f} sec      │")
            logging.log(level, f"{indent}└{'─' * 38}")
            _benchmark_call_stack.pop()

    return wrapper
