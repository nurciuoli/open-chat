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
                                         "description":"name to give file (ex. main, testing,ect)"},
                        "file_type": {
                            "type": "string",
                            "description": "file type ending to use (py,csv,txt,ect)",
                        },
                        "job_type":{"type":"string","description":"whether the worker should create a new file or edit an existing (either NEW or EDIT)"},
                        "choices": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["instructions","file_name","file_type","job_type"],
                },
            },
        },
        "required": ["objective", "files"],
    },
}


get_file_contents_json = {
    "name": "get_file_contents",
    "description": "use this to get back the contents of a project file",
    "parameters": {
        "type": "object",
        "properties": {
            "filename": {
                "type": "string",
                "description": "name of the file to return",
            },
        },
        "required": ["filename"],
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

