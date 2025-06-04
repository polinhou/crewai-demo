import os
import google.generativeai as genai
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai.llms.base_llm import BaseLLM
from typing import Optional, List, Dict, Any, Union

# 載入環境變數
load_dotenv()

# 初始化 Gemini 客戶端
gemini_api_key = os.getenv('GEMINI_API_KEY')
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set")

genai.configure(api_key=gemini_api_key)

# 創建一個簡單的客戶端封裝
class GeminiClient:
    def __init__(self):
        self.chat = self
        self.completions = self
        self.model = None
    
    def create(self, **kwargs):
        # 這個方法只是為了兼容性，實際不會被調用
        raise NotImplementedError("Use generate_content directly")
    
    def generate_content(self, **kwargs):
        # 初始化模型（如果尚未初始化）
        if self.model is None:
            model_name = kwargs.get('model', 'gemini-pro').replace('models/', '')
            self.model = genai.GenerativeModel(model_name)
        
        # 準備生成配置
        generation_config = kwargs.get('generation_config', {})
        safety_settings = kwargs.get('safety_settings', [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ])
        
        # 調用模型
        response = self.model.generate_content(
            contents=kwargs.get('contents', []),
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        return response

# 初始化客戶端
client = GeminiClient()

class CustomLLM:
    def __init__(self, client):
        self.client = client
        self.model_name = "gemini-2.0-flash-lite"  # 使用 gemini-pro 模型
    
    def generate(self, messages, **kwargs):
        try:
            # 確保 messages 格式正確
            formatted_messages = [
                {"role": msg.get("role", "user"), "content": msg.get("content", "")}
                for msg in messages
            ]
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=formatted_messages,
                **kwargs
            )
            
            if hasattr(response, 'choices') and len(response.choices) > 0:
                return response.choices[0].message.content
            return ""
        except Exception as e:
            print(f"Error in CustomLLM: {str(e)}")
            raise

class GeminiLLM(BaseLLM):
    model_name = "gemini-2.0-flash-lite"  # Updated to match the actual model name
    
    def __init__(self, client, **kwargs):
        super().__init__(model=self.model_name, **kwargs)
        self.client = client
        # Initialize the model once
        self.model = genai.GenerativeModel(self.model_name)
    
    def call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        **kwargs
    ) -> str:
        try:
            # Clean up kwargs to only include supported parameters
            kwargs.pop('callbacks', None)
            kwargs.pop('stream', None)
            
            # Prepare generation config
            generation_config = {
                'temperature': kwargs.get('temperature', 0.7),
                'max_output_tokens': kwargs.get('max_tokens', 2048),
                'top_p': kwargs.get('top_p', 0.95),
                'top_k': kwargs.get('top_k', 40)
            }
            
            # Format the prompt for Gemini
            # Gemini expects a list of content parts
            if isinstance(prompt, str):
                prompt_parts = [prompt]
            else:
                prompt_parts = [str(part) for part in prompt]
            
            # Make the API call
            response = self.model.generate_content(
                prompt_parts,
                generation_config=generation_config,
                safety_settings=[
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "threshold": "BLOCK_NONE"
                    },
                    {
                        "category": "HARM_CATEGORY_HATE_SPEECH",
                        "threshold": "BLOCK_NONE"
                    },
                    {
                        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        "threshold": "BLOCK_NONE"
                    },
                    {
                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "threshold": "BLOCK_NONE"
                    }
                ]
            )
            
            # Extract and return the response text
            if hasattr(response, 'text'):
                return response.text
            elif hasattr(response, 'candidates') and response.candidates:
                return response.candidates[0].content.parts[0].text
            elif hasattr(response, 'result') and response.result:
                return response.result()
            return ""
            
        except Exception as e:
            print(f"Error in GeminiLLM: {str(e)}")
            print(f"Prompt type: {type(prompt)}")
            print(f"Prompt content: {prompt}")
            raise
            
    def _generate(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager=None,
        **kwargs
    ) -> str:
        return self.call(prompt, stop=stop, **kwargs)

