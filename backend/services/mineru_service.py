import json
import time
import zipfile
from pathlib import Path
from typing import Optional, Dict, Any
import requests
from .task_manager import task_manager, TaskType, TaskStatus
from utils.config import TOKEN, RAW_JSON_DIR
from utils.storage import storage

UPLOAD_URL = "https://mineru.net/api/v4/file-urls/batch"
RESULT_URL_TEMPLATE = "https://mineru.net/api/v4/extract-results/batch/{batch_id}"
HEADER = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {TOKEN}"
}
PROXIES = {"http": None, "https": None}
POLL_INTERVAL = 3
POLL_TIMEOUT = 300


class MinerUService:
    def __init__(self):
        self.output_dir = RAW_JSON_DIR

    async def extract(self, file_path: Path, task_id: str) -> Optional[Path]:
        task = task_manager.get_task(task_id)
        if not task:
            return None

        try:
            task.update_status(TaskStatus.PROCESSING, progress=10, step="准备上传文件...")

            data_id = file_path.stem.lower().replace(' ', '_').replace('-', '_')
            data = {
                "files": [{"name": file_path.name, "data_id": data_id, "file_type": file_path.suffix.lower()}],
                "model_version": "vlm"
            }

            task.update_status(TaskStatus.PROCESSING, progress=20, step="申请上传URL...")
            response = requests.post(UPLOAD_URL, headers=HEADER, json=data, timeout=30, proxies=PROXIES)
            response.raise_for_status()
            result = response.json()

            if result["code"] != 0:
                raise RuntimeError(f'申请上传URL失败: {result["msg"]}')

            batch_id = result["data"]["batch_id"]
            urls = result["data"]["file_urls"]

            task.update_status(TaskStatus.PROCESSING, progress=30, step="上传文件到云存储...")
            with file_path.open("rb") as f:
                upload_response = requests.put(urls[0], data=f, timeout=120, proxies=PROXIES)
            if upload_response.status_code != 200:
                raise RuntimeError(f"上传失败: {upload_response.status_code}")

            task.update_status(TaskStatus.PROCESSING, progress=40, step="等待MinerU处理...")
            extract_results = self._wait_until_done(batch_id, task)

            task.update_status(TaskStatus.PROCESSING, progress=80, step="下载并处理结果...")
            result_path = self._download_and_process(extract_results[0], file_path.stem)

            if result_path:
                task.update_status(TaskStatus.COMPLETED, progress=100, step="完成")
                task.set_result(str(result_path))
                return result_path
            else:
                raise RuntimeError("处理结果失败")

        except Exception as e:
            task.set_error(str(e))
            return None

    def _wait_until_done(self, batch_id: str, task) -> list:
        start_time = time.time()
        while time.time() - start_time < POLL_TIMEOUT:
            response = requests.get(
                RESULT_URL_TEMPLATE.format(batch_id=batch_id),
                headers=HEADER, timeout=30, proxies=PROXIES
            )
            response.raise_for_status()
            result = response.json()

            if result["code"] != 0:
                raise RuntimeError(f'查询结果失败: {result["msg"]}')

            extract_results = result["data"].get("extract_result", [])
            if extract_results:
                states = [item["state"] for item in extract_results]
                if any(state == "failed" for state in states):
                    raise RuntimeError("MinerU处理失败")
                if all(state == "done" for state in states):
                    return extract_results

                progress = 40 + int(30 * len([s for s in states if s == "done"]) / len(states))
                task.update_status(TaskStatus.PROCESSING, progress=progress, step=f"处理中... {states}")

            time.sleep(POLL_INTERVAL)

        raise TimeoutError(f"轮询超时，超过{POLL_TIMEOUT}秒")

    def _download_and_process(self, extract_result: dict, file_stem: str) -> Optional[Path]:
        zip_url = extract_result["full_zip_url"]
        zip_path = self.output_dir / f"{file_stem}.zip"
        extract_dir = self.output_dir / file_stem

        try:
            response = requests.get(zip_url, stream=True, timeout=120, proxies=PROXIES)
            response.raise_for_status()

            with zip_path.open("wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            extract_dir.mkdir(exist_ok=True)

            with zipfile.ZipFile(zip_path, "r") as zip_file:
                content_list_json = None
                for file_info in zip_file.filelist:
                    if file_info.filename.endswith('_content_list.json'):
                        zip_file.extract(file_info, extract_dir)
                        content_list_json = extract_dir / file_info.filename
                        break

                if not content_list_json:
                    for file_info in zip_file.filelist:
                        if file_info.filename.endswith('.json'):
                            zip_file.extract(file_info, extract_dir)
                            content_list_json = extract_dir / file_info.filename
                            break

            zip_path.unlink()

            if content_list_json:
                for file in extract_dir.iterdir():
                    if file.name != content_list_json.name:
                        file.unlink()
                return content_list_json

        except Exception as e:
            print(f"下载或处理失败: {e}")

        return None

    async def extract_batch(self, file_paths: list, task_ids: list) -> list:
        results = []
        for file_path, task_id in zip(file_paths, task_ids):
            result = await self.extract(file_path, task_id)
            results.append(result)
        return results


mineru_service = MinerUService()
