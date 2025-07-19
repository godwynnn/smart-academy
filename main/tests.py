# from django.test import TestCase
# from transformers import pipeline
import json
data = """
        [
            {
                "question": "Which of the following is NOT a characteristic of living things?",
                "options": ["Movement", "Respiration", "Growth", "Crystallization"],
                "answer": "Crystallization"
            },
            {
                "question": "The process by which green plants manufacture their food is called:",
                "options": ["Respiration", "Photosynthesis", "Transpiration", "Excretion"],
                "answer": "Photosynthesis"
            },
            {
                "question": "What is the basic unit of life?",
                "options": ["Tissue", "Organ", "Cell", "Organism"],
                "answer": "Cell"
            },
            {
                "question": "Which of these is an example of a vertebrate?",
                "options": ["Spider", "Grasshopper", "Snake", "Earthworm"],
                "answer": "Snake"
            },
            {
                "question": "The transfer of pollen grains from the anther to the stigma is called:",
                "options": ["Fertilization", "Pollination", "Germination", "Dispersal"],
                "answer": "Pollination"
            }
        ]

    """


def normalize_quiz_data(raw_data):
    """
    Applies ETL to ensure the data is always wrapped with a 'quiz' key.
    """

    # --------- Extract ---------
    if isinstance(raw_data, str):
        try:
            data = json.loads(raw_data)
        except json.JSONDecodeError as e:
            raise ValueError("Invalid JSON input") from e
    else:
        data = raw_data

    # --------- Transform ---------
    if isinstance(data, list):
        # Wrap the list in a 'quiz' key
        normalized_data = {"quiz": data}
    elif isinstance(data, dict) and "quiz" in data:
        normalized_data = data
    else:
        raise ValueError(
            "Data format not recognized: must be a list or dict with 'quiz' key.")

    # --------- Load (e.g. return, store, or export) ---------
    return normalized_data


print(normalize_quiz_data(data))