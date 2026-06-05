with revenue_by_channel as (

    select
        channel,
        sum(net_revenue) as revenue,
        count(distinct order_id) as orders,
        count(distinct customer_id) as customers

    from {{ ref('fct_orders') }}

    group by 1

),

spend_by_channel as (

    select
        channel,
        sum(spend) as spend,
        sum(clicks) as clicks,
        sum(impressions) as impressions

    from {{ ref('fct_ad_spend') }}

    group by 1

),

sessions_by_channel as (

    select
        channel,
        count(distinct session_id) as sessions,
        sum(converted) as conversions

    from {{ ref('fct_sessions') }}

    group by 1

),

combined as (

    select
        coalesce(r.channel, s.channel, w.channel) as channel,
        coalesce(r.revenue, 0) as revenue,
        coalesce(r.orders, 0) as orders,
        coalesce(r.customers, 0) as customers,
        coalesce(s.spend, 0) as spend,
        coalesce(s.clicks, 0) as clicks,
        coalesce(s.impressions, 0) as impressions,
        coalesce(w.sessions, 0) as sessions,
        coalesce(w.conversions, 0) as conversions

    from revenue_by_channel r

    full outer join spend_by_channel s
        on r.channel = s.channel

    full outer join sessions_by_channel w
        on coalesce(r.channel, s.channel) = w.channel

),

final as (

    select
        channel,
        revenue,
        orders,
        customers,
        spend,
        clicks,
        impressions,
        sessions,
        conversions,
        safe_divide(revenue, spend) as roas,
        safe_divide(spend, clicks) as cpc,
        safe_divide(spend, impressions) * 1000 as cpm,
        safe_divide(conversions, sessions) as conversion_rate,
        safe_divide(spend, customers) as cac

    from combined

)

select *
from final
