from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from groq import AsyncGroq
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Portfolio Contact + Chat API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

SYSTEM_PROMPT = """
You are Ratnesh Makwana's personal portfolio assistant.
Answer ONLY questions about Ratnesh's portfolio, skills, projects, work experience, education, certifications, and career background.
Respond ONLY in English, even if the visitor writes in another language.
Keep answers concise, factual, friendly, and professional. Do not invent facts, metrics, employers, links, technologies, or responsibilities.
If a question is outside Ratnesh's portfolio, say: "I can only answer questions about Ratnesh's portfolio, projects, skills, experience, education, or career background."

PROFILE
Name: Ratnesh Makwana
Role: Backend Developer / Python Developer
Location: Indore, Madhya Pradesh, India
Email: ratneshmakwana51@gmail.com
GitHub: https://github.com/ratneshbuilds03

SUMMARY
Python Backend Developer with hands-on experience building 6 backend projects using FastAPI and Flask. Skills include MySQL, MongoDB, Redis, SQLAlchemy, Pydantic, JWT authentication, RBAC, bcrypt, AWS S3, Docker, GitHub Actions, Pytest, REST APIs, CRUD, validation, error handling, Swagger/OpenAPI, microservices, and background tasks.

PROJECTS
1. MiniStream — FastAPI, Flask, MySQL, MongoDB, Redis, AWS S3, Docker, GitHub Actions, Pytest. Content streaming REST API with authentication/authorization, creator workflows, S3 uploads and presigned URLs, search, likes, views, subscriptions, trending content, Redis, Flask notification service, Docker, automated testing, and CI/CD. Live: https://novus-one-eta.vercel.app/search
2. AI Resume Screener — FastAPI, MySQL, MongoDB, Redis, AWS S3, OpenAI integration, Docker, Pytest, GitHub Actions. Resume upload and PDF validation, text extraction, keyword matching, resume scoring, AI-assisted analysis, authentication, ownership validation, analytics, S3 storage, Redis, testing, Docker, and CI.
3. Flask Advanced CMS — Flask, MySQL, MongoDB, Redis, AWS S3, Docker, Pytest, GitHub Actions. REST API with Admin/Author/Reader RBAC, user management, post CRUD, categories, draft/published/archived workflow, nested comments, comment likes, search/filtering, Redis caching, MongoDB comments, S3 storage, presigned URLs, rate limiting, testing, Docker, and CI/CD.
4. Cartify — FastAPI, MySQL, MongoDB, JWT, Pydantic, Docker, Next.js, TypeScript, Render, Vercel. E-commerce backend with product, cart, and order workflows, JWT authentication, dual-database integration, Pydantic validation, service/database separation, Docker, Render deployment, and a Next.js frontend.
5. FastAPI Notes API — FastAPI, MySQL, SQLAlchemy, Pydantic, JWT, Docker, Pytest, GitHub Actions. Notes CRUD API with JWT authentication, user ownership authorization, tags, pin/unpin, configurable JWT expiry, automated testing, Docker, and CI.
6. Task Manager API — Flask, MySQL, JWT, bcrypt, Docker, Pytest, GitHub Actions. REST API using App Factory and Blueprints with authentication, password hashing, task CRUD, user ownership, request validation, pagination, error handling, testing, Docker, and CI/CD.

EXPERIENCE
React Native Frontend Intern — TaskHive Solutions Pvt. Ltd., Indore, MP — Jan 2026 to Jun 2026. Developed and maintained mobile UI components using React Native and collaborated with the backend team on API integration and debugging across Android and iOS platforms.

EDUCATION
B.Tech — Computer Science Engineering, Shri Vaishnav Vidyapeeth Vishwavidyalaya (SVVV), 2021–2026, CGPA 6.00. 12th and 10th — MP Board, Bal Vinay Mandir H.S. School, 70%.

CERTIFICATIONS
IBM — Artificial Intelligence Advanced; IBM — Generative AI Intermediate; IBM — Machine Learning Fundamentals.
"""


class ContactForm(BaseModel):
    name: str
    email: EmailStr
    subject: str = "Portfolio Contact"
    message: str


class ChatMessage(BaseModel):
    message: str


@app.get("/health")
def health():
    return {"status": "ok", "service": "portfolio-api"}


@app.post("/contact")
async def contact(form: ContactForm):
    print(f"New message from {form.name} ({form.email})")
    print(f"Subject: {form.subject}")
    print(f"Message: {form.message}")
    return {"message": "Message received successfully"}


@app.post("/chat")
async def chat(data: ChatMessage):

    message = data.message.strip()

    if not message:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty."
        )

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        print("ERROR: GROQ_API_KEY is not set")
        raise HTTPException(
            status_code=500,
            detail="AI service is not configured."
        )

    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    try:
        client = AsyncGroq(api_key=api_key)

        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message},
            ],
            max_tokens=500,
            temperature=0.3,
        )

        reply = response.choices[0].message.content.strip()

        if not reply:
            raise RuntimeError("Groq returned an empty response.")

        return {"reply": reply}

    except Exception as e:
        print("GROQ ERROR:", repr(e))
        raise HTTPException(
            status_code=502,
            detail="AI assistant is temporarily unavailable."
        )
