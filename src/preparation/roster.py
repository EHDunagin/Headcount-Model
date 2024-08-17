import polars as pl
from datetime import date

def get_roster(data_path):
    """
    Reads in an input headcount roster from a .csv file fills missing start and end dates.

    Input -> path to headcount roster input (string)
    Output -> Polars Dataframe of roster
    """
    roster = pl.read_csv(
        data_path,
        try_parse_dates=True,
        columns=[
            "Role ID",
            "Employee ID",
            "Employee Name",
            "Title",
            "Department",
            "Employment type",
            "Location",
            "Start Date",
            "End Date",
            "Salary",
            "Bonus",
            "Commission",
        ],
        schema_overrides={
            "Role ID": pl.Int32,
            "Employee ID": pl.Utf8,
            "Employee Name": pl.Utf8,
            "Title": pl.Utf8,
            "Department": pl.Utf8,
            "Employment type": pl.Utf8,
            "Location": pl.Utf8,
            "Salary": pl.Float64,
            "Bonus": pl.Float64,
            "Commission": pl.Float64,
        },
    )

    # Convert start and end to dates
    roster = roster.with_columns(
        pl.col("Start Date").str.strptime(
            pl.Date, format="%m/%d/%y", strict=False, exact=True
        ),
        pl.col("End Date").str.strptime(
            pl.Date, format="%m/%d/%y", strict=False, exact=True
        ),
    )

    # Set minimal start date
    roster = roster.with_columns(
        pl.col("Start Date").fill_null(date.min).alias("start_date_complete")
    )

    # Set maximal end date
    roster = roster.with_columns(
        pl.col("End Date").fill_null(date.max).alias("end_date_complete")
    )

    return roster


if __name__ == "__main__":
    from tkinter.filedialog import askopenfilename

    roster_path = askopenfilename(title="Choose a headcount roster file")

    with pl.Config(tbl_cols=-1):
        print(get_roster(roster_path))
