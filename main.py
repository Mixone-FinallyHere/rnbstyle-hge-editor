from config import Config
from csv_parser import list_csv_files, read_csv, parse_csv
from export import print_data
from validity_checker import init_defines
from file_manager import create_backup

# main.py
def main(config):
    from csv_parser import list_csv_files, read_csv, parse_csv
    from export import print_data
    from validity_checker import init_defines
    from file_manager import create_backup

    init_defines()

    if config.CREATE_BACKUP:
        create_backup(config.OUTPUT_FILE, config.BACKUP_FILE)

    csv_files = list_csv_files(config.INPUT_DIR)

    for file in csv_files:
        rows = read_csv(file)
        data = parse_csv(rows)
        print_data(data, config.OUTPUT_FILE)


if __name__ == "__main__":
    from config import Config
    main(Config())

