from datetime import datetime, timezone, timedelta
from aiomysql import Pool, DictCursor

from database.connection import get_pool


class UserData:

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.credits = 100
        self.model = 'gpt-3.5-turbo'
        self.credits_spent = 0
        self.prompt_amount = 0
        self.last_used = datetime.now()
        self.created = datetime.now()
        self.plans = []

    def __repr__(self):
        return f"UserData(discord_user_id={self.user_id}, credits_left_today={self.credits}, model={self.model}," \
               f" credits_refilled={self.last_used}, created={self.created}, plans={self.plans})"

    async def load(self):
        # Load data from database
        pool: Pool = await get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor(DictCursor) as cur:
                await cur.execute("SELECT * FROM users WHERE user_id = %s", (self.user_id,))
                data = await cur.fetchone()
                if data is None:
                    await cur.execute("INSERT INTO users (user_id) VALUES (%s)",
                                      self.user_id)
                    await conn.commit()
                    print("Created new user entry for user with id", self.user_id)
                    return self
                self.credits = data['credits']
                self.model = data['model']
                self.credits_spent = data['credits_spent']
                self.prompt_amount = data['prompt_amount']
                self.last_used = data['last_used']
                self.created = data['created']
                print("Loaded user entry for user with id", self.user_id)

        pool.close()
        await pool.wait_closed()
        await self.load_plans()
        last_used_utc = datetime.replace(self.last_used, tzinfo=timezone.utc)
        if last_used_utc < datetime.now(timezone.utc) - timedelta(days=1):
            user_credits = 100
            if self.plans:
                for plan in self.plans:
                    if plan.start_date.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc) < plan.end_date.replace(tzinfo=timezone.utc):
                        user_credits += plan.daily_credits
            self.credits = user_credits
            self.last_used = datetime.now()
            await self.save()
        return self

    async def load_plans(self):
        pool: Pool = await get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor(DictCursor) as cur:
                await cur.execute("SELECT * FROM user_plans WHERE user_id = %s", (self.user_id,))
                data = await cur.fetchall()
                if data is None:
                    return
                for plan in data:
                    self.plans.append(PlanData(plan['id'], plan['user_id'], plan['daily_credits'], plan['start_date'], plan['end_date']))
                print(f"Loaded {len(self.plans)} plans for user with id", self.user_id)
        pool.close()
        await pool.wait_closed()
        return self

    async def save(self):
        pool: Pool = await get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("UPDATE users SET credits = %s, model = %s, last_used = %s WHERE user_id = %s", (self.credits, self.model, self.last_used, self.user_id))
                await conn.commit()
                print("Saved user entry for user with id", self.user_id)
        pool.close()
        await pool.wait_closed()


class PlanData:

    def __init__(self, user_plan_id: int, user_id: str = None, daily_credits: int = 0, start_date: datetime = None, end_date: datetime = None):
        self.id = user_plan_id
        self.user_id = user_id
        self.daily_credits = daily_credits
        self.start_date = start_date
        self.end_date = end_date

    def __repr__(self):
        return f"PlanData(daily_credits={self.daily_credits}, start_date={self.start_date}, end_date={self.end_date})"
