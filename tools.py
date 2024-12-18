#Agent util jsons
gpt_agent_tools = {"code_env":{"type":"code_interpreter"},
                   "write_file":
                        {
                          "type": "function",
                          "function": {
                            "name": "write_file",
                            "description": "Use this to write to files of different types, including .txt, .py, and more",
                            "parameters": {
                              "type": "object",
                              "properties": {
                                "file_name": {
                                  "type": "string",
                                  "description": "name for file (no extension)"
                                },
                                "file_type": {
                                  "type": "string",
                                  "enum": [".txt", ".py", ".md", ".html", ".js"]
                                },
                                "content": {
                                  "type": "string",
                                  "description": "content to populate file of respective type"
                                }
                              },
                              "required": ["file_name", "file_type", "content"]
                            }
                          }
                        },
                    "edit_file":{
                      "type": "function",
                      "function": {
                        "name": "edit_file",
                        "description": "Use this to replace the contents of an existing file",
                        "parameters": {
                          "type": "object",
                          "properties": {
                            "file_name": {
                              "type": "string"
                            },
                            "content": {
                              "type": "string",
                              "description": "edited content to overwrite existing file"
                            }
                          },
                          "required": ["file_name", "content"]
                        }
                      }
                    },
                  }


universal_tools={"write_file":{
                          "name": "write_file",
                          "description": "Use this to write to files of different types, including .txt, .py, and more",
                          "input_schema": {
                              "type": "object",
                              "properties": {
                                  "file_name": {"type": "string",
                                                "description":"name for file (no extension)"},
                                  "file_type":{"type":"string",
                                              "enum": [".txt", ".py", ".md",".html",".js"]},
                                  "content": {"type":"string",
                                              "description":"content to populate file of respective type",
                                              },
                                  },
                              "required": ["file_name","file_type","content"],
                          },
                      },
                      "edit_file":{
                          "name": "edit_file",
                          "description": "Use this replace the contents of an existing file",
                          "input_schema": {
                              "type": "object",
                              "properties": {
                                  "file_name": {"type": "string"},#"enum": ["edit","delete"]},         
                                  "content": {"type":"string",
                                              "description":"edited content to overwrite existing file",
                                              },
                                  },
                              "required": ["file_name","content"],
                          },
                      },
                      "replace_from_file":{
                          "name": "replace_from_file",
                          "description": "Use this replace the contents of an existing file",
                          "input_schema": {
                              "type": "object",
                              "properties": {  
                                  "content_to_replace": {"type":"string",
                                              "description":"string pattern of existing content",
                                              },
                                  "replace_with_content": {"type":"string",
                                              "description":"content to replace existing content with",
                                              },
                                  },
                              "required": ["content_to_replace",'replace_with_content'],
                          },
                      },
                      }


claude_agent_tools = {"write_file":{
                          "name": "write_file",
                          "description": "Use this to write to files of different types, including .txt, .py, and more",
                          "input_schema": {
                              "type": "object",
                              "properties": {
                                  "file_name": {"type": "string",
                                                "description":"name for file (no extension)"},
                                  "file_type":{"type":"string",
                                              "enum": [".txt", ".py", ".md",".html",".js"]},
                                  "content": {"type":"string",
                                              "description":"content to populate file of respective type",
                                              },
                                  },
                              "required": ["file_name","file_type","content"],
                          },
                      },
                      "edit_file":{
                          "name": "edit_file",
                          "description": "Use this replace the contents of an existing file",
                          "input_schema": {
                              "type": "object",
                              "properties": {
                                  "file_name": {"type": "string"},#"enum": ["edit","delete"]},         
                                  "content": {"type":"string",
                                              "description":"edited content to overwrite existing file",
                                              },
                                  },
                              "required": ["file_name","content"],
                          },
                      },
                      }


gemini_agent_tools = {"code_env":"code_execution"}
