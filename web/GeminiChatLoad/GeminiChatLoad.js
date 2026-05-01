(function() {
    const selectors = [
        'div[class*="message"]',
        'div[class*="content"]',
        '.markdown',
        '[role="presentation"]'
    ];

    const elements = document.querySelectorAll(selectors.join(','));
    let chatLog = "--- DIALOG OUTPUT (IMPROVED SCRIPT) ---\n\n";
    let lastText = "";

    elements.forEach((el) => {
        const hasChildMatch = Array.from(el.querySelectorAll(selectors.join(','))).length > 0;
        const text = el.innerText.trim();

        if (text && !hasChildMatch && text !== lastText && text.length > 1) {
            const isModel = el.closest('[class*="model"]') || el.innerHTML.includes('svg');
            const role = isModel ? "GEMINI" : "USER";

            chatLog += `[${role}]:\n${text}\n`;
            chatLog += "-".repeat(40) + "\n\n";
            lastText = text;
        }
    });

    if (chatLog.length < 200) {
        console.warn("No exact blocks found, try emergency method...");
        chatLog += document.body.innerText;
    }

    const blob = new Blob([chatLog], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat_rescue_export.txt`;
    a.click();

    console.log("If the file downloaded, check the contents. If it's a mess, the interface is too secure.");
})();