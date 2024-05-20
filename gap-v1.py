import os
import csv
import time
import datetime
import threading
from datetime import datetime
from tabulate import tabulate
from collections import Counter
from collections import defaultdict
import pandas as pd

# from your_module_name import get_category

# Define the ITEM_MAPPING dictionary
ITEM_MAPPING = {
    "to": "TOMATO",
    "ca": "CABBAGE",
    "co": "CORN",
    "cr": "CARROT",
    "10": "HOT DOG",
    "15": "MEAT SKEWERS",
    "25": "CHICKEN THIGHS",
    "45": "BEEF",
    "pi": "PIZZA",
    "sa": "SALAD",
}

MEATS = ["BEEF", "CHICKEN THIGHS", "MEAT SKEWERS", "HOT DOG", "PIZZA"]
VEGES = ["TOMATO", "CABBAGE", "CORN", "CARROT", "SALAD"]


def is_meat(item):
    return item in MEATS


def get_category(item):
    if is_meat(item):
        return "meats"
    else:
        return "veges"


def get_results_by_round(round_number):
    results_folder = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "results", "sorted&merged"
    )
    round_results = []

    for filename in os.listdir(results_folder):
        if filename.endswith(".csv"):
            csv_file = os.path.join(results_folder, filename)
            with open(csv_file, "r", newline="") as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    if "Round" in row and row["Round"] == str(round_number):
                        if "Result" in row:
                            round_results.append((row["Result"], row["Time"]))

    return round_results

def show_tables_for_round(round_number):
    results = get_results_by_round(round_number)
    if results:
        result_count = Counter()
        times_by_result = {}  # Dictionary to store times for each result

        for result, time_value in results:
            result_count[result] += 1
            times_by_result.setdefault(result, []).append(time_value)

        table_data = []
        for result, count in result_count.items():
            times = times_by_result[result]
            times_str = ", ".join(
                f"{time} ({times.count(time)})" for time in sorted(set(times))
            )

            # Calculate percentage with one decimal place
            percentage = (count / len(results)) * 100
            percentage_str = f"{percentage:.1f}%"

            table_data.append([result, count, percentage_str, times_str])

        headers = ["Result", "Count", "Percentage", "Times"]
        print(f"Search Results for Round {round_number}:")
        print_table_with_sort(table_data, headers)
        add_cons_items_table(table_data)
    else:
        print(f"No results found for Round {round_number}.")


def continue_from_current_round(current_round, increment=1):  # Option 2
    stop_flag = False

    def automatic_search():
        nonlocal current_round
        while not stop_flag and current_round <= 2160:
            results = get_results_by_round(current_round)
            if results:
                result_count = {}
                for result, time_value in results:
                    result_count[result] = result_count.get(
                        result, {"count": 0, "times": []}
                    )
                    result_count[result]["count"] += 1
                    result_count[result]["times"].append(time_value)

                table_data = []
                for result, info in result_count.items():
                    times_count = Counter(info["times"])
                    times_str = ", ".join(
                        [f"{time} ({count})" for time, count in times_count.items()]
                    )
                    count = info["count"]
                    percentage = (
                        count / sum(info["count"] for info in result_count.values())
                    ) * 100
                    table_data.append([result, count, f"{percentage:.1f}%", times_str])

                headers = ["Result", "Count", "Percentage", "Times"]
                print(f"Search Results for Round {current_round}:")
                # print(tabulate(table_data, headers=headers, tablefmt="grid"))
                print_table_with_sort(table_data, headers)
                add_cons_items_table(table_data)
            else:
                print(f"No results found for Round {current_round}.")

            current_round += increment
            time.sleep(15)

    def stop_function():
        nonlocal stop_flag
        stop_flag = True

    automatic_search_thread = threading.Thread(target=automatic_search)
    automatic_search_thread.start()

    while not stop_flag:
        user_input = input(
            "Enter 'c' to continue automatic search, 's' to stop, or 'exit' to go back to the main menu: "
        )
        if user_input.lower() == "c":
            continue
        elif user_input.lower() == "s":
            stop_function()
        elif user_input.lower() == "exit":
            stop_function()
            break
        else:
            print("Invalid input. Please enter 'c', 's', or 'exit'.")

    automatic_search_thread.join()


def continue_from_current_round_with_increment(current_round):
    increment = 1
    while True:
        continue_from_current_round(current_round, increment)


