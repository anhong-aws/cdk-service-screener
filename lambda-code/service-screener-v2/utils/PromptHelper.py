import json
from pathlib import Path

class PromptHelper:
    def __init__(self, root_dir):
        self.root_dir = Path(root_dir)
        summary_prompts_file = self.root_dir / 'summary_prompts.json'
        try:
            with summary_prompts_file.open('r', encoding='utf-8') as f:
                self.summary_prompts = json.load(f)
        except FileNotFoundError:
            self.summary_prompts = {}
            print(f"Warning: {summary_prompts_file} not found. Using an empty dictionary.")
            # 这里再次引发异常
            raise FileNotFoundError(f"{summary_prompts_file} not found.")

    def getPromptByService(self, summary_type, service):
        prompt = self.summary_prompts[summary_type][0].format(service=service)
        # print(f"------ai prompt 1------:\n{prompt}")
        return prompt
    def getPromptByServices(self, summary_type, services):
        services_str = ','.join(services)
        prompt = self.summary_prompts[summary_type][1].format(services=services_str)
        # print(f"------ai prompt 2------:\n{prompt}")
        return prompt