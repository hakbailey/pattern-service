import json
import logging
import os

from .models import Pattern
from .models import Task
from .utils import build_collection_uri
from .utils import download_collection

logger = logging.getLogger(__name__)


def run_pattern_task(pattern_id: int, task_id: int) -> None:
    """
    Orchestrates downloading a collection and saving a pattern definition.
    """
    task = Task.objects.get(id=task_id)
    try:
        pattern = Pattern.objects.get(id=pattern_id)
        task.update_task_status("Running", {"info": "Processing pattern"})
        with download_collection(
            pattern.collection_name, pattern.collection_version
        ) as collection_path:
            path_to_definition = os.path.join(
                collection_path,
                "extensions",
                "patterns",
                pattern.pattern_name,
                "meta",
                "pattern.json",
            )
            with open(path_to_definition, "r") as file:
                definition = json.load(file)

            pattern.pattern_definition = definition
            pattern.collection_version_uri = build_collection_uri(
                pattern.collection_name, pattern.collection_version
            )
            pattern.save(update_fields=["pattern_definition", "collection_version_uri"])
        task.update_task_status("Completed", {"info": "Pattern processed successfully"})
    except FileNotFoundError:
        logger.error(f"Could not find pattern definition for task {task_id}")
        task.update_task_status("Failed", {"error": "Pattern definition not found."})
    except Exception as e:
        logger.error(f"Task {task_id} failed: {e}")
        task.update_task_status("Failed", {"error": str(e)})
