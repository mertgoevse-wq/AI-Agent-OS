"""Tests for the Model Router and Mock Provider."""

import pytest
from src.models.router import ModelRouter, ModelProvider, ModelResponse
from src.models.providers import MockProvider


class TestMockProvider:
    """Test the Mock Provider."""

    @pytest.mark.asyncio
    async def test_generate_response(self):
        provider = MockProvider()
        messages = [{"role": "user", "content": "Hello"}]
        response = await provider.generate(messages, model="mock")
        assert isinstance(response, ModelResponse)
        assert response.content is not None
        assert "Hello" in response.content
        assert response.provider == "mock"
        assert response.usage["total_tokens"] == 30

    @pytest.mark.asyncio
    async def test_generate_empty_message(self):
        provider = MockProvider()
        messages = []
        response = await provider.generate(messages, model="mock")
        assert "No input provided" in response.content

    @pytest.mark.asyncio
    async def test_call_count(self):
        provider = MockProvider()
        assert provider.call_count == 0
        await provider.generate([{"role": "user", "content": "Hi"}])
        assert provider.call_count == 1
        await provider.generate([{"role": "user", "content": "Hi"}])
        assert provider.call_count == 2

    @pytest.mark.asyncio
    async def test_stream(self):
        provider = MockProvider()
        messages = [{"role": "user", "content": "Hello world"}]
        tokens = []
        async for token in provider.stream(messages):
            tokens.append(token)
        assert len(tokens) > 0
        full_response = "".join(tokens)
        assert "Hello" in full_response

    @pytest.mark.asyncio
    async def test_delay(self):
        """Test that delay parameter works."""
        import time
        provider = MockProvider(delay=0.05)
        messages = [{"role": "user", "content": "Hello"}]
        start = time.time()
        await provider.generate(messages)
        elapsed = time.time() - start
        assert elapsed >= 0.05


class TestModelRouter:
    """Test the Model Router."""

    def setup_method(self):
        self.router = ModelRouter()
        self.mock = MockProvider()
        self.router.register_provider("mock", self.mock)
        self.router.register_provider("openai", self.mock)  # Use mock for testing

    def test_register_provider(self):
        assert "mock" in self.router.list_providers()
        assert "openai" in self.router.list_providers()

    def test_get_provider(self):
        provider = self.router.get_provider("mock")
        assert provider is not None
        assert isinstance(provider, MockProvider)

    def test_get_provider_not_found(self):
        with pytest.raises(ValueError, match="not registered"):
            self.router.get_provider("nonexistent")

    def test_list_providers(self):
        providers = self.router.list_providers()
        assert "mock" in providers
        assert "openai" in providers

    @pytest.mark.asyncio
    async def test_route_to_mock(self):
        """Default model should route to mock provider."""
        messages = [{"role": "user", "content": "Test"}]
        response = await self.router.generate(messages, model="mock")
        assert response.provider == "mock"

    @pytest.mark.asyncio
    async def test_route_openai_model(self):
        """Model starting with 'gpt' should route to openai provider."""
        messages = [{"role": "user", "content": "Test"}]
        response = await self.router.generate(messages, model="gpt-4o")
        assert response is not None

    @pytest.mark.asyncio
    async def test_route_unknown_model_defaults_to_mock(self):
        """Unknown model should default to mock."""
        messages = [{"role": "user", "content": "Test"}]
        response = await self.router.generate(messages, model="unknown-model")
        assert response.provider == "mock"

    @pytest.mark.asyncio
    async def test_stream_routing(self):
        """Stream should route correctly."""
        messages = [{"role": "user", "content": "Test"}]
        tokens = []
        async for token in self.router.stream(messages, model="mock"):
            tokens.append(token)
        assert len(tokens) > 0

    @pytest.mark.asyncio
    async def test_generate_with_kwargs(self):
        """Extra kwargs should be passed through."""
        provider = MockProvider()
        self.router.register_provider("custom", provider)
        messages = [{"role": "user", "content": "Hello"}]
        response = await self.router.generate(
            messages, model="custom", temperature=0.5, max_tokens=100
        )
        assert response is not None