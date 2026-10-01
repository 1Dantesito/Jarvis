import pytest
from core.media_provider import TrackItem, MediaCapability
from core.music_queue import MusicQueue, SmartQueue
from core.music_history import MusicHistory
from core.music_preferences import MusicPreferences
from core.recommendation_engine import RecommendationEngine
from core.music_engine import MusicEngine, PlaybackState
from core.orchestrator import JarvisOrchestrator
from providers.mock_provider import MockAIProvider

def test_music_queue_operations():
    q = MusicQueue()
    assert q.is_empty() is True

    t1 = TrackItem(id="vid1", title="In the End", artist="Linkin Park")
    t2 = TrackItem(id="vid2", title="Numb", artist="Linkin Park")
    t3 = TrackItem(id="vid3", title="Faint", artist="Linkin Park")

    q.add_multiple([t1, t2, t3])
    assert q.size() == 3
    assert q.get_current().id == "vid1"

    # Next track
    nxt = q.next_track()
    assert nxt.id == "vid2"
    assert q.get_current().id == "vid2"

    # Upcoming tracks
    upcoming = q.get_upcoming(limit=5)
    assert len(upcoming) == 1
    assert upcoming[0].id == "vid3"

    # Clear
    q.clear()
    assert q.is_empty() is True

def test_smart_queue_refill_logic():
    q = MusicQueue()
    sq = SmartQueue(q)
    assert sq.needs_refill() is True

    tracks = [TrackItem(id=f"id_{i}", title=f"Track {i}", artist="Artist") for i in range(6)]
    sq.add_smart_tracks(tracks)
    assert sq.needs_refill() is False

def test_recommendation_scoring_and_explanation():
    pref = MusicPreferences()
    hist = MusicHistory()
    engine = RecommendationEngine(pref, hist)

    t1 = TrackItem(id="lp_1", title="Crawling", artist="Linkin Park")
    t2 = TrackItem(id="pop_1", title="Random Pop", artist="Unknown Pop Singer")

    score_lp = engine.score_track(t1, reference_artist="Linkin Park")
    score_pop = engine.score_track(t2, reference_artist="Linkin Park")
    assert score_lp > score_pop

    exp = engine.explain_recommendation(t1, reference_artist="Linkin Park")
    assert "Linkin Park" in exp

def test_music_history_and_preference_learning():
    pref = MusicPreferences()
    hist = MusicHistory()
    t1 = TrackItem(id="song_1", title="Heavy Song", artist="New Metal Band")

    # Record play
    hist.record_play(t1)
    assert len(hist.get_recent_history()) == 1

    # Mark completed -> positive affinity
    initial_affinity = pref.get_artist_affinity("New Metal Band")
    pref.adjust_artist("New Metal Band", 0.05)
    assert pref.get_artist_affinity("New Metal Band") > initial_affinity

@pytest.mark.asyncio
async def test_music_engine_play_and_controls(monkeypatch):
    from unittest.mock import AsyncMock
    from core.youtube_provider import YouTubeProvider
    mock_tracks = [
        TrackItem(id="vid_lp_1", title="In the End", artist="Linkin Park"),
        TrackItem(id="vid_lp_2", title="Numb", artist="Linkin Park"),
        TrackItem(id="vid_lp_3", title="Faint", artist="Linkin Park")
    ]
    monkeypatch.setattr(YouTubeProvider, "search_tracks", AsyncMock(return_value=mock_tracks))

    engine = MusicEngine()
    res = await engine.play_query("Linkin Park")
    assert res["success"] is True
    assert res["status"] == "PLAYBACK_STARTED"
    assert len(res["playlist"]) > 0

    # Pause
    res_pause = engine.pause()
    assert res_pause["status"] == "PAUSED"

    # Resume
    res_resume = engine.resume()
    assert res_resume["status"] == "PLAYING"

    # Skip
    res_skip = await engine.skip()
    assert res_skip["success"] is True

    # Now playing
    np = engine.get_now_playing()
    assert np["is_playing"] is True

    # Clear queue
    cl = engine.clear_queue()
    assert cl["success"] is True

@pytest.mark.asyncio
async def test_orchestrator_multimedia_prompts(monkeypatch):
    from unittest.mock import AsyncMock
    from core.youtube_provider import YouTubeProvider
    mock_tracks = [
        TrackItem(id="vid_lp_1", title="In the End", artist="Linkin Park")
    ]
    monkeypatch.setattr(YouTubeProvider, "search_tracks", AsyncMock(return_value=mock_tracks))

    orch = JarvisOrchestrator(primary_provider=MockAIProvider())
    res = await orch.process_user_input("Ponme Linkin Park")
    assert res["success"] is True
    tools = [t["tool_name"] for t in res["tools_executed"]]
    assert "play_music" in tools
