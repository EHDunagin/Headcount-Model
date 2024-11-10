# calculations.py
import polars as pl


def rate_forecast(forecast, base_column, new_column_name, applied_rate):
    """
    Add a new column to a forecast that is an amount calculated as a percentage of an existing column

    Inputs
    forecast: dataframe - current forecast
    base_column: str - column to calculate % of
    new_column_name: str - name of new column
    applied_rate: float - percentage rate to apply

    Output
    dataframe with new column added
    """

    # Check if the base_column exists in the forecast
    if base_column not in forecast.columns:
        raise ValueError(
            f"\nColumn '{base_column}' not found in forecast. Cannot apply rate.\n"
        )

    # Check if the base_column is of a numeric type
    elif not forecast[base_column].dtype.is_numeric():
        raise ValueError(
            f"\nColumn '{base_column}' is not a numeric type. Cannot apply rate.\n"
        )
        return forecast

    # Add the new column as a percentage of the base_column
    else:
        forecast = forecast.with_columns(
            (pl.col(base_column) * applied_rate).alias(new_column_name)
        )

    return forecast


def capped_rate_forecast(
    forecast, base_column, new_column_name, applied_rate, cap_base_column, cap_amount
):
    """
    Add a new column to a forecast that is an amount calculated as a percentage of an existing column,
    with a cap on the base amount.

    Inputs
    forecast: dataframe - current forecast
    base_column: str - column to calculate % of
    new_column_name: str - name of new column
    applied_rate: float - percentage rate to apply
    cap_base_column: str - column used to determine the whether cap has been exceeded
    cap_amount: float - maximum amount of cap_base_column to apply the rate to

    Output
    DataFrame with the new column added.
    """

    # Ensure base_column and cap_base_column exist and are numeric
    if base_column not in forecast.columns or cap_base_column not in forecast.columns:
        raise ValueError(
            f"\nForecast could not be applied: column '{base_column}' or '{cap_base_column}' not found.\n"
        )

    if (
        not forecast[base_column].dtype.is_numeric()
        or not forecast[cap_base_column].dtype.is_numeric()
    ):
        raise ValueError(
            f"\nForecast could not be applied: column '{base_column}' or '{cap_base_column}' is not numeric.\n"
        )

    # Compute the capped rate
    capped_rate_expr = pl.when(pl.col(cap_base_column) <= cap_amount)
    capped_rate_expr = capped_rate_expr.then(pl.col(base_column) * applied_rate)
    capped_rate_expr = capped_rate_expr.when(
        pl.col(cap_base_column) - pl.col(base_column) >= cap_amount
    )
    capped_rate_expr = capped_rate_expr.then(pl.lit(0))
    capped_rate_expr = capped_rate_expr.otherwise(
        (cap_amount - pl.col(cap_base_column) + pl.col(base_column)).clip(lower_bound=0)
        * applied_rate
    ).alias(new_column_name)

    return forecast.with_columns(capped_rate_expr)


def per_head_forecast(forecast, new_column_name, amount):
    """
    Add a new column to a forecast that is a flat amount adjusted for inflation for any month an employee is active

    Inputs
    forecast: dataframe - current forecast
    new_column_name: str - name of new column
    amount: number - monthly amount of expense

    Output
    DataFrame with the new column added.
    """

    # Ensure that proration and inflation_factor columns exist and are numeric
    if (
        "proration" not in forecast.columns
        or "inflation_factor" not in forecast.columns
        or not forecast["proration"].dtype.is_numeric()
        or not forecast["inflation_factor"].dtype.is_numeric()
    ):
        raise ValueError(
            "\nForecast could not be applied: column 'proration' or 'inflation_factor' not found or not numeric.\n"
        )

    # Find the maximum proration per Employee ID and start_of_month
    max_prorations = forecast.group_by(["Employee ID", "start_of_month"]).agg(
        pl.col("proration").max().alias("max_proration")
    )

    # Join back to the original forecast to identify rows with the maximum proration
    forecast = forecast.join(max_prorations, on=["Employee ID", "start_of_month"])

    # Apply the amount only to the rows with the maximum proration to avoid duplication when an employee changes roles mid month
    forecast = forecast.with_columns(
        pl.when(
            (pl.col("proration") == pl.col("max_proration")) & (pl.col("proration") > 0)
        )
        .then(pl.col("inflation_factor") * amount)
        .otherwise(0)
        .alias(new_column_name)
    )

    # Drop the temporary max_proration column
    forecast = forecast.drop("max_proration")

    return forecast
