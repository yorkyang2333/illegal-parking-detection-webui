document.addEventListener('DOMContentLoaded', function() {
    const runButton = document.getElementById('run-button');
    const promptInput = document.getElementById('prompt-input');
    
    const finalOutput = document.getElementById('final-output');
    const resetButton = document.getElementById('reset-button');
    const converter = new showdown.Converter();

    const PREFILLED_PROMPT_TEXT = `现有一段违停的分析报告：
[粘贴Gemini生成的违停分析报告]
由QVQ-Max重新识别了车牌号为：
[粘贴QVQ-Max识别到的车牌号]
请帮我把QVQ-Max识别到的车牌号替换报告中原先识别到的车牌号，依据且仅依据原报告中的内容，重新生成一份详尽违停报告。请依次输出：
1.违停车辆车牌号
2.该车辆违停原因（根据原分析报告中的内容进一步总结得出）
3.建议处罚（根据现行《中华人民共和国道路交通安全法》）
请确保仅按照原报告中的内容进行重新输出，保证格式清晰明确，逻辑性强，不要主观臆断。`;

    let prompt = [
        {
            "role": "user",
            "content": [
                {"video": []},
                {"text" : ""}
            ]
        }
    ];

    

    

    // Helper function to add/remove notification badge
    function toggleNotificationBadge(element, show, targetElementSelector = null) {
        let targetElement = element;
        if (targetElementSelector) {
            targetElement = element.querySelector(targetElementSelector);
            if (!targetElement) {
                console.warn(`Target element not found for selector: ${targetElementSelector}`);
                return;
            }
        }

        let badge = targetElement.querySelector('.notification-badge');
        if (show && !badge) {
            badge = document.createElement('span');
            badge.classList.add('notification-badge');
            targetElement.appendChild(badge);
        } else if (!show && badge) {
            targetElement.removeChild(badge);
        }
    }

    runButton.addEventListener('click', () => {
        console.log("Run button clicked!");
        runInference(prompt, promptInput.value);
    });

    const runInference = async (initialPrompt, user_input) => {
            runButton.textContent = '思考中...';
        runButton.disabled = true;
        finalOutput.innerHTML = ''; // Clear previous final output
            const finalPrompt = JSON.parse(JSON.stringify(initialPrompt));
        finalPrompt[0].content[1].text = user_input;
        const selectedModel = 'dashscope';

        try {
            const response = await fetch('/run', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ prompt: finalPrompt, model: selectedModel }),
            });

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let finalText = '';

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;
                
                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = JSON.parse(line.substring(5));
                        if (data.output && data.output.choices && data.output.choices.length > 0) {
                            const choice = data.output.choices[0];
                            
                            if (choice.message.content && choice.message.content.length > 0) {
                                finalText += choice.message.content[0].text;
                                finalOutput.innerHTML = converter.makeHtml(finalText);
                                // Show notification badge on output tab
                                
                            }
                        }
                    }
                }
            }
        } catch (error) {
            console.error('Error during inference:', error);
            alert('Error during inference. Check console for details.');
        } finally {
            runButton.textContent = '运行';
            runButton.disabled = false; // Ensure button is re-enabled after process finishes or errors
        }
    };

    resetButton.addEventListener('click', async () => {
        // Clear UI elements
        promptInput.value = PREFILLED_PROMPT_TEXT;
        finalOutput.textContent = '';

        // Reset run button
        runButton.textContent = '运行';
        runButton.disabled = false;
    });


    const inputLink = document.getElementById('input-link');
    const outputLink = document.getElementById('output-link');
    const inputPage = document.getElementById('input-page');
    const outputPage = document.getElementById('output-page');
    

    function showPage(pageToShow) {
        // Hide all pages
        inputPage.classList.remove('active');
        outputPage.classList.remove('active');

        // Remove active class from all links
        inputLink.classList.remove('active');
        outputLink.classList.remove('active');

        // Show the selected page and set active link
        if (pageToShow === 'input') {
            inputPage.classList.add('active');
            inputLink.classList.add('active');
        } else if (pageToShow === 'output') {
            outputPage.classList.add('active');
            outputLink.classList.add('active');
        }
    }

    // Initial page load
    showPage('input');
    promptInput.value = PREFILLED_PROMPT_TEXT;

    inputLink.addEventListener('click', (e) => {
        e.preventDefault();
        showPage('input');
    });

    outputLink.addEventListener('click', (e) => {
        e.preventDefault();
        showPage('output');
        toggleNotificationBadge(outputLink, false, 'i'); // Reset badge on click
    });

    
});
