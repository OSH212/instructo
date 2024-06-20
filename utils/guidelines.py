EVALUATION_CRITERIA = {
    "Factual accuracy": {
        "description": "Assess the correctness of presented information.",
        "rubric": [
            "1: Contains multiple factual errors",
            "3: Mostly accurate with minor errors",
            "5: Completely accurate and well-supported"
        ],
        "prompt": "Verify key claims against reliable sources. Highlight any inaccuracies found."
    },
    "Clarity of expression": {
        "description": "Evaluate how well ideas are communicated.",
        "rubric": [
            "1: Confusing and difficult to follow",
            "3: Generally clear with some complex passages",
            "5: Crystal clear and easily understood"
        ],
        "prompt": "Identify any unclear passages. Suggest rephrasing for improved clarity."
    },
    "Relevance to the prompt": {
        "description": "Determine how well the content addresses the given prompt.",
        "rubric": [
            "1: Mostly off-topic or tangential",
            "3: Addresses main points with some digressions",
            "5: Directly and comprehensively addresses the prompt"
        ],
        "prompt": "Compare content to the original prompt. Note any irrelevant sections."
    },
    "Depth of analysis": {
        "description": "Assess the level of critical thinking and insight.",
        "rubric": [
            "1: Surface-level treatment of the topic",
            "3: Some in-depth analysis with room for improvement",
            "5: Thorough, nuanced exploration of the subject"
        ],
        "prompt": "Identify areas where the analysis could be deepened. Suggest additional perspectives or angles."
    },
    "Coherence and structure": {
        "description": "Evaluate the logical flow and organization of ideas.",
        "rubric": [
            "1: Disjointed and poorly organized",
            "3: Generally logical flow with minor inconsistencies",
            "5: Well-structured with clear progression of ideas"
        ],
        "prompt": "Outline the main structure. Propose improvements for smoother transitions between ideas."
    },
    "Use of supporting evidence": {
        "description": "Assess the quality and relevance of evidence used.",
        "rubric": [
            "1: Lack of supporting evidence",
            "3: Some relevant evidence, but could be stronger",
            "5: Strong, varied, and well-integrated evidence"
        ],
        "prompt": "List the main pieces of evidence used. Suggest additional or more robust evidence where needed."
    },
    "Objectivity and lack of bias": {
        "description": "Evaluate the balance and fairness of the content.",
        "rubric": [
            "1: Heavily biased or one-sided",
            "3: Generally balanced with some subjective elements",
            "5: Objective and presents multiple perspectives fairly"
        ],
        "prompt": "Identify any biased language or one-sided arguments. Propose ways to present a more balanced view."
    }
}



def get_evaluation_prompt(content):
    """
    Generates a detailed evaluation prompt based on predefined criteria for assessing content.

    Args:
    content (str): The content to be evaluated.

    Returns:
    str: A formatted string containing the evaluation prompt.
    """
    prompt = "Evaluate the following content based on these criteria:\n\n"
    for criterion, details in EVALUATION_CRITERIA.items():
        prompt += f"{criterion}:\n"
        prompt += f"Description: {details['description']}\n"
        prompt += "Rubric:\n" + "\n".join(details['rubric']) + "\n"
        prompt += f"Evaluation task: {details['prompt']}\n\n"
    
    prompt += f"Content to evaluate:\n\n{content}\n\n"
    prompt += "For each criterion, provide:\n"
    prompt += "1. A score (1-5) based on the rubric\n"
    prompt += "2. A brief explanation for the score\n"
    prompt += "3. Specific suggestions for improvement\n"
    prompt += "\nFinally, provide an overall assessment and key recommendations for improvement."
    
    return prompt