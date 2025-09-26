import random
import json
from typing import Dict, List

class ScenarioGenerator:
    def __init__(self):
        self.scenarios_db = {
            "Bargain Hunter": {
                "Easy": [
                    {
                        "description": "A customer is looking at a discounted shirt but wants an additional discount",
                        "customer_dialogue": "This shirt is already 30% off, but I saw it cheaper online. Can you match that price?",
                        "challenge": "Price objection handling",
                        "learning_outcome": "Learn to handle price objections while maintaining value proposition"
                    },
                    {
                        "description": "Customer comparing multiple similar products by price only",
                        "customer_dialogue": "These two shirts look the same to me. Why is this one ₹200 more expensive?",
                        "challenge": "Value differentiation",
                        "learning_outcome": "Communicate product value beyond just price"
                    }
                ],
                "Medium": [
                    {
                        "description": "Customer wants to negotiate bulk discount for family shopping",
                        "customer_dialogue": "I'm buying for my whole family today. What kind of bulk discount can you offer?",
                        "challenge": "Negotiation and bundle selling",
                        "learning_outcome": "Handle bulk purchase negotiations professionally"
                    }
                ],
                "Hard": [
                    {
                        "description": "Aggressive price negotiator threatening to leave",
                        "customer_dialogue": "Your competitor is offering 50% off everything. I'll leave right now unless you can beat that.",
                        "challenge": "Aggressive negotiation tactics",
                        "learning_outcome": "Handle high-pressure situations while protecting margins"
                    }
                ]
            },
            "Overwhelmed Parent": {
                "Easy": [
                    {
                        "description": "Parent with crying child needs quick clothing solution",
                        "customer_dialogue": "I need school uniforms for my son quickly. He's getting restless. What do you have in size 8?",
                        "challenge": "Time-pressured service",
                        "learning_outcome": "Provide efficient service under time pressure"
                    }
                ],
                "Medium": [
                    {
                        "description": "Parent shopping for multiple children with different needs",
                        "customer_dialogue": "I need clothes for three kids - school wear for one, party dress for another, and casual wear for the third. Where do I start?",
                        "challenge": "Complex multi-need situations",
                        "learning_outcome": "Organize and prioritize multiple customer needs"
                    }
                ],
                "Hard": [
                    {
                        "description": "Frustrated parent with budget constraints and picky children",
                        "customer_dialogue": "My daughter hates everything I pick, my budget is tight, and we need clothes today. This is impossible!",
                        "challenge": "Managing stress and constraints",
                        "learning_outcome": "Handle emotionally charged situations with empathy"
                    }
                ]
            },
            "Trend-Seeking Influencer": {
                "Easy": [
                    {
                        "description": "Young customer looking for Instagram-worthy outfit",
                        "customer_dialogue": "I need something that will look amazing in photos. What's your most Instagram-worthy piece?",
                        "challenge": "Style consultation",
                        "learning_outcome": "Provide fashion advice and styling suggestions"
                    }
                ],
                "Medium": [
                    {
                        "description": "Influencer wanting exclusive or limited edition items",
                        "customer_dialogue": "Do you have anything exclusive that my followers haven't seen everywhere else?",
                        "challenge": "Exclusivity and differentiation",
                        "learning_outcome": "Position products as unique and desirable"
                    }
                ],
                "Hard": [
                    {
                        "description": "High-maintenance influencer with specific brand requirements",
                        "customer_dialogue": "I only wear sustainable, ethically-made clothes that photograph well under studio lights. What can you show me?",
                        "challenge": "Specific and demanding requirements",
                        "learning_outcome": "Handle complex product specifications and customer demands"
                    }
                ]
            }
        }
    
    def get_scenario(self, persona: str, difficulty: str) -> Dict:
        """Get random scenario for given persona and difficulty"""
        if persona in self.scenarios_db and difficulty in self.scenarios_db[persona]:
            scenarios = self.scenarios_db[persona][difficulty]
            scenario = random.choice(scenarios)
            scenario['persona'] = persona
            scenario['difficulty'] = difficulty
            return scenario
        else:
            return {
                "description": "Generic customer interaction",
                "customer_dialogue": "Hello, I'm looking for some clothes.",
                "challenge": "General customer service",
                "learning_outcome": "Practice basic customer interaction",
                "persona": persona,
                "difficulty": difficulty
            }
    
    def add_custom_scenario(self, persona: str, difficulty: str, scenario: Dict):
        """Add custom scenario to database"""
        if persona not in self.scenarios_db:
            self.scenarios_db[persona] = {}
        if difficulty not in self.scenarios_db[persona]:
            self.scenarios_db[persona][difficulty] = []
        
        self.scenarios_db[persona][difficulty].append(scenario)