def generate_most_common_rounds_table(search_item):
    round_frequencies = {}

    results_folder = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "results", "sorted&merged"
    )
    for filename in os.listdir(results_folder):
        if filename.endswith(".csv"):
            csv_file = os.path.join(results_folder, filename)
            with open(csv_file, "r", newline="") as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    if "Result" in row and row["Result"].lower() == search_item.lower():
                        round_number = row.get("Round", "Unknown")
                        time_value = row.get("Time", "Unknown")

                        round_frequencies[round_number] = round_frequencies.get(
                            round_number, {"count": 0, "times": []}
                        )
                        round_frequencies[round_number]["count"] += 1
                        round_frequencies[round_number]["times"].append(time_value)

    # Sort by count in descending order
    sorted_rounds = sorted(
        round_frequencies.items(), key=lambda x: x[1]["count"], reverse=True
    )

    # Generate the table data with a separate percentage column
    total_occurrences = sum(info["count"] for _, info in round_frequencies.items())
    table_data = []
    for round_number, info in sorted_rounds:
        times_str = ", ".join(info["times"])
        occurrence_count = len(info["times"])
        percentage = (info["count"] / total_occurrences) * 100
        table_data.append([round_number, info["count"], percentage, times_str])

    headers = ["Round", "Count", "Percentage", "Times"]
    print(f"Most Common Rounds for '{search_item}':")
    print(tabulate(table_data, headers=headers, tablefmt="grid"))


def item_based_search(item):
    results_folder = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "results", "sorted&merged"
    )
    day_counts = {}
    day_items = {}

    for filename in os.listdir(results_folder):
        if filename.endswith(".csv"):
            csv_file = os.path.join(results_folder, filename)
            with open(csv_file, "r", newline="") as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    if "Result" in row and item.lower() == row["Result"].lower():
                        date_value = row.get("Date", "Unknown")
                        # Convert date to a datetime object with the correct format
                        date_object = datetime.strptime(date_value, "%d/%m/%Y")
                        # Get the day of the week (Monday = 0, Sunday = 6)
                        day_of_week = date_object.strftime("%A")

                        key = f"{day_of_week}"
                        if key not in day_counts:
                            day_counts[key] = 0
                            day_items[key] = {"times": [], "rounds": []}
                        day_counts[key] += 1
                        day_items[key]["times"].append(row.get("Time", "Unknown"))
                        day_items[key]["rounds"].append(
                            (row.get("Round", "Unknown"), row.get("Time", "Unknown"))
                        )

    table_data = []
    for key, count in day_counts.items():
        day_info = day_items[key]
        round_info = day_info["rounds"]
        round_info.sort(key=lambda x: x[1])  # Sort by time

        # Group round numbers based on their occurrence count
        round_count = Counter(round_num for round_num, _ in round_info)
        rounds = ", ".join(
            [f"{round_num} ({count})" for round_num, count in round_count.items()]
        )
        times = ", ".join([time for _, time in round_info])

        # Add a new line every 15 entries
        times = "\n".join([times[i : i + 20] for i in range(0, len(times), 20)])
        rounds = "\n".join([rounds[i : i + 20] for i in range(0, len(rounds), 20)])

        table_data.append((key, count, times, rounds))

    # Sort by count in descending order
    table_data.sort(key=lambda x: x[1], reverse=True)
    headers = ["Day", "Count", "Times", "Round Numbers"]
    print(f"Item Search Results for '{item}':")

    # Print the table using tabulate with the "grid" format
    print(tabulate(table_data, headers=headers, tablefmt="grid"))

    # Second table for most common round numbers and minutes
    most_common_rounds = []
    for key, day_info in day_items.items():
        round_info = day_info["rounds"]
        round_count = Counter(round_num for round_num, _ in round_info)
        if round_count:
            most_common_round = max(round_count, key=round_count.get)
            most_common_rounds.append(
                (key, most_common_round, round_count[most_common_round])
            )

    most_common_rounds.sort(key=lambda x: x[2], reverse=True)
    most_common_rounds_headers = ["Day", "Most Common Round", "Count"]

    print("\nMost Common Round Numbers and Minutes:")
    # Print the most common round numbers and minutes table using tabulate with the "grid" format
    print(
        tabulate(
            most_common_rounds, headers=most_common_rounds_headers, tablefmt="grid"
        )
    )

    # Export table data to a CSV file
    export_option = input("Export table data to CSV? (yes/no): ")
    if export_option.lower() == "yes":
        df = pd.DataFrame(table_data, columns=headers)
        df.to_csv(f"{item}_search_results.csv", index=False)
        print(f"Table data exported to {item}_search_results.csv")

