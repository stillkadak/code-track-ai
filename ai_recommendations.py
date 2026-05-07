"""
AI Recommendations Module using Google Gemini API
"""

import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Check if API key exists
if GEMINI_API_KEY and GEMINI_API_KEY.startswith('AIza'):
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        # Updated to use the latest model
        model = genai.GenerativeModel('gemini-1.5-pro')
        AI_AVAILABLE = True
        print("✅ Gemini AI is configured and ready!")
    except Exception as e:
        print(f"⚠️ Error configuring AI: {e}")
        AI_AVAILABLE = False
        model = None
else:
    AI_AVAILABLE = False
    model = None
    print("⚠️ GEMINI_API_KEY not found or invalid. AI features disabled.")

def get_ai_coaching(weak_topics, total_solved, streak_days):
    """Get AI coaching recommendations based on user performance"""
    
    if not AI_AVAILABLE:
        return get_fallback_coaching(weak_topics, total_solved, streak_days)
    
    try:
        topics_str = ', '.join(weak_topics[:3]) if weak_topics else "Not enough data yet"
        
        prompt = f"""
        As an AI coding coach for a CSE student:
        
        Stats:
        - Problems solved: {total_solved}
        - Current streak: {streak_days} days
        - Topics practiced: {topics_str}
        
        Provide a concise, motivational coaching message (max 100 words) covering:
        1. Encouragement based on their progress
        2. 2-3 specific topics to focus on
        3. A practical tip for improving
        
        Keep it energetic and actionable.
        """
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        print(f"AI Error: {e}")
        return get_fallback_coaching(weak_topics, total_solved, streak_days)

def get_fallback_coaching(weak_topics, total_solved, streak_days):
    """Fallback coaching when AI is unavailable"""
    if total_solved == 0:
        return """
        🚀 **Welcome to CodeTrack AI!**
        
        Start by adding your first problem using the 'Add Problem' tab.
        The more you track, the better insights I can provide!
        
        **Quick tip:** Start with easy problems to build confidence, 
        then gradually increase difficulty. Consistency is key!
        """
    else:
        return f"""
        💪 **Great progress!** You've solved {total_solved} problems with a {streak_days} day streak!
        
        **Focus areas:** {', '.join(weak_topics[:3]) if weak_topics else 'Keep practicing all topics'}
        
        **Today's goal:** Solve 2 problems - one easy and one medium difficulty.
        
        Remember: Every expert was once a beginner. Keep coding! 🎯
        """

def analyze_weak_topics(topic_counts):
    """Analyze which topics need improvement"""
    
    if not AI_AVAILABLE:
        return get_fallback_analysis(topic_counts)
    
    try:
        if not topic_counts:
            return "Start solving problems to get personalized weak topic analysis!"
        
        topics_str = ", ".join([f"{topic}: {count}" for topic, count in topic_counts.items()])
        
        prompt = f"""
        Based on solved problems distribution:
        {topics_str}
        
        Provide a brief analysis (max 150 words) identifying:
        1. The weakest area (least practiced topic)
        2. Why mastering this topic matters for interviews
        3. A simple 3-day improvement plan
        
        Be specific and actionable.
        """
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return get_fallback_analysis(topic_counts)

def get_fallback_analysis(topic_counts):
    """Fallback analysis when AI is unavailable"""
    if not topic_counts:
        return """
        📊 **No topic data yet!**
        
        Add problems across different topics to get detailed analysis.
        Try solving problems in: Arrays, Strings, Hash Tables to start.
        """
    
    # Find weakest topic
    sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1])
    weakest = sorted_topics[0][0] if sorted_topics else "various topics"
    
    return f"""
    📈 **Your Topic Analysis**
    
    Based on your solved problems:
    - Most practiced: {sorted_topics[-1][0] if sorted_topics else 'None'}
    - Needs improvement: {weakest}
    
    **Recommendations:**
    1. Focus on {weakest} - solve 2-3 problems this week
    2. Mix difficulties (Easy + Medium)
    3. Review concepts before solving
    
    Keep tracking to see improvement trends!
    """

def get_daily_challenge(topic_counts, total_solved):
    """Generate a daily coding challenge"""
    
    if not AI_AVAILABLE:
        return get_fallback_challenge(total_solved)
    
    try:
        # Determine difficulty based on experience
        if total_solved < 20:
            difficulty = "Easy"
            topic = "Arrays or Strings"
        elif total_solved < 50:
            difficulty = "Medium"
            if topic_counts:
                weakest = min(topic_counts, key=topic_counts.get)
                topic = weakest
            else:
                topic = "Hash Tables"
        else:
            difficulty = "Medium/Hard"
            topic = "Advanced topics like DP or Graphs" if not topic_counts else min(topic_counts, key=topic_counts.get)
        
        prompt = f"""
        Create a coding challenge for a student who has solved {total_solved} problems.
        
        Challenge specs:
        - Difficulty: {difficulty}
        - Focus topic: {topic}
        
        Provide in this format:
        **Problem:** [Title]
        **Description:** [2-3 lines]
        **Key Concepts:** [2-3 concepts]
        **Expected Time:** [X minutes]
        **Hint 1:** [First hint]
        **Hint 2:** [Second hint]
        
        Make it practical and interview-relevant.
        """
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return get_fallback_challenge(total_solved)

def get_fallback_challenge(total_solved):
    """Fallback challenge generator"""
    if total_solved < 20:
        return """
        🎯 **Today's Challenge: Two Sum**
        
        **Description:** Find two numbers in an array that add up to a target value.
        
        **Key Concepts:** Arrays, Hash Maps, Hash Tables
        **Expected Time:** 20-30 minutes
        
        **Hint 1:** Use a hash map to store numbers you've seen
        **Hint 2:** For each number, check if (target - num) exists in your map
        
        **Try solving it on LeetCode!**
        """
    elif total_solved < 50:
        return """
        🎯 **Today's Challenge: Valid Parentheses**
        
        **Description:** Check if a string containing brackets is valid.
        
        **Key Concepts:** Stack, String parsing
        **Expected Time:** 25-35 minutes
        
        **Hint 1:** Use a stack to track opening brackets
        **Hint 2:** When you see a closing bracket, check if it matches the top of stack
        
        **Common interview question!**
        """
    else:
        return """
        🎯 **Today's Challenge: Merge Intervals**
        
        **Description:** Merge overlapping intervals in a collection.
        
        **Key Concepts:** Sorting, Arrays, Intervals
        **Expected Time:** 30-40 minutes
        
        **Hint 1:** Sort intervals by start time first
        **Hint 2:** Compare current interval with last merged interval
        
        **Medium difficulty - Great for interview prep!**
        """