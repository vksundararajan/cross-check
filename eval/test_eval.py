import pytest
import dotenv
from pathlib import Path
from google.adk.evaluation.agent_evaluator import AgentEvaluator

pytest_plugins = ("pytest_asyncio",)


@pytest.fixture(scope="session", autouse=True)
def load_env():
    env_path = Path(__file__).parent.parent / ".env"
    if not env_path.exists():
        env_path = ".env"
    dotenv.load_dotenv(str(env_path))


@pytest.mark.asyncio
async def test_legitimate():
    data_path = Path(__file__).parent / "data/legitimate.evalset.json"
    await AgentEvaluator.evaluate(
        agent_module="engine",
        eval_dataset_file_path_or_dir=str(data_path),
        num_runs=1
    )


@pytest.mark.asyncio
async def test_phishing():
    data_path = Path(__file__).parent / "data/phishing.evalset.json"
    await AgentEvaluator.evaluate(
        agent_module="engine",
        eval_dataset_file_path_or_dir=str(data_path),
        num_runs=1
    )


@pytest.mark.asyncio
async def test_behavioral():
    data_path = Path(__file__).parent / "data/behavioral.evalset.json"
    await AgentEvaluator.evaluate(
        agent_module="engine",
        eval_dataset_file_path_or_dir=str(data_path),
        num_runs=1
    )