def time_based_search(search_time):
    while True:
        try:
            validate_time_format(search_time)
            break
        except ValueError as e:
            print(e)
            search_time = input("Please enter the correct date format: ")

    results_folder = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "results", "sorted&merged"
    )
    matching_items = {}

    for filename in os.listdir(results_folder):
        if filename.endswith(".csv"):
            csv_file = os.path.join(results_folder, filename)
            with open(csv_file, "r", newline="") as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    if "Time" in row and is_time_match(row["Time"], search_time):
                        result = row.get("Result", "Unknown")
                        matching_items[result] = matching_items.get(result, 0) + 1

    total_occurrences = sum(count for count in matching_items.values())
    table_data = [
        (result, count, f"{(count / total_occurrences) * 100:.2f}%")
        for result, count in matching_items.items()
    ]

    # Sort by count in descending order
    table_data.sort(key=lambda x: x[1], reverse=True)
    headers = ["Result", "Count", "Percentage"]
    print(f"Results for '{search_time}':")
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    add_cons_items_table(table_data)


def is_time_match(actual_time, search_time):
    if "*" in search_time:
        search_hour, search_minute = search_time.split(":")
        actual_hour, actual_minute = actual_time.split(":")

        # Check if the minute matches after masking the first digit
        if search_minute[0] == '*' and actual_minute[1] == search_minute[1]:
            return True

        # Check if the hour matches
        if search_hour == "*":
            return actual_minute == search_minute
        elif search_minute == "*":
            return actual_hour == search_hour
    else:
        # Allow search in various formats
        actual_hour, actual_minute = actual_time.split(":")
        search_hour, search_minute = search_time.split(":")
        return (
            (actual_hour.zfill(2) == search_hour.zfill(2) and actual_minute == search_minute) or
            (actual_hour == search_hour and actual_minute == search_minute) or
            (actual_hour == search_time or actual_hour == search_time.split(" ")[0])
        )


def validate_time_format(time_str):
    try:
        # Attempt to parse the input time string
        _ = time_str.split(":")
    except ValueError:
        raise ValueError("Invalid time format. Please enter a valid time format.")

def print_table_with_sort(table_data, headers):  # sort function for all tables
    # Sort table_data in descending order based on the count column
    table_data.sort(key=lambda x: int(x[1]) if x[1] else 0, reverse=True)
    print(tabulate(table_data, headers=headers, tablefmt="grid"))


def calculate_total_occurrences(table_data):  # for all functions
    return sum(int(row[1]) if row[1] else 0 for row in table_data)


def add_cons_items_table(table_data):
    total_occurrences = calculate_total_occurrences(table_data)

    cons_items_data = [
        ["TOMATO (SKEWERS)", 0],
        ["CABBAGE (CHICKEN THIGH)", 0],
        ["CORN (BEEF)", 0],
        ["CARROT (HOT DOG)", 0],
        # ["SALAD (CABBAGE)", 0],
        # ["PIZZA (BEEF)", 0]
    ]

    times_counter = Counter()  # Counter to store unique times and their counts

    for row in table_data:
        item = row[0]
        count = row[1]
        times_str = row[2]

        # Check if times_str is a valid string
        if times_str and isinstance(times_str, str):
            times = times_str.split(", ")

            for time in times:
                if "(" in time:
                    time, count_in_braces = time.split("(")
                    count_in_braces = int(count_in_braces.strip(")"))
                    times_counter[time.strip()] += count_in_braces
                else:
                    times_counter[time.strip()] += 1

        if item == "MEAT SKEWERS":
            cons_items_data[0][1] += count
        elif item == "CHICKEN THIGHS":
            cons_items_data[1][1] += count
        elif item == "BEEF":
            cons_items_data[2][1] += count
        elif item == "HOT DOG":
            cons_items_data[3][1] += count
        elif item == "CARROT":
            cons_items_data[3][1] += count
        elif item == "TOMATO":
            cons_items_data[0][1] += count
        elif item == "CABBAGE":
            cons_items_data[1][1] += count
        elif item == "CORN":
            cons_items_data[2][1] += count
        # elif item == "PIZZA":
        # cons_items_data[2][1] += count
        # elif item == "SALAD":
        # cons_items_data[2][1] += count

    # Sort by count in descending order
    cons_items_data.sort(key=lambda x: x[1], reverse=True)

    # Calculate and add the percentage column with one decimal place
    for row in cons_items_data:
        percentage = (row[1] / total_occurrences) * 100
        row.append(
            f"{percentage:.1f}%"
        )  # Round off percentage to 1 decimal place and add '%' symbol

    headers = ["Cons. Items", "Count", "Percentage"]
    print_table_with_sort(cons_items_data, headers)


