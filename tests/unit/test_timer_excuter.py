import asyncio
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp

from app.models.timer import TimerTask
from app.services.timer_excuter import TimerExecutor


class TestTimerExecutor(unittest.TestCase):
    def setUp(self):
        self.executor = TimerExecutor()

    def tearDown(self):
        asyncio.run(self.executor.close())

    @patch("aiohttp.ClientSession.get")
    def test_execute_task_success(self, mock_get):
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value="Success")
        mock_get.return_value.__aenter__.return_value = mock_response

        response = asyncio.run(self.executor.execute_task("http://example.com"))

        self.assertEqual(response.status, 200)
        self.assertEqual(response.content, "Success")

    @patch("aiohttp.ClientSession.get")
    def test_execute_task_failure(self, mock_get):
        mock_get.side_effect = aiohttp.ClientError("Connection error")

        response = asyncio.run(self.executor.execute_task("http://example.com"))

        self.assertEqual(response.status, 500)
        self.assertEqual(response.content, "Connection error")

    @patch("aiohttp.ClientSession.get")
    def test_create_task(self, mock_get):
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value="Success")
        mock_get.return_value.__aenter__.return_value = mock_response

        timer_task = TimerTask(
            id=1, url="http://example.com", expires_at=datetime.now(timezone.utc) + timedelta(seconds=1)
        )

        response = asyncio.run(self.executor.create_task(timer_task))

        self.assertEqual(response.status, 200)
        self.assertEqual(response.content, "Success")
        self.assertNotIn(timer_task.id, self.executor.tasks)

    @patch("aiohttp.ClientSession.get")
    def test_add_task(self, mock_get):
        timer_task = TimerTask(
            id=1, url="http://example.com", expires_at=datetime.now(timezone.utc) + timedelta(seconds=1)
        )

        self.executor.add_task(timer_task)

        self.assertIn(timer_task.id, self.executor.tasks)
        self.assertTrue(asyncio.isfuture(self.executor.tasks[timer_task.id]))


if __name__ == "__main__":
    unittest.main()
