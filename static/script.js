document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('upload-form');
    const videoFile = document.getElementById('video-file');
    const dropZone = document.getElementById('drop-zone');
    const frameImage = document.getElementById('frame-image');
    const prevFrameButton = document.getElementById('prev-frame');
    const nextFrameButton = document.getElementById('next-frame');
    const frameCounter = document.getElementById('frame-counter');
    const runButton = document.getElementById('run-button');
    const promptInput = document.getElementById('prompt-input');
    const thinkingOutput = document.getElementById('thinking-output');
    const finalOutput = document.getElementById('final-output');
    const resetButton = document.getElementById('reset-button');
    const debugModeCheckbox = document.getElementById('debug-mode-checkbox');
    const debugOptions = document.getElementById('debug-options');

    const converter = new showdown.Converter();

    let frames = [];
    let currentFrame = 0;
    let prompt = null;

    // Debug mode toggle
    debugModeCheckbox.addEventListener('change', () => {
        if (debugModeCheckbox.checked) {
            debugOptions.style.display = 'block';
        } else {
            debugOptions.style.display = 'none';
        }
    });

    // Handle drag and drop
    dropZone.addEventListener('click', () => videoFile.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('highlight');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('highlight');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('highlight');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            videoFile.files = files;
            uploadForm.dispatchEvent(new Event('submit'));
        }
    });

    videoFile.addEventListener('change', () => {
        if (videoFile.files.length > 0) {
            uploadForm.dispatchEvent(new Event('submit'));
        }
    });

    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const formData = new FormData(uploadForm);
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            frames = data.frames_path;
            prompt = data.prompt;
            currentFrame = 0;
            updateFrame();

            // Update dropZone content
                        // Update dropZone content
            dropZone.querySelector('.upload-content').style.display = 'none';
            dropZone.querySelector('.done-content').style.display = 'block';

        } else {
            alert('Error uploading video.');
        }
    });

    function updateFrame() {
        if (frames.length > 0) {
            const timestamp = new Date().getTime();
            frameImage.src = `/frames/${frames[currentFrame]}?t=${timestamp}`;
            frameCounter.textContent = `${currentFrame + 1} / ${frames.length}`;
        }
    }

    prevFrameButton.addEventListener('click', () => {
        if (currentFrame > 0) {
            currentFrame--;
            updateFrame();
        }
    });

    nextFrameButton.addEventListener('click', () => {
        if (currentFrame < frames.length - 1) {
            currentFrame++;
            updateFrame();
        }
    });

    runButton.addEventListener('click', async () => {
        if (!prompt) {
            alert('Please upload a video first.');
            return;
        }

        // Change button text and disable it
        runButton.textContent = '请稍候……';
        runButton.disabled = true;

        prompt[0].content[1].text = promptInput.value;
        thinkingOutput.innerHTML = '';
        finalOutput.innerHTML = '';

        const response = await fetch('/run', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ prompt })
        });

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let thinkingText = '';
        let finalText = '';
        let reasoningStarted = false;

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
                        if (choice.message.reasoning_content) {
                            thinkingText += choice.message.reasoning_content;
                            thinkingOutput.innerHTML = converter.makeHtml(thinkingText);
                            if (!reasoningStarted) {
                                runButton.textContent = '完成！';
                                reasoningStarted = true;
                            }
                        }
                        if (choice.message.content && choice.message.content.length > 0) {
                            finalText += choice.message.content[0].text;
                            finalOutput.innerHTML = converter.makeHtml(finalText);
                        }
                    }
                }
            }
        }
    });

    resetButton.addEventListener('click', async () => {
        // Clear UI elements
        videoFile.value = '';
        frameImage.src = '';
        frameCounter.textContent = '';
        promptInput.value = '';
        thinkingOutput.textContent = '';
        finalOutput.textContent = '';
        frames = [];
        currentFrame = 0;
        prompt = null;

        // Reset run button
        runButton.textContent = '运行';
        runButton.disabled = false;

        // Reset dropZone content
        dropZone.querySelector('.upload-content').style.display = 'block';
        dropZone.querySelector('.done-content').style.display = 'none';

        // Send request to clear cache
        try {
            const response = await fetch('/clear_cache', {
                method: 'POST'
            });
            if (response.ok) {
                console.log('Cache cleared successfully.');
            } else {
                console.error('Failed to clear cache.');
            }
        } catch (error) {
            console.error('Error clearing cache:', error);
        }
    });

    
});

function equalizeCardHeights(className) {
    let cards = document.getElementsByClassName(className);
    let maxHeight = 0;

    // Reset heights first
    for (let i = 0; i < cards.length; i++) {
        cards[i].style.height = 'auto';
    }

    // Find the max height
    for (let i = 0; i < cards.length; i++) {
        if (cards[i].offsetHeight > maxHeight) {
            maxHeight = cards[i].offsetHeight;
        }
    }

    // Set all cards to the max height
    for (let i = 0; i < cards.length; i++) {
        cards[i].style.height = maxHeight + 'px';
    }
}

window.addEventListener('load', function() {
    equalizeCardHeights('card-row-1');
    equalizeCardHeights('card-row-2');
});

window.addEventListener('resize', function() {
    equalizeCardHeights('card-row-1');
    equalizeCardHeights('card-row-2');
});