def get_common_items_for_round_range(start_round, end_round):
    common_items = {}
    for round_num in range(start_round, end_round + 1):
        results = get_results_by_round(round_num)
        for result, time_value in results:
            common_items[result] = common_items.get(result, {"count": 0, "times": []})
            common_items[result]["count"] += 1
            common_items[result]["times"].append(time_value)

    table_data = []
    for result, info in common_items.items():
        times = info["times"]
        times_str = ", ".join(
            f"{time} ({times.count(time)})" for time in sorted(set(times))
        )
        table_data.append([result, info["count"], times_str])

    # Sort by count in descending order
    table_data.sort(key=lambda x: x[1], reverse=True)
    headers = ["Result", "Count", "Times"]
    print(f"Common Items from Round {start_round} to Round {end_round}:")
    print_table_with_sort(table_data, headers)
    add_cons_items_table(table_data)


def search_next_three_items(search_items):
    items_to_search = search_items.split()
    search_sequence = " ".join(
        [ITEM_MAPPING.get(item, item) for item in items_to_search]
    )
    found_items = []

    with open("sorted_merged_file.csv", "r", newline="") as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            if "Result" in row:
                result_item = row["Result"]
                if result_item == search_sequence:
                    next_three_items = []
                    reverse_three_items = []

                    for _ in range(3):
                        next_row = next(csv_reader, None)
                        if next_row and "Result" in next_row:
                            next_item_name = ITEM_MAPPING.get(
                                next_row["Result"], next_row["Result"]
                            )
                            next_three_items.append(next_item_name)

                    # Reset the file pointer to find the reverse three items
                    file.seek(0)
                    for r_row in csv_reader:
                        if "Result" in r_row:
                            r_result_item = r_row["Result"]
                            if r_result_item == search_sequence:
                                break
                    prev_rows = []
                    for _ in range(
                        4
                    ):  # Fetch the four previous items (including the searched item)
                        prev_row = next(csv_reader, None)
                        if prev_row and "Result" in prev_row:
                            prev_item_name = ITEM_MAPPING.get(
                                prev_row["Result"], prev_row["Result"]
                            )
                            prev_rows.insert(
                                0, prev_item_name
                            )  # Insert at the beginning for reverse order

                    # Extract the reverse three items from the prev_rows
                    reverse_three_items = prev_rows[:3]

                    found_items.append(
                        (search_sequence, next_three_items, reverse_three_items)
                    )

    if found_items:
        headers = [
            "Searched Sequence",
            "Occurrence Count",
            "Next Three Items",
            "Reverse Three Items",
        ]
        table_data = [
            [item, len(found), ", ".join(next_items), ", ".join(rev_items)]
            for item, next_items, rev_items in found_items
        ]
        print(f"Search Results for '{search_sequence}':")
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
    else:
        print(f"No results found for the searched sequence: '{search_sequence}'.")


def categorize_items(items):
    meat = ["BEEF", "CHICKEN THIGHS", "MEAT SKEWERS", "HOT DOG", "PIZZA"]
    veg = ["TOMATO", "CABBAGE", "CORN", "CARROT", "SALAD"]

    meat_count = sum(1 for item in items if item in meat)
    veg_count = sum(1 for item in items if item in veg)

    if meat_count > veg_count:
        return "more meats"
    elif veg_count > meat_count:
        return "more veges"
    else:
        return "balanced"


def analyze_periods(results_folder):
    periods_table = {}
    meat_periods = 0
    veg_periods = 0

    for filename in os.listdir(results_folder):
        if filename.endswith(".csv"):
            csv_file = os.path.join(results_folder, filename)
            with open(csv_file, "r", newline="") as file:
                csv_reader = csv.DictReader(file)
                current_period = None
                current_items = []

                for row in csv_reader:
                    if "Result" in row:
                        result_item = row["Result"]
                        if (
                            result_item.startswith("to")
                            or result_item.startswith("ca")
                            or result_item.startswith("co")
                            or result_item.startswith("cr")
                        ):
                            if current_period:
                                category = categorize_items(current_items)
                                periods_table[current_period] = category
                                if category == "more meats":
                                    meat_periods += 1
                                elif category == "more veges":
                                    veg_periods += 1

                            current_period = row["Period"]
                            current_items = []

                        current_items.append(result_item)

                if current_period:
                    category = categorize_items(current_items)
                    periods_table[current_period] = category
                    if category == "more meats":
                        meat_periods += 1
                    elif category == "more veges":
                        veg_periods += 1

    total_periods = meat_periods + veg_periods
    periods_table_with_percentage = {
        period: (category, (count / total_periods) * 100)
        for period, category in periods_table.items()
    }

    return periods_table_with_percentage


