import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the dataset
df = pd.read_csv("ai_job_dataset.csv")

# --- Corrected Column Name for Salary ---
salary_column_name = "salary_usd"  # Confirmed from previous output

# --- Data Cleaning & Initial Transformation ---
# No missing values were found previously, and duplicates were handled.
df.drop_duplicates(inplace=True)

# Transformation: Convert 'posting_date' to datetime and extract year
if "posting_date" in df.columns:
    df["posting_date"] = pd.to_datetime(df["posting_date"], errors="coerce")
    df["work_year"] = df["posting_date"].dt.year
    print("\n'work_year' column created from 'posting_date'.")
    print(df[["posting_date", "work_year"]].head())
    # Check for NaNs introduced by coerce if any dates were invalid
    print(f"NaNs in work_year after conversion: {df['work_year'].isnull().sum()}")
    # Drop rows where work_year could not be determined, if any
    df.dropna(subset=["work_year"], inplace=True)
    df["work_year"] = df["work_year"].astype(int)  # Convert to integer if no NaNs
else:
    print(
        "\nERROR: 'posting_date' column not found. Cannot create 'work_year'. Salary trend plot will be skipped."
    )
    # Ensure work_year exists as a column, even if empty or to be ignored, to prevent later NameErrors
    # Or, more robustly, check for its existence before using it. For now, plots depending on it will check.

# --- Inspect and Correct Experience Levels ---
if "experience_level" in df.columns:
    actual_experience_levels = df["experience_level"].unique()
    print(f"\nActual unique values in 'experience_level': {actual_experience_levels}")

    # Define a mapping from abbreviations to full names for better plot labels
    # This is an assumption; if the actual values are different, this map needs adjustment.
    experience_level_map = {
        "EN": "Entry-level",
        "MI": "Mid-level",
        "SE": "Senior-level",
        "EX": "Executive",  # Assuming EX might be used for Executive
        # Add other mappings if new abbreviations appear from the print output
    }
    # Create a new column with full experience level names for plotting
    df["experience_level_full"] = (
        df["experience_level"].map(experience_level_map).fillna(df["experience_level"])
    )

    # Order for plots - use the mapped full names
    experience_order_full = [
        experience_level_map[key]
        for key in ["EN", "MI", "SE", "EX"]
        if key in experience_level_map
        and experience_level_map[key] in df["experience_level_full"].unique()
    ]
    print(f"Order for experience level plots (full names): {experience_order_full}")
else:
    print(
        "\nERROR: 'experience_level' column not found. Some visualizations will be affected."
    )
    df["experience_level_full"] = pd.Series(
        dtype="str"
    )  # create empty series to avoid NameError
    experience_order_full = []


# Store the cleaned and transformed DataFrame
df.to_csv("cleaned_transformed_ai_job_dataset.csv", index=False)
print(
    "\nCleaned and transformed data saved to 'cleaned_transformed_ai_job_dataset.csv'"
)

# --- Visualizations ---

# Visualization 1: Distribution of Experience Levels (using mapped full names)
plt.figure(figsize=(10, 6))
if (
    "experience_level_full" in df.columns
    and not df["experience_level_full"].value_counts().empty
):
    sns.countplot(
        data=df,
        y="experience_level_full",
        order=df["experience_level_full"].value_counts().index,
        palette="viridis",
        hue="experience_level_full",
        dodge=False,
    )
    plt.title("Distribution of Job Postings by Experience Level")
    plt.xlabel("Number of Job Postings")
    plt.ylabel("Experience Level")
    plt.legend([], [], frameon=False)
    plt.tight_layout()
    plt.savefig("experience_level_distribution.png")
    plt.show()
    print("\nGenerated 'experience_level_distribution.png'")
else:
    print(
        "\nSkipping 'experience_level_distribution.png': 'experience_level_full' data unavailable."
    )

# Visualization 2: Top 10 Company Locations
plt.figure(figsize=(12, 7))
if "company_location" in df.columns and not df["company_location"].value_counts().empty:
    top_10_locations = df["company_location"].value_counts().nlargest(10)
    sns.barplot(
        x=top_10_locations.values,
        y=top_10_locations.index,
        palette="mako",
        hue=top_10_locations.index,
        dodge=False,
    )
    plt.title("Top 10 Company Locations by Number of Job Postings")
    plt.xlabel("Number of Job Postings")
    plt.ylabel("Company Location")
    plt.legend([], [], frameon=False)
    plt.tight_layout()
    plt.savefig("top_10_company_locations.png")
    plt.show()
    print("\nGenerated 'top_10_company_locations.png'")
else:
    print(
        "\nSkipping 'top_10_company_locations.png': 'company_location' data unavailable."
    )

