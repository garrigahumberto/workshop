from psycopg2 import sql


def _map_procedure_state(state):
    if state == 'published':
        return 'published'
    if state in {'retired', 'archived'}:
        return 'archived'
    return 'draft'


def _table_columns(cr, table_name):
    cr.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = current_schema() AND table_name = %s
    """, [table_name])
    return {row[0] for row in cr.fetchall()}


def migrate(cr, version):
    cr.execute("SELECT to_regclass('workshop_procedure')")
    if cr.fetchone()[0] is None:
        return

    cr.execute("""
        ALTER TABLE workshop_procedure
            ADD COLUMN IF NOT EXISTS revision integer,
            ADD COLUMN IF NOT EXISTS state varchar,
            ADD COLUMN IF NOT EXISTS change_summary text,
            ADD COLUMN IF NOT EXISTS published_by_id integer,
            ADD COLUMN IF NOT EXISTS published_at timestamp,
            ADD COLUMN IF NOT EXISTS archived_by_id integer,
            ADD COLUMN IF NOT EXISTS archived_at timestamp
    """)
    cr.execute("""
        SELECT conname
        FROM pg_constraint
        WHERE conrelid = 'workshop_procedure'::regclass
          AND contype = 'u'
          AND pg_get_constraintdef(oid) = 'UNIQUE (code)'
    """)
    for (constraint_name,) in cr.fetchall():
        cr.execute(sql.SQL('ALTER TABLE workshop_procedure DROP CONSTRAINT {}').format(
            sql.Identifier(constraint_name)
        ))
    cr.execute("""
        UPDATE workshop_procedure
        SET revision = 1,
            state = CASE WHEN active THEN 'draft' ELSE 'archived' END
        WHERE revision IS NULL OR state IS NULL
    """)

    cr.execute("SELECT to_regclass('workshop_procedure_version')")
    if cr.fetchone()[0] is not None:
        version_columns = _table_columns(cr, 'workshop_procedure_version')
        optional_columns = [
            'state',
            'change_summary',
            'published_by',
            'retired_by',
            'published_at',
            'retired_at',
            'create_uid',
            'create_date',
        ]
        expressions = [
            column if column in version_columns else 'NULL'
            for column in optional_columns
        ]
        cr.execute("""
            SELECT id, procedure_id, version_number, {}
            FROM workshop_procedure_version
            ORDER BY procedure_id, version_number, id
        """.format(', '.join(expressions)))
        versions = cr.fetchall()
        for (
            version_id,
            procedure_id,
            revision,
            old_state,
            change_summary,
            published_by,
            retired_by,
            published_at,
            retired_at,
            create_uid,
            create_date,
        ) in versions:
            state = _map_procedure_state(old_state)
            if revision == 1:
                cr.execute("""
                    UPDATE workshop_procedure
                    SET state = %s,
                        active = %s,
                        change_summary = %s,
                        published_by_id = %s,
                        published_at = %s,
                        archived_by_id = %s,
                        archived_at = %s
                    WHERE id = %s
                """, [
                    state,
                    state != 'archived',
                    change_summary,
                    published_by,
                    published_at,
                    retired_by,
                    retired_at,
                    procedure_id,
                ])
                continue

            cr.execute("""
                INSERT INTO workshop_procedure (
                    name, code, description, active, revision, state,
                    change_summary, published_by_id, published_at,
                    archived_by_id, archived_at, create_uid, write_uid,
                    create_date, write_date
                )
                SELECT name, code, description, %s, %s, %s, %s, %s, %s,
                       %s, %s, %s, write_uid, %s, write_date
                FROM workshop_procedure
                WHERE id = %s
            """, [
                state != 'archived',
                revision,
                state,
                change_summary,
                published_by,
                published_at,
                retired_by,
                retired_at,
                create_uid,
                create_date,
                procedure_id,
            ])

    cr.execute("SELECT to_regclass('workshop_order')")
    if cr.fetchone()[0] is None:
        return

    cr.execute("""
        UPDATE workshop_order
        SET state = CASE
            WHEN state IN ('cerrada', 'closed') THEN 'closed'
            WHEN state IN ('cancelada', 'cancelled') THEN 'cancelled'
            ELSE 'open'
        END
    """)
    cr.execute("""
        ALTER TABLE workshop_order
            ADD COLUMN IF NOT EXISTS technician_id integer,
            ADD COLUMN IF NOT EXISTS received_by_id integer
    """)
    order_columns = _table_columns(cr, 'workshop_order')
    if 'user_id' in order_columns:
        cr.execute("""
            UPDATE workshop_order
            SET technician_id = user_id
            WHERE technician_id IS NULL AND user_id IS NOT NULL
        """)
    if 'create_uid' in order_columns:
        cr.execute("""
            UPDATE workshop_order
            SET received_by_id = create_uid
            WHERE received_by_id IS NULL AND create_uid IS NOT NULL
        """)
