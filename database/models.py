# TODO: Make this more efficient by caching the data
# TODO: Make this parallel read/write safe

from __future__ import annotations

from typing import (
    List,
    Optional,
    TypedDict
)

import os
import logging

from discord.utils import setup_logging
from datetime import datetime, timezone, timedelta
from aiomysql import Pool, DictCursor


_log = setup_logging(
    'database',
    level=getattr(logging, os.getenv('DB_LOG_LEVEL', 'INFO'), logging.INFO),
    root=False
)


class PlanDataStructure(TypedDict):
    plan_id: int
    user_id: str
    daily_credits: int
    start_date: datetime
    end_date: datetime

    
class UserDataStructure(TypedDict):
    user_id: str
    credits: int
    model: str
    credits_spent: int
    prompt_amount: int
    last_used: datetime
    created: datetime
    plans: List[PlanDataStructure]
    
    
class UserData:
    pool: Pool
    
    def __init__(
            self,
            user_id: str,
            *,
            credits: int = 100,
            model: str = 'gpt-3.5-turbo',
            credits_spent: int = 0,
            prompt_amount: int = 0,
            last_used: datetime = datetime.now(),
            created: datetime = datetime.now(),
            plans: List[PlanData] = []
    ):
        self.user_id: str = user_id
        self.credits: int = credits
        self.model: str = model
        self.credits_spent: int = credits_spent
        self.prompt_amount: int = prompt_amount
        self.last_used: datetime = last_used
        self.created: datetime = created
        self.plans: List[PlanData] = plans

    def __repr__(self):
        return f"UserData(discord_user_id={self.user_id}, credits_left_today={self.credits}, model={self.model}," \
               f" credits_refilled={self.last_used}, created={self.created}, plans={self.plans})"
    
    @classmethod
    async def load(cls, user_id: str) -> UserData:
        # Load data from database
        async with cls.pool.acquire() as conn:
            async with conn.cursor(DictCursor) as cur:
                await cur.execute(
                    "SELECT * FROM users WHERE user_id = %s",
                    (user_id,)
                )
                data: Optional[UserDataStructure] = await cur.fetchone()
                if data is None:  # TODO: This can be handled by the db in one query
                    await cur.execute(
                        "INSERT INTO users (user_id) VALUES (%s)", user_id
                    )
                    await conn.commit()  # TODO: Why is this needed when we have autocommit enabled?
                    _log.debug("Created new user entry for user with id %s", user_id)
                    return cls(user_id)
                
                _log.debug("Loaded user entry for user with id %s", user_id)
                
                self = cls(**data)

        plans = await self.load_plans()
        
        last_used_utc = datetime.replace(self.last_used, tzinfo=timezone.utc)  # TODO: Store the time in UTC instead of local time
        if last_used_utc < datetime.now(timezone.utc) - timedelta(days=1):
            user_credits = 100
            for plan in plans:
                if plan.start_date.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc) < plan.end_date.replace(tzinfo=timezone.utc):
                    user_credits += plan.daily_credits
            
            self.credits = user_credits
            self.last_used = datetime.now()
            
        await self.save()
        return self
    
    async def load_plans(self) -> List[PlanData]:
        plans = []
        async with self.pool.acquire() as conn:
            async with conn.cursor(DictCursor) as cur:
                await cur.execute("SELECT * FROM user_plans WHERE user_id = %s", (self.user_id,))
                data: Optional[List[PlanDataStructure]] = await cur.fetchall()
                if data:
                    _log.debug(f"Loaded {len(data)} plans for user with id %s", self.user_id)
                    plans = [PlanData(**plan_data) for plan_data in data]
                
                self.plans = plans
                return plans

    async def save(self) -> None:
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "UPDATE users SET credits = %s, model = %s, last_used = %s WHERE user_id = %s",
                    (self.credits, self.model, self.last_used, self.user_id)
                )
                await conn.commit()  # TODO: Why is this needed when we have autocommit enabled?
                _log.debug("Saved user entry for user with id %s", self.user_id)


class PlanData:

    def __init__(
            self,
            id: int,
            user_id: str,
            daily_credits: int,
            start_date: datetime,
            end_date: datetime
    ) -> None:
        self.id: int = id
        self.user_id: str = user_id
        self.daily_credits: int = daily_credits
        self.start_date: datetime = start_date
        self.end_date: datetime = end_date

    def __repr__(self) -> str:
        return f"PlanData(daily_credits={self.daily_credits}, start_date={self.start_date}, end_date={self.end_date})"
