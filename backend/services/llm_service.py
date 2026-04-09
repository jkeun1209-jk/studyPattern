import os
import json
import anthropic
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """You are a Java Spring Boot expert specializing in design patterns.
When generating code examples, follow this layered package structure:
- contract/   : Interfaces and port definitions
- application/: Application services and use cases
- domain/     : Domain objects and business logic
- infra/      : Infrastructure implementations (Repository impl, external adapters)
- presentation/: Controllers, DTOs, Request/Response objects

IMPORTANT: Only include layers that are actually needed for the specific pattern.
Not every pattern requires all 5 layers.

All responses must be in JSON format only. Do not include any text outside the JSON object."""

EXAMPLE_PROMPT = """Generate a Java Spring Boot example for the **{pattern_name}** design pattern.

Return a JSON object with exactly these fields:
{{
  "overview": "2-3 sentence description of the pattern intent (in Korean)",
  "use_case": "2-3 sentences on when/why to use this in Spring Boot (in Korean)",
  "layers_used": ["list", "of", "layers", "actually", "used"],
  "example_code": "All Java classes in one string. Use '// ===== [PackagePath/ClassName.java] =====' as separator between each class file.",
  "package_structure": "Directory tree as a plain text string using ASCII characters (├──, └──, │)",
  "key_benefits": ["Korean benefit 1", "Korean benefit 2", "Korean benefit 3"]
}}

Requirements for the code:
- Base package: com.example.{pattern_key}
- Use appropriate Spring annotations (@Component, @Service, @Bean, @RestController, etc.)
- Include only layers meaningful for this pattern
- Code must be compilable and realistic for a real Spring Boot project
- Each class must have proper package declaration and imports"""


class LLMService:
    def __init__(self):
        self.client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    async def generate_example(self, pattern_name: str) -> dict:
        pattern_key = pattern_name.lower().replace(" ", "_").replace("-", "_")
        prompt = EXAMPLE_PROMPT.format(
            pattern_name=pattern_name, pattern_key=pattern_key
        )

        message = await self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )

        raw = message.content[0].text

        # JSON 블록이 포함된 경우 추출
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0].strip()

        result = json.loads(raw)

        return {
            "overview": result.get("overview", ""),
            "use_case": result.get("use_case", ""),
            "layers_used": result.get("layers_used", []),
            "example_code": result.get("example_code", ""),
            "package_structure": result.get("package_structure", ""),
            "key_benefits": result.get("key_benefits", []),
        }
