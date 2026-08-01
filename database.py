import aiosqlite

DB_NAME = "moderbot.db"


async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS group_warnings (
                chat_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                warnings INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (chat_id, user_id)
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                message_id INTEGER NOT NULL,
                reported_user_id INTEGER NOT NULL,
                reporter_user_id INTEGER NOT NULL,
                reason TEXT,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await db.commit()


async def get_warnings(chat_id: int, user_id: int) -> int:
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            """
            SELECT warnings
            FROM group_warnings
            WHERE chat_id = ? AND user_id = ?
            """,
            (chat_id, user_id),
        )

        row = await cursor.fetchone()
        return row[0] if row else 0


async def add_warning(chat_id: int, user_id: int) -> int:
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            INSERT INTO group_warnings (chat_id, user_id, warnings)
            VALUES (?, ?, 1)
            ON CONFLICT(chat_id, user_id)
            DO UPDATE SET warnings = warnings + 1
            """,
            (chat_id, user_id),
        )

        await db.commit()

        cursor = await db.execute(
            """
            SELECT warnings
            FROM group_warnings
            WHERE chat_id = ? AND user_id = ?
            """,
            (chat_id, user_id),
        )

        row = await cursor.fetchone()
        return row[0]


async def reset_warnings(chat_id: int, user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            DELETE FROM group_warnings
            WHERE chat_id = ? AND user_id = ?
            """,
            (chat_id, user_id),
        )
        await db.commit()


async def create_report(
    chat_id: int,
    message_id: int,
    reported_user_id: int,
    reporter_user_id: int,
    reason: str,
) -> int:
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            """
            INSERT INTO reports (
                chat_id,
                message_id,
                reported_user_id,
                reporter_user_id,
                reason
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                chat_id,
                message_id,
                reported_user_id,
                reporter_user_id,
                reason,
            ),
        )

        await db.commit()
        return cursor.lastrowid


async def close_report(report_id: int, status: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            UPDATE reports
            SET status = ?
            WHERE id = ? AND status = 'pending'
            """,
            (status, report_id),
        )
        await db.commit()

async def get_report(report_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            """
            SELECT
                chat_id,
                message_id,
                reported_user_id,
                reason,
                status
            FROM reports
            WHERE id = ?
            """,
            (report_id,),
        )

        return await cursor.fetchone()