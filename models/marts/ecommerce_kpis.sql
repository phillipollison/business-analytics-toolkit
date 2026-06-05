with order_metrics as (

    select
        sum(net_revenue) as revenue,
        count(distinct order_id) as orders,
        count(distinct customer_id) as customers,
        safe_divide(sum(net_revenue), count(distinct order_id)) as average_order_value,
        safe_divide(sum(net_revenue), count(distinct customer_id)) as ltv,
        safe_divide(sum(refund_amount), nullif(sum(revenue), 0)) as refund_rate

    from {{ ref('fct_orders') }}

),

repeat_customers as (

    select
        safe_divide(
            countif(order_count > 1),
            count(*)
        ) as repeat_purchase_rate

    from (
        select
            customer_id,
            count(distinct order_id) as order_count

        from {{ ref('fct_orders') }}

        group by 1
    )

),

ad_metrics as (

    select
        sum(spend) as ad_spend,
        sum(clicks) as clicks,
        sum(impressions) as impressions

    from {{ ref('fct_ad_spend') }}

),

session_metrics as (

    select
        count(distinct session_id) as sessions,
        sum(converted) as conversions,
        safe_divide(sum(converted), count(distinct session_id)) as conversion_rate

    from {{ ref('fct_sessions') }}

),

subscription_metrics as (

    select
        countif(is_active) as active_subscriptions,
        countif(is_canceled) as canceled_subscriptions,
        count(*) as subscriptions,
        sum(case when is_active then monthly_price else 0 end) as mrr,
        safe_divide(countif(is_canceled), count(*)) as churn_rate

    from {{ ref('fct_subscriptions') }}

),

final as (

    select
        o.revenue,
        o.orders,
        o.customers,
        o.average_order_value,
        o.ltv,
        o.refund_rate,
        r.repeat_purchase_rate,
        a.ad_spend,
        safe_divide(o.revenue, a.ad_spend) as roas,
        safe_divide(a.ad_spend, o.customers) as cac,
        safe_divide(a.ad_spend, a.clicks) as cpc,
        safe_divide(a.ad_spend, a.impressions) * 1000 as cpm,
        s.sessions,
        s.conversions,
        s.conversion_rate,
        sub.active_subscriptions,
        sub.canceled_subscriptions,
        sub.subscriptions,
        sub.churn_rate,
        sub.mrr

    from order_metrics o
    cross join repeat_customers r
    cross join ad_metrics a
    cross join session_metrics s
    cross join subscription_metrics sub

)

select *
from final
