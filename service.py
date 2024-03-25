'''
This module contains service methods
'''

def get_id_from_message(text: str) -> int:
    text_list = text.split("\n")
    for item in text_list:
        if "id" in item:
            task_id = int(item.split('-')[1])
            return task_id