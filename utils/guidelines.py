EVALUATION_CRITERIA = {
    "Content Quality": {
        "description": "Assess the accuracy, depth, and relevance of the information presented.",
        "rubric": [
            "1-2: Significant errors, shallow treatment, or off-topic",
            "3-4: Some inaccuracies or lacks depth in key areas",
            "5-6: Generally accurate and relevant but could be more comprehensive",
            "7-8: Accurate, relevant, and fairly in-depth treatment",
            "9-10: Exceptionally accurate, comprehensive, and insightful"
        ],
        "prompt": "Evaluate the accuracy, depth, and relevance of the content. Consider complexity of ideas, use of expert knowledge, and alignment with the given prompt/objective. Suggest areas for improvement or expansion."
    },
    "Critical Analysis and Argumentation": {
        "description": "Assess the level of critical thinking, insights, and quality of argumentation.",
        "rubric": [
            "1-2: Superficial analysis with poor argumentation",
            "3-4: Basic analysis with limited original thought or weak arguments",
            "5-6: Some critical analysis and adequate argumentation, but could go deeper",
            "7-8: Good critical analysis with well-constructed arguments",
            "9-10: Exceptional critical thinking with compelling argumentation"
        ],
        "prompt": "Evaluate the depth of analysis, presence of original insights, and strength of arguments. Assess the use of evidence/sources. Identify areas where the analysis could be deepened or argumentation improved."
    },
    "Structure and Clarity": {
        "description": "Evaluate how well ideas are organized and communicated.",
        "rubric": [
            "1-2: Confusing and poorly structured",
            "3-4: Some clear points but overall difficult to follow",
            "5-6: Generally clear but with some organizational issues",
            "7-8: Clear and well-structured with minor issues",
            "9-10: Exceptionally clear, coherent, and well-organized"
        ],
        "prompt": "Assess the clarity of expression and logical flow of ideas. Identify any unclear passages or structural issues. Suggest improvements for clarity and coherence."
    },
    "Language and Style": {
        "description": "Evaluate the quality of writing, including grammar, vocabulary, and stylistic choices.",
        "rubric": [
            "1-2: Poor grammar and inappropriate style",
            "3-4: Frequent language errors or inconsistent style",
            "5-6: Generally correct language with an appropriate style",
            "7-8: Well-written with good command of language and style",
            "9-10: Exceptional writing with masterful use of language and style"
        ],
        "prompt": "Assess the quality of writing, including grammar, vocabulary, and style. Consider the appropriateness for the intended audience and purpose. Suggest improvements in language use and style."
    },
    "Perspective and Objectivity": {
        "description": "Evaluate the appropriateness of the perspective taken and the level of objectivity (when required).",
        "rubric": [
            "1-2: Heavily biased or inappropriate perspective",
            "3-4: Noticeable bias or misaligned perspective",
            "5-6: Generally appropriate perspective with some bias",
            "7-8: Well-balanced perspective, mostly objective when required",
            "9-10: Perfectly aligned perspective, objective when required"
        ],
        "prompt": "Assess whether the perspective taken is appropriate for the given prompt/objective. If objectivity is required, evaluate its presence. If a specific viewpoint is needed, assess how well it's presented. Suggest ways to improve the balance or perspective as needed."
    },
    "Relevance to Initial Objective": {
        "description": "Assess how well the content addresses the initial user-given objective.",
        "rubric": [
            "1-2: Content largely ignores or misses the initial objective",
            "3-4: Content partially addresses the initial objective with significant gaps",
            "5-6: Content addresses the initial objective but lacks depth or comprehensiveness",
            "7-8: Content fully addresses the initial objective with good relevance",
            "9-10: Content exceptionally addresses and expands upon the initial objective"
        ],
        "prompt": "Compare the content to the initial user-given objective. Evaluate how well it addresses and fulfills this objective."
    },
    "Creativity and Originality": {
        "description": "Assess the level of creativity and originality in the content.",
        "rubric": [
            "1-2: Entirely derivative or lacking creativity",
            "3-4: Mostly conventional with little originality",
            "5-6: Some creative elements but largely conventional",
            "7-8: Good level of creativity and originality",
            "9-10: Exceptionally creative and original"
        ],
        "prompt": "Evaluate the creativity and originality of the content. Consider unique approaches, novel ideas, or innovative presentations. Suggest areas where more creative approaches could be applied."
    }
}


def get_evaluation_prompt(content, objective):
    prompt = "Evaluate the following content based on these criteria:\n\n"
    for criterion, details in EVALUATION_CRITERIA.items():
        prompt += f"{criterion}:\n"
        prompt += f"Description: {details['description']}\n"
        prompt += "Rubric:\n" + "\n".join(details['rubric']) + "\n"
        prompt += f"Evaluation task: {details['prompt'].format(objective=objective)}\n\n"
    
    prompt += f"Content to evaluate:\n\n{content}\n\n"
    prompt += "For each criterion, provide:\n"
    prompt += "1. A score (1-10) based on the rubric\n"
    prompt += "2. A brief explanation for the score\n"
    prompt += "3. Specific suggestions for improvement\n"
    prompt += "\nFinally, provide an overall assessment and key recommendations for improvement."
    
    return prompt