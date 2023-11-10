import os
import argparse
import sys
import configparser
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import threading
import multiprocessing
from tqdm import tqdm
import time

BUFFER_SIZE = 1000  # liczba par do buforowania
total_pairs_found = 0  # liczba znalezionych par
total_files_removed = 0  # liczba usuniętych plików

def process_files(root, files, pair_conditions, dirty_files, valid_pairs, lock, progress_bar, scanned_files_count, log_file, config):
    global total_pairs_found
    for file in files:
        if os.path.splitext(file)[1].lower() == '.mp3':
            file_path = os.path.normpath(os.path.join(root, file))
            progress_bar.set_postfix(file=file, refresh=True, count="")
            scanned_files_count.increment()  # Increment the scanned files counter
            for condition in pair_conditions:
                clean_tag = condition.get("clean_condition")
                dirty_tag = condition.get("dirty_condition")
                if clean_tag and dirty_tag:
                    if clean_tag.lower() in file.lower():
                        for dirty_file in dirty_files:
                            if os.path.basename(file_path).split(clean_tag)[0] == os.path.basename(dirty_file).split(dirty_tag)[0]:
                                with lock:
                                    if check_pair_conditions(file_path, dirty_file, pair_conditions):
                                        valid_pairs.append((file_path, dirty_file))
                                        progress_bar.update(1)
                                        log_to_file(log_file, f"Znaleziono parę plików: {file_path}, {dirty_file}", config)
                                        total_pairs_found += 1  # Increment the global variable
                                break

def check_pair_conditions(file_path, dirty_file, pair_conditions):
    for condition in pair_conditions:
        condition_clean = condition.get("clean_condition")
        condition_dirty = condition.get("dirty_condition")
        if condition_clean and condition_dirty:
            if condition_clean.lower() in file_path.lower() and condition_dirty.lower() in dirty_file.lower():
                return True
    return False

def write_pairs_to_file(output_file, pairs):
    with open(output_file, 'a', encoding='utf-8') as f:
        for pair in pairs:
            f.write(pair[0] + "\n")
            f.write(pair[1] + "\n")

def log_to_file(log_file, message, config):
    # Sprawdź, czy logowanie jest włączone
    if config.getboolean('GENERAL', 'log', fallback=False):
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(message + "\n")

def remove_files_based_on_condition(output_file, remove_condition, autoremove=False, log_file=None, config=None):
    global total_files_removed
    if not remove_condition:
        print("Brak warunków do usunięcia plików.")
        return

    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            files_to_remove = [line.strip().lower() for line in f if any(cond in line for cond in remove_condition)]

        if autoremove or not files_to_remove:
            for file_path in files_to_remove:
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        total_files_removed += 1  # Increment the global variable
                        print(f"Usunięto plik: {file_path}")
                        log_to_file(log_file, f"Usunięto plik: {file_path}", config)
                    else:
                        print(f"Plik nie istnieje: {file_path}")
                        log_to_file(log_file, f"Plik nie istnieje: {file_path}", config)
                except Exception as e:
                    print(f"Błąd podczas usuwania pliku {file_path}: {e}")
                    log_to_file(log_file, f"Błąd podczas usuwania pliku {file_path}: {e}", config)
        else:
            print("\nCzy chcesz usunąć następujące pliki? (Yes/No)\n")
            for file_path in files_to_remove:
                print(file_path)

            user_input = input("\nWpisz Yes, aby potwierdzić usunięcie, lub No, aby anulować: ").lower().strip()

            if user_input == 'yes':
                for file_path in files_to_remove:
                    try:
                        if os.path.exists(file_path):
                            os.remove(file_path)
                            total_files_removed += 1  # Increment the global variable
                            print(f"Usunięto plik: {file_path}")
                            log_to_file(log_file, f"Usunięto plik: {file_path}", config)
                        else:
                            print(f"Plik nie istnieje: {file_path}")
                            log_to_file(log_file, f"Plik nie istnieje: {file_path}", config)
                    except Exception as e:
                        print(f"Błąd podczas usuwania pliku {file_path}: {e}")
                        log_to_file(log_file, f"Błąd podczas usuwania pliku {file_path}: {e}", config)
            else:
                print("Operacja usunięcia anulowana.")

    except FileNotFoundError:
        print(f"Plik {output_file} nie istnieje. Brak plików do usunięcia.")

