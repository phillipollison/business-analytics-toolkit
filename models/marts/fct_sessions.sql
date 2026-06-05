with sessions as (

    select
        session_id,
        session_date,
        date_trunc(session_date, month) as session_month,
        channel,
        customer_id,
        converted

    from {{ ref('stg_web_sessions') }}

)

select *
from sessions
