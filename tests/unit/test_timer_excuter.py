import asyncio
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp

from app.models.timer import TimerTask
from app.services.timer_excuter import TimerExecutor