def analyze_continuous_meats(filename):
    continuous_meats = []
    with open(filename, "r", newline="") as file:
        csv_reader = csv.DictReader(file)
        prev_item = ""
        count = 0
        dates_meat_mapping = (
            {}
        )  # To store detected dates and their corresponding meat names
        times = []  # To store detected times

        for row in csv_reader:
            if "Result" in row:
                result_item = row["Result"]
                date = row["Date"]  # Use "Date" column
                if result_item == prev_item:
                    count += 1
                    times.append(row["Time"])
                else:
                    if count >= 3 and is_meat(prev_item):
                        if date in dates_meat_mapping:
                            dates_meat_mapping[date]["meat_names"].add(prev_item)
                        else:
                            dates_meat_mapping[date] = {
                                "meat_names": {prev_item},
                                "times": times,
                            }
                    prev_item = result_item
                    count = 1
                    times = [row["Time"]]

        # Add the last detected sequence if it's a meat and meets the count requirement
        if count >= 3 and is_meat(prev_item):
            if date in dates_meat_mapping:
                dates_meat_mapping[date]["meat_names"].add(prev_item)
            else:
                dates_meat_mapping[date] = {"meat_names": {prev_item}, "times": times}

    return dates_meat_mapping


def display_continuous_meats_table(meats_data):
    headers = ["Date", "Day", "Meat Names", "Times"]
    table_data = []

    for date, data in meats_data.items():
        meat_names_str = ", ".join(data["meat_names"])
        times_str = ", ".join(data["times"])

        # Calculate the day of the week
        date_obj = datetime.strptime(date, "%d/%m/%Y")
        day_of_week = date_obj.strftime("%A")

        table_data.append([date, day_of_week, meat_names_str, times_str])

    print(tabulate(table_data, headers=headers, tablefmt="grid"))


def analyze_alternate_meats(filename):
    alternate_meats = []
    with open(filename, "r", newline="") as file:
        csv_reader = csv.DictReader(file)
        prev_item = ""
        prev_category = ""
        count = 0
        for row in csv_reader:
            if "Result" in row:
                result_item = row["Result"]
                category = get_category(result_item)
                if category == prev_category:
                    count += 1
                else:
                    count = 1
                if count >= 3 and is_meat(category) != is_meat(prev_category):
                    alternate_meats.append((result_item, count))
                prev_item = result_item
                prev_category = category

    return alternate_meats


def analyze_period_with_most_items(item_type, filename):
    periods_table = analyze_periods(
        "results"
    )  # Provide the correct results folder path

    headers = [
        "Period",
        "Category",
        "Percentage",
        "Between Common Meats",
        "Veges",
        "Days",
        "Count",
        "Times",
    ]
    table_data = []

    # Loop through each period and analyze data
    for period, (category, percentage) in periods_table.items():
        if category != item_type:
            continue

        # Get the common items for the current period
        common_items = get_common_items_for_period(filename, period)

        # Filter common items to get only veges
        common_veges = [item for item in common_items if item not in MEATS]

        # Analyze between common meats and veges
        analyze_result = analyze_between_common_items(common_veges, filename)

        # Append the data to the table
        table_data.append(
            [
                period,
                category,
                f"{percentage:.2f}%",
                analyze_result["common_meats"],
                analyze_result["common_veges"],
                analyze_result["days"],
                analyze_result["count"],
                analyze_result["times"],
            ]
        )

    print(tabulate(table_data, headers=headers, tablefmt="grid"))


def get_common_items_for_period(filename, period):
    common_items = []
    with open(filename, "r", newline="") as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            if "Period" in row and row["Period"] == period and "Result" in row:
                common_items.append(row["Result"])
    return common_items


def analyze_between_common_items(common_veges, filename):
    common_meats = ["BEEF", "CHICKEN THIGHS", "MEAT SKEWERS", "HOT DOG"]

    days = set()
    count = 0
    times = []

    with open(filename, "r", newline="") as file:
        csv_reader = csv.DictReader(file)
        prev_item = ""
        prev_day = ""
        for row in csv_reader:
            if "Date" in row and "Result" in row:
                date = row["Date"]
                item = row["Result"]
                if item in common_meats and prev_item in common_veges:
                    days.add(date)
                    if prev_day != date:
                        count += 1
                    times.append(row["Time"])
                prev_item = item
                prev_day = date

    return {
        "common_meats": ", ".join(common_meats),
        "common_veges": ", ".join(common_veges),
        "days": ", ".join(days),
        "count": count,
        "times": ", ".join(times),
    }


