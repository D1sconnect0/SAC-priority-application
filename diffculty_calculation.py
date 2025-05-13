import pandas as pd
import numpy as np

def calculate_difficulty(sac_score_percent, wanted_score, sac_marks, max_possible_marks):
    target_percent = (wanted_score / 50) * 100
    relative_perf = max(0.0, 1 - (sac_score_percent / target_percent))
    mark_weight = sac_marks / max_possible_marks
    return 1 - ((1 - relative_perf) * (1 - mark_weight))

def calculate_urgency(days_until, k=0.16):
    return np.exp(-k * days_until)

def calculate_priority(difficulty, urgency):
    return 1 - ((1 - difficulty) * (1 - urgency))

# Load CSV
df = pd.read_csv("percentage.csv")  # Must contain required columns

# Apply calculations
df["difficulty"] = df.apply(
    lambda row: calculate_difficulty(
        row["sac_score_percent"],
        row["wanted_score"],
        row["sac_marks"],
        row["max_possible_marks"]
    ), axis=1)

df["urgency"] = df["days_until"].apply(lambda d: calculate_urgency(d, k=0.4))

df["priority"] = df.apply(
    lambda row: round(calculate_priority(row["difficulty"], row["urgency"]), 3),
    axis=1)

# Save
df.to_csv("prioritized_output.csv", index=False)
print("Done! Output saved to 'prioritized_output.csv'")
