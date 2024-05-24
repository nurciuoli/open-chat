#Agent util jsons
delegate_instructions_json = {
    "name": "delegate_instructions",
    "description": "Assign an engineer to each specific file needed for the project and include detailed instructions",
    "parameters": {
        "type": "object",
        "properties": {
            "objective": {"type": "string",
                          "description":"a short description of the project"},
            "files": {
                "type": "array",
                "description": "Each individual, separate file in the project",
                "items": {
                    "type": "object",
                    "properties": {
                        "instructions": {"type": "string",
                                         "description":"a detailed prompt describing exactly what is needed"},
                        "file_name":{"type": "string",
                                         "description":"name and folder path of file"},
                        "file_type": {
                            "type": "string",
                            "description": "file type ending to use (.py,.csv,.txt,ect)",
                        },
                        "choices": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["instructions","file_name","file_type"],
                },
            },
        },
        "required": ["objective", "files"],
    },
}


get_review_json = {
    "name": "get_review",
    "description": "Use to get a peer review on your final work",
    "parameters": {
        "type": "object",
        "properties": {
            "files": {
                "type": "array",
                "description": "Files to have reviewed and detailed background on the question you are asking",
                "items": {
                    "type": "object",
                    "properties": {
                        "file_name_with_ext": {"type": "string",
                                      "description":"a name and filepath for the file. EXAMPLE: main.py, poem1.txt, templates/index.html"},
                        "content": {"type": "string",
                                    "description":"a summary of what you want reviewed in the file"},
                                    "choices": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["file_name_with_extension","content"],
                },
            },
        },
        "required": ["files"],
    },
}


get_second_opinion_json = {
    "name": "get_second_opinion",
    "description": "Use this to ask a peer a question or get their opinion",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "question to get advice or help get answered",
            },
        },
        "required": ["question"],
    },
}

