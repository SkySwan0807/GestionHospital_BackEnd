import httpx


class SpecialtyServiceUnavailableError(Exception):
    pass


class SpecialtyClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    async def validate_specialty(self, specialty_id: int) -> bool:
        url = f"{self.base_url}/api/v1/specialties/{specialty_id}"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
                
            if response.status_code == 200:
                return True
            elif response.status_code == 404:
                return False
            else:
                raise SpecialtyServiceUnavailableError(f"Unexpected status from specialty service: {response.status_code}")
                
        except httpx.RequestError as e:
            raise SpecialtyServiceUnavailableError(f"Cannot reach specialty service: {e}")
