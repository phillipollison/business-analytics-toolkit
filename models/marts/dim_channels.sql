with channels as (

    select distinct channel
    from {{ ref('fct_orders') }}

    union distinct

    select distinct channel
    from {{ ref('fct_ad_spend') }}

    union distinct

    select distinct channel
    from {{ ref('fct_sessions') }}

),

final as (

    select
        channel,
        case
            when lower(channel) in ('meta', 'google', 'tiktok', 'facebook', 'paid social', 'paid search') then 'Paid'
            when lower(channel) in ('email', 'sms') then 'Owned'
            when lower(channel) in ('organic', 'direct') then 'Organic'
            else 'Other'
        end as channel_type

    from channels

)

select *
from final
