# LLM Interface for Strategy Generation and Explanation

class LLMAgent:
    def __init__(self, model_name="gemini-1.5-pro"):
        self.model_name = model_name
        
    def explain_factor(self, factor_code):
        """
        Explains what a specific alpha factor does in plain English.
        """
        pass
        
    def generate_strategy(self, description):
        """
        Generates Python code for a strategy based on a text description.
        """
        pass
