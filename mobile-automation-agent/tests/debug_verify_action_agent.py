
def test_prompt_formatting():
    task_goal = "test goal"
    screen_summary = {"type": "home"}
    previous_actions = []
    
    try:
        # Replicating the f-string from agents/action_agent.py
        prompt = f"""
        Current Goal: {task_goal}
        
        Screen State:
        {screen_summary}
        
        Previous Actions:
        {previous_actions}
        
        Determine the next single action.
        
        RESPONSE FORMAT:
        {{
            "action": {{
                "type": "tap" | "input" | "scroll" | "wait" | "finish",
                "target": "element_description_or_id",
                "value": "text_to_type_if_input"
            }}
        }}
        """
        print("✅ F-string formatting successful!")
        print(prompt)
    except ValueError as e:
        print(f"❌ F-string formatting failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_prompt_formatting()
