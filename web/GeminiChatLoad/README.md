# GeminiChatLoad

A universal JavaScript utility designed for quick extraction and local archiving of message history from LLM web interfaces into a plain text file (`.txt`).

## Description
This tool employs heuristic DOM analysis to identify message containers. Using flexible selectors, the script is capable of "scraping" text not only from **Gemini** but also from most popular AI platforms, including ChatGPT, Claude, and DeepSeek.

## Important Notes (Disclaimer)
*   **Role Labeling**: The logic is hardcoded to label AI responses as `[GEMINI]` and author messages as `[USER]`. This remains consistent even when used on platforms other than Gemini.
*   **Privacy**: The script operates entirely on the client side. No data is transmitted to external servers; the file is generated and downloaded locally within your browser.

## How to Use
1.  **Preparation**: Open the desired chat and scroll to the very top to ensure the browser has loaded the full message history into the page memory.
2.  **Execution**:
    *   Press `F12` (or `Ctrl + Shift + I`) and navigate to the **Console** tab.
    *   Paste the code from `GeminiChatLoad.js` into the input field.
    *   Press `Enter`.
3.  **Result**: Your browser will automatically prompt you to save `chat_rescue_export.txt` containing the entire conversation.

## Technical Features
*   **Atomic Data Collection**: The script performs nested element checks to prevent text duplication (ignoring parent containers once the leaf text has been extracted).
*   **Emergency Mode**: If standard selectors fail due to UI updates, the script triggers a fallback method to export all accessible page text via `document.body.innerText`.
*   **Formatting**: Each message is separated by a visual divider for better readability in text editors.

---
*Created by [REvDl](https://github.com/REvDl)*