def display_periods_table(periods_table):
    headers = ["Period", "Category", "Percentage", "File Name", "Days"]
    table_data = []

    for period, category in periods_table.items():
        percentage = f"{(1 / len(periods_table)) * 100:.2f}%"
        file_name = f"results/period_{period}.csv"

        with open(file_name, "r", newline="") as file:
            csv_reader = csv.DictReader(file)
            days = ""
            for row in csv_reader:
                if "Days" in row:
                    days = row["Days"]
                    break

            table_data.append([period, category, percentage, file_name, days])

    print(tabulate(table_data, headers=headers, tablefmt="grid"))


def calculate_round_difference(item):
    results_folder = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "results", "sorted&merged"
    )
    round_diff_counts = defaultdict(list)

    for filename in os.listdir(results_folder):
        if filename.endswith(".csv"):
            csv_file = os.path.join(results_folder, filename)
            with open(csv_file, "r", newline="") as file:
                csv_reader = csv.DictReader(file)
                prev_round_number = None
                for row in csv_reader:
                    if "Result" in row and item.lower() == row["Result"].lower():
                        round_number = row.get("Round", "Unknown")
                        if prev_round_number is not None:
                            round_diff = abs(int(round_number) - int(prev_round_number))
                            rounds = f"{prev_round_number} - {round_number}"
                            round_diff_counts[round_diff].append(rounds)
                        prev_round_number = round_number

    # Check if there are enough consecutive occurrences to calculate differences
    if not round_diff_counts:
        print(f"Not enough consecutive occurrences of '{item}' found.")
        return

    # Prepare the data for the first table
    table_data = []
    for round_diff, rounds_list in sorted(
        round_diff_counts.items(), key=lambda x: len(x[1]), reverse=True
    ):
        table_data.append((round_diff, "\n".join(rounds_list), len(rounds_list)))

    # Display the first table using tabulate
    headers = ["Round Difference", "Rounds", "Occurrence Count"]
    print(f"Round Differences for '{item}':")
    print(tabulate(table_data, headers=headers, tablefmt="grid"))

    # Allow the user to export the table as a CSV file
    export_csv = input("Export the table as a CSV file? (yes/no): ").strip().lower()
    if export_csv == "yes":
        csv_filename = f"{item}_round_differences.csv"
        csv_filepath = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "results", csv_filename
        )
        with open(csv_filepath, "w", newline="") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(headers)
            csv_writer.writerows(table_data)
        print(f"Table exported as '{csv_filename}'.")


def search_items_by_ending_minute(ending_minute):
    if ending_minute not in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
        print("Invalid input. Ending minute must be between 0 and 9.")
        return

    results_folder = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "results", "sorted&merged"
    )
    item_counts = Counter()

    for filename in os.listdir(results_folder):
        if filename.endswith(".csv"):
            csv_file = os.path.join(results_folder, filename)
            with open(csv_file, "r", newline="") as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    time_value = row.get("Time", "Unknown")
                    # Extract the last digit (minute) from the time
                    last_digit = time_value[-1]
                    if last_digit == ending_minute:
                        item = row.get("Result", "Unknown")
                        item_counts[item] += 1

    # Create a table with item counts and percentages
    total_items = sum(item_counts.values())
    table_data = [
        (item, count, f"{(count / total_items) * 100:.2f}%")
        for item, count in item_counts.items()
    ]

    # Sort the table by count in descending order
    table_data.sort(key=lambda x: x[1], reverse=True)

    # Print the table with percentages
    headers = ["Item", "Count", "Percentage"]
    print(f"Items Found Ending with Minute '{ending_minute}':")

    # Print the table using tabulate with the "grid" format
    print_table_with_sort(table_data, headers)


