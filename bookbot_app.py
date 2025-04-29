import json
import openai
import streamlit as st

# Load books
with open('books_data.json', 'r', encoding='utf-8') as f:
    books = json.load(f)

# Set OpenRouter client
client = openai.OpenAI(
    api_key=st.secrets["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1",  # <--- Important
    default_headers={
        "HTTP-Referer": "https://your-app-name.com",  # optional but recommended
        "X-Title": "BookBot"  # optional, your app name
    }
)
# System prompt
system_prompt = """
You are a personal book advisor for the user based on an reading's history of an influencer called An.
You know the influencer's reading history: her books, ratings, genres, reviews, book popularity, and whether she had read the books or just put it in to read list.
Answer questions based ONLY on the influencer's reading history as if the influencer is giving out the recommendation.
If a book is mentioned, you can quote the user's review or rating.
Example:
<user>: Please give me some recommend on thriller books
<Influencer An>: Here are 3 great thriller books I have read and given high rating with one sentence review for each of them.
'<insert book name + author name+ my rating + one sentence review>'. You can also try this thriller book <insert book name + author name> on my to-read list that has a high average rating.
"""

# STOPWORDS = {"i", "want", "some", "the", "is", "are", "in", "at", "and", "about", "to", "of", "for"}

# def search_relevant_books(user_question, books, top_k=20):
#     matches = []
#     question_lower = user_question.lower()
#     words = question_lower.split()
#     keywords = [word for word in words if word not in STOPWORDS]

#     for book in books:
#         text = (str(book.get('Title', '')) + ' ' +
#                 str(book.get('My Review', '')) + ' ' +
#                 str(book.get('Bookshelves', ''))).lower()

#         if any(keyword in text for keyword in keywords):
#             matches.append(book)

#     if not matches:
#         matches = sorted(books, key=lambda x: -x.get('My Rating', 0))

#     return matches[:top_k]

def build_book_context(books):
    context = ""
    for book in books:
        if book.get('My Review'):
            review = str(book.get('My Review', ''))
            short_review = review[:300] + ('...' if len(review) > 300 else '')
            context += f"My Review: {short_review}\n"
        context += f"Title: {str(book.get('Title'))}\n"
        context += f"Author: {str(book.get('Author'))}\n"
        if book.get('My Rating'):
            context += f"My Rating: {book.get('My Rating')}\n"
        if book.get('Bookshelves'):
            context += f"Genres: {str(book.get('Bookshelves'))}\n"
        context += f"Average Rating: {book.get('Average Rating')}\n\n"
    return context

def ask_chatbot(user_question, model_name="tngtech/deepseek-r1t-chimera:free"):
    #relevant_books = search_relevant_books(user_question, books)
    book_context = build_book_context(books)

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"My book data:\n{book_context}\n\nNow answer:\n{user_question}"}
            ],
            temperature=0.6
        )

        if response and response.choices:
            return response.choices[0].message.content.strip()
        else:
            return "(No response received.)"

    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return "(Error calling the AI.)"

# --- Streamlit app ---
st.set_page_config(page_title="an's little forest of books", page_icon="📚", layout="centered")
#Add banner at the top
st.image("banner_2.png", use_container_width=True)
st.markdown("""
    <style>
    .stApp {
        background-color: #f9f9f9;
        padding: 2rem;
    }
    h1 {
        color: #2c3e50;
        font-size: 2.5rem;
        text-align: center;
    }
    .css-1cpxqw2 {
        padding-top: 2rem;
    }
    .stTextInput > div > div > input {
        background-color: #ffffff;
        border: 1px solid #cccccc;
        padding: 0.75rem;
    }
    </style>
""", unsafe_allow_html=True)


st.title("📚 an's little forest of books")
st.caption("Ask me anything about the books I've read!")

# Model selector
model_options = {
     "🚀 Meta Llama4 (Fastest!)": "meta-llama/llama-4-maverick:free",
    "🔎 DeepSeek R1t (Most Accurate)": "tngtech/deepseek-r1t-chimera:free",
    "🧠 Microsoft Mai": "microsoft/mai-ds-r1:free"
}

# Show dropdown with friendly labels
friendly_name = st.selectbox("Choose AI Model", list(model_options.keys()))

# Get the actual model name for use in the API
model_choice = model_options[friendly_name]

# # Input box
# user_input = st.text_input("Your question:", placeholder="Recommend me some children books")

# # Submit button
# if st.button("Ask"):
#     if user_input.strip() != "":
#         with st.spinner('Hang on a second...'):
#             answer = ask_chatbot(user_input, model_name=model_choice)
#         st.success("You can explore all my books at [📚 Goodreads](https://www.goodreads.com/review/list/75616482)")
#         st.markdown(answer)
#     else:
#         st.warning("Please type your question!")



with st.form("question_form"):
    user_input = st.text_input("Your question:", placeholder="Recommend me some children books")
    submitted = st.form_submit_button("Ask")

if submitted: 
    if user_input.strip()!="":
        with st.spinner('Hang on a second...'):
            answer = ask_chatbot(user_input, model_name=model_choice)
        st.success("You can explore all my books at [📚 Goodreads](https://www.goodreads.com/review/list/75616482)")
        st.markdown(answer)
    else:
        st.warning("Please type your question!")