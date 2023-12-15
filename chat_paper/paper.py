class Paper:
    def __init__(self, json_filename) -> None:
            self.json_complete = False
            self.json_filename = json_filename
            
    def set_json_complete(self):
        self.json_complete = True
    
    def get_json_complete(self):
        return self.json_complete