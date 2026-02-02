class PromptGenerator:
    def generate(self, scene_data):
        return f"Generate a video for scene: {scene_data.get('title')}"
