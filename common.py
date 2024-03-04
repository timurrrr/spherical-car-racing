# This file defines various things shared between all/most races.

def compare_lap_time_with_record_and_reference(lap_time, record, reference_time):
    time_round = round(lap_time, 3)
    if time_round < record:
        print("NEW RECORD! Congrats!! Please reach out to timurrrr@ to certify.")
    elif time_round == record:
        print("Congrats, you've matched the record!")
    else:
        if time_round < reference_time:
            print("Good effort, but can you go quicker?")
        elif time_round > reference_time:
            print(f"This was slower than the reference solution ({reference_time:.3f} seconds).")
        print(f"The current record is {record:.3f} seconds.")

