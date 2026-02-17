from fastapi import APIRouter
from app.database import quotes_collection
import random

router = APIRouter(prefix="/api", tags=["Quotes"])

# Seed quotes
SEED_QUOTES = [
    {"text": "Knowledge is a treasure, but practice is the key to it.", "author": "Lao Tzu"},
    {"text": "The beautiful thing about learning is that no one can take it away from you.", "author": "B.B. King"},
    {"text": "Education is the passport to the future.", "author": "Malcolm X"},
    {"text": "Share your knowledge. It is a way to achieve immortality.", "author": "Dalai Lama"},
    {"text": "The mind is not a vessel to be filled, but a fire to be kindled.", "author": "Plutarch"},
    {"text": "Alone we can do so little; together we can do so much.", "author": "Helen Keller"},
    {"text": "Wisdom is not a product of schooling but of the lifelong attempt to acquire it.", "author": "Albert Einstein"},
    {"text": "Live as if you were to die tomorrow. Learn as if you were to live forever.", "author": "Mahatma Gandhi"},
    {"text": "The more that you read, the more things you will know.", "author": "Dr. Seuss"},
    {"text": "Change is the end result of all true learning.", "author": "Leo Buscaglia"},
    {"text": "Knowledge is power. Information is liberating.", "author": "Kofi Annan"},
    {"text": "Develop a passion for learning. If you do, you will never cease to grow.", "author": "Anthony D'Angelo"},
    {"text": "Learning never exhausts the mind.", "author": "Leonardo da Vinci"},
    {"text": "The best way to predict your future is to create it.", "author": "Peter Drucker"},
    {"text": "Education breeds confidence. Confidence breeds hope.", "author": "Confucius"},
]


def seed_quotes():
    """Insert quotes if collection is empty."""
    if quotes_collection.count_documents({}) == 0:
        quotes_collection.insert_many(SEED_QUOTES)
        print("✅ Seeded quotes collection")


@router.get("/quotes/random")
def get_random_quote():
    count = quotes_collection.count_documents({})
    if count == 0:
        return {"text": "Sharing knowledge is the first step toward collective growth.", "author": "EduHub"}
    
    rand_index = random.randint(0, count - 1)
    quote = quotes_collection.find().skip(rand_index).limit(1)
    quote = list(quote)[0]
    quote["_id"] = str(quote["_id"])
    return quote