def calculate_item_occurrences_by_combinations():
    results_folder = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "results", "sorted&merged"
    )

    # Initialize a dictionary to store item occurrences by combinations
    item_combinations = {}

    for round_ending in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
        for minute_ending in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
            round_ending_key = f"Round Ending {round_ending}"
            minute_ending_key = f"Minute Ending {minute_ending}"

            # Initialize the dictionaries for each combination key
            item_combinations[round_ending_key] = Counter()
            item_combinations[minute_ending_key] = Counter()

    for filename in os.listdir(results_folder):
        if filename.endswith(".csv"):
            csv_file = os.path.join(results_folder, filename)
            with open(csv_file, "r", newline="") as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    item = row.get("Result", "Unknown")
                    round_number = row.get("Round", "Unknown")
                    time_value = row.get("Time", "Unknown")
                    # Extract the last digit (minute) from the time
                    last_digit = time_value[-1]

                    # Check if the round and minute ending are in the range 0 to 9
                    if round_number.endswith(
                        ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9")
                    ) and last_digit in (
                        "0",
                        "1",
                        "2",
                        "3",
                        "4",
                        "5",
                        "6",
                        "7",
                        "8",
                        "9",
                    ):
                        # Create combination keys based on the round and minute ending
                        round_ending_key = f"Round Ending {round_number[-1]}"
                        minute_ending_key = f"Minute Ending {last_digit}"

                        # Update item counts for the combination keys
                        item_combinations[round_ending_key][item] += 1
                        item_combinations[minute_ending_key][item] += 1

    # Calculate the total occurrences for each combination
    total_occurrences = {}
    for combination_key, item_counts in item_combinations.items():
        total_occurrences[combination_key] = sum(item_counts.values())

    # Prepare the data for tabulate
    table_data = []
    for combination_key, item_counts in sorted(item_combinations.items()):
        percentage_data = [
            (item, count, f"{(count / total_occurrences[combination_key]) * 100:.2f}%")
            for item, count in item_counts.items()
        ]
        headers = ["Item", "Count", "Percentage"]
        table_data.extend([(combination_key,) + data for data in percentage_data])

    # Display the table using tabulate
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    headers = ["Combination", "Item", "Count", "Percentage"]


def digit_mask_r(round_number, mask):
    results_folder = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "results", "sorted&merged"
    )
    """
    Mask the round number based on the provided mask.

    Parameters:
    - round_number (int): The original round number.
    - mask (str): The masking pattern (up to 3 digits of asterisks).

    Returns:
    - str: The masked round number.
    """
    round_str = str(round_number).zfill(4)  # Convert to 4-digit string
    masked_round = "".join(
        char if mask_char == "*" else mask_char
        for char, mask_char in zip(round_str, mask)
    )
    return masked_round


def get_results_by_masked_round(mask, results_folder):
    masked_results = []

    for filename in os.listdir(results_folder):
        if filename.endswith(".csv"):
            csv_file = os.path.join(results_folder, filename)
            with open(csv_file, "r", newline="") as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    if "Round" in row:
                        csv_round = int(row["Round"])
                        masked_round = mask_round_number(csv_round, mask)
                        if masked_round == mask:
                            masked_results.append((row["Result"], row["Time"]))

    return masked_results


def show_tables_for_masked_round(mask, results_folder):
    results = get_results_by_masked_round(mask, results_folder)
    if results:
        result_count = Counter()
        times_by_result = {}  # Dictionary to store times for each result

        for result, time_value in results:
            result_count[result] += 1
            times_by_result.setdefault(result, []).append(time_value)

        table_data = []
        for result, count in result_count.items():
            times = times_by_result[result]
            times_str = ", ".join(
                f"{time} ({times.count(time)})" for time in sorted(set(times))
            )

            # Calculate percentage with one decimal place
            percentage = (count / len(results)) * 100
            percentage_str = f"{percentage:.1f}%"

            table_data.append([result, count, percentage_str, times_str])

        headers = ["Result", "Count", "Percentage", "Times"]
        print(f"Search Results for Masked Round {mask}:")
        print_table_with_sort(table_data, headers)
        add_cons_items_table(table_data)
    else:
        print(f"No results found for Masked Round {mask}.")