def find_and_save_files(base_folder, output_file, pair_conditions, use_threadpool_executor, buffer_size, remove_files, autoremove, config):
    clean_files = set()
    dirty_files = set()
    valid_pairs = []
    lock = threading.Lock()
    buffer = []

    log_enabled = config.getboolean('GENERAL', 'log', fallback=False)

    if use_threadpool_executor:
        executor_class = ThreadPoolExecutor
        max_workers = os.cpu_count()
    else:
        executor_class = ProcessPoolExecutor
        max_workers = multiprocessing.cpu_count()

    start_time = time.time()
    scanned_files_count = Counter()  # Initialize the scanned files counter

    with tqdm(total=buffer_size) as progress_bar:
        with executor_class(max_workers=max_workers) as executor:
            futures = []
            for root, dirs, files in os.walk(base_folder):
                for file in files:
                    if os.path.splitext(file)[1].lower() == '.mp3':
                        file_path = os.path.normpath(os.path.join(root, file))
                        for condition in pair_conditions:
                            clean_tag = condition.get("clean_condition")
                            dirty_tag = condition.get("dirty_condition")
                            if clean_tag and dirty_tag:
                                if clean_tag.lower() in file.lower():
                                    clean_files.add(file_path)
                                elif dirty_tag.lower() in file.lower():
                                    dirty_files.add(file_path)
                                else:
                                    pass
                        progress_bar.update(1)

            if log_enabled:
                log_file = config.get('LOG', 'log_file', fallback='log.txt')
            else:
                log_file = None  # Ustawiamy log_file na None, aby uniknąć tworzenia niepotrzebnego pliku logów

            for root, dirs, files in os.walk(base_folder):
                futures.append(executor.submit(process_files, root, files, pair_conditions, dirty_files, valid_pairs, lock, progress_bar, scanned_files_count, log_file, config))

            for future in futures:
                future.result()

    elapsed_time = time.time() - start_time

    for pair in valid_pairs:
        buffer.append(pair)
        if len(buffer) >= buffer_size:
            write_pairs_to_file(output_file, buffer)
            buffer = []

    if buffer:
        write_pairs_to_file(output_file, buffer)

    if autoremove:
        remove_condition = load_remove_condition(config)
        remove_files_based_on_condition(output_file, remove_condition, autoremove=True, log_file=log_file, config=config)
    elif remove_files:
        remove_condition = load_remove_condition(config)
        remove_files_based_on_condition(output_file, remove_condition, autoremove=False, log_file=log_file, config=config)

    # Dodano informacje o liczbie znalezionych par i liczbie usuniętych plików na końcu pliku logów
    if log_enabled:
        log_to_file(log_file, f"Liczba znalezionych par: {total_pairs_found}", config)
        log_to_file(log_file, f"Liczba usuniętych plików: {total_files_removed}", config)

    print(f"Znaleziono {len(valid_pairs)} par plików.")
    print(f"Zeskanowano {scanned_files_count.value} plików.")
    print(f"Czas operacji: {elapsed_time} sekundy.")

class Counter:
    def __init__(self):
        self.value = 0

    def increment(self):
        self.value += 1

def load_remove_condition(config):
    remove_condition = set()
    if 'WHATAUTOREMOVE' in config.sections():
        for option in config.options('WHATAUTOREMOVE'):
            remove_condition.add(config.get('WHATAUTOREMOVE', option))
    return remove_condition

def load_config(file_path):
    config = configparser.ConfigParser()
    try:
        config.read(file_path)

        pair_conditions = []
        use_threadpool_executor = False
        buffer_size = BUFFER_SIZE
        remove_files = False
        autoremove = False

        for section in config.sections():
            if section.startswith('PAIR'):
                conditions = {option: config.get(section, option) for option in config.options(section)}
                pair_conditions.append(conditions)

        if 'GENERAL' in config.sections():
            use_threadpool_executor = config.getboolean('GENERAL', 'use_threadorpoolexecutor', fallback=False)
            buffer_size = config.getint('GENERAL', 'buffer_size', fallback=BUFFER_SIZE)
            remove_files = config.getboolean('GENERAL', 'remove', fallback=False)
            autoremove = config.getboolean('GENERAL', 'autoremove', fallback=False)

        return config, pair_conditions, use_threadpool_executor, buffer_size, remove_files, autoremove
    except Exception as e:
        print(f"Błąd odczytu pliku konfiguracyjnego: {e}")
        return None, None, None, None, None, None

def print_help():
    print("FCDJ - File Cloner DJPools Detector 0.1 by DJ PD\n")
    print("Options:")
    print("  -base BASE      (Base folder for searching)")
    print("  -output OUTPUT  (Output file to store valid pairs.)")
    print("  -config CONFIG  (Path to the config file)")
    print("Example usage:")
    print("python script.py -config config.cfg")

def main():
    parser = argparse.ArgumentParser(
        description="FCDJ - File Cloner DJPools Detector 0.1 by Piotr Dawidczyk",
        epilog="Example usage:\npython script.py -config config.cfg",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("-base", required=False, default="", help="(Base folder for searching)")
    parser.add_argument("-output", required=False, default="", help="(Output file to store valid pairs.)")
    parser.add_argument("-config", required=False, default="", help="(Path to the config file)")
    parser.add_argument("-help", action="store_true", help="Show help message")

    args = parser.parse_args()

    if args.help:
        print_help()
        sys.exit()

    if args.config:
        config, pair_conditions, use_threadpool_executor, buffer_size, remove_files, autoremove = load_config(args.config)

        if config is not None:
            base_folder = config.get("BASE", "path")
            output_file = config.get("OUTPUT", "output_file")
            find_and_save_files(base_folder, output_file, pair_conditions, use_threadpool_executor, buffer_size, remove_files, autoremove, config)
    else:
        find_and_save_files(args.base, args.output, pair_conditions, use_threadpool_executor, BUFFER_SIZE, False, None, False)

if __name__ == "__main__":
    main()
