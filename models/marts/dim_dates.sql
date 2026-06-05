with dates as (

    select order_date as date_day
    from {{ ref('fct_orders') }}

    union distinct

    select spend_date as date_day
    from {{ ref('fct_ad_spend') }}

    union distinct

    select session_date as date_day
    from {{ ref('fct_sessions') }}

    union distinct

    select start_date as date_day
    from {{ ref('fct_subscriptions') }}

),

final as (

    select
        date_day,
        extract(year from date_day) as year,
        extract(month from date_day) as month,
        format_date('%B', date_day) as month_name,
        extract(quarter from date_day) as quarter,
        date_trunc(date_day, month) as month_start,
        date_trunc(date_day, quarter) as quarter_start,
        date_trunc(date_day, year) as year_start

    from dates

    where date_day is not null

)

select *
from final
