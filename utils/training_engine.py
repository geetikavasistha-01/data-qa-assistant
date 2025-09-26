import openai
import json
import random
from supabase import Client
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

class TrainingEngine:
    def __init__(self, supabase: Client):
        self.supabase = supabase
        self.personas = self._load_personas()
    
    def _load_personas(self) -> list:
        """Load personas from database"""
        try:
            result = self.supabase.table('personas').select('*').execute()
            return result.data
        except Exception as e:
            print(f"Error loading personas: {e}")
            return []
    
    def get_personas(self) -> list:
        """Return available personas"""
        return self.personas
    
    def generate_scenario(self, persona_name: str, difficulty: str) -> dict:
        """Generate training scenario using OpenAI"""
        persona = next((p for p in self.personas if p['name'] == persona_name), None)
        
        if not persona:
            return {"error": "Persona not found"}
        
        prompt = f"""
        Generate a realistic sales training scenario for Max Fashion store.
        
        Customer Persona: {persona['name']}
        Profile: {persona['profile']}
        Difficulty: {difficulty}
        
        Create a scenario with:
        1. Context/situation description
        2. Customer's initial dialogue
        3. Customer's specific challenge/objection
        4. Expected learning outcome
        
        Make it specific to fashion retail and appropriate for {difficulty.lower()} difficulty level.
        
        Return as JSON with keys: description, customer_dialogue, challenge, learning_outcome
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )
            
            scenario_data = json.loads(response.choices[0].message.content)
            scenario_data.update({
                'persona': persona_name,
                'difficulty': difficulty,
                'id': random.randint(1000, 9999)
            })
            
            return scenario_data
            
        except Exception as e:
            return {
                'description': f"Error generating scenario: {e}",
                'customer_dialogue': "Technical error occurred",
                'challenge': "System error",
                'learning_outcome': "Retry scenario generation",
                'persona': persona_name,
                'difficulty': difficulty
            }
    
    def evaluate_response(self, scenario: dict, user_response: str) -> dict:
        """Evaluate user's response using AI"""
        prompt = f"""
        Evaluate this sales manager's response to a customer scenario.
        
        Scenario: {scenario['description']}
        Customer said: {scenario['customer_dialogue']}
        Sales manager responded: {user_response}
        
        Rate the response on a scale of 1-5 for each dimension:
        1. Accuracy (factual correctness, product knowledge)
        2. Application (practical application of sales techniques)
        3. Communication (clarity, empathy, professionalism)
        4. Adaptability (flexibility to customer needs)
        
        Also provide:
        - Overall feedback (2-3 sentences)
        - Specific improvement suggestions (2-3 points)
        
        Return as JSON with keys: accuracy, application, communication, adaptability, feedback, suggestions
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.3
            )
            
            evaluation = json.loads(response.choices[0].message.content)
            
            # Save evaluation to database
            self._save_training_result(scenario, user_response, evaluation)
            
            return evaluation
            
        except Exception as e:
            return {
                'accuracy': 3,
                'application': 3,
                'communication': 3,
                'adaptability': 3,
                'feedback': f"Error in evaluation: {e}",
                'suggestions': ["Please try again", "Technical error occurred"]
            }
    
    def _save_training_result(self, scenario: dict, response: str, evaluation: dict):
        """Save training result to database"""
        try:
            session_data = {
                'scenario': scenario,
                'responses': [response],
                'scores': evaluation,
                'persona': scenario['persona'],
                'difficulty': scenario['difficulty']
            }
            
            # This would be called with user_id in actual implementation
            # insert_training_session(self.supabase, user_id, session_data)
            
        except Exception as e:
            print(f"Error saving training result: {e}")

    def get_adaptive_difficulty(self, user_id: str, current_difficulty: str) -> str:
        """Determine next difficulty level based on performance"""
        # Get recent performance
        history = self.supabase.table('training_sessions').select('scores').eq('user_id', user_id).limit(5).execute()
        
        if not history.data:
            return current_difficulty
        
        # Calculate average score
        total_scores = []
        for session in history.data:
            if session['scores']:
                avg_score = sum(session['scores'].values()) / len(session['scores'])
                total_scores.append(avg_score)
        
        if total_scores:
            avg_performance = sum(total_scores) / len(total_scores)
            
            # Adaptive logic
            if avg_performance >= 4.5 and current_difficulty != "Expert":
                difficulty_levels = ["Easy", "Medium", "Hard", "Expert"]
                current_index = difficulty_levels.index(current_difficulty)
                return difficulty_levels[min(current_index + 1, 3)]
            elif avg_performance < 3.0 and current_difficulty != "Easy":
                difficulty_levels = ["Easy", "Medium", "Hard", "Expert"]
                current_index = difficulty_levels.index(current_difficulty)
                return difficulty_levels[max(current_index - 1, 0)]
        
        return current_difficulty