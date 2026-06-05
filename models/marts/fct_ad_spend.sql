with ad_spend as (

    select
        spend_date,
        date_trunc(spend_date, month) as spend_month,
        channel,
        campaign,
        spend,
        clicks,
        impressions

    from {{ ref('stg_ad_spend') }}

)

select *
from ad_spend
