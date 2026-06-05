select
    safe_cast(date as date) as spend_date,
    coalesce(safe_cast(channel as string), 'Unknown') as channel,
    coalesce(safe_cast(campaign as string), 'Unknown') as campaign,
    coalesce(safe_cast(spend as numeric), 0) as spend,
    coalesce(safe_cast(clicks as numeric), 0) as clicks,
    coalesce(safe_cast(impressions as numeric), 0) as impressions

from {{ source('raw', 'ad_spend') }}
