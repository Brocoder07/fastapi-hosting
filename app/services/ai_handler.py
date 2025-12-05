from groq import Groq
from sentence_transformers import SentenceTransformer
from ..config import settings

class AIHandler:
    def __init__(self):
        # 1. Initialize Groq (The Brain)
        self.groq_client = Groq(api_key=settings.GROQ_API_KEY)
        
        # 2. Initialize Embeddings (The Translator)
        print(f"Loading AI Model ({settings.EMBEDDING_MODEL})...")
        self.embed_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        print("AI Model Loaded.")

    def get_embedding(self, text: str) -> list:
        """Converts text to vector."""
        return self.embed_model.encode(text).tolist()

    def generate_answer(self, user_query: str, context: str) -> str:
        """Sends prompt to Groq/Llama 3."""
        system_instruction = f"""
        You are an expert Clinical Acupuncture Assistant.
        Your goal is to help a practitioner identify the correct Pattern based on the user's query.
        
        Instructions:
        1. Analyze the User's Query.
        2. Compare it specifically against the provided MEDICAL CONTEXT below.
        3. Suggest the most likely Pattern(s) and explain WHY based on the matching symptoms.
        4. List the Treatment Points for the identified pattern.
        5. Be concise and professional. Do not hallucinate information not in the context.
        
        MEDICAL CONTEXT:
        {context}
        """

        chat_completion = self.groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_query}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.1,
        )
        return chat_completion.choices[0].message.content

# Singleton Instance (Initialized once when app starts)
ai_service = AIHandler()