def generate_prompt(result):

    bpm = result["bpm"]
    key = result["key"]

    prompt = f"""
emotional pop song
BPM {bpm}
key {key}

female vocal
modern production
clean mix
dramatic chorus
"""

    return prompt