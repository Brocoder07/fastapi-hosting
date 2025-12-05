from groq import Groq
from fastembed import TextEmbedding
from ..config import settings

class AIHandler:
    def __init__(self):
        # 1. Initialize Groq
        self.groq_client = Groq(api_key=settings.GROQ_API_KEY)
        
        # 2. Initialize FastEmbed (Lightweight ONNX)
        print(f"Loading AI Model ({settings.EMBEDDING_MODEL})...")
        # fastembed downloads and caches the quantized model automatically
        self.embed_model = TextEmbedding(model_name=settings.EMBEDDING_MODEL)
        print("AI Model Loaded.")

    def get_embedding(self, text: str) -> list:
        """Converts text to vector using ONNX."""
        # FastEmbed expects a list of documents and returns a generator
        # We wrap 'text' in a list, get the generator, convert to list, take the first item
        embedding_generator = self.embed_model.embed([text])
        vector = list(embedding_generator)[0]
        return vector.tolist() # Convert numpy array to standard list

    def generate_answer(self, user_query: str, context: str) -> str:
        # ... (This method remains exactly the same as before) ...
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

ai_service = AIHandler()
