# 智能寫作助手 (AI Writing Assistant)

這是一個使用 CrewAI 框架構建的智能寫作助手，能夠自動生成高質量的文章內容。系統由多個 AI 代理協同工作，包括研究員、作家和編輯，共同完成從主題研究到最終文章生成的全過程。

## 功能特點

- **自動研究**：自動收集和分析主題相關資訊
- **高質量寫作**：生成結構清晰、內容豐富的文章
- **專業編輯**：確保內容準確性、連貫性和風格一致性
- **可自定義**：可調整目標讀者、字數和主題

## 環境需求

- Python 3.10-3.12
- [Poetry](https://python-poetry.org/) (Python 套件管理工具)
- Google Gemini API 金鑰

## 安裝步驟

1. 克隆此儲存庫
   ```bash
   git clone <repository-url>
   cd crewai-writing-assistant
   ```

2. 使用 Poetry 安裝依賴套件
   ```bash
   # 安裝 Poetry (如果尚未安裝)
   curl -sSL https://install.python-poetry.org | python3 -
   
   # 安裝專案依賴
   poetry install
   ```

3. 設定環境變數
   - 複製 `.env.example` 為 `.env`
   - 在 `.env` 中設置您的 Google Gemini API 金鑰
   ```
   GEMINI_API_KEY=your_google_gemini_api_key_here
   ```

## 使用方法

1. 編輯 `writing_assistant.py` 中的以下參數：
   - `topic`：您想要撰寫的主題
   - `target_audience`：目標讀者群體
   - `word_count`：期望的文章字數（可選，預設1000字）

2. 使用 Poetry 運行腳本：
   ```bash
   # 進入 Poetry shell（可選）
   poetry shell
   
   # 或者直接運行
   poetry run python writing_assistant.py
   ```

3. 生成的文章將保存為 `generated_article.txt`

## 開發

### 安裝新的依賴

使用 Poetry 添加新的依賴：

```bash
poetry add package_name
```

### 更新依賴

更新所有依賴到最新版本：

```bash
poetry update
```

### 檢查更新

檢查過時的依賴：

```bash
poetry show --outdated
```

## 自定義選項

- 在 `WritingAssistantCrew` 類中，您可以調整代理的提示詞和任務描述以滿足特定需求
- 可以添加更多代理（如校對員、SEO專家等）來擴展功能
- 調整 `llm` 參數以使用不同的語言模型

## 範例輸出

運行腳本後，您將獲得一個結構完整的文章，包含：
- 吸引人的標題
- 引人入勝的引言
- 結構清晰的主體段落
- 簡潔有力的結論

## 授權

MIT License

## 貢獻

歡迎提交 Issue 和 Pull Request
