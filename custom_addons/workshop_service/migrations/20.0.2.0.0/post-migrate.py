def _table_columns(cr, table_name):
    cr.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = current_schema() AND table_name = %s
    """, [table_name])
    return {row[0] for row in cr.fetchall()}


def migrate(cr, version):
    cr.execute("SELECT to_regclass('workshop_order_event')")
    if cr.fetchone()[0] is None:
        return

    order_columns = _table_columns(cr, 'workshop_order')
    actor = (
        'COALESCE(order_row.write_uid, order_row.create_uid)'
        if {'write_uid', 'create_uid'} <= order_columns
        else 'order_row.create_uid'
    )
    date_columns = [
        f'order_row.{column}'
        for column in ('closed_at', 'cancelled_at', 'write_date', 'request_date')
        if column in order_columns
    ]
    event_date = f"COALESCE({', '.join(date_columns)})"
    reason = (
        'order_row.cancellation_reason'
        if 'cancellation_reason' in order_columns
        else 'NULL'
    )
    cr.execute("""
        INSERT INTO workshop_order_event (
            order_id, event_type, reason, follow_up_type,
            user_id, event_date, create_uid, write_uid, create_date, write_date
        )
        SELECT id, 'opened', NULL, NULL, create_uid, request_date,
               create_uid, create_uid, request_date, request_date
        FROM workshop_order
        WHERE NOT EXISTS (
            SELECT 1 FROM workshop_order_event event
            WHERE event.order_id = workshop_order.id
        )
    """)
    cr.execute("""
        INSERT INTO workshop_order_event (
            order_id, event_type, reason, follow_up_type,
            user_id, event_date, create_uid, write_uid, create_date, write_date
        )
        SELECT order_row.id,
               CASE WHEN order_row.state = 'closed' THEN 'closed' ELSE 'cancelled' END,
               {},
               NULL,
               {},
               {},
               {},
               {},
               {},
               {}
        FROM workshop_order order_row
        WHERE order_row.state IN ('closed', 'cancelled')
          AND NOT EXISTS (
              SELECT 1 FROM workshop_order_event event
              WHERE event.order_id = order_row.id
                AND event.event_type IN ('closed', 'cancelled')
          )
    """.format(reason, actor, event_date, actor, actor, event_date, event_date))
