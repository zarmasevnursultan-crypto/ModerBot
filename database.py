import aiosqlite

DB_NAME = "moderbot.db"


async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS warnings (
                user_id INTEGER PRIMARY KEY,
                warnings INTEGER DEFAULT 0
            )
        """)
        await db.commit()

async def get_warnings(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT warnings FROM warnings WHERE user_id = ?",
            (user_id,)
        )

        row = await cursor.fetchone()

        if row is None:
            return 0

        return row[0]


async def add_warning(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            "SELECT warnings FROM warnings WHERE user_id = ?",
            (user_id,)
        )

        row = await cursor.fetchone()

        if row is None:
            await db.execute(
                "INSERT INTO warnings (user_id, warnings) VALUES (?, ?)",
                (user_id, 1)
            )
            await db.commit()
            return 1

        warnings = row[0] + 1

        await db.execute(
            "UPDATE warnings SET warnings = ? WHERE user_id = ?",
            (warnings, user_id)
        )

        await db.commit()

        return warnings


async def reset_warnings(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "DELETE FROM warnings WHERE user_id = ?",
            (user_id,)
        )
        await db.commit()