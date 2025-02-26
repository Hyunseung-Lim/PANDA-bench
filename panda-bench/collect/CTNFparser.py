from langchain_community.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
import json
import os

os.environ["OPENAI_API_KEY"] = ""
chat = ChatOpenAI(model="gpt-4o")

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
input_folder = os.path.join(parent_dir, "data", "record")
output_folder = os.path.join(parent_dir, "data", "parsed_CTNF")
PROMPT_PATH = os.path.join(current_dir, "parsing_prompt.txt")

os.makedirs(output_folder, exist_ok=True)

def load_prompt():
    try:
        with open(PROMPT_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"프롬프트 파일을 찾을 수 없습니다: {PROMPT_PATH}")

question = load_prompt()

def main(start_num: int, end_num: int):
    for i in range(start_num, end_num + 1):
        formatted_num = f"{i:05d}"  # 5자리 숫자로 포맷팅 (00001, 00002, ...)
        
        # rec_r00001_로 시작하는 파일 찾기
        target_file = None
        for file_name in os.listdir(input_folder):
            if file_name.startswith(f"rec_r{formatted_num}_") and file_name.endswith(".json"):
                target_file = file_name
                break
        
        if not target_file:
            print(f"File not found for number: {formatted_num}")
            continue

        file_path = os.path.join(input_folder, target_file)
        # JSON 읽기
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        application_number = data.get("applicationNumber", "").strip()
        claims = data.get("initialClaims", "")
        ctnf_body_text = data.get("CTNFBodyText", "").strip()

        response = chat([HumanMessage(content=question +  "\n Corressponding Claims:\n" + "\n".join(claims) + "\n CTNF document:\n" + ctnf_body_text)])

        # Save the response to a JSON file
        response_content = response.content.strip()
        if response_content.startswith("```json") and response_content.endswith("```"):
            # ```json과 ```를 제거하고 중간의 JSON만 추출
            json_content = response_content[7:-3].strip()
        else:
            # ```json ``` 형식이 아니라면 그대로 사용
            json_content = response_content

        try:
            data = json.loads(json_content)
        except json.JSONDecodeError:
            print("Invalid JSON format in the response.")
            data = {}

        output_file_name = f"pC_r{formatted_num}_{application_number}.json"
        output_path = os.path.join(output_folder, output_file_name)

        # JSON 저장
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        print(f"Response saved to {output_file_name}")

start_num = 7  # 시작 번호
end_num = 25   # 끝 번호
main(start_num, end_num)