if __name__ == "__main__":
    while True:
        print("Analysis Options:")
        print("1. Round Search (Simple Search)")
        print("2. Start from current round")
        print("3. Item Search")
        print("4. Range Search")
        print("5. Time-based search")
        print("6. Search Next Three Items")
        print("7. Analyze Periods with More Meats/Veges")
        print("8. Calculate Round Difference for an Item")
        print("9. Search Items by Ending Minute")
        print("10. Item Occurrences by Combinations")
        print("11. Round Time Search")
        print("12. Round Masked Search")  # New option
        print("13. Exit")

        option = input("Select your option: ")

        if option.lower() == "exit":
            print("Exiting the program.")
            break

        try:
            option = int(option)
        except ValueError:
            print("Invalid input. Please enter a number corresponding to the option.")
            continue

        if option == 1:
            while True:
                round_number = input(
                    "Enter the Round number (or type 'exit' to go back to the main menu): "
                )
                if round_number.lower() == "exit":
                    break

                try:
                    round_number = int(round_number)
                except ValueError:
                    print(
                        "Invalid input. Please enter a valid Round number or type 'exit' to go back to the main menu."
                    )
                    continue

                continue_option1 = True
                while continue_option1:
                    show_tables_for_round(round_number)
                    print("Options:")
                    print("'c' to continue displaying next set of table")
                    print("'s' to stop the automatic search")
                    print("'exit' to exit from option 1")
                    user_input = input("Enter your choice: ")
                    if user_input == "c":
                        round_number += 1
                    elif user_input == "s":
                        continue_option1 = False
                    elif user_input == "exit":
                        break
                    else:
                        print("Invalid choice. Please enter 'c', 's', or 'exit'.")

        elif option == 2:
            while True:
                round_number = input(
                    "Enter the Round number (or type 'exit' to go back to the main menu): "
                )
                if round_number.lower() == "exit":
                    break

                try:
                    round_number = int(round_number)
                except ValueError:
                    print(
                        "Invalid input. Please enter a valid Round number or type 'exit' to go back to the main menu."
                    )
                    continue

                continue_from_current_round_with_increment(round_number)
                print()  # Add a blank line for better readability

        elif option == 3:
            while True:
                item_to_search = input(
                    "Enter the item to search (or type 'exit' to go back to the main menu): "
                )
                if item_to_search.lower() == "exit":
                    break

                item_based_search(item_to_search)
                print()  # Add a blank line for better readability

        elif option == 4:
            while True:
                start_round = input(
                    "Enter the start Round number (or type 'exit' to go back to the main menu): "
                )
                if start_round.lower() == "exit":
                    break

                end_round = input(
                    "Enter the end Round number (or type 'exit' to go back to the main menu): "
                )
                if end_round.lower() == "exit":
                    break

                try:
                    start_round = int(start_round)
                    end_round = int(end_round)
                except ValueError:
                    print(
                        "Invalid input. Please enter valid Round numbers or type 'exit' to go back to the main menu."
                    )
                    continue

                get_common_items_for_round_range(start_round, end_round)
                print()  # Add a blank line for better readability

        elif option == 5:
            while True:
                search_time = input(
                    "Enter the time to search (hh:mm), or use masks *:mm or hh:*: "
                )
                if search_time.lower() == "exit":
                    break

                time_based_search(search_time)
                print()  # Add a blank line for better readability

        elif option == 6:  # Not working
            search_items = input("Enter the series of items separated by space: ")
            search_next_three_items(search_items)

        elif option == 7:
            while True:
                print("Period Analysis Options:")
                print("1. Analyze Periods with More Meats")
                print("2. Analyze Periods with More Veges")
                print("3. Analyze Balanced Periods")
                print("4. Analyze Continuous Meats")
                print("5. Analyze Alternate Meats")
                print("6. Exit Period Analysis")

                period_option = input("Select your option: ")

                if period_option == "1":
                    analyze_period_with_most_items(
                        "more meats", "sorted_merged_file.csv"
                    )
                elif period_option == "2":
                    analyze_period_with_most_items(
                        "more veges", "sorted_merged_file.csv"
                    )
                elif period_option == "3":
                    analyze_balanced_periods("sorted_merged_file.csv")
                elif period_option == "4":
                    continuous_meats_data = analyze_continuous_meats(
                        "sorted_merged_file.csv"
                    )
                    display_continuous_meats_table(continuous_meats_data)
                elif period_option == "5":
                    alternate_meats_data = analyze_alternate_meats(
                        "sorted_merged_file.csv"
                    )
                    alternate_meats_headers = ["Alternate Meats", "Count"]
                    display_continuous_alternate_meats_table(
                        alternate_meats_data, alternate_meats_headers
                    )
                elif period_option == "6":
                    print("Exiting Period Analysis.")
                    break
                else:
                    print("Invalid option. Please select a valid option.")

        elif option == 8:
            while True:
                item_to_search = input(
                    "Enter the item for which you want to calculate round differences (or type 'exit' to go back to the main menu): "
                )
                if item_to_search.lower() == "exit":
                    break

                calculate_round_difference(item_to_search)
                print()  # Add a blank line for better readability

        elif option == 9:
            while True:
                ending_minute = input(
                    "Enter the ending minute to search for (0-9) (or type 'exit' to go back to the main menu): "
                )
                if ending_minute.lower() == "exit":
                    break

                search_items_by_ending_minute(ending_minute)
                print()  # Add a blank line for better readability

        elif option == 10:
            # Call the new function for Item Occurrences by Combinations
            calculate_item_occurrences_by_combinations()

        elif option == 11:
            round_time_seq()

        elif option == 12:  # New option for round masked search
            while True:
                round_mask = input("Enter the round mask (e.g., ***1): ")
                if round_mask.lower() == "exit":
                    break

                show_tables_for_masked_round(round_mask, results_folder)
                print()  # Add a blank line for better readability

        elif option == 13:
            print("Exiting the program.")
            break

        else:
            print("Invalid option. Please select a valid option from the menu.")
        print()  # Add a blank line for better readability
