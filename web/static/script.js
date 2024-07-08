document.addEventListener('DOMContentLoaded', () => {
    const generateBtn = document.getElementById('generate-btn');
    const promptInput = document.getElementById('prompt-input');
    const generatedContent = document.getElementById('content-section');
    const evaluationResults = document.getElementById('evaluation-section');
    const userEvaluationForm = document.getElementById('user-evaluation-form');
    const submitFeedbackBtn = document.getElementById('submit-feedback-btn');
    const aiFeedback = document.getElementById('feedback-section');

    let currentEvaluation = null;
    let currentFeedback = null;

    function formatAIResponse(response) {
        if (typeof response === 'string') {
            return response.replace(/###\s*(.*)/g, '<h3>$1</h3>')
                           .replace(/\n/g, '<br>');
        } else if (typeof response === 'object') {
            let formattedResponse = '';
            for (const [key, value] of Object.entries(response)) {
                formattedResponse += `<h3>${key}</h3>`;
                if (typeof value === 'string') {
                    formattedResponse += value.replace(/###\s*(.*)/g, '<h4>$1</h4>')
                                             .replace(/\n/g, '<br>');
                } else if (typeof value === 'object' && value !== null) {
                    formattedResponse += formatAIResponse(value);
                } else {
                    formattedResponse += JSON.stringify(value, null, 2)
                                             .replace(/\n/g, '<br>')
                                             .replace(/ /g, '&nbsp;');
                }
            }
            return formattedResponse;
        }
        return JSON.stringify(response, null, 2);
    }

    function formatContent(content) {
        const acknowledgmentRegex = /Acknowledgment of previous feedback:([\s\S]*?)(?=\n\n|$)/;
        const match = content.match(acknowledgmentRegex);
        
        let formattedContent = '';
        if (match) {
            formattedContent += `<div class="acknowledgment"><h3>Acknowledgment of previous feedback:</h3>${match[1].trim()}</div>`;
            content = content.replace(match[0], '');
        }
        
        formattedContent += content.replace(/###\s*(.*)/g, '<h3>$1</h3>')
                                   .replace(/\n/g, '<br>');
        return formattedContent;
    }

    function handleAction(action) {
        switch (action) {
            case 'continue':
                if (currentFeedback.improvements_needed.trim().toUpperCase().startsWith('YES')) {
                    generateBtn.click();
                } else {
                    alert('No further improvements needed. You can start a new interaction.');
                    resetUI();
                }
                break;
            case 'disagree':
                const additionalFeedback = prompt('Please provide additional feedback for improvement:');
                if (additionalFeedback) {
                    fetch('/incorporate_feedback', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            feedback: currentFeedback,
                            additional_feedback: additionalFeedback
                        })
                    })
                    .then(response => response.json())
                    .then(data => {
                        currentFeedback = data.feedback;
                        aiFeedback.innerHTML = `<h2>Updated AI Feedback</h2><div class="ai-response">${formatAIResponse(data.feedback)}</div>`;
                        showActionButtons();
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        alert('An error occurred while incorporating additional feedback.');
                    });
                }
                break;
            case 'quit':
                resetUI();
                break;
        }
    }

    function showActionButtons() {
        const actionButtons = document.createElement('div');
        actionButtons.id = 'action-buttons';
        actionButtons.innerHTML = `
            <button onclick="handleAction('continue')">Continue</button>
            <button onclick="handleAction('disagree')">Disagree</button>
            <button onclick="handleAction('quit')">Quit</button>
        `;
        aiFeedback.appendChild(actionButtons);
    }

    function resetUI() {
        promptInput.value = '';
        generatedContent.innerHTML = '<h2>Generated Content</h2>';
        evaluationResults.innerHTML = '<h2>AI Evaluation</h2>';
        userEvaluationForm.innerHTML = '';
        aiFeedback.innerHTML = '<h2>AI Feedback</h2>';
        submitFeedbackBtn.style.display = 'none';
    }

    generateBtn.addEventListener('click', () => {
        const prompt = promptInput.value;
        fetch('/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt: prompt })
        })
        .then(response => response.json())
        .then(data => {
            generatedContent.innerHTML = `<h2>Generated Content</h2><div class="generated-content">${formatContent(data.content)}</div>`;
            evaluationResults.innerHTML = `<h2>AI Evaluation</h2><div class="ai-response">${formatAIResponse(data.evaluation)}</div>`;
            createUserEvaluationForm(data.criteria);
            currentEvaluation = data.evaluation;
            submitFeedbackBtn.style.display = 'block';
        })
        .catch(error => {
            console.error('Error:', error);
            generatedContent.innerHTML = '<h2>Generated Content</h2><pre>An error occurred while generating content.</pre>';
        });
    });

    function createUserEvaluationForm(criteria) {
        userEvaluationForm.innerHTML = '';
        criteria.forEach(criterion => {
            const div = document.createElement('div');
            div.innerHTML = `
                <h3>${criterion}</h3>
                <input type="number" min="0" max="10" step="0.1" id="rating-${criterion}" placeholder="Rate (0-10)">
                <textarea id="feedback-${criterion}" placeholder="Provide feedback for ${criterion}"></textarea>
            `;
            userEvaluationForm.appendChild(div);
        });
        const evaluatorFeedbackDiv = document.createElement('div');
        evaluatorFeedbackDiv.innerHTML = `
            <h3>Feedback for Evaluator</h3>
            <textarea id="evaluator-feedback" placeholder="Provide feedback for the evaluator"></textarea>
        `;
        userEvaluationForm.appendChild(evaluatorFeedbackDiv);
        submitFeedbackBtn.style.display = 'block';
    }

    submitFeedbackBtn.addEventListener('click', () => {
        const userEvaluation = { scores: {}, feedbacks: {} };
        const criteria = Array.from(userEvaluationForm.querySelectorAll('h3')).map(h3 => h3.textContent);

        criteria.forEach(criterion => {
            if (criterion !== 'Feedback for Evaluator') {
                const scoreInput = document.getElementById(`rating-${criterion}`);
                const feedbackInput = document.getElementById(`feedback-${criterion}`);
                
                const score = scoreInput.value ? parseFloat(scoreInput.value) : 5;
                const feedback = feedbackInput.value || '';
                
                userEvaluation.scores[criterion] = score;
                userEvaluation.feedbacks[criterion] = feedback;
            }
        });

        const evaluatorFeedback = document.getElementById('evaluator-feedback').value || '';

        fetch('/submit_feedback', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                recent_iterations: [],
                prompt: promptInput.value,
                content: generatedContent.querySelector('.generated-content').innerHTML,
                evaluation: currentEvaluation,
                user_eval_content: userEvaluation,
                user_feedback_evaluator: evaluatorFeedback
            })
        })
        .then(response => response.json())
        .then(data => {
            currentFeedback = data.feedback;
            aiFeedback.innerHTML = `<h2>AI Feedback</h2><div class="ai-response">${formatAIResponse(data.feedback)}</div>`;
            showActionButtons();
        })
        .catch(error => {
            console.error('Error:', error);
            aiFeedback.innerHTML = '<h2>AI Feedback</h2><pre>An error occurred while submitting feedback.</pre>';
        });
    });

    window.handleAction = handleAction;
});