# 創建自定義 LLM 實例
llm = GeminiLLM(client)

class WritingAssistantCrew:
    def __init__(self):
        self.researcher = Agent(
            role='資深研究員',
            goal='進行主題研究並收集相關資訊',
            backstory='''你是一位經驗豐富的研究員，擅長收集、分析並整理資訊。
            你擅長使用各種來源來獲取準確且相關的資訊。''',
            verbose=True,
            llm=llm
        )
        
        self.writer = Agent(
            role='專業作家',
            goal='撰寫高質量、引人入勝的內容',
            backstory='''你是一位才華洋溢的作家，擅長將複雜的資訊轉化為
            易於理解且引人入勝的內容。你特別擅長根據研究資料創作文章。''',
            verbose=True,
            llm=llm
        )
        
        self.editor = Agent(
            role='資深編輯',
            goal='確保內容準確、連貫且符合風格指南',
            backstory='''你是一位嚴謹的編輯，對細節有敏銳的觀察力。
            你擅長改進寫作風格、糾正錯誤並確保內容流暢。''',
            verbose=True,
            llm=llm
        )
    
    def create_article(self, topic, target_audience, word_count=1000):
        # 定義任務
        research_task = Task(
            description=f'''為主題"{topic}"進行深入研究。
            目標讀者：{target_audience}
            收集足夠的資訊來撰寫一篇{word_count}字的文章。
            確保資訊準確、相關且最新。''',
            agent=self.researcher,
            expected_output=f'''關於{topic}的詳細研究報告，包含：
            - 主要概念和定義
            - 關鍵事實和數據
            - 相關例子和案例研究
            - 當前趨勢和發展'''
        )
        
        write_task = Task(
            description=f'''根據研究結果，撰寫一篇關於"{topic}"的{word_count}字文章。
            目標讀者：{target_audience}
            確保內容：
            - 結構清晰
            - 資訊準確
            - 引人入勝
            - 符合目標讀者的需求''',
            agent=self.writer,
            expected_output=f'''一篇結構完整、內容豐富的{word_count}字文章，
            涵蓋{topic}的所有重要面向，並針對{target_audience}進行優化。'''
        )
        
        edit_task = Task(
            description=f'''編輯並改進作家撰寫的關於"{topic}"的文章。
            檢查以下內容：
            - 語法和拼寫錯誤
            - 內容準確性
            - 結構和流程
            - 風格一致性
            - 可讀性
            確保最終文章符合高標準的寫作質量。''',
            agent=self.editor,
            expected_output=f'''經過專業編輯的最終版文章，
            確保內容準確、風格一致且易於{target_audience}理解。'''
        )
        
        # 創建並運行團隊
        crew = Crew(
            agents=[self.researcher, self.writer, self.editor],
            tasks=[research_task, write_task, edit_task],
            verbose=True,  # 啟用詳細日誌
            process=Process.sequential  # 任務按順序執行
        )
        
        # 執行任務
        result = crew.kickoff()
        return result

# 使用範例
if __name__ == "__main__":
    # 創建寫作助手團隊
    writing_crew = WritingAssistantCrew()
    
    # 定義文章主題和目標讀者
    topic = "人工智慧在現代醫療中的應用"
    target_audience = "醫療專業人員和技術愛好者"
    
    print(f"開始生成關於'{topic}'的文章...")
    
    # 生成文章
    article = writing_crew.create_article(
        topic="人工智慧在現代醫療中的應用",
        target_audience="醫療專業人員和技術愛好者",
        word_count=1000
    )

    # 儲存文章
    with open("generated_article.md", "w", encoding="utf-8") as f:
        f.write(str(article))
    
    print("\n文章已生成並儲存為 generated_article.md")
    print("\n文章預覽：")
    print(str(article)[:500] + "...")  # 顯示前500個字符作為預覽