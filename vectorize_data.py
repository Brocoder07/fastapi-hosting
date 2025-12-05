import os
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Load environment variables (ensure you have a .env file with MONGO_URI)
load_dotenv()

# 1. Initialize the Embedding Model (Downloads automatically)
print("Loading AI Model (all-MiniLM-L6-v2)...")
model = SentenceTransformer('all-MiniLM-L6-v2')

# 2. Connect to MongoDB Atlas
mongo_uri = os.getenv("MONGO_URI")
if not mongo_uri:
    raise ValueError("MONGO_URI not found in environment variables")

client = MongoClient(mongo_uri)
db = client.accupuncture_db
collection = db.get_collection("accupuncture_data")

def serialize_pattern(organ, pattern_data):
    """
    Combines clinical data into a single rich text block for the AI to read.
    Format: "Organ: [Name]. Pattern: [Name]. Symptoms: [List]. Treatment: [Points]"
    """
    symptoms_text = ", ".join(pattern_data.get('symptoms', []))
    points_text = ", ".join(pattern_data.get('treatment_points', []))
    pattern_name = pattern_data.get('pattern', 'Unknown')
    
    # This is the "Semantic String" the AI will understand
    return f"Organ: {organ}. Pattern: {pattern_name}. Symptoms: {symptoms_text}. Treatment Points: {points_text}."

def process_and_update():
    # Fetch all organ documents
    documents = list(collection.find({}))
    print(f"Found {len(documents)} organ documents to process.")

    total_patterns = 0
    
    for doc in documents:
        organ_name = doc['organ']
        updated_patterns = []
        
        # We process each pattern *inside* the organ document
        for pattern in doc['patterns']:
            # 1. Create the text representation
            text_to_embed = serialize_pattern(organ_name, pattern)
            
            # 2. Generate Vector (List of 768 floats)
            vector = model.encode(text_to_embed).tolist()
            
            # 3. Save it inside the pattern object
            # We add a new field 'embedding' to the pattern
            pattern['embedding'] = vector
            updated_patterns.append(pattern)
            total_patterns += 1
            
        # 4. Update the document in MongoDB with the new "smart" patterns
        collection.update_one(
            {'_id': doc['_id']},
            {'$set': {'patterns': updated_patterns}}
        )
        print(f"Updated {organ_name} with vectors.")

    print(f"✅ Success! Vectorized {total_patterns} clinical patterns.")

if __name__ == "__main__":
    process_and_update()