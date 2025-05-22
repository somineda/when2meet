import httpx
from starlette.status import HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_422_UNPROCESSABLE_ENTITY
from tortoise.contrib.test import TestCase

from app import app
from app.tortoise_models.meeting import MeetingModel


class TestMeetingRouter(TestCase):
    async def test_api_create_meeting_mysql(self) -> None:
        # When
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.post(url="/v1/mysql/meetings")

        # Then: 테스트 결과를 검증
        assert response.status_code == HTTP_200_OK
        url_code = response.json()["code"]

        assert (await MeetingModel.filter(url_code=url_code).exists()) is True

    async def test_api_get_meeting_mysql(self) -> None:

        async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app),
                base_url="http://test",
        ) as client:
            # Given
            meeting_create_response = await client.post("/v1/mysql/meetings")
            url_code = meeting_create_response.json()["url_code"]

            # When
            response = await client.get(f"v1/mysql/meetings/{url_code}")

        # Then
        self.assertEqual(response.status_code, HTTP_200_OK)
        response_body = response.json()
        self.assertEqual(response_body["url_code"], url_code)

    async def test_api_get_meeting_mysql_404(self) -> None:

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            # Given
            invalid_url_code = "invalid_url_code"

            # When
            response = await client.get(f"v1/mysql/meetings/{invalid_url_code}")

        # Then
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)
        response_body = response.json()
        self.assertEqual(response_body["detail"], "meeting with url_code: invalid_url_code not found")

    async def test_api_update_meeting_date_range_mysql(self) -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            # Given
            meeting_create_response = await client.post("/v1/mysql/meetings")
            url_code = meeting_create_response.json()["url_code"]

            # When
            response = await client.patch(
                f"v1/mysql/meetings/{url_code}/date_range",
                json={"start_date": "2025-10-12", "end_date": "2025-10-22"},
            )

        # Then
        self.assertEqual(response.status_code, HTTP_200_OK)
        response_body = response.json()
        self.assertEqual(response_body["url_code"], url_code)
        self.assertEqual(response_body["start_date"], "2025-10-12")
        self.assertEqual(response_body["end_date"], "2025-10-22")
        meeting = await MeetingModel.filter(url_code=url_code).get()
        self.assertEqual(meeting.start_date, date(2025, 10, 12))
        self.assertEqual(meeting.end_date, date(2025, 10, 22))


    async def test_can_not_update_meeting_date_range_when_range_is_too_long(self) -> None:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            # Given
            create_meeting_response = await client.post(url="/v1/mysql/meetings")
            url_code = create_meeting_response.json()["url_code"]

            # When
            response = await client.patch(
                url=f"/v1/mysql/meetings/{url_code}/date_range",
                json={"start_date": (start := "2025-10-10"), "end_date": (end := "2030-10-20")},
            )

        # Then
        assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY
        response_body = response.json()
        assert response_body["detail"] == f"start {start} and end {end} should be within {MEETING_DATE_MAX_RANGE.days} days"

    async def test_can_not_update_meeting_date_range_when_it_is_already_set(self) -> None:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            # Given
            create_meeting_response = await client.post(url="/v1/mysql/meetings")
            url_code = create_meeting_response.json()["url_code"]
            await client.patch(
                url=f"/v1/mysql/meetings/{url_code}/date_range",
                json={"start_date": "2025-10-10", "end_date": "2025-10-20"},
            )

            # When
            response = await client.patch(
                url=f"/v1/mysql/meetings/{url_code}/date_range",
                json={"start_date": "2025-10-12", "end_date": "2025-10-22"},
            )

        # Then
        assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY
        response_body = response.json()
        assert response_body["detail"] == f"meeting: {url_code} start: 2025-10-10 end: 2025-10-20 are already set"

    async def test_can_not_update_meeting_does_not_exists(self) -> None:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            # Given
            url_code = "invalid_url"

            # When
            response = await client.patch(
                url=f"/v1/mysql/meetings/{url_code}/date_range",
                json={"start_date": "2025-10-12", "end_date": "2025-10-22"},
            )

        # Then
        assert response.status_code == HTTP_404_NOT_FOUND
        response_body = response.json()
        assert response_body["detail"] == "meeting with url_code: invalid_url not found"
