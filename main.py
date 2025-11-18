import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from database import db, create_document, get_documents
from schemas import Course, Lesson, Enrollment, Review

app = FastAPI(title="E-Learning API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "E-Learning Backend Running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"

    return response


# -----------------------------
# Course Catalog Endpoints
# -----------------------------

@app.post("/api/courses", response_model=dict)
async def create_course(course: Course):
    try:
        course_id = create_document("course", course)
        return {"id": course_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/courses", response_model=List[dict])
async def list_courses(tag: Optional[str] = None, q: Optional[str] = None, limit: int = 50):
    try:
        filter_dict = {}
        if tag:
            filter_dict["tags"] = {"$in": [tag]}
        if q:
            filter_dict["$or"] = [
                {"title": {"$regex": q, "$options": "i"}},
                {"subtitle": {"$regex": q, "$options": "i"}},
                {"description": {"$regex": q, "$options": "i"}},
                {"tags": {"$regex": q, "$options": "i"}},
            ]
        courses = get_documents("course", filter_dict, limit)
        return courses
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/courses/{course_id}", response_model=dict)
async def get_course(course_id: str):
    try:
        from bson import ObjectId
        if not ObjectId.is_valid(course_id):
            raise HTTPException(status_code=400, detail="Invalid course ID")
        docs = get_documents("course", {"_id": ObjectId(course_id)}, limit=1)
        if not docs:
            raise HTTPException(status_code=404, detail="Course not found")
        return docs[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------
# Lessons
# -----------------------------

@app.post("/api/lessons", response_model=dict)
async def create_lesson(lesson: Lesson):
    try:
        lesson_id = create_document("lesson", lesson)
        return {"id": lesson_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/courses/{course_id}/lessons", response_model=List[dict])
async def list_lessons(course_id: str):
    try:
        lessons = get_documents("lesson", {"course_id": course_id}, limit=200)
        lessons = sorted(lessons, key=lambda x: x.get("order", 0))
        return lessons
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------
# Enrollment
# -----------------------------

@app.post("/api/enroll", response_model=dict)
async def enroll(enrollment: Enrollment):
    try:
        en_id = create_document("enrollment", enrollment)
        return {"id": en_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/courses/{course_id}/enrollments", response_model=List[dict])
async def list_enrollments(course_id: str):
    try:
        docs = get_documents("enrollment", {"course_id": course_id}, limit=500)
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------
# Reviews
# -----------------------------

@app.post("/api/reviews", response_model=dict)
async def create_review(review: Review):
    try:
        rev_id = create_document("review", review)
        return {"id": rev_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/courses/{course_id}/reviews", response_model=List[dict])
async def list_reviews(course_id: str):
    try:
        docs = get_documents("review", {"course_id": course_id}, limit=200)
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------
# Seed Demo Content (for quick start)
# -----------------------------

@app.post("/api/seed")
async def seed_demo():
    try:
        # Only seed if there are no courses yet
        existing = get_documents("course", {}, limit=1)
        if existing:
            return {"status": "ok", "message": "Courses already exist"}

        demo_courses = [
            Course(
                title="React for Beginners",
                subtitle="Build dynamic UIs with hooks",
                description="Learn the fundamentals of React, components, hooks, and state management by building hands-on projects.",
                instructor_name="Alex Johnson",
                instructor_email="alex@example.com",
                price=19.99,
                thumbnail_url="https://images.unsplash.com/photo-1526378722484-bd91ca387e72?w=800&q=80&auto=format&fit=crop",
                tags=["react", "frontend", "javascript"],
                level="Beginner"
            ),
            Course(
                title="FastAPI Bootcamp",
                subtitle="Modern APIs with Python",
                description="Create high-performance APIs with FastAPI, Pydantic, and MongoDB. Includes deployment tips.",
                instructor_name="Samantha Lee",
                instructor_email="sam@example.com",
                price=24.99,
                thumbnail_url="https://images.unsplash.com/photo-1518779578993-ec3579fee39f?w=800&q=80&auto=format&fit=crop",
                tags=["python", "api", "backend"],
                level="Intermediate"
            ),
            Course(
                title="Design Systems 101",
                subtitle="Build cohesive UI libraries",
                description="From typography to components, learn how to create maintainable design systems.",
                instructor_name="Taylor Kim",
                instructor_email="taylor@example.com",
                price=0.0,
                thumbnail_url="https://images.unsplash.com/photo-1529336953121-ad5a0d43d0d2?w=800&q=80&auto=format&fit=crop",
                tags=["design", "ui", "ux"],
                level="All Levels"
            ),
        ]

        created_ids = []
        for idx, c in enumerate(demo_courses):
            cid = create_document("course", c)
            created_ids.append(cid)
            # Create 3 demo lessons per course
            for l_idx in range(1, 4):
                create_document(
                    "lesson",
                    Lesson(
                        course_id=cid,
                        title=f"Lesson {l_idx}: Topic Overview",
                        content=f"This is the content for lesson {l_idx}. You'll learn key concepts and apply them in a mini project.",
                        video_url=None,
                        order=l_idx,
                    ),
                )

        return {"status": "ok", "created_courses": created_ids}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