# Visualization 3: Salary Distribution by Experience Level (using mapped full names)
if (
    salary_column_name
    and "experience_level_full" in df.columns
    and experience_order_full
):
    plot_df_experience = df[
        df["experience_level_full"].isin(experience_order_full)
        & df[salary_column_name].notna()
    ]
    if not plot_df_experience.empty and pd.api.types.is_numeric_dtype(
        plot_df_experience[salary_column_name]
    ):
        plt.figure(figsize=(12, 8))
        sns.boxplot(
            data=plot_df_experience,
            x="experience_level_full",
            y=salary_column_name,
            palette="crest",
            order=experience_order_full,
        )
        plt.title(f"Salary Distribution by Experience Level ({salary_column_name})")
        plt.xlabel("Experience Level")
        plt.ylabel(f"Salary ({salary_column_name})")
        # Check for wide salary range to apply log scale
        s_min = plot_df_experience[salary_column_name].min()
        s_max = plot_df_experience[salary_column_name].max()
        if (
            s_min > 0 and s_max / s_min > 10
        ):  # Avoid division by zero or negative min; ensure significant range
            plt.yscale("log")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig("salary_distribution_by_experience.png")
        plt.show()
        print("\nGenerated 'salary_distribution_by_experience.png'")
    else:
        print(
            "\nSkipping 'salary_distribution_by_experience.png': Filtered data is empty or salary is not numeric."
        )
else:
    print(
        "\nSkipping salary distribution plot: Salary column, experience data, or defined order is unavailable."
    )

# Visualization 4: Trend of Average Salary Over Years by Experience Level (using mapped full names)
if (
    salary_column_name
    and "experience_level_full" in df.columns
    and "work_year" in df.columns
    and experience_order_full
):
    df_filtered_experience = df[
        df["experience_level_full"].isin(experience_order_full)
        & df["work_year"].notna()
        & df[salary_column_name].notna()
    ]
    if not df_filtered_experience.empty and pd.api.types.is_numeric_dtype(
        df_filtered_experience[salary_column_name]
    ):
        average_salary_trend = (
            df_filtered_experience.groupby(["work_year", "experience_level_full"])[
                salary_column_name
            ]
            .mean()
            .unstack()
        )
        if not average_salary_trend.empty and not average_salary_trend.columns.empty:
            plt.figure(figsize=(14, 8))
            average_salary_trend.plot(kind="line", marker="o", ax=plt.gca())
            plt.title(
                f"Trend of Average Salary ({salary_column_name}) Over Years by Experience Level"
            )
            plt.xlabel("Work Year")
            plt.ylabel(f"Average Salary ({salary_column_name})")
            plt.legend(
                title="Experience Level",
                labels=[col for col in average_salary_trend.columns],
            )
            plt.grid(True)
            plt.tight_layout()
            plt.savefig("average_salary_trend_by_experience.png")
            plt.show()
            print("\nGenerated 'average_salary_trend_by_experience.png'")
        else:
            print(
                "\nCould not generate average salary trend plot (unstacked data is empty or has no columns)."
            )
    else:
        print(
            "\nSkipping average salary trend plot: Filtered data for trend is empty or salary is non-numeric."
        )
else:
    print(
        "\nSkipping average salary trend: One or more required columns (salary, experience, work_year) or experience order is unavailable."
    )

# Visualization 5: Top 10 Most Common Job Titles
plt.figure(figsize=(12, 8))
if "job_title" in df.columns and not df["job_title"].value_counts().empty:
    top_10_job_titles = df["job_title"].value_counts().nlargest(10)
    sns.barplot(
        x=top_10_job_titles.values,
        y=top_10_job_titles.index,
        palette="cubehelix",
        hue=top_10_job_titles.index,
        dodge=False,
    )
    plt.title("Top 10 Most Common Job Titles")
    plt.xlabel("Number of Job Postings")
    plt.ylabel("Job Title")
    plt.legend([], [], frameon=False)
    plt.tight_layout()
    plt.savefig("top_10_job_titles.png")
    plt.show()
    print("\nGenerated 'top_10_job_titles.png'")
else:
    print("\nSkipping 'top_10_job_titles.png': 'job_title' data unavailable.")

print("\nFinal DataFrame info after transformations:")
df.info()
print("\nFirst 5 rows of the final (cleaned & transformed) DataFrame (sample):")
print(
    df[
        [
            "job_title",
            salary_column_name,
            "experience_level",
            "experience_level_full",
            "work_year",
        ]
    ].head()
)

print(
    "\nAnalysis and visualization complete. Check the generated PNG files and CSV: 'cleaned_transformed_ai_job_dataset.csv'."
)
