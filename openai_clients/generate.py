import os
from openai_client import openai_client


class LLMDialog:
    def __init__(self):
        self.messages = []

    def assign(self, role, content):
        self.messages.append({"role": role, "content": content})

    def to_openai(self):
        return self.messages


class StableDiffusionSummary:
    def __init__(self):
        self.client = openai_client()

    def process(self, data):

        # Формирование диалога
        dialog = LLMDialog()
        summarized_text = (
            "Extract the key visual and thematic elements from the following text and make it into a prompt for "
            "generating an image in Stable Diffusion with maximum length of && tokens:\n\n" + data
        )
        dialog.assign("user", summarized_text)

        # Отправка запроса в Azure OpenAI или обычный OpenAI
        openai_chat_completion_model_name = os.getenv("OPENAI_CHAT_COMPLETION_MODEL_NAME")

        response = self.client.chat(model=openai_chat_completion_model_name,
                                    messages=dialog.to_openai())

        result = ''
        for choice in response['choices']:
            result += choice['message']['content']
        # Убираем ненужные начальные заголовки
        unwanted_prompt_starts = [
            "Prompt for Stable Diffusion:",
            "Prompt for Stable Diffusion Image Generation:"
        ]
        for unwanted in unwanted_prompt_starts:
            if result.startswith(unwanted):
                result = result[len(unwanted):].strip()
        return result.strip()  # Убедимся, что нет лишних пробелов в начале и конце

def generate_curl_command(prompt):
    curl_command = (
        f"curl -x socks5://127.0.0.1:1080 -d \"prompt='{prompt}'&seed=5466973843955452462\" "
        "-X POST https://dev.wisebuddy.ai/sdPoombCapibara/generate --output save.png"
    )
    return curl_command

if __name__ == "__main__":
    os.environ["OPENAI_CHAT_COMPLETION_MODEL_NAME"] = "gpt-4o"

    summary_generator = StableDiffusionSummary()
    data = """
Understanding the gravity of the situation, you turn to the owl-like creatures, who have been quietly observing your progress. Their wise, knowing eyes and augmented reality glasses give them an aura of sagacity. You approach the closest one, a particularly large owl whose feathers glint with tiny embedded circuits.
"Wise ones," you begin, bowing your head slightly in respect, "I could use your guidance to ensure that I perform the alignments correctly and efficiently."
The large owl nods solemnly, its mechanical eyes lighting up with a deep, cerulean glow. "Greetings, Lucky Capybara," it hoots softly, a ripple of harmonious sound emanating from its beak. "We’ve watched as you’ve deftly handled the fragment and initiated the balancing process. The sphere requires precise alignment of the stone pillars to harness its full power. We shall assist you."
The owl begins to explain the nuances of the alignment process. "Each pillar resonates with a different frequency. By touching them in sequence, you must harmonize their energies to that of the sphere. Follow the tones you hear and watch how the runes react; they will guide your path."
Another owl flutters over, holding a small, crystalline device. "This tuning crystal will help you," it says, handing you the device. "Use it to adjust the frequencies of the stone pillars. We’ll monitor your progress and provide feedback."
With the guidance of the owls and the tuning crystal in your paw, you return to the stone pillars. Each one hums at a different pitch, their runes glowing in varying shades and intensities. You begin to work, using the tuning crystal to adjust each pillar’s frequency.
As you touch the tuning crystal to the first pillar, the runes flare brightly, emitting a harmonious tone that reverberates through the clearing. The owl-like creatures hoot in approval, their feedback keeping you on track.
One by one, you move from pillar to pillar, carefully adjusting each frequency. The symbols react positively, aligning themselves with the central sphere. The stone pillars and the sphere seem to form a resonant loop, their glowing energies synchronizing more with each step you take.
"""
    prompt = summary_generator.process(data)
    curl_command = generate_curl_command(prompt)
    print(curl_command)
