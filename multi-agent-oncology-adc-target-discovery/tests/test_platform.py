from src.coordinator import Coordinator
from src.llm import OpenRouterFreeLLM
def test_defaults(monkeypatch):
 monkeypatch.delenv("OPENROUTER_API_KEY",raising=False);x=OpenRouterFreeLLM();assert x.model=="openrouter/free";assert x.base_url=="https://openrouter.ai/api/v1";assert not x.available
def test_rank():
 r,p=Coordinator("data").rank("NSCLC");assert r[0].gene=="TROP2";assert len(r)==5
def test_json_extract():assert OpenRouterFreeLLM._extract_json_object("x {\"a\":1} y")["